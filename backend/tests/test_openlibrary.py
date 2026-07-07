"""OpenLibrary cover client — no real network; httpx.Client.get is monkeypatched."""

import httpx

import app.infra.openlibrary as ol


class _Resp:
    def __init__(self, data: dict) -> None:
        self._data = data

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._data


def _patch(monkeypatch, data: dict) -> None:
    monkeypatch.setattr(httpx.Client, "get", lambda self, url, params: _Resp(data))


def test_returns_cover_url(monkeypatch):
    _patch(monkeypatch, {"docs": [{"cover_i": 8231856}]})
    assert ol.fetch_book_cover("1984", "George Orwell") == (
        "https://covers.openlibrary.org/b/id/8231856-L.jpg"
    )


def test_skips_docs_without_cover(monkeypatch):
    _patch(monkeypatch, {"docs": [{"cover_i": None}, {"cover_i": 42}]})
    assert ol.fetch_book_cover("X") == "https://covers.openlibrary.org/b/id/42-L.jpg"


def test_no_docs_is_none(monkeypatch):
    _patch(monkeypatch, {"docs": []})
    assert ol.fetch_book_cover("Nothing") is None


def test_empty_title_is_none(monkeypatch):
    assert ol.fetch_book_cover("") is None
