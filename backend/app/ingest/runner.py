"""Ingestion runner: fetch → normalize → embed → upsert.

Idempotent: re-running updates existing items (keyed by category_id + external_id)
rather than duplicating them. Embeddings and the keyword tsvector are computed and
stored alongside each item so retrieval (Phase 3) is a pure DB read."""

import structlog
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.ai.embedder import get_embedder
from app.infra.db import SessionLocal
from app.infra.models import Category, Item, ItemEmbedding
from app.ingest.registry import get_adapter

log = structlog.get_logger()


def ingest_category(category_key: str, source: str = "auto", limit: int = 1000) -> int:
    """Ingest one category. Returns the number of items upserted."""
    adapter = get_adapter(category_key, source)
    items = list(adapter.fetch(limit))
    if not items:
        log.warning("ingest.no_items", category=category_key)
        return 0

    embedder = get_embedder()
    vectors = embedder.embed_texts([i.embedding_text() for i in items])

    with SessionLocal() as db:
        category_id = _category_id(db, category_key)
        for item, vector in zip(items, vectors, strict=True):
            item_id = _upsert_item(db, category_id, item)
            _upsert_embedding(db, item_id, vector, item.embedding_text())
        db.commit()

    log.info("ingest.done", category=category_key, count=len(items), source=source)
    return len(items)


def _category_id(db: Session, category_key: str) -> int:
    row = db.execute(select(Category.id).where(Category.key == category_key)).scalar_one_or_none()
    if row is None:
        raise ValueError(f"Unknown category '{category_key}' — run migrations first")
    return row


def _upsert_item(db: Session, category_id: int, item) -> int:
    stmt = (
        pg_insert(Item)
        .values(
            category_id=category_id,
            external_id=item.external_id,
            title=item.title,
            description=item.description,
            item_metadata=item.metadata,
            image_url=item.image_url,
            source_url=item.source_url,
        )
        .on_conflict_do_update(
            constraint="uq_item_external",
            set_={
                "title": item.title,
                "description": item.description,
                "metadata": item.metadata,
                "image_url": item.image_url,
                "source_url": item.source_url,
            },
        )
        .returning(Item.id)
    )
    return db.execute(stmt).scalar_one()


def _upsert_embedding(db: Session, item_id: int, vector: list[float], text: str) -> None:
    tsv = func.to_tsvector("english", text)
    stmt = (
        pg_insert(ItemEmbedding)
        .values(item_id=item_id, embedding=vector, search_tsv=tsv)
        .on_conflict_do_update(
            index_elements=["item_id"],
            set_={"embedding": vector, "search_tsv": tsv},
        )
    )
    db.execute(stmt)
