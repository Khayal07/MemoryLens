"""Search + history routes. Search is allowed anonymously; history requires auth."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.cleaning import QueryError
from app.api.deps import get_current_user, get_optional_user
from app.core.errors import ValidationError
from app.core.rate_limit import rate_limiter
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


@router.post(
    "/search",
    response_model=SearchResponse,
    dependencies=[Depends(rate_limiter("search", limit=10))],
)
def search(
    body: SearchRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
) -> SearchResponse:
    try:
        return search_service.run_search(
            db, body.category, body.query, user.id if user else None
        )
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
