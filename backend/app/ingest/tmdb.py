"""Live TMDB adapter covering movies, TV and actors (one API, three categories).
Used when TMDB_API_KEY is set; otherwise the runner falls back to fixtures.
Raw responses should be cached in a real ingest run — kept simple here."""

from collections.abc import Iterable

import httpx

from app.core.config import get_settings
from app.infra.omdb import fetch_poster
from app.ingest.base import NormalizedItem

TMDB_BASE = "https://api.themoviedb.org/3"
IMG_BASE = "https://image.tmdb.org/t/p/w500"

# How each category maps onto TMDB's "popular" endpoints + field names.
_CONFIG = {
    "movies": {"path": "/movie/popular", "title": "title", "date": "release_date"},
    "tv": {"path": "/tv/popular", "title": "name", "date": "first_air_date"},
    "actors": {"path": "/person/popular", "title": "name", "date": None},
}

# TMDB category → OMDb `type` for the poster fallback (person has no OMDb equivalent).
_OMDB_KIND = {"movies": "movie", "tv": "series"}


class TMDBAdapter:
    def __init__(self, category_key: str) -> None:
        if category_key not in _CONFIG:
            raise ValueError(f"TMDB adapter does not handle category '{category_key}'")
        self.category_key = category_key
        self._cfg = _CONFIG[category_key]
        self._key = get_settings().tmdb_api_key

    def fetch(self, limit: int = 200) -> Iterable[NormalizedItem]:
        if not self._key:
            raise RuntimeError("TMDB_API_KEY is not set")
        fetched = 0
        page = 1
        with httpx.Client(timeout=20.0) as client:
            while fetched < limit:
                resp = client.get(
                    f"{TMDB_BASE}{self._cfg['path']}",
                    params={"api_key": self._key, "page": page},
                )
                resp.raise_for_status()
                results = resp.json().get("results", [])
                if not results:
                    break
                for row in results:
                    if fetched >= limit:
                        break
                    item = self._normalize(row)
                    if item:
                        yield item
                        fetched += 1
                page += 1

    def _normalize(self, row: dict) -> NormalizedItem | None:
        title = row.get(self._cfg["title"])
        if not title:
            return None
        if self.category_key == "actors":
            known = [k.get("title") or k.get("name") for k in row.get("known_for", [])]
            description = f"Known for: {', '.join(filter(None, known))}." if known else ""
            poster = row.get("profile_path")
            metadata = {"known_for": [k for k in known if k]}
        else:
            description = row.get("overview", "")
            poster = row.get("poster_path")
            year = (row.get(self._cfg["date"]) or "")[:4]
            metadata = {"year": year, "popularity": row.get("popularity")}

        if poster:
            image_url = f"{IMG_BASE}{poster}"
        elif self.category_key in _OMDB_KIND:
            # TMDb had no poster for this movie/series — try OMDb by title + year.
            image_url = fetch_poster(title, year, _OMDB_KIND[self.category_key])
        else:
            image_url = None

        return NormalizedItem(
            external_id=f"tmdb:{row['id']}",
            title=title,
            description=description,
            image_url=image_url,
            source_url=f"https://www.themoviedb.org/{_route(self.category_key)}/{row['id']}",
            metadata=metadata,
        )


def _route(category_key: str) -> str:
    return {"movies": "movie", "tv": "tv", "actors": "person"}[category_key]
