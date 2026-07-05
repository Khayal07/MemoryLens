"""Item DTOs. `SimilarItem` is the lean shape for the "more like this" section — a
catalog neighbour with no confidence/reason (there is no query to explain against)."""

from pydantic import BaseModel, Field


class SimilarItem(BaseModel):
    item_id: int
    title: str
    description: str = ""
    image_url: str | None = None
    source_url: str | None = None
    metadata: dict = Field(default_factory=dict)
