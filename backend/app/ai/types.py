"""Shared AI-layer data types. Kept in their own module so retriever and reranker
can both depend on them without importing each other."""

from dataclasses import dataclass, field


@dataclass
class Candidate:
    """One retrieved catalog item flowing through the search pipeline.

    `retrieval_score` is the hybrid fusion score; `rerank_score` is filled by the
    cross-encoder. Phase 4 blends these (plus the LLM's rating) into a confidence."""

    item_id: int
    title: str
    description: str
    image_url: str | None = None
    source_url: str | None = None
    metadata: dict = field(default_factory=dict)
    retrieval_score: float = 0.0
    rerank_score: float | None = None

    def rerank_text(self) -> str:
        return f"{self.title}. {self.description}".strip()
