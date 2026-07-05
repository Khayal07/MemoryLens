"""Collections use-case: named lists of saved catalog items, owned by a user.
Ownership is enforced here; routers stay thin. Only real catalog items can be
saved (FK to items) — free-form answers have no item to reference."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import ConflictError, NotFoundError
from app.infra.models import Collection, CollectionItem, Item


def list_collections(db: Session, user_id: int) -> Sequence[Collection]:
    return (
        db.execute(
            select(Collection)
            .where(Collection.user_id == user_id)
            .order_by(Collection.created_at.desc())
            .options(
                selectinload(Collection.items)
                .selectinload(CollectionItem.item)
                .selectinload(Item.category)
            )
        )
        .scalars()
        .all()
    )


def create_collection(db: Session, user_id: int, name: str) -> Collection:
    name = name.strip()
    if _name_taken(db, user_id, name):
        raise ConflictError("A collection with this name already exists.")
    coll = Collection(user_id=user_id, name=name)
    db.add(coll)
    db.commit()
    db.refresh(coll)
    return coll


def rename_collection(db: Session, user_id: int, collection_id: int, name: str) -> Collection:
    coll = _owned(db, user_id, collection_id)
    name = name.strip()
    if _name_taken(db, user_id, name, exclude_id=collection_id):
        raise ConflictError("A collection with this name already exists.")
    coll.name = name
    db.commit()
    db.refresh(coll)
    return coll


def delete_collection(db: Session, user_id: int, collection_id: int) -> None:
    db.delete(_owned(db, user_id, collection_id))
    db.commit()


def add_item(db: Session, user_id: int, collection_id: int, item_id: int) -> None:
    _owned(db, user_id, collection_id)
    if db.get(Item, item_id) is None:
        raise NotFoundError("Item not found.")
    exists = db.execute(
        select(CollectionItem.id).where(
            CollectionItem.collection_id == collection_id,
            CollectionItem.item_id == item_id,
        )
    ).scalar_one_or_none()
    if exists is None:
        db.add(CollectionItem(collection_id=collection_id, item_id=item_id))
        db.commit()


def remove_item(db: Session, user_id: int, collection_id: int, item_id: int) -> None:
    _owned(db, user_id, collection_id)
    row = db.execute(
        select(CollectionItem).where(
            CollectionItem.collection_id == collection_id,
            CollectionItem.item_id == item_id,
        )
    ).scalar_one_or_none()
    if row is not None:
        db.delete(row)
        db.commit()


def _owned(db: Session, user_id: int, collection_id: int) -> Collection:
    coll = db.get(Collection, collection_id)
    if coll is None or coll.user_id != user_id:
        raise NotFoundError("Collection not found.")
    return coll


def _name_taken(db: Session, user_id: int, name: str, exclude_id: int | None = None) -> bool:
    stmt = select(Collection.id).where(
        Collection.user_id == user_id, Collection.name == name
    )
    if exclude_id is not None:
        stmt = stmt.where(Collection.id != exclude_id)
    return db.execute(stmt).scalar_one_or_none() is not None
