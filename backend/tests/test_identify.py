"""Free-form identification: parser + the pipeline's low-confidence fallback logic.
No network — a fake LLM stands in for the real client."""

import json

import pytest

from app.ai.identify import IdentifyParseError, parse_identification
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


class FakeCategory:
    display_name = "Songs"
    key = "songs"  # not an OMDb-poster category, so no network call in these tests


def _identify_payload(title="Counting Stars", conf=0.82):
    return json.dumps(
        {
            "title": title,
            "detail": "OneRepublic, 2013",
            "reason": "Upbeat 2010s pop-rock song literally titled after counting stars.",
            "confidence": conf,
        }
    )


def _pipeline(llm, floor=65.0, enabled=True):
    return SearchPipeline(
        retriever=None,
        reranker=None,
        llm=llm,
        freeform_enabled=enabled,
        freeform_confidence_floor=floor,
    )


def _grounded(confidence: float) -> ResultItem:
    return ResultItem(item_id=5, title="Viva la Vida", description="x", confidence=confidence)


# --- parser ---------------------------------------------------------------


def test_parse_identification_valid():
    ident = parse_identification(_identify_payload())
    assert ident.title == "Counting Stars"
    assert ident.confidence == pytest.approx(0.82)


def test_parse_identification_code_fenced():
    raw = "```json\n" + _identify_payload() + "\n```"
    assert parse_identification(raw).title == "Counting Stars"


def test_parse_identification_empty_raises():
    with pytest.raises(IdentifyParseError):
        parse_identification("")


# --- fallback logic -------------------------------------------------------


def test_strong_grounded_result_skips_freeform():
    llm = FakeLLM(_identify_payload())
    p = _pipeline(llm)
    results = [_grounded(90.0)]
    out = p._maybe_add_freeform(FakeCategory(), "count the stars", results, max_results=5)
    assert out == results
    assert llm.json_calls == 0  # never called the LLM


def test_weak_grounded_result_triggers_freeform_as_primary():
    llm = FakeLLM(_identify_payload())
    p = _pipeline(llm)
    out = p._maybe_add_freeform(FakeCategory(), "count the stars", [_grounded(58.9)], max_results=5)
    assert llm.json_calls == 1
    assert out[0].title == "Counting Stars"  # freeform is now the top result
    assert out[0].metadata.get("source") == "gpt-knowledge"
    assert out[0].image_url is None
    assert out[1].title == "Viva la Vida"  # weak catalog match kept as alternative


def test_no_results_triggers_freeform():
    llm = FakeLLM(_identify_payload())
    p = _pipeline(llm)
    out = p._maybe_add_freeform(FakeCategory(), "count the stars", [], max_results=5)
    assert out and out[0].title == "Counting Stars"


def test_empty_title_not_added():
    llm = FakeLLM(_identify_payload(title=""))
    p = _pipeline(llm)
    out = p._maybe_add_freeform(FakeCategory(), "mystery", [], max_results=5)
    assert out == []


def test_confidence_capped_below_certainty():
    llm = FakeLLM(_identify_payload(conf=1.0))
    p = _pipeline(llm)
    out = p._maybe_add_freeform(FakeCategory(), "count the stars", [], max_results=5)
    assert out[0].confidence <= 90.0


def test_freeform_disabled_returns_unchanged():
    llm = FakeLLM(_identify_payload())
    p = _pipeline(llm, enabled=False)
    out = p._maybe_add_freeform(FakeCategory(), "count the stars", [], max_results=5)
    assert out == []
    assert llm.json_calls == 0
