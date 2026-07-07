"""RAWG game-image client — no real network; httpx.Client.get is monkeypatched."""

import httpx

import app.infra.rawg as rawg


class _Settings:
    rawg_api_key = "testkey"


class _Resp:
    def __init__(self, data: dict) -> None:
        self._data = data

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._data


def _patch(monkeypatch, data: dict) -> None:
    monkeypatch.setattr(rawg, "get_settings", lambda: _Settings())
    monkeypatch.setattr(httpx.Client, "get", lambda self, url, params: _Resp(data))


def test_returns_first_image(monkeypatch):
    _patch(monkeypatch, {"results": [{"background_image": "https://x/g.jpg"}]})
    assert rawg.fetch_game_image("Red Dead Redemption 2") == "https://x/g.jpg"


def test_skips_results_without_image(monkeypatch):
    _patch(
        monkeypatch,
        {"results": [{"background_image": None}, {"background_image": "https://x/two.jpg"}]},
    )
    assert rawg.fetch_game_image("X") == "https://x/two.jpg"


def test_no_results_is_none(monkeypatch):
    _patch(monkeypatch, {"results": []})
    assert rawg.fetch_game_image("Nothing") is None


def test_no_key_is_none(monkeypatch):
    class _NoKey:
        rawg_api_key = ""

    monkeypatch.setattr(rawg, "get_settings", lambda: _NoKey())
    assert rawg.fetch_game_image("X") is None
