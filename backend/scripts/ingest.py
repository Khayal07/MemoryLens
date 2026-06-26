"""CLI to seed the catalog.

    python -m scripts.ingest --all
    python -m scripts.ingest --category movies --source live --limit 200
    python -m scripts.ingest --category songs            # fixtures
"""

import argparse

from app.domain.categories import CATEGORY_KEYS
from app.ingest.runner import ingest_category


def main() -> None:
    parser = argparse.ArgumentParser(description="MemoryLens catalog ingestion")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--category", choices=sorted(CATEGORY_KEYS))
    group.add_argument("--all", action="store_true", help="ingest every category")
    parser.add_argument("--source", choices=["auto", "fixture", "live"], default="auto")
    parser.add_argument("--limit", type=int, default=1000)
    args = parser.parse_args()

    targets = sorted(CATEGORY_KEYS) if args.all else [args.category]
    total = 0
    for key in targets:
        count = ingest_category(key, source=args.source, limit=args.limit)
        print(f"  {key:8} → {count} items")
        total += count
    print(f"Done. {total} items ingested.")


if __name__ == "__main__":
    main()
