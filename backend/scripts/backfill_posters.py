"""Backfill posters for catalog rows TMDb left without one, using OMDb.

    python -m scripts.backfill_posters

Scans movies/tv items with a null image_url, looks each up on OMDb by title + the
stored year, and writes any poster found. Idempotent and safe to re-run; skips rows
OMDb can't resolve. Needs OMDB_API_KEY set.
"""

from sqlalchemy import select

from app.core.config import get_settings
from app.infra.db import SessionLocal
from app.infra.models import Category, Item
from app.infra.omdb import fetch_poster

# category key → OMDb `type`
_KINDS = {"movies": "movie", "tv": "series"}


def main() -> None:
    if not get_settings().omdb_api_key:
        print("OMDB_API_KEY is not set — nothing to do.")
        return

    filled = 0
    with SessionLocal() as db:
        for key, kind in _KINDS.items():
            rows = db.execute(
                select(Item)
                .join(Category, Category.id == Item.category_id)
                .where(Category.key == key, Item.image_url.is_(None))
            ).scalars().all()
            print(f"{key}: {len(rows)} rows without a poster")
            for item in rows:
                year = (item.item_metadata or {}).get("year")
                poster = fetch_poster(item.title, year, kind)
                if poster:
                    item.image_url = poster
                    filled += 1
                    print(f"  ✓ {item.title} → {poster}")
        db.commit()
    print(f"Done. Filled {filled} posters.")


if __name__ == "__main__":
    main()
