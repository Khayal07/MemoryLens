"""Admin catalog operations — diagnose and seed the catalog in an environment
without shell access (e.g. Railway). Guarded by X-Admin-Token in the API layer."""

import structlog
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infra.itunes import fetch_song_cover
from app.infra.models import Category, Item, ItemEmbedding

log = structlog.get_logger()


def catalog_stats(db: Session) -> dict:
    """Per-category counts — proves or disproves an empty/sparse prod catalog."""
    categories = db.execute(select(Category).order_by(Category.key)).scalars().all()
    per_category = []
    for cat in categories:
        base = Item.category_id == cat.id
        items = db.execute(select(func.count(Item.id)).where(base)).scalar_one()
        with_embedding = db.execute(
            select(func.count(Item.id))
            .select_from(Item)
            .join(ItemEmbedding, ItemEmbedding.item_id == Item.id)
            .where(base)
        ).scalar_one()
        with_image = db.execute(
            select(func.count(Item.id)).where(base, Item.image_url.is_not(None))
        ).scalar_one()
        gpt_rows = db.execute(
            select(func.count(Item.id)).where(base, Item.external_id.like("gpt:%"))
        ).scalar_one()
        per_category.append(
            {
                "key": cat.key,
                "display_name": cat.display_name,
                "items": items,
                "with_embedding": with_embedding,
                "with_image": with_image,
                "gpt_rows": gpt_rows,
            }
        )
    total_items = sum(c["items"] for c in per_category)
    return {"total_items": total_items, "categories": per_category}


def backfill_song_covers(db: Session) -> dict:
    """Fill missing iTunes cover art for song rows. Mirrors scripts/backfill_song_covers."""
    rows = (
        db.execute(
            select(Item)
            .join(Category, Category.id == Item.category_id)
            .where(Category.key == "songs", Item.image_url.is_(None))
        )
        .scalars()
        .all()
    )
    filled = 0
    for item in rows:
        artist = (item.item_metadata or {}).get("artist")
        cover = fetch_song_cover(item.title, artist)
        if cover:
            item.image_url = cover
            filled += 1
    db.commit()
    log.info("admin.backfill_song_covers", scanned=len(rows), filled=filled)
    return {"scanned": len(rows), "filled": filled}
