"""Ports (interfaces) for the AI layer. Concrete implementations live alongside
and are wired by dependency injection, so any stage is swappable (SOLID: DIP)."""

from typing import Protocol, runtime_checkable


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
