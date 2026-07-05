"""Analytics route — a global usage overview, visible to any signed-in user."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.infra.db import get_db
from app.infra.models import User
from app.schemas.analytics import AnalyticsOverview
from app.services import analytics_service

router = APIRouter()


@router.get("/analytics", response_model=AnalyticsOverview)
def analytics(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> AnalyticsOverview:
    return analytics_service.overview(db)
