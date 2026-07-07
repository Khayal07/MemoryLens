"""iTunes cover-art client — no real network; httpx.Client.get is monkeypatched."""

import httpx

import app.infra.itunes as itunes


class _Resp:
    def __init__(self, data: dict) -> None:
        self._data = data

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._data


def _patch(monkeypatch, data: dict) -> None:
    monkeypatch.setattr(httpx.Client, "get", lambda self, url, params: _Resp(data))


def test_returns_upscaled_cover(monkeypatch):
    _patch(monkeypatch, {"results": [{"artworkUrl100": "https://x/a/100x100bb.jpg"}]})
    assert itunes.fetch_song_cover("We Will Rock You", "Queen") == "https://x/a/600x600bb.jpg"


def test_no_results_is_none(monkeypatch):
    _patch(monkeypatch, {"results": []})
    assert itunes.fetch_song_cover("Nothing") is None


def test_empty_title_is_none(monkeypatch):
    assert itunes.fetch_song_cover("") is None
