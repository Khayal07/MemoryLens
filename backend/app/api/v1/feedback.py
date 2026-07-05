"""Feedback route — a logged-in user votes a grounded result up or down."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.infra.db import get_db
from app.infra.models import User
from app.schemas.feedback import FeedbackRequest
from app.services import feedback_service

router = APIRouter()


@router.post("/feedback", status_code=204)
def submit_feedback(
    body: FeedbackRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    feedback_service.record_vote(db, user.id, body.search_id, body.item_id, body.vote)
