"""Constellation DTOs — the user's found/saved items as a similarity star map."""

from pydantic import BaseModel, Field


class ConstellationNode(BaseModel):
    id: int
    title: str
    category: str
    image_url: str | None = None
    source_url: str | None = None
    # How many of the user's searches surfaced this item (saved-only items → 1).
    seen_count: int = 1


class ConstellationEdge(BaseModel):
    a: int
    b: int
    # Cosine similarity 0..1 between the two items' embeddings.
    weight: float = Field(ge=0.0, le=1.0)


class ConstellationResponse(BaseModel):
    nodes: list[ConstellationNode] = Field(default_factory=list)
    edges: list[ConstellationEdge] = Field(default_factory=list)
