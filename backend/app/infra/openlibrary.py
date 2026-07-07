"""OpenLibrary cover lookup — a cover for a free-form book Best Match, so a book shows
its cover like a movie shows its poster. Keyless. Best-effort: a network error or no
match/cover returns None so nothing breaks."""

import httpx
import structlog

log = structlog.get_logger()
SEARCH_URL = "https://openlibrary.org/search.json"
COVER_URL = "https://covers.openlibrary.org/b/id/{cover}-L.jpg"


def fetch_book_cover(title: str, author: str | None = None) -> str | None:
    """Return a cover-image URL for a book (optionally sharpened by author), or None if
    unavailable. Never raises. Takes the first result that actually has a cover id."""
    if not title:
        return None
    params: dict = {"title": title, "fields": "cover_i", "limit": 3}
    if author:
        params["author"] = author
    try:
        with httpx.Client(timeout=8.0, headers={"User-Agent": "MemoryLens/0.1"}) as client:
            resp = client.get(SEARCH_URL, params=params)
            resp.raise_for_status()
            docs = resp.json().get("docs", [])
    except (httpx.HTTPError, ValueError) as exc:
        log.warning("openlibrary.cover_fetch_failed", title=title, error=str(exc))
        return None
    for doc in docs:
        cover = doc.get("cover_i")
        if cover:
            return COVER_URL.format(cover=cover)
    return None
