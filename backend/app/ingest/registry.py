"""Resolves a (category, source) pair to a concrete adapter. New categories or
sources plug in here without touching the runner."""

from app.core.config import get_settings
from app.ingest.base import CategoryAdapter
from app.ingest.fixture_adapter import FixtureAdapter
from app.ingest.tmdb import TMDBAdapter

# Which live adapter serves each category. Categories without a live adapter yet
# (songs, books, games) always use fixtures in V1.
_LIVE = {
    "movies": TMDBAdapter,
    "tv": TMDBAdapter,
    "actors": TMDBAdapter,
}


def get_adapter(category_key: str, source: str = "auto") -> CategoryAdapter:
    """source: 'fixture' forces bundled data; 'live' forces the external API;
    'auto' uses live when a key is configured, else fixtures."""
    if source == "fixture":
        return FixtureAdapter(category_key)

    live_cls = _LIVE.get(category_key)
    has_key = bool(get_settings().tmdb_api_key)

    if source == "live":
        if not live_cls:
            raise ValueError(f"No live adapter for category '{category_key}'")
        return live_cls(category_key)

    # auto
    if live_cls and has_key:
        return live_cls(category_key)
    return FixtureAdapter(category_key)
