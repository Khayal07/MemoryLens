"""Song-guess parsing + pipeline routing. No network: a fake LLM/retriever prove
that only songs route through the guess and that any failure falls back cleanly."""

from types import SimpleNamespace

import pytest

from app.ai.llm import LLMError
from app.ai.pipeline import SearchPipeline
from app.ai.song_guess import SongGuessParseError, parse_song_guess


# --- parser ------------------------------------------------------------------


def test_parse_valid():
    g = parse_song_guess('{"title": "Bohemian Rhapsody", "artist": "Queen", "description": "rock"}')
    assert g.title == "Bohemian Rhapsody" and g.artist == "Queen" and g.description == "rock"


def test_parse_code_fenced():
    g = parse_song_guess('```json\n{"title": "Yesterday", "artist": "The Beatles"}\n```')
    assert g.title == "Yesterday" and g.artist == "The Beatles"


def test_parse_empty_title_allowed():
    # The model saying "I don't know" is valid — the caller falls back to plain expansion.
    g = parse_song_guess('{"title": "", "artist": "", "description": ""}')
    assert g.title == ""


def test_parse_missing_artist_defaults_blank():
    g = parse_song_guess('{"title": "Imagine"}')
    assert g.title == "Imagine" and g.artist == ""


def test_parse_garbage_raises():
    with pytest.raises(SongGuessParseError):
        parse_song_guess("not json at all")
    with pytest.raises(SongGuessParseError):
        parse_song_guess("")


# --- pipeline routing --------------------------------------------------------


class RecordingRetriever:
    def __init__(self):
        self.calls = []

    def search(self, db, category_id, query, k=30, embed_text=None):
        self.calls.append({"keyword": query, "embed": embed_text})
        return []


class GuessLLM:
    def __init__(self, exc=None):
        self.exc = exc
        self.json_calls = 0

    def complete_json(self, system, user, **kw):
        self.json_calls += 1
        if self.exc:
            raise self.exc
        return '{"title": "Bohemian Rhapsody", "artist": "Queen", "description": "operatic rock"}'

    def complete_text(self, system, user, **kw):
        return ""


class CatDB:
    """_resolve_category needs only db.execute(...).scalar_one_or_none()."""

    def __init__(self, category):
        self._category = category

    def execute(self, _stmt):
        return SimpleNamespace(scalar_one_or_none=lambda: self._category)


def _pipeline(retriever, llm, song_guess_enabled=True):
    return SearchPipeline(
        retriever=retriever,
        reranker=None,
        llm=llm,
        hyde_enabled=False,
        translate_enabled=False,
        freeform_enabled=False,   # empty candidates → return [] without touching LLM/db
        clarify_enabled=False,
        song_guess_enabled=song_guess_enabled,
    )


def _cat(key):
    return SimpleNamespace(id=1, key=key, display_name=key.capitalize())


def test_songs_route_through_guess():
    r, llm = RecordingRetriever(), GuessLLM()
    _pipeline(r, llm).run(CatDB(_cat("songs")), "songs", "is this the real life is this just fantasy")
    assert llm.json_calls == 1
    call = r.calls[0]
    assert "Bohemian Rhapsody" in call["keyword"] and "Queen" in call["keyword"]
    assert "by Queen" in call["embed"]


def test_non_songs_do_not_call_song_guess():
    r, llm = RecordingRetriever(), GuessLLM()
    _pipeline(r, llm).run(CatDB(_cat("movies")), "movies", "twelve angry jurors in one room")
    assert llm.json_calls == 0
    # Keyword query is the plain memory, no injected title.
    assert "Bohemian Rhapsody" not in r.calls[0]["keyword"]


def test_song_guess_disabled_skips_expansion():
    r, llm = RecordingRetriever(), GuessLLM()
    _pipeline(r, llm, song_guess_enabled=False).run(CatDB(_cat("songs")), "songs", "a lyric memory")
    assert llm.json_calls == 0


def test_song_guess_llm_error_falls_back():
    r, llm = RecordingRetriever(), GuessLLM(exc=LLMError("boom"))
    _pipeline(r, llm).run(CatDB(_cat("songs")), "songs", "a lyric memory here")
    # Guess attempted but failed → plain keyword query, retrieval still ran.
    assert llm.json_calls == 1
    assert "Bohemian Rhapsody" not in r.calls[0]["keyword"]
