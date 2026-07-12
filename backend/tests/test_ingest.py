"""Ingestion tests that need no network and no torch — they exercise fixture
loading, normalization and adapter selection only."""

import pytest

from app.domain.categories import CATEGORY_KEYS
from app.ingest.base import NormalizedItem
from app.ingest.fixture_adapter import FixtureAdapter
from app.ingest.registry import get_adapter


@pytest.mark.parametrize("key", sorted(CATEGORY_KEYS))
def test_every_category_has_a_nonempty_fixture(key: str) -> None:
    items = list(FixtureAdapter(key).fetch())
    assert items, f"fixture for '{key}' is empty"
    for item in items:
        assert item.external_id
        assert item.title
        assert isinstance(item.metadata, dict)


def test_embedding_text_combines_title_and_description() -> None:
    item = NormalizedItem(external_id="x", title="Title", description="A plot.")
    assert item.embedding_text() == "Title. A plot."


def test_embedding_text_folds_in_song_artist() -> None:
    # Songs carry an artist so "<lyric> by <artist>" memories match; the artist lands
    # in both the embedding and the keyword tsvector.
    item = NormalizedItem(
        external_id="s", title="Bohemian Rhapsody", description="An operatic rock epic.",
        metadata={"artist": "Queen"},
    )
    assert item.embedding_text() == "Bohemian Rhapsody. Queen. An operatic rock epic."


def test_embedding_text_without_artist_is_unchanged() -> None:
    item = NormalizedItem(
        external_id="m", title="Title", description="A plot.", metadata={"year": 1999}
    )
    assert item.embedding_text() == "Title. A plot."


def test_fixture_source_forces_fixture_adapter() -> None:
    assert isinstance(get_adapter("movies", source="fixture"), FixtureAdapter)


def test_auto_falls_back_to_fixture_without_api_key() -> None:
    # No TMDB key in the test env → auto should choose fixtures even for movies.
    assert isinstance(get_adapter("movies", source="auto"), FixtureAdapter)


def test_limit_is_respected() -> None:
    items = list(FixtureAdapter("movies").fetch(limit=2))
    assert len(items) == 2


def test_movies_fixture_includes_verification_title() -> None:
    titles = {i.title for i in FixtureAdapter("movies").fetch()}
    assert "12 Angry Men" in titles
