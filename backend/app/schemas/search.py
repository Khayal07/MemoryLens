"""Search DTOs — the contract between the pipeline and the API (Phase 5). The first
result is the best match; the rest are alternatives. `suggestion` carries the soft
category-mismatch nudge (never an automatic switch)."""

from datetime import datetime

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    category: str
    query: str = Field(min_length=3, max_length=1000)


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
    # Id of the persisted search row — the client attaches result feedback to it.
    # 0 until the search is recorded (set by the service, not the pipeline).
    search_id: int = 0
    results: list[ResultItem] = Field(default_factory=list)
    suggestion: MismatchSuggestion | None = None


class SearchSummary(BaseModel):
    id: int
    category: str
    query: str
    created_at: datetime
    result_count: int
