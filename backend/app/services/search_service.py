"""Search use-case: run the AI pipeline, then persist the search and its results
(for history). Category validation lives here so the API stays thin."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai.pipeline import get_pipeline
from app.core.errors import NotFoundError
from app.domain.categories import CATEGORY_KEYS
from app.infra import cache
from app.infra.models import Category, Search, SearchResult
from app.schemas.search import SearchResponse


def run_search(
    db: Session, category_key: str, query: str, user_id: int | None
) -> SearchResponse:
    if category_key not in CATEGORY_KEYS:
        raise NotFoundError(f"Unknown category '{category_key}'.")

    response = cache.get_cached(category_key, query)
    if response is None:
        response = get_pipeline().run(db, category_key, query)
        cache.set_cached(category_key, query, response)

    # Always record the search so history reflects every request, cached or not.
    _persist(db, category_key, query, user_id, response)
    return response


def _persist(
    db: Session, category_key: str, query: str, user_id: int | None, response: SearchResponse
) -> None:
    category_id = db.execute(
        select(Category.id).where(Category.key == category_key)
    ).scalar_one()
    search = Search(user_id=user_id, category_id=category_id, raw_query=query)
    db.add(search)
    db.flush()
    for rank, result in enumerate(response.results):
        db.add(
            SearchResult(
                search_id=search.id,
                item_id=result.item_id,
                confidence=result.confidence,
                rank=rank,
                reason=result.reason,
            )
        )
    db.commit()


def list_history(db: Session, user_id: int, limit: int = 50) -> list[dict]:
    rows = db.execute(
        select(
            Search.id,
            Category.key,
            Search.raw_query,
            Search.created_at,
            func.count(SearchResult.id),
        )
        .join(Category, Category.id == Search.category_id)
        .outerjoin(SearchResult, SearchResult.search_id == Search.id)
        .where(Search.user_id == user_id)
        .group_by(Search.id, Category.key)
        .order_by(Search.created_at.desc())
        .limit(limit)
    ).all()
    return [
        {
            "id": sid,
            "category": key,
            "query": q,
            "created_at": created,
            "result_count": count,
        }
        for sid, key, q, created, count in rows
    ]
