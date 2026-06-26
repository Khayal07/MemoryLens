"""Loads a curated, bundled catalog from JSON fixtures. This makes ingestion +
embeddings runnable end-to-end with no external API keys — ideal for the demo and
CI. Live adapters (tmdb.py, ...) replace it for a larger catalog."""

import json
from collections.abc import Iterable
from pathlib import Path

from app.ingest.base import NormalizedItem

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class FixtureAdapter:
    def __init__(self, category_key: str) -> None:
        self.category_key = category_key

    def fetch(self, limit: int = 1000) -> Iterable[NormalizedItem]:
        path = FIXTURES_DIR / f"{self.category_key}.json"
        if not path.exists():
            raise FileNotFoundError(f"No fixture for category '{self.category_key}': {path}")
        rows = json.loads(path.read_text(encoding="utf-8"))
        for row in rows[:limit]:
            yield NormalizedItem(
                external_id=row["external_id"],
                title=row["title"],
                description=row.get("description", ""),
                image_url=row.get("image_url"),
                source_url=row.get("source_url"),
                metadata=row.get("metadata", {}),
            )
