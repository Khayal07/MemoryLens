"""Analytics DTOs — a global usage overview for any signed-in user."""

from pydantic import BaseModel, Field


class LabelCount(BaseModel):
    label: str
    count: int


class AnalyticsOverview(BaseModel):
    total_searches: int
    searches_last_7d: int
    avg_confidence: float
    grounded_searches: int
    freeform_only_searches: int
    upvotes: int
    downvotes: int
    by_category: list[LabelCount] = Field(default_factory=list)
    top_queries: list[LabelCount] = Field(default_factory=list)
