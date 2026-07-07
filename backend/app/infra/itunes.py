"""iTunes Search cover-art lookup — album artwork for a free-form song Best Match, so
a song shows a cover like a movie shows its poster. No API key needed. Best-effort: a
network error or no match returns None so nothing breaks."""

import httpx
import structlog

log = structlog.get_logger()
ITUNES_BASE = "https://itunes.apple.com/search"


def fetch_song_cover(title: str, artist: str | None = None) -> str | None:
    """Return an album-art URL for a song (optionally sharpened by artist), or None if
    unavailable. Never raises. iTunes returns a 100px thumb whose URL upscales to 600px
    by swapping the size token."""
    if not title:
        return None
    term = f"{title} {artist}".strip() if artist else title
    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(
                ITUNES_BASE, params={"term": term, "entity": "song", "limit": 1}
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
    except (httpx.HTTPError, ValueError) as exc:
        log.warning("itunes.fetch_failed", term=term, error=str(exc))
        return None
    for row in results:
        art = row.get("artworkUrl100")
        if art:
            return art.replace("100x100bb", "600x600bb")
    return None
