"""Admin surface: token gate (fail-closed) + catalog_stats shape. Fake session,
no Postgres/network."""

from types import SimpleNamespace

import pytest

from app.api.v1 import admin
from app.core.errors import NotFoundError, UnauthorizedError
from app.services import catalog_admin


# --- token gate --------------------------------------------------------------


def _patch_token(monkeypatch, token):
    monkeypatch.setattr(admin, "get_settings", lambda: SimpleNamespace(admin_token=token))


def test_require_admin_blank_token_is_404(monkeypatch):
    _patch_token(monkeypatch, "")
    with pytest.raises(NotFoundError):
        admin.require_admin("anything")


def test_require_admin_wrong_token_is_401(monkeypatch):
    _patch_token(monkeypatch, "secret")
    with pytest.raises(UnauthorizedError):
        admin.require_admin("nope")
    with pytest.raises(UnauthorizedError):
        admin.require_admin(None)


def test_require_admin_correct_token_passes(monkeypatch):
    _patch_token(monkeypatch, "secret")
    assert admin.require_admin("secret") is None


# --- catalog_stats -----------------------------------------------------------


class _Scalars:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return self

    def all(self):
        return self._items


class _One:
    def __init__(self, value):
        self._value = value

    def scalar_one(self):
        return self._value


class StatsDB:
    """Replays: category list, then 4 counts per category (items, with_embedding,
    with_image, gpt_rows)."""

    def __init__(self, categories, counts):
        self._responses = [_Scalars(categories)] + [_One(c) for c in counts]

    def execute(self, _stmt):
        return self._responses.pop(0)


def test_catalog_stats_shape():
    cat = SimpleNamespace(id=1, key="movies", display_name="Movies")
    db = StatsDB([cat], counts=[10, 8, 9, 1])
    stats = catalog_admin.catalog_stats(db)
    assert stats["total_items"] == 10
    assert stats["categories"] == [
        {
            "key": "movies",
            "display_name": "Movies",
            "items": 10,
            "with_embedding": 8,
            "with_image": 9,
            "gpt_rows": 1,
        }
    ]


def test_catalog_stats_empty_catalog():
    db = StatsDB([], counts=[])
    stats = catalog_admin.catalog_stats(db)
    assert stats == {"total_items": 0, "categories": []}
