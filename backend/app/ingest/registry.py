"""Resolves a (category, source) pair to a concrete adapter. New categories or
sources plug in here without touching the runner."""

from app.core.config import get_settings
from app.ingest.base import CategoryAdapter
from app.ingest.fixture_adapter import FixtureAdapter
from app.ingest.openlibrary import OpenLibraryAdapter
from app.ingest.rawg import RAWGAdapter
from app.ingest.tmdb import TMDBAdapter

# Live adapter per category. TMDB takes the category key (it serves three);
# the others are single-category. Songs have no live adapter (free metadata
# sources lack the thematic descriptions memory search needs) → fixtures.
_LIVE_MULTI = {"movies": TMDBAdapter, "tv": TMDBAdapter, "actors": TMDBAdapter}
_LIVE_SINGLE = {"books": OpenLibraryAdapter, "games": RAWGAdapter}


def _build_live(category_key: str) -> CategoryAdapter | None:
    if category_key in _LIVE_MULTI:
        return _LIVE_MULTI[category_key](category_key)
    if category_key in _LIVE_SINGLE:
        return _LIVE_SINGLE[category_key]()
    return None


def _has_key(category_key: str) -> bool:
    settings = get_settings()
    if category_key in _LIVE_MULTI:
        return bool(settings.tmdb_api_key)
    if category_key == "games":
        return bool(settings.rawg_api_key)
    if category_key == "books":
        return True  # OpenLibrary is keyless
    return False


def get_adapter(category_key: str, source: str = "auto") -> CategoryAdapter:
    """source: 'fixture' forces bundled data; 'live' forces the external API;
    'auto' uses live when usable (key present / keyless), else fixtures."""
    if source == "fixture":
        return FixtureAdapter(category_key)

    if source == "live":
        live = _build_live(category_key)
        if live is None:
            raise ValueError(f"No live adapter for category '{category_key}'")
        return live

    # auto
    if _has_key(category_key):
        live = _build_live(category_key)
        if live is not None:
            return live
    return FixtureAdapter(category_key)
