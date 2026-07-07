"""TMDB person-image client — no real network; httpx.Client.get is monkeypatched."""

import httpx

import app.infra.tmdb as tmdb


class _Settings:
    tmdb_api_key = "testkey"


class _Resp:
    def __init__(self, data: dict) -> None:
        self._data = data

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._data


def _patch(monkeypatch, data: dict) -> None:
    monkeypatch.setattr(tmdb, "get_settings", lambda: _Settings())
    monkeypatch.setattr(httpx.Client, "get", lambda self, url, params: _Resp(data))


def test_returns_first_photo(monkeypatch):
    _patch(monkeypatch, {"results": [{"profile_path": "/abc.jpg"}]})
    assert tmdb.fetch_person_image("Carrie-Anne Moss") == "https://image.tmdb.org/t/p/w500/abc.jpg"


def test_skips_results_without_photo(monkeypatch):
    _patch(
        monkeypatch,
        {"results": [{"profile_path": None}, {"profile_path": "/second.jpg"}]},
    )
    assert tmdb.fetch_person_image("Someone") == "https://image.tmdb.org/t/p/w500/second.jpg"


def test_no_results_is_none(monkeypatch):
    _patch(monkeypatch, {"results": []})
    assert tmdb.fetch_person_image("Nobody") is None


def test_no_key_is_none(monkeypatch):
    class _NoKey:
        tmdb_api_key = ""

    monkeypatch.setattr(tmdb, "get_settings", lambda: _NoKey())
    assert tmdb.fetch_person_image("Carrie-Anne Moss") is None
