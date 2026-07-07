"""Search pipeline orchestrator — wires every stage:

validate → clean → resolve category → hybrid retrieve → rerank → LLM reason →
confidence → alternatives → mismatch suggestion → response.

The LLM only selects/explains among grounded candidates; results are always real
catalog items. Confidence is computed from blended signals, not the model's claim."""

import re
import urllib.parse
from functools import lru_cache

import structlog
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.cleaning import clean_query, validate_query
from app.ai.confidence import compute_confidence
from app.ai.identify import IdentifyParseError, parse_identification
from app.ai.llm import LLMClient, LLMError
from app.ai.prompts import hyde, identify, translate
from app.ai.prompts.reasoning import SYSTEM_PROMPT, build_user_prompt
from app.ai.reasoning import LLMReasoning, ReasoningParseError, parse_reasoning
from app.ai.reranker import get_reranker
from app.ai.retriever import HybridRetriever
from app.ai.types import Candidate
from app.core.config import get_settings
from app.domain.categories import CATEGORY_KEYS
from app.infra.models import Category, Item
from app.infra.itunes import fetch_song_cover
from app.infra.omdb import fetch_poster
from app.infra.openlibrary import fetch_book_cover
from app.infra.rawg import fetch_game_image
from app.infra.tmdb import fetch_person_image
from app.schemas.search import MismatchSuggestion, ResultItem, SearchResponse

log = structlog.get_logger()

_REPAIR_HINT = "\n\nIMPORTANT: respond with ONLY valid JSON of the required shape."
# Anything outside 7-bit ASCII implies a non-English memory worth translating for
# the English-only local retrieval/rerank models (Azerbaijani ə, ğ, ş, ç, ö, ü, ı …).
_NON_ASCII = re.compile(r"[^\x00-\x7f]")
# MemoryLens only targets Latin-script languages (English, Azerbaijani). Cyrillic in
# an LLM reply is always a nano language slip — scrub it unless the memory itself
# was Cyrillic (a genuine Russian query still gets Russian answers).
_CYRILLIC = re.compile(r"[Ѐ-ӿ]")
# Categories OMDb can poster (film/series) and the year pattern in a free-form detail.
_OMDB_KIND = {"movies": "movie", "tv": "series"}
# Person categories: a free-form answer here is someone's name, so its "poster" is a
# TMDB profile photo (searched by name) rather than an OMDb film poster.
_PERSON_KEYS = {"actors"}
# Music categories: a free-form answer's "poster" is iTunes album cover art.
_SONG_KEYS = {"songs"}
# Book categories: OpenLibrary cover art. Game categories: RAWG key art.
_BOOK_KEYS = {"books"}
_GAME_KEYS = {"games"}
_YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
# Shown when the LLM picks a grounded match but returns no explanation for it.
_FALLBACK_REASON = "A close match in the catalog for your memory."
# Generic role labels a free-form `detail` may carry next to the real creator name, so
# _artist_from skips them when hunting for the artist/author.
_ROLE_WORDS = {
    "author", "artist", "band", "song", "singer", "singer-songwriter", "writer",
    "composer", "novel", "book", "film", "movie", "director", "actor", "actress",
}


def _is_language_slip(text: str | None, query: str) -> bool:
    """True when an LLM reply drifted to a different language than the memory — a nano
    slip we scrub so the UI never shows a foreign explanation. Two cases:
    - Cyrillic reply to a non-Cyrillic memory (a genuine Russian query keeps Russian).
    - Non-ASCII reply (e.g. Portuguese "é uma série") to a plain-English (ASCII) memory;
      an in-language answer to a non-ASCII memory (Azerbaijani, etc.) is left untouched."""
    if not text:
        return False
    if _CYRILLIC.search(text) and not _CYRILLIC.search(query):
        return True
    if query.isascii() and not text.isascii():
        return True
    return False


def _year_from(detail: str | None) -> str | None:
    """Pull the first 4-digit year out of a free-form detail like "1957 / Lumet"."""
    match = _YEAR_RE.search(detail or "")
    return match.group(0) if match else None


def _artist_from(detail: str | None) -> str | None:
    """Pull the creator (artist/author) out of a free-form detail to sharpen a cover-art
    search. Details vary — "OneRepublic, 2013", "1925 / Franz Kafka / author",
    "George Orwell / 1949" — so split on commas AND slashes and return the first segment
    that's neither a bare year nor a generic role word."""
    for part in re.split(r"[,/]", detail or ""):
        p = part.strip()
        if p and not _YEAR_RE.fullmatch(p) and p.lower() not in _ROLE_WORDS:
            return p
    return None


