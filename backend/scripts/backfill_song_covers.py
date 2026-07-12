"""Backfill iTunes album cover art for catalog song rows without an image.

    python -m scripts.backfill_song_covers

Scans song items with a null image_url, looks each up on iTunes by title + the stored
artist, and writes any cover found. Keyless (iTunes Search). Idempotent and safe to
re-run; skips songs iTunes can't resolve. Shares its loop with the /admin surface via
app.services.catalog_admin.
"""

from app.infra.db import SessionLocal
from app.services.catalog_admin import backfill_song_covers


def main() -> None:
    with SessionLocal() as db:
        result = backfill_song_covers(db)
    print(f"Done. Scanned {result['scanned']} rows, filled {result['filled']} covers.")


if __name__ == "__main__":
    main()
