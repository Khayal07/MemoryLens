"""RAWG game-image lookup — key art for a free-form game Best Match, so a game shows
an image like a movie shows its poster. Needs RAWG_API_KEY. Best-effort: a missing key,
network error, or a game with no image all return None so nothing breaks."""

import httpx
import structlog

from app.core.config import get_settings

log = structlog.get_logger()
SEARCH_URL = "https://api.rawg.io/api/games"


def fetch_game_image(name: str) -> str | None:
    """Return a RAWG background-image URL for a game searched by name, or None if
    unavailable. Never raises. Takes the first result that actually has an image."""
    key = get_settings().rawg_api_key
    if not key or not name:
        return None
    try:
        with httpx.Client(timeout=8.0, headers={"User-Agent": "MemoryLens/0.1"}) as client:
            resp = client.get(SEARCH_URL, params={"key": key, "search": name, "page_size": 3})
            resp.raise_for_status()
            results = resp.json().get("results", [])
    except (httpx.HTTPError, ValueError) as exc:
        log.warning("rawg.image_fetch_failed", name=name, error=str(exc))
        return None
    for row in results:
        img = row.get("background_image")
        if img:
            return img
    return None