def _slug(title: str) -> str:
    """Lowercase, keep [a-z0-9], collapse everything else to single hyphens, and cap
    length so `gpt:<slug>` stays inside the external_id String(128) column."""
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:120] or "untitled"


def _same_title(a: str, b: str) -> bool:
    """Loose title equality for grey-zone freeform vs grounded comparison: slug-normalize
    and treat one being contained in the other as a match (so "Hello" ≈ "Hello from the
    Other Side", but "We Will Rock You" ≠ "Don't Stop Believin'")."""
    sa, sb = _slug(a), _slug(b)
    return sa == sb or sa in sb or sb in sa


def _google_url(title: str, category: Category) -> str:
    """A best-effort 'View source' for an answer that isn't in the catalog: a Google
    search for the title within its category."""
    q = urllib.parse.quote_plus(f"{title} {category.display_name}")
    return f"https://www.google.com/search?q={q}"


class SearchPipeline:
    def __init__(
        self,
        retriever,
        reranker,
        llm,
        rerank_top_n: int = 12,
        hyde_enabled: bool = True,
        translate_enabled: bool = True,
        freeform_enabled: bool = True,
        freeform_confidence_floor: float = 65.0,
        freeform_grey_margin: float = 8.0,
    ) -> None:
        self.retriever = retriever
        self.reranker = reranker
        self.llm = llm
        self.rerank_top_n = rerank_top_n
        self.hyde_enabled = hyde_enabled
        self.translate_enabled = translate_enabled
        self.freeform_enabled = freeform_enabled
        self.freeform_confidence_floor = freeform_confidence_floor
        self.freeform_grey_margin = freeform_grey_margin

    def run(
        self, db: Session, category_key: str, query: str, max_results: int = 5
    ) -> SearchResponse:
        validate_query(query)
        cleaned = clean_query(query)
        category = self._resolve_category(db, category_key)

        # English key for the local (English-only) retrieval + rerank models; the
        # original `cleaned` text still drives reasoning so answers stay in-language.
        retrieval_query = self._to_retrieval_query(cleaned)
        embed_text = self._expand_query(category, retrieval_query)
        candidates = self.retriever.search(
            db, category.id, retrieval_query, k=30, embed_text=embed_text
        )

        if not candidates:
            # Nothing in the catalog resembled the memory — let the LLM name it.
            results = self._maybe_add_freeform(db, category, cleaned, [], max_results)
            return SearchResponse(query=query, category=category_key, results=results)

        reranked = self.reranker.rerank(retrieval_query, candidates, top_n=self.rerank_top_n)
        reasoning = self._reason(category, cleaned, reranked)
        results, suggestion = self._build_results(
            category_key, cleaned, reranked, reasoning, max_results
        )
        results = self._maybe_add_freeform(db, category, cleaned, results, max_results)
        return SearchResponse(
            query=query, category=category_key, results=results, suggestion=suggestion
        )

    def _to_retrieval_query(self, query: str) -> str:
        """Translate a non-English memory to English for the local retrieval/rerank
        models. Skipped for plain-ASCII (English) text; best-effort — any LLM failure
        falls back to the raw query so retrieval never depends on the network."""
        if not self.translate_enabled or not _NON_ASCII.search(query):
            return query
        try:
            english = self.llm.complete_text(translate.SYSTEM_PROMPT, query).strip()
        except LLMError as exc:
            log.warning("pipeline.translate_failed", error=str(exc))
            return query
        return english or query

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
        self, db: Session, category, query: str, results: list[ResultItem], max_results: int
    ) -> list[ResultItem]:
        """When the grounded catalog gives no confident match, ask the LLM to name the
        real item from its own knowledge and promote that answer to the top. The weak
        catalog matches are kept below as alternatives."""
        if not self.freeform_enabled:
            return results
        top = max((r.confidence for r in results), default=0.0)
        if top >= self.freeform_confidence_floor + self.freeform_grey_margin:
            return results  # confident grounded match — trust the catalog, skip the LLM
        item = self._identify_freeform(db, category, query)
        if item is None:
            return results
        # Grey zone (floor ≤ top < floor+margin): a grounded match exists but is shaky.
        # Only let the world-knowledge answer displace it when it names a *different*
        # title — that's the signal the catalog pick was wrong (e.g. "We Will Rock You"
        # grounded to "Don't Stop Believin'"). Same title → keep the grounded row so its
        # real poster/source survive.
        if top >= self.freeform_confidence_floor and results:
            if _same_title(item.title, results[0].title):
                return results
        return [item, *results][:max_results]

    def _identify_freeform(self, db: Session, category, query: str) -> ResultItem | None:
        """Ungrounded identification: the LLM names the most likely real title. The
        answer is materialized as a lightweight catalog row (no embedding, so it stays
        out of retrieval) which gives it a real item_id — the UI can then save it to a
        collection and vote on it like any grounded result. Returns None on any failure
        or when the model can't identify anything."""
        try:
            system = identify.SYSTEM_PROMPT.format(category=category.display_name)
            user = identify.build_user_prompt(category.display_name, query)
            ident = parse_identification(self.llm.complete_json(system, user))
        except (LLMError, IdentifyParseError) as exc:
            log.warning("pipeline.identify_failed", error=str(exc))
            return None
        title = ident.title.strip()
        if not title:
            return None
        # Ungrounded, so cap below certainty and flag the source for the UI.
        confidence = round(min(ident.confidence, 0.9) * 100, 1)
        description = ident.detail or "Identified from world knowledge — not in the catalog."
        # The free-form hero has no catalog poster; give the prominent Best Match a real
        # image so it isn't a blank frame, from the right source per category. Best-effort.
        image_url = None
        kind = _OMDB_KIND.get(category.key)
        if kind:
            image_url = fetch_poster(title, _year_from(ident.detail), kind)  # films/series
        elif category.key in _PERSON_KEYS:
            image_url = fetch_person_image(title)  # TMDB profile photo
        elif category.key in _SONG_KEYS:
            image_url = fetch_song_cover(title, _artist_from(ident.detail))  # iTunes art
        elif category.key in _BOOK_KEYS:
            image_url = fetch_book_cover(title, _artist_from(ident.detail))  # OpenLibrary
        elif category.key in _GAME_KEYS:
            image_url = fetch_game_image(title)  # RAWG key art
        reason = ident.reason or None
        if _is_language_slip(reason, query):
            reason = None

        metadata = {"source": "gpt-knowledge", "detail": ident.detail}
        source_url = _google_url(title, category)
        item_id = self._materialize_freeform(
            db, category, title, description, image_url, source_url, metadata
        )
        return ResultItem(
            item_id=item_id,
            title=title,
            description=description,
            image_url=image_url,
            source_url=source_url,
            metadata=metadata,
            confidence=confidence,
            reason=reason,
        )

    @staticmethod
    def _materialize_freeform(
        db: Session,
        category,
        title: str,
        description: str,
        image_url: str | None,
        source_url: str,
        metadata: dict,
    ) -> int:
        """Find-or-create a catalog row for a free-form answer, keyed by
        (category_id, "gpt:<slug>") so repeated searches reuse one row. No embedding is
        created, so the row is invisible to retrieval. Falls back to item_id=0 on any DB
        error so a search never fails on a materialize hiccup."""
        external_id = f"gpt:{_slug(title)}"
        try:
            item = db.execute(
                select(Item).where(
                    Item.category_id == category.id, Item.external_id == external_id
                )
            ).scalar_one_or_none()
            if item is None:
                item = Item(
                    category_id=category.id,
                    external_id=external_id,
                    title=title,
                    description=description,
                    item_metadata=metadata,
                    image_url=image_url,
                    source_url=source_url,
                )
                db.add(item)
            elif image_url and not item.image_url:
                item.image_url = image_url  # backfill a poster we now have
            db.flush()
            return item.id
        except Exception as exc:  # pragma: no cover - defensive
            log.warning("pipeline.materialize_failed", error=str(exc))
            db.rollback()
            return 0

    def _build_results(
        self,
        category_key: str,
        query: str,
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
                reason = None if _is_language_slip(match.reason, query) else match.reason
                if not (reason and reason.strip()) and query.isascii():
                    # nano sometimes omits the reason for an obvious match (e.g. an
                    # actor). Show a neutral English line rather than a blank one; a
                    # non-ASCII (in-language) memory is left as-is to avoid a language mix.
                    reason = _FALLBACK_REASON
                results.append(
                    self._to_result(
                        cand,
                        compute_confidence(
                            match.rating, cand.rerank_score, cand.retrieval_score, max_retrieval
                        ),
                        reason,
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

        return results[:max_results], self._validate_mismatch(category_key, query, reasoning)

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
        category_key: str, query: str, reasoning: LLMReasoning | None
    ) -> MismatchSuggestion | None:
        if not reasoning or not reasoning.category_mismatch:
            return None
        suspected = reasoning.category_mismatch.suspected_category
        if suspected not in CATEGORY_KEYS or suspected == category_key:
            return None
        message = reasoning.category_mismatch.message
        if _is_language_slip(message, query):
            message = ""  # frontend banner falls back to a neutral template
        return MismatchSuggestion(suspected_category=suspected, message=message)


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
        translate_enabled=settings.translate_enabled,
        freeform_enabled=settings.freeform_enabled,
        freeform_confidence_floor=settings.freeform_confidence_floor,
        freeform_grey_margin=settings.freeform_grey_margin,
    )
