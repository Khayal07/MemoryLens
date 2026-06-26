"""Ports (interfaces) for the AI layer. Concrete implementations live alongside
and are wired by dependency injection, so any stage is swappable (SOLID: DIP)."""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.ai.types import Candidate


@runtime_checkable
class Embedder(Protocol):
    """Turns text into dense vectors for semantic retrieval."""

    dim: int

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of documents."""
        ...

    def embed_query(self, text: str) -> list[float]:
        """Embed a single search query (may use a query-specific instruction)."""
        ...


class Retriever(Protocol):
    """Returns category-grounded candidates for a query."""

    def search(
        self, db: "Session", category_id: int, query: str, k: int = 30
    ) -> "list[Candidate]":
        ...


class Reranker(Protocol):
    """Re-orders candidates by (query, candidate) relevance, keeping the top N."""

    def rerank(
        self, query: str, candidates: "list[Candidate]", top_n: int = 8
    ) -> "list[Candidate]":
        ...
