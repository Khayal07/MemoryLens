"""Daily-challenge routes — today's clues (gated by progress) and guess submission."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.infra.db import get_db
from app.infra.models import User
from app.schemas.challenge import ChallengeState, GuessRequest
from app.services import challenge_service

router = APIRouter()


@router.get("/challenge/today", response_model=ChallengeState)
def today(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ChallengeState:
    return challenge_service.get_state(db, user.id)


@router.post("/challenge/guess", response_model=ChallengeState)
def guess(
    payload: GuessRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ChallengeState:
    return challenge_service.submit_guess(db, user.id, payload.guess)
