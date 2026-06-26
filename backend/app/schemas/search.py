"""Search DTOs — the contract between the pipeline and the API (Phase 5). The first
result is the best match; the rest are alternatives. `suggestion` carries the soft
category-mismatch nudge (never an automatic switch)."""

from pydantic import BaseModel, Field


class ResultItem(BaseModel):
    item_id: int
    title: str
    description: str
    image_url: str | None = None
    source_url: str | None = None
    metadata: dict = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=100.0)
    reason: str | None = None


class MismatchSuggestion(BaseModel):
    suspected_category: str
    message: str


class SearchResponse(BaseModel):
    query: str
    category: str
    results: list[ResultItem] = Field(default_factory=list)
    suggestion: MismatchSuggestion | None = None
