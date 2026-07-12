"""Admin catalog routes — diagnose and seed the catalog in a deployment without
shell access. Guarded by a shared X-Admin-Token; when ADMIN_TOKEN is unset the whole
surface returns 404 (fail closed — the endpoints simply don't exist)."""

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import NotFoundError, UnauthorizedError, ValidationError
from app.domain.categories import CATEGORY_KEYS
from app.infra.db import get_db
from app.ingest.runner import ingest_category
from app.services import catalog_admin

router = APIRouter()


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    expected = get_settings().admin_token
    if not expected:
        # Fail closed: without a configured token the admin surface does not exist.
        raise NotFoundError("Not found.")
    if x_admin_token != expected:
        raise UnauthorizedError("Invalid or missing admin token.")


class IngestRequest(BaseModel):
    category: str
    source: str = "auto"  # auto | fixture | live
    limit: int = Field(default=1000, ge=1, le=5000)


@router.get("/admin/catalog/stats", dependencies=[Depends(require_admin)])
def catalog_stats(db: Session = Depends(get_db)) -> dict:
    return catalog_admin.catalog_stats(db)


@router.post("/admin/ingest", dependencies=[Depends(require_admin)])
def ingest(payload: IngestRequest) -> dict:
    if payload.category not in CATEGORY_KEYS:
        raise ValidationError(f"Unknown category '{payload.category}'.")
    if payload.source not in {"auto", "fixture", "live"}:
        raise ValidationError("source must be one of: auto, fixture, live.")
    count = ingest_category(payload.category, source=payload.source, limit=payload.limit)
    return {"category": payload.category, "source": payload.source, "upserted": count}


@router.post("/admin/backfill/song-covers", dependencies=[Depends(require_admin)])
def backfill_song_covers(db: Session = Depends(get_db)) -> dict:
    return catalog_admin.backfill_song_covers(db)
