"""Constellation route — the signed-in user's finds as a similarity star map."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.infra.db import get_db
from app.infra.models import User
from app.schemas.constellation import ConstellationResponse
from app.services import constellation_service

router = APIRouter()


@router.get("/constellation", response_model=ConstellationResponse)
def constellation(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ConstellationResponse:
    return constellation_service.build(db, user.id)
