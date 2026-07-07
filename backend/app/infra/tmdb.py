"""TMDB person-image lookup — a face for a free-form (AI-identified) actor, so a
person Best Match shows a photo like a movie shows its poster. Best-effort: a missing
key, network error, or a person with no photo all return None so nothing breaks."""

import httpx
import structlog

from app.core.config import get_settings

log = structlog.get_logger()
TMDB_BASE = "https://api.themoviedb.org/3"
IMG_BASE = "https://image.tmdb.org/t/p/w500"


def fetch_person_image(name: str) -> str | None:
    """Return a TMDB profile-photo URL for a person searched by name, or None if
    unavailable. Never raises. Takes the first result that actually has a photo."""
    key = get_settings().tmdb_api_key
    if not key or not name:
        return None
    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(
                f"{TMDB_BASE}/search/person", params={"api_key": key, "query": name}
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
    except (httpx.HTTPError, ValueError) as exc:
        log.warning("tmdb.person_fetch_failed", name=name, error=str(exc))
        return None
    for row in results:
        path = row.get("profile_path")
        if path:
            return f"{IMG_BASE}{path}"
    return None
