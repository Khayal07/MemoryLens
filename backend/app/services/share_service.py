"""Public sharing: mint an unguessable token for a user's own search and serve the
snapshotted response to anyone holding the token (no auth)."""

import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.infra.models import Search
from app.schemas.search import SearchResponse


def create_share(db: Session, search_id: int, user_id: int) -> str:
    """Return a share token for the owner's search, minting one on first request
    (idempotent). Raises NotFoundError if the search isn't the caller's."""
    search = db.get(Search, search_id)
    if search is None or search.user_id != user_id:
        raise NotFoundError("Search not found.")
    if not search.share_token:
        search.share_token = secrets.token_urlsafe(16)  # ~22 url-safe chars
        db.commit()
    return search.share_token


def get_shared(db: Session, token: str) -> SearchResponse:
    search = db.execute(
        select(Search).where(Search.share_token == token)
    ).scalar_one_or_none()
    if search is None or search.response_json is None:
        raise NotFoundError("Shared search not found.")
    return SearchResponse.model_validate(search.response_json)
