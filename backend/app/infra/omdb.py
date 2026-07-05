"""OMDb poster lookup — a fallback image source when TMDb has no poster. Used both
at ingestion (catalog rows) and live (the free-form Best Match hero). Best-effort:
a missing key, network error, or "N/A" poster all return None so nothing breaks."""

import httpx
import structlog

from app.core.config import get_settings

log = structlog.get_logger()
OMDB_BASE = "https://www.omdbapi.com/"


def fetch_poster(title: str, year: str | None = None, kind: str = "movie") -> str | None:
    """Return an OMDb poster URL for a title (optionally disambiguated by year and
    type "movie"/"series"), or None if unavailable. Never raises.

    A wrong/ambiguous year (common in LLM output — e.g. V for Vendetta 2005 vs 2006)
    makes OMDb miss, so if a year-scoped lookup fails we retry on the title alone."""
    key = get_settings().omdb_api_key
    if not key or not title:
        return None
    with httpx.Client(timeout=8.0) as client:
        poster = _lookup(client, key, title, year, kind)
        if poster is None and year:
            poster = _lookup(client, key, title, None, kind)
    return poster


def _lookup(
    client: httpx.Client, key: str, title: str, year: str | None, kind: str
) -> str | None:
    params = {"t": title, "apikey": key, "type": kind}
    if year:
        params["y"] = year
    try:
        resp = client.get(OMDB_BASE, params=params)
        resp.raise_for_status()
        data = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        log.warning("omdb.fetch_failed", title=title, error=str(exc))
        return None
    if data.get("Response") != "True":
        return None
    poster = data.get("Poster")
    if not poster or poster == "N/A":
        return None
    return poster
