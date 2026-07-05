"""Result feedback: users vote a grounded result up/down. Votes become a small,
bounded, item-level popularity signal that nudges confidence/order on future
searches — a lightweight learning-to-rank, never overriding the model wholesale."""

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ValidationError
from app.infra.models import Item, ResultFeedback, Search
from app.schemas.search import SearchResponse

# Each net vote shifts confidence by this much, capped at ±MAX_DELTA points.
_VOTE_WEIGHT = 2.0
_MAX_DELTA = 8.0


def record_vote(
    db: Session, user_id: int, search_id: int | None, item_id: int, vote: int
) -> None:
    if vote not in (-1, 1):
        raise ValidationError("Vote must be +1 or -1.")
    if db.get(Item, item_id) is None:
        raise NotFoundError("Item not found.")
    # Ignore a search_id that doesn't exist rather than failing the vote.
    if search_id is not None and db.get(Search, search_id) is None:
        search_id = None

    existing = db.execute(
        select(ResultFeedback).where(
            ResultFeedback.user_id == user_id, ResultFeedback.item_id == item_id
        )
    ).scalar_one_or_none()
    if existing is not None:
        existing.vote = vote
        existing.search_id = search_id
    else:
        db.add(
            ResultFeedback(
                user_id=user_id, search_id=search_id, item_id=item_id, vote=vote
            )
        )
    db.commit()


def get_item_scores(db: Session, item_ids: Sequence[int]) -> dict[int, int]:
    if not item_ids:
        return {}
    rows = db.execute(
        select(ResultFeedback.item_id, func.coalesce(func.sum(ResultFeedback.vote), 0))
        .where(ResultFeedback.item_id.in_(item_ids))
        .group_by(ResultFeedback.item_id)
    ).all()
    return {item_id: int(total) for item_id, total in rows}


def apply_feedback(db: Session, response: SearchResponse) -> None:
    """Nudge grounded results by their net feedback and re-order best-first. Runs on
    every search (cache hit or miss) so votes take effect immediately. Free-form
    answers (item_id 0) have no votes and keep their confidence."""
    grounded_ids = [r.item_id for r in response.results if r.item_id > 0]
    scores = get_item_scores(db, grounded_ids)
    if not scores:
        return
    for r in response.results:
        net = scores.get(r.item_id)
        if net:
            delta = max(-_MAX_DELTA, min(_MAX_DELTA, net * _VOTE_WEIGHT))
            r.confidence = round(min(100.0, max(0.0, r.confidence + delta)), 1)
    response.results.sort(key=lambda r: r.confidence, reverse=True)
