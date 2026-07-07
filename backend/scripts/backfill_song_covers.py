"""Backfill iTunes album cover art for catalog song rows without an image.

    python -m scripts.backfill_song_covers

Scans song items with a null image_url, looks each up on iTunes by title + the stored
artist, and writes any cover found. Keyless (iTunes Search). Idempotent and safe to
re-run; skips songs iTunes can't resolve.
"""

from sqlalchemy import select

from app.infra.db import SessionLocal
from app.infra.itunes import fetch_song_cover
from app.infra.models import Category, Item


def main() -> None:
    filled = 0
    with SessionLocal() as db:
        rows = (
            db.execute(
                select(Item)
                .join(Category, Category.id == Item.category_id)
                .where(Category.key == "songs", Item.image_url.is_(None))
            )
            .scalars()
            .all()
        )
        print(f"songs: {len(rows)} rows without a cover")
        for item in rows:
            artist = (item.item_metadata or {}).get("artist")
            cover = fetch_song_cover(item.title, artist)
            if cover:
                item.image_url = cover
                filled += 1
                print(f"  ✓ {item.title} → {cover}")
            else:
                print(f"  · {item.title} — no cover found")
        db.commit()
    print(f"Done. Filled {filled} covers.")


if __name__ == "__main__":
    main()
