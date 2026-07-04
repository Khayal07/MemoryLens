"""Search pipeline orchestrator — wires every stage:

validate → clean → resolve category → hybrid retrieve → rerank → LLM reason →
confidence → alternatives → mismatch suggestion → response.

The LLM only selects/explains among grounded candidates; results are always real
catalog items. Confidence is computed from blended signals, not the model's claim."""

from functools import lru_cache

import structlog
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.cleaning import clean_query, validate_query
from app.ai.confidence import compute_confidence
from app.ai.identify import IdentifyParseError, parse_identification
from app.ai.llm import LLMClient, LLMError
from app.ai.prompts import hyde, identify
from app.ai.prompts.reasoning import SYSTEM_PROMPT, build_user_prompt
from app.ai.reasoning import LLMReasoning, ReasoningParseError, parse_reasoning
from app.ai.reranker import get_reranker
from app.ai.retriever import HybridRetriever
from app.ai.types import Candidate
from app.core.config import get_settings
from app.domain.categories import CATEGORY_KEYS
from app.infra.models import Category
from app.schemas.search import MismatchSuggestion, ResultItem, SearchResponse

log = structlog.get_logger()

_REPAIR_HINT = "\n\nIMPORTANT: respond with ONLY valid JSON of the required shape."


class SearchPipeline:
    def __init__(
        self,
        retriever,
        reranker,
        llm,
        rerank_top_n: int = 12,
        hyde_enabled: bool = True,
        freeform_enabled: bool = True,
        freeform_confidence_floor: float = 65.0,
    ) -> None:
        self.retriever = retriever
        self.reranker = reranker
        self.llm = llm
        self.rerank_top_n = rerank_top_n
        self.hyde_enabled = hyde_enabled
        self.freeform_enabled = freeform_enabled
        self.freeform_confidence_floor = freeform_confidence_floor

    def run(
        self, db: Session, category_key: str, query: str, max_results: int = 5
    ) -> SearchResponse:
        validate_query(query)
        cleaned = clean_query(query)
        category = self._resolve_category(db, category_key)

        embed_text = self._expand_query(category, cleaned)
        candidates = self.retriever.search(db, category.id, cleaned, k=30, embed_text=embed_text)

        if not candidates:
            # Nothing in the catalog resembled the memory — let the LLM name it.
            results = self._maybe_add_freeform(category, cleaned, [], max_results)
            return SearchResponse(query=query, category=category_key, results=results)

        reranked = self.reranker.rerank(cleaned, candidates, top_n=self.rerank_top_n)
        reasoning = self._reason(category, cleaned, reranked)
        results, suggestion = self._build_results(category_key, reranked, reasoning, max_results)
        results = self._maybe_add_freeform(category, cleaned, results, max_results)
        return SearchResponse(
            query=query, category=category_key, results=results, suggestion=suggestion
        )

    def _expand_query(self, category: Category, query: str) -> str:
        """HyDE: ask the LLM for a hypothetical catalog description and append it to the
        query for the semantic leg. Best-effort — on any failure fall back to the query
        alone so retrieval never depends on the network."""
        if not self.hyde_enabled:
            return query
        try:
            system = hyde.SYSTEM_PROMPT.format(category=category.display_name)
            user = hyde.build_user_prompt(category.display_name, query)
            hypothesis = self.llm.complete_text(system, user).strip()
        except LLMError as exc:
            log.warning("pipeline.hyde_failed", error=str(exc))
            return query
        if not hypothesis:
            return query
        return f"{query}\n{hypothesis}"

    def _resolve_category(self, db: Session, category_key: str) -> Category:
        category = db.execute(
            select(Category).where(Category.key == category_key)
        ).scalar_one_or_none()
        if category is None:
            raise ValueError(f"Unknown category '{category_key}'")
        return category

    def _reason(
        self, category: Category, query: str, candidates: list[Candidate]
    ) -> LLMReasoning | None:
        """Call the LLM and parse strict JSON; retry once with a repair hint, then
        give up (the pipeline falls back to rerank order)."""
        user = build_user_prompt(category.display_name, sorted(CATEGORY_KEYS), query, candidates)
        for attempt in range(2):
            try:
                raw = self.llm.complete_json(
                    SYSTEM_PROMPT, user if attempt == 0 else user + _REPAIR_HINT
                )
                return parse_reasoning(raw)
            except ReasoningParseError:
                log.warning("pipeline.reasoning_parse_failed", attempt=attempt)
            except LLMError as exc:
                log.warning("pipeline.llm_failed", error=str(exc))
                return None
        return None

    def _maybe_add_freeform(
        self, category, query: str, results: list[ResultItem], max_results: int
    ) -> list[ResultItem]:
        """When the grounded catalog gives no confident match, ask the LLM to name the
        real item from its own knowledge and promote that answer to the top. The weak
        catalog matches are kept below as alternatives."""
        if not self.freeform_enabled:
            return results
        top = max((r.confidence for r in results), default=0.0)
        if top >= self.freeform_confidence_floor:
            return results
        item = self._identify_freeform(category, query)
        if item is None:
            return results
        return [item, *results][:max_results]

    def _identify_freeform(self, category, query: str) -> ResultItem | None:
        """Ungrounded identification: the LLM names the most likely real title. Returns
        None on any failure or when the model can't identify anything."""
        try:
            system = identify.SYSTEM_PROMPT.format(category=category.display_name)
            user = identify.build_user_prompt(category.display_name, query)
            ident = parse_identification(self.llm.complete_json(system, user))
        except (LLMError, IdentifyParseError) as exc:
            log.warning("pipeline.identify_failed", error=str(exc))
            return None
        if not ident.title.strip():
            return None
        # Ungrounded, so cap below certainty and flag the source for the UI.
        confidence = round(min(ident.confidence, 0.9) * 100, 1)
        description = ident.detail or "Identified from world knowledge — not in the catalog."
        return ResultItem(
            item_id=0,
            title=ident.title.strip(),
            description=description,
            image_url=None,
            source_url=None,
            metadata={"source": "gpt-knowledge", "detail": ident.detail},
            confidence=confidence,
            reason=ident.reason or None,
        )

    def _build_results(
        self,
        category_key: str,
        reranked: list[Candidate],
        reasoning: LLMReasoning | None,
        max_results: int,
    ) -> tuple[list[ResultItem], MismatchSuggestion | None]:
        by_id = {c.item_id: c for c in reranked}
        max_retrieval = max((c.retrieval_score for c in reranked), default=0.0)
        results: list[ResultItem] = []

        if reasoning and reasoning.matches:
            for match in reasoning.matches:
                cand = by_id.get(match.item_id)
                if cand is None:
                    continue  # ignore any id the model invented
                results.append(
                    self._to_result(
                        cand,
                        compute_confidence(
                            match.rating, cand.rerank_score, cand.retrieval_score, max_retrieval
                        ),
                        match.reason,
                    )
                )

        if not results:
            # Fallback: trust the deterministic rerank order, no LLM reasons.
            for cand in reranked[:max_results]:
                results.append(
                    self._to_result(
                        cand,
                        compute_confidence(
                            0.5, cand.rerank_score, cand.retrieval_score, max_retrieval
                        ),
                        None,
                    )
                )

        return results[:max_results], self._validate_mismatch(category_key, reasoning)

    @staticmethod
    def _to_result(cand: Candidate, confidence: float, reason: str | None) -> ResultItem:
        return ResultItem(
            item_id=cand.item_id,
            title=cand.title,
            description=cand.description,
            image_url=cand.image_url,
            source_url=cand.source_url,
            metadata=cand.metadata,
            confidence=confidence,
            reason=reason,
        )

    @staticmethod
    def _validate_mismatch(
        category_key: str, reasoning: LLMReasoning | None
    ) -> MismatchSuggestion | None:
        if not reasoning or not reasoning.category_mismatch:
            return None
        suspected = reasoning.category_mismatch.suspected_category
        if suspected not in CATEGORY_KEYS or suspected == category_key:
            return None
        return MismatchSuggestion(
            suspected_category=suspected, message=reasoning.category_mismatch.message
        )


@lru_cache
def get_pipeline() -> SearchPipeline:
    """Build the default pipeline. Heavy local models load on first construction."""
    settings = get_settings()
    return SearchPipeline(
        HybridRetriever(),
        get_reranker(),
        LLMClient(),
        rerank_top_n=settings.rerank_top_n,
        hyde_enabled=settings.hyde_enabled,
        freeform_enabled=settings.freeform_enabled,
        freeform_confidence_floor=settings.freeform_confidence_floor,
    )
