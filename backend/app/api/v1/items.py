"""Item routes. Currently just "more like this" — catalog neighbours of a grounded
item. Public: no auth needed, no user data involved."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.ai.retriever import find_similar
from app.infra.db import get_db
from app.schemas.items import SimilarItem

router = APIRouter()


@router.get("/items/{item_id}/similar", response_model=list[SimilarItem])
def similar(
    item_id: int,
    # Cap the fan-out so a caller can't request an unbounded neighbour scan.
    limit: int = Query(6, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[SimilarItem]:
    items = find_similar(db, item_id, k=limit)
    return [
        SimilarItem(
            item_id=it.id,
            title=it.title,
            description=it.description or "",
            image_url=it.image_url,
            source_url=it.source_url,
            metadata=it.item_metadata,
        )
        for it in items
    ]
