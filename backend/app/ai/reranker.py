"""Cross-encoder reranker. Unlike the bi-encoder embedder (which scores query and
document independently), a cross-encoder reads (query, candidate) together, giving
much sharper relevance — but it's expensive, so we only run it on the fused top-N.
Local model → free and deterministic."""

from functools import lru_cache

from app.ai.types import Candidate
from app.core.config import get_settings


class CrossEncoderReranker:
    def __init__(self, model_name: str) -> None:
        from sentence_transformers import CrossEncoder

        self._model = CrossEncoder(model_name)

    def rerank(self, query: str, candidates: list[Candidate], top_n: int = 8) -> list[Candidate]:
        if not candidates:
            return []
        pairs = [(query, c.rerank_text()) for c in candidates]
        scores = self._model.predict(pairs)
        for candidate, score in zip(candidates, scores, strict=True):
            candidate.rerank_score = float(score)
        ranked = sorted(candidates, key=lambda c: c.rerank_score or 0.0, reverse=True)
        return ranked[:top_n]


@lru_cache
def get_reranker() -> CrossEncoderReranker:
    return CrossEncoderReranker(get_settings().reranker_model)
