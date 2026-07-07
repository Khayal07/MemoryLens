"""Akinator mode: clarify parser + the pipeline's weak-search question logic.
No network — a fake LLM stands in for the real client."""

import json

import pytest

from app.ai.clarify import ClarifyParseError, parse_clarification
from app.ai.llm import LLMError
from app.ai.pipeline import SearchPipeline
from app.schemas.search import ResultItem


class FakeLLM:
    def __init__(self, payload: str) -> None:
        self.payload = payload
        self.json_calls = 0

    def complete_json(self, system: str, user: str, temperature: float = 0.2) -> str:
        self.json_calls += 1
        return self.payload

    def complete_text(self, system: str, user: str, temperature: float = 0.3) -> str:
        return ""


class BoomLLM(FakeLLM):
    def complete_json(self, system: str, user: str, temperature: float = 0.2) -> str:
        raise LLMError("provider down")


class FakeCategory:
    id = 1
    display_name = "Movies"
    key = "misc"  # outside every free-form image source set — no network


def _clarify_payload(question="Was it animated or live-action?"):
    return json.dumps({"question": question})


def _pipeline(llm, floor=65.0, enabled=True):
    return SearchPipeline(
        retriever=None,
        reranker=None,
        llm=llm,
        clarify_enabled=enabled,
        clarify_floor=floor,
    )


def _result(confidence: float, title="Inception", source: str | None = None) -> ResultItem:
    meta = {"source": source} if source else {}
    return ResultItem(
        item_id=5, title=title, description="x", confidence=confidence, metadata=meta
    )


# --- parser ---------------------------------------------------------------


def test_parse_clarification_valid():
    assert parse_clarification(_clarify_payload()).question == "Was it animated or live-action?"


def test_parse_clarification_code_fenced():
    raw = "```json\n" + _clarify_payload() + "\n```"
    assert parse_clarification(raw).question == "Was it animated or live-action?"


def test_parse_clarification_empty_raises():
    with pytest.raises(ClarifyParseError):
        parse_clarification("")


def test_parse_clarification_garbage_raises():
    with pytest.raises(ClarifyParseError):
        parse_clarification("no json here")


# --- pipeline logic ---------------------------------------------------------


def test_question_attached_below_floor():
    llm = FakeLLM(_clarify_payload())
    p = _pipeline(llm)
    q = p._maybe_clarify(FakeCategory(), "a dream movie", [_result(40.0)])
    assert q == "Was it animated or live-action?"
    assert llm.json_calls == 1


def test_no_question_above_floor():
    llm = FakeLLM(_clarify_payload())
    p = _pipeline(llm)
    q = p._maybe_clarify(FakeCategory(), "a dream movie", [_result(80.0)])
    assert q is None
    assert llm.json_calls == 0  # never called the LLM


def test_corroborated_freeform_hero_suppresses_question():
    # The catalog's best grounded row names the SAME title as the AI hero — settled.
    llm = FakeLLM(_clarify_payload())
    p = _pipeline(llm)
    results = [
        _result(90.0, title="12 Angry Men", source="gpt-knowledge"),
        _result(62.6, title="12 Angry Men"),
    ]
    assert p._maybe_clarify(FakeCategory(), "people arguing in a room", results) is None
    assert llm.json_calls == 0


def test_uncorroborated_freeform_hero_still_asks():
    # The AI guessed one title, the catalog another — genuinely unsettled, so ask.
    llm = FakeLLM(_clarify_payload())
    p = _pipeline(llm)
    results = [
        _result(80.0, title="The Fugitive", source="gpt-knowledge"),
        _result(29.8, title="Lost Youth"),
    ]
    q = p._maybe_clarify(FakeCategory(), "a chase in the rain", results)
    assert q == "Was it animated or live-action?"


def test_freeform_hero_without_any_grounded_asks():
    # World-knowledge answer with zero catalog backup — still worth one question.
    llm = FakeLLM(_clarify_payload())
    p = _pipeline(llm)
    results = [_result(85.0, title="Counting Stars", source="gpt-knowledge")]
    assert p._maybe_clarify(FakeCategory(), "counting song", results) is not None


def test_no_results_still_asks():
    llm = FakeLLM(_clarify_payload())
    p = _pipeline(llm)
    assert p._maybe_clarify(FakeCategory(), "a dream movie", []) is not None


def test_no_question_when_disabled():
    llm = FakeLLM(_clarify_payload())
    p = _pipeline(llm, enabled=False)
    assert p._maybe_clarify(FakeCategory(), "a dream movie", []) is None
    assert llm.json_calls == 0


def test_empty_question_dropped():
    p = _pipeline(FakeLLM(_clarify_payload(question="")))
    assert p._maybe_clarify(FakeCategory(), "a dream movie", []) is None


def test_language_slip_question_scrubbed():
    # nano asked in Russian on an English memory — the whole question is dropped.
    p = _pipeline(FakeLLM(_clarify_payload(question="Это был мультфильм?")))
    assert p._maybe_clarify(FakeCategory(), "a dream movie", []) is None


def test_in_language_question_kept():
    # Azerbaijani memory keeps its Azerbaijani (non-ASCII) question.
    p = _pipeline(FakeLLM(_clarify_payload(question="Film cizgi filmi idi, yoxsa çəkiliş?")))
    q = p._maybe_clarify(FakeCategory(), "yuxu haqqında film, çox qəribə", [])
    assert q == "Film cizgi filmi idi, yoxsa çəkiliş?"


def test_llm_failure_returns_none():
    p = _pipeline(BoomLLM(""))
    assert p._maybe_clarify(FakeCategory(), "a dream movie", []) is None
