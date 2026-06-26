"""Canonical V1 categories. Single source of truth — reused by the seed migration
and the API. Adding a new category later means adding an entry here plus an
ingestion adapter; the search pipeline does not change (Open/Closed)."""

CATEGORIES: list[dict] = [
    {"key": "movies", "display_name": "Movies", "config": {"icon": "🎬", "adapter": "tmdb"}},
    {"key": "tv", "display_name": "TV Series", "config": {"icon": "📺", "adapter": "tmdb"}},
    {"key": "songs", "display_name": "Songs", "config": {"icon": "🎵", "adapter": "musicbrainz"}},
    {"key": "books", "display_name": "Books", "config": {"icon": "📚", "adapter": "openlibrary"}},
    {"key": "games", "display_name": "Games", "config": {"icon": "🎮", "adapter": "rawg"}},
    {"key": "actors", "display_name": "Actors", "config": {"icon": "👤", "adapter": "tmdb"}},
]

CATEGORY_KEYS: set[str] = {c["key"] for c in CATEGORIES}
