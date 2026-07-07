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
from app.services import feedback_service


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
    response.search_id = _persist(db, category_key, query, user_id, response)
    # Apply crowd feedback every request (cache-independent) so votes take effect now.
    feedback_service.apply_feedback(db, response)
    return response


def _persist(
    db: Session, category_key: str, query: str, user_id: int | None, response: SearchResponse
) -> int:
    category_id = db.execute(
        select(Category.id).where(Category.key == category_key)
    ).scalar_one()
    search = Search(user_id=user_id, category_id=category_id, raw_query=query)
    db.add(search)
    db.flush()  # assign search.id before snapshotting/linking rows
    response.search_id = search.id
    # Snapshot the full response (incl. the free-form hero) for faithful sharing.
    search.response_json = response.model_dump()
    for rank, result in enumerate(response.results):
        # Free-form (LLM-identified) answers have no catalog item to reference — the
        # item_id FK would fail — so record only the grounded results in history.
        if not result.item_id:
            continue
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
    return search.id


def _top_result(snapshot: dict | None) -> tuple[str | None, str | None, float | None]:
    """Best-match title/poster/confidence from a search's response snapshot, for the
    history timeline. Searches predating the snapshot column yield (None, None, None)."""
    results = (snapshot or {}).get("results") or []
    if not results or not isinstance(results[0], dict):
        return None, None, None
    best = results[0]
    return best.get("title"), best.get("image_url"), best.get("confidence")


def list_history(db: Session, user_id: int, limit: int = 50) -> list[dict]:
    rows = db.execute(
        select(
            Search.id,
            Category.key,
            Search.raw_query,
            Search.created_at,
            func.count(SearchResult.id),
            # Selecting by Search.id group is fine: PG derives the rest of the
            # searches columns from the PK (functional dependency).
            Search.response_json,
        )
        .join(Category, Category.id == Search.category_id)
        .outerjoin(SearchResult, SearchResult.search_id == Search.id)
        .where(Search.user_id == user_id)
        .group_by(Search.id, Category.key)
        .order_by(Search.created_at.desc())
        .limit(limit)
    ).all()
    out = []
    for sid, key, q, created, count, snapshot in rows:
        top_title, top_image, top_confidence = _top_result(snapshot)
        out.append(
            {
                "id": sid,
                "category": key,
                "query": q,
                "created_at": created,
                "result_count": count,
                "top_title": top_title,
                "top_image": top_image,
                "top_confidence": top_confidence,
            }
        )
    return out
