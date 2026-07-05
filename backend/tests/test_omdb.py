"""OMDb poster client — no real network; httpx.Client.get is monkeypatched."""

import httpx

import app.infra.omdb as omdb


class _Settings:
    omdb_api_key = "testkey"


class _Resp:
    def __init__(self, data: dict) -> None:
        self._data = data

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._data


def _patch(monkeypatch, *responses: dict) -> None:
    monkeypatch.setattr(omdb, "get_settings", lambda: _Settings())
    calls = iter(responses)
    monkeypatch.setattr(
        httpx.Client, "get", lambda self, url, params: _Resp(next(calls))
    )


def test_returns_poster(monkeypatch):
    _patch(monkeypatch, {"Response": "True", "Poster": "http://x/p.jpg"})
    assert omdb.fetch_poster("12 Angry Men", "1957", "movie") == "http://x/p.jpg"


def test_na_poster_is_none(monkeypatch):
    _patch(monkeypatch, {"Response": "True", "Poster": "N/A"})
    assert omdb.fetch_poster("X", None, "movie") is None


def test_not_found_is_none(monkeypatch):
    # With a year: a miss retries without the year — both come back "not found".
    _patch(
        monkeypatch,
        {"Response": "False", "Error": "not found"},
        {"Response": "False", "Error": "not found"},
    )
    assert omdb.fetch_poster("X", "2000", "movie") is None


def test_wrong_year_retries_without_year(monkeypatch):
    # First (year-scoped) lookup misses; retry on the title alone finds it.
    _patch(
        monkeypatch,
        {"Response": "False", "Error": "not found"},
        {"Response": "True", "Poster": "http://x/hit.jpg"},
    )
    assert omdb.fetch_poster("V for Vendetta", "2005", "movie") == "http://x/hit.jpg"


def test_no_key_is_none(monkeypatch):
    class _NoKey:
        omdb_api_key = ""

    monkeypatch.setattr(omdb, "get_settings", lambda: _NoKey())
    assert omdb.fetch_poster("X", "2000", "movie") is None
