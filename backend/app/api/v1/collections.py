"""Collection routes — all require auth; a user only ever sees/edits their own."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.infra.db import get_db
from app.infra.models import Collection, User
from app.schemas.collections import (
    AddItemRequest,
    CollectionCreate,
    CollectionOut,
    CollectionRename,
    SavedItem,
)
from app.services import collections_service

router = APIRouter()


def _to_out(coll: Collection) -> CollectionOut:
    items = [
        SavedItem(
            item_id=ci.item.id,
            title=ci.item.title,
            description=ci.item.description or "",
            image_url=ci.item.image_url,
            source_url=ci.item.source_url,
            category=ci.item.category.key,
            metadata=ci.item.item_metadata,
        )
        for ci in sorted(coll.items, key=lambda c: c.created_at, reverse=True)
    ]
    return CollectionOut(id=coll.id, name=coll.name, created_at=coll.created_at, items=items)


@router.get("/collections", response_model=list[CollectionOut])
def list_collections(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[CollectionOut]:
    return [_to_out(c) for c in collections_service.list_collections(db, user.id)]


@router.post("/collections", response_model=CollectionOut, status_code=201)
def create_collection(
    body: CollectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CollectionOut:
    return _to_out(collections_service.create_collection(db, user.id, body.name))


@router.patch("/collections/{collection_id}", response_model=CollectionOut)
def rename_collection(
    collection_id: int,
    body: CollectionRename,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CollectionOut:
    return _to_out(
        collections_service.rename_collection(db, user.id, collection_id, body.name)
    )


@router.delete("/collections/{collection_id}", status_code=204)
def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    collections_service.delete_collection(db, user.id, collection_id)


@router.post("/collections/{collection_id}/items", status_code=204)
def add_item(
    collection_id: int,
    body: AddItemRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    collections_service.add_item(db, user.id, collection_id, body.item_id)


@router.delete("/collections/{collection_id}/items/{item_id}", status_code=204)
def remove_item(
    collection_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    collections_service.remove_item(db, user.id, collection_id, item_id)
