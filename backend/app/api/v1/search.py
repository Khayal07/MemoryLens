"""Search + history routes. Search requires auth so every request maps to a user we
can rate-limit and bill; history/sharing require auth too."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.cleaning import QueryError
from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.errors import ValidationError
from app.core.rate_limit import daily_quota, user_rate_limiter
from app.infra.db import get_db
from app.infra.models import User
from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchSummary,
    ShareResponse,
)
from app.services import search_service, share_service

router = APIRouter()
_settings = get_settings()


@router.post(
    "/search",
    response_model=SearchResponse,
    # Paid LLM call: pace bursts per-user AND cap total spend per user per day.
    dependencies=[
        Depends(user_rate_limiter("search", _settings.search_rate_per_min)),
        Depends(daily_quota("search", _settings.search_daily_quota)),
    ],
)
def search(
    body: SearchRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SearchResponse:
    try:
        return search_service.run_search(db, body.category, body.query, user.id)
    except QueryError as exc:
        raise ValidationError(str(exc)) from exc


@router.get("/searches", response_model=list[SearchSummary])
def history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[SearchSummary]:
    rows = search_service.list_history(db, user.id)
    return [SearchSummary(**row) for row in rows]


@router.post("/searches/{search_id}/share", response_model=ShareResponse)
def share_search(
    search_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ShareResponse:
    return ShareResponse(token=share_service.create_share(db, search_id, user.id))


@router.get("/share/{token}", response_model=SearchResponse)
def shared_search(token: str, db: Session = Depends(get_db)) -> SearchResponse:
    return share_service.get_shared(db, token)
