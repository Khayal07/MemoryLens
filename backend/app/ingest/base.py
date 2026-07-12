"""Ingestion ports. Each category is ingested through a CategoryAdapter that
fetches raw data from a source and normalizes it to a common shape. Adding a new
category = add an adapter; the runner and search pipeline are untouched (OCP)."""

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class NormalizedItem:
    """Source-agnostic representation of one catalog entry."""

    external_id: str
    title: str
    description: str
    image_url: str | None = None
    source_url: str | None = None
    metadata: dict = field(default_factory=dict)

    def embedding_text(self) -> str:
        """Text fed to the embedder (and the keyword tsvector). Title carries the most
        signal; description adds the plot/attribute details users tend to half-remember.
        Songs also fold in the artist so "<lyric> by <artist>" style memories match —
        only songs carry `artist`, so every other category is byte-identical."""
        artist = (self.metadata or {}).get("artist")
        if artist:
            return f"{self.title}. {artist}. {self.description}".strip()
        return f"{self.title}. {self.description}".strip()


class CategoryAdapter(Protocol):
    category_key: str

    def fetch(self, limit: int) -> Iterable[NormalizedItem]:
        ...
