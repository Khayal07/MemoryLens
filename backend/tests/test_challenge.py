"""Daily challenge: clue parsing/leak-guarding, progress gating, answer hiding,
guess matching, and deterministic pick — fake DB objects, no Postgres/network."""

from datetime import date
from types import SimpleNamespace

import pytest

from app.ai.matching import same_title
from app.services.challenge_service import (
    GUESS_LIMIT,
    _fallback_clues,
    _leaks_title,
    _mask_title,
    _parse_clues,
    _pick_item,
    _to_state,
)


def _category(display="Movies"):
    return SimpleNamespace(id=1, key="movies", display_name=display)


def _item(title="The Blair Witch Project", description="Students film a legend in the woods."):
    return SimpleNamespace(
        id=7,
        category_id=1,
        title=title,
        description=description,
        image_url="http://img/x.jpg",
        source_url="http://src/x",
        category=_category(),
    )


def _challenge(clues=None):
    return SimpleNamespace(
        id=42,
        challenge_date=date(2026, 7, 8),
        item_id=7,
        item=_item(),
        clues=clues if clues is not None else ["c1", "c2", "c3"],
    )


def _attempt(guesses=0, solved=False):
    return SimpleNamespace(guesses_used=guesses, solved=solved)


class StateDB:
    """Only _to_state's db.get(Category, ...) is needed."""

    def get(self, _model, _pk):
        return _category()


# --- clue parsing / leak guard ---------------------------------------------


def test_parse_clues_valid():
    raw = '{"clues": ["one", "two", "three"]}'
    assert _parse_clues(raw) == ["one", "two", "three"]


def test_parse_clues_code_fenced_and_capped():
    raw = '```json\n{"clues": ["a", "b", "c", "d"]}\n```'
    assert _parse_clues(raw) == ["a", "b", "c"]


def test_parse_clues_garbage_raises():
    with pytest.raises(ValueError):
        _parse_clues("not json")
    with pytest.raises(ValueError):
        _parse_clues('{"noclues": 1}')


def test_leaks_title_detects_title_words():
    assert _leaks_title("A blair project gone wrong", "The Blair Witch Project")
    assert not _leaks_title("Found footage in dark woods", "The Blair Witch Project")


def test_leaks_title_ignores_stopwords_and_short_words():
    # "the"/"of" and 2-letter words never count as leaks.
    assert not _leaks_title("One of the best", "The Lord of the Rings")


def test_mask_title_blocks_answer():
    masked = _mask_title("The Blair Witch Project is a witch film.", "The Blair Witch Project")
    assert "Blair" not in masked and "witch" not in masked.lower()
    assert "▮▮▮" in masked


def test_fallback_clues_never_leak_and_fill_three():
    clues = _fallback_clues(_item(description="The Blair Witch Project scares students."))
    assert len(clues) == 3
    assert all(not _leaks_title(c, "The Blair Witch Project") for c in clues)


def test_clue_topup_is_positional():
    """When the LLM supplied 2 good clues, slot 3 gets the MOST revealing fallback
    (masked description), not the generic 'catalog shelf' opener."""
    from app.services.challenge_service import _clues_for

    class TwoClueLLM:
        def complete_json(self, system, user, temperature=0.2):
            return '{"clues": ["cryptic one", "concrete two", "contains blair so dropped"]}'

    clues = _clues_for(_item(), llm=TwoClueLLM())
    assert clues[:2] == ["cryptic one", "concrete two"]
    assert "shelf of the catalog" not in clues[2]  # positional, most-revealing fallback
    assert not _leaks_title(clues[2], "The Blair Witch Project")


# --- progress gating / answer hiding ----------------------------------------


def test_fresh_state_shows_one_clue_and_no_answer():
    s = _to_state(StateDB(), _challenge(), None)
    assert s.clues == ["c1"]
    assert s.guesses_used == 0
    assert not s.finished
    assert s.answer is None  # never leak the answer mid-game


def test_wrong_guess_reveals_next_clue_only():
    s = _to_state(StateDB(), _challenge(), _attempt(guesses=1))
    assert s.clues == ["c1", "c2"]
    assert s.answer is None


def test_solved_reveals_answer_and_all_clues():
    s = _to_state(StateDB(), _challenge(), _attempt(guesses=2, solved=True), correct=True)
    assert s.solved and s.finished and s.correct
    assert s.clues == ["c1", "c2", "c3"]
    assert s.answer is not None and s.answer.title == "The Blair Witch Project"


def test_exhausted_reveals_answer():
    s = _to_state(StateDB(), _challenge(), _attempt(guesses=GUESS_LIMIT), correct=False)
    assert s.finished and not s.solved
    assert s.answer is not None


# --- guess matching -----------------------------------------------------------


def test_guess_matching_is_fuzzy():
    assert same_title("blair witch", "The Blair Witch Project")
    assert same_title("the blair witch project!", "The Blair Witch Project")
    assert not same_title("The Ring", "The Blair Witch Project")


# --- deterministic pick --------------------------------------------------------


class _ScalarsAll:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return self

    def all(self):
        return self._items


class _ScalarOne:
    def __init__(self, value):
        self._value = value

    def scalar_one(self):
        return self._value


class SeqDB:
    """Replays a fixed sequence of query results: categories, count, item."""

    def __init__(self, item):
        self._responses = [
            _ScalarsAll([_category()]),
            _ScalarOne(3),
            _ScalarOne(item),
        ]

    def execute(self, _stmt):
        return self._responses.pop(0)


def test_pick_is_deterministic_for_a_date():
    item = _item()
    day = date(2026, 7, 8)
    assert _pick_item(SeqDB(item), day) is item
    assert _pick_item(SeqDB(item), day) is item  # same date, same data → same pick
