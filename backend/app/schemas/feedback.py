"""Feedback DTO."""

from typing import Literal

from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    search_id: int | None = None
    item_id: int
    vote: Literal[-1, 1]
