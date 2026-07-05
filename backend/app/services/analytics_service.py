"""Usage analytics: aggregate global stats over searches, results and feedback.
Read-only; no per-user scoping (any signed-in user sees the same overview)."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infra.models import Category, ResultFeedback, Search, SearchResult
from app.schemas.analytics import AnalyticsOverview, LabelCount


def overview(db: Session) -> AnalyticsOverview:
    total = db.execute(select(func.count(Search.id))).scalar_one()
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    last_7d = db.execute(
        select(func.count(Search.id)).where(Search.created_at >= week_ago)
    ).scalar_one()

    avg_conf = db.execute(select(func.avg(SearchResult.confidence))).scalar_one() or 0.0

    # A search with ≥1 grounded result vs one that only produced a free-form answer.
    grounded = db.execute(
        select(func.count(func.distinct(SearchResult.search_id)))
    ).scalar_one()

    ups = db.execute(
        select(func.count(ResultFeedback.id)).where(ResultFeedback.vote == 1)
    ).scalar_one()
    downs = db.execute(
        select(func.count(ResultFeedback.id)).where(ResultFeedback.vote == -1)
    ).scalar_one()

    by_category = db.execute(
        select(Category.key, func.count(Search.id))
        .join(Search, Search.category_id == Category.id)
        .group_by(Category.key)
        .order_by(func.count(Search.id).desc())
    ).all()

    top_queries = db.execute(
        select(Search.raw_query, func.count(Search.id))
        .group_by(Search.raw_query)
        .order_by(func.count(Search.id).desc())
        .limit(8)
    ).all()

    return AnalyticsOverview(
        total_searches=total,
        searches_last_7d=last_7d,
        avg_confidence=round(float(avg_conf), 1),
        grounded_searches=grounded,
        freeform_only_searches=max(0, total - grounded),
        upvotes=ups,
        downvotes=downs,
        by_category=[LabelCount(label=k, count=c) for k, c in by_category],
        top_queries=[LabelCount(label=q, count=c) for q, c in top_queries],
    )
