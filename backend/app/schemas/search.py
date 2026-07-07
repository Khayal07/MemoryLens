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
    # Per-signal contribution (percentage points) behind `confidence`: llm/rerank/
    # retrieval for grounded rows, ai_knowledge for free-form, feedback when votes
    # nudged it. None on legacy cached responses.
    breakdown: dict[str, float] | None = None
    # Free-form only: the model's own sentence on why it is this confident.
    confidence_note: str | None = None


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
    # Akinator mode: ONE follow-up question attached when the grounded match is weak;
    # the client re-searches with the answer folded into the query. None when confident.
    clarifying_question: str | None = None


class SearchSummary(BaseModel):
    id: int
    category: str
    query: str
    created_at: datetime
    result_count: int
    # Best match from the response snapshot, for the history timeline view.
    # None on searches that predate the snapshot column.
    top_title: str | None = None
    top_image: str | None = None
    top_confidence: float | None = None


class ShareResponse(BaseModel):
    token: str
