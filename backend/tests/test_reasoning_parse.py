"""Unit tests for LLM output parsing — no network."""

import pytest

from app.ai.reasoning import ReasoningParseError, parse_reasoning


def test_parses_plain_json() -> None:
    raw = '{"matches": [{"item_id": 1, "reason": "fits", "rating": 0.9}], "category_mismatch": null}'
    result = parse_reasoning(raw)
    assert len(result.matches) == 1
    assert result.matches[0].item_id == 1
    assert result.category_mismatch is None


def test_parses_code_fenced_json() -> None:
    raw = '```json\n{"matches": [], "category_mismatch": null}\n```'
    result = parse_reasoning(raw)
    assert result.matches == []


def test_extracts_json_from_surrounding_prose() -> None:
    raw = 'Sure! Here it is: {"matches": [], "category_mismatch": ' \
          '{"suspected_category": "songs", "message": "Sounds like a song."}} Hope that helps.'
    result = parse_reasoning(raw)
    assert result.category_mismatch is not None
    assert result.category_mismatch.suspected_category == "songs"


def test_rating_out_of_range_rejected() -> None:
    raw = '{"matches": [{"item_id": 1, "reason": "x", "rating": 5}]}'
    with pytest.raises(ReasoningParseError):
        parse_reasoning(raw)


def test_empty_raises() -> None:
    with pytest.raises(ReasoningParseError):
        parse_reasoning("   ")


def test_garbage_raises() -> None:
    with pytest.raises(ReasoningParseError):
        parse_reasoning("no json here at all")
