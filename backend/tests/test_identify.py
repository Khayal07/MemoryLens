"""Free-form identification: parser + the pipeline's low-confidence fallback logic.
No network — a fake LLM stands in for the real client."""

import json

import pytest

from app.ai.identify import IdentifyParseError, parse_identification
from app.ai.pipeline import SearchPipeline
from app.infra.models import Item
from app.schemas.search import ResultItem


class FakeLLM:
    def __init__(self, payload: str) -> None:
        self.payload = payload
        self.json_calls = 0

    def complete_json(
        self, system: str, user: str, temperature: float = 0.2, model: str | None = None
    ) -> str:
        self.json_calls += 1
        self.last_model = model
        return self.payload

    def complete_text(self, system: str, user: str, temperature: float = 0.3) -> str:
        return ""


class FakeResult:
    def __init__(self, item):
        self._item = item

    def scalar_one_or_none(self):
        return self._item


class FakeDB:
    """Minimal stand-in for a Session so the materialize path runs without Postgres.
    `existing` is the row returned from the find query (None → insert)."""

    def __init__(self, existing: Item | None = None) -> None:
        self.existing = existing
        self.added: list[Item] = []
        self._next_id = 100

    def execute(self, _stmt):
        return FakeResult(self.existing)

    def add(self, obj):
        self.added.append(obj)

    def flush(self):
        for obj in self.added:
            if getattr(obj, "id", None) is None:
                obj.id = self._next_id
                self._next_id += 1

    def rollback(self):
        pass


class FakeCategory:
    id = 1
    display_name = "Songs"
    # A key outside every free-form image source set (all 6 real categories now have
    # one), so these tests never hit OMDb / TMDB / iTunes / OpenLibrary / RAWG.
    key = "misc"


def _identify_payload(
    title="Counting Stars",
    conf=0.82,
    conf_reason="Lyrics match exactly.",
    description="",
):
    return json.dumps(
        {
            "title": title,
            "detail": "OneRepublic, 2013",
            "description": description,
            "reason": "Upbeat 2010s pop-rock song literally titled after counting stars.",
            "confidence": conf,
            "confidence_reason": conf_reason,
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


def test_parse_identification_confidence_reason():
    ident = parse_identification(_identify_payload(conf_reason="Title is literal."))
    assert ident.confidence_reason == "Title is literal."
    # And the field is optional for older/other payload shapes.
    legacy = json.dumps({"title": "X", "confidence": 0.5})
    assert parse_identification(legacy).confidence_reason == ""


def test_freeform_result_carries_confidence_note():
    p = _pipeline(FakeLLM(_identify_payload()))
    out = p._maybe_add_freeform(
        FakeDB(), FakeCategory(), "count the stars", [_grounded(58.9)], max_results=5
    )
    assert out[0].confidence_note == "Lyrics match exactly."


def test_confidence_note_language_slip_scrubbed():
    # Portuguese-style non-ASCII note to an ASCII memory → scrubbed to None.
    p = _pipeline(FakeLLM(_identify_payload(conf_reason="é uma correspondência exata")))
    out = p._maybe_add_freeform(
        FakeDB(), FakeCategory(), "count the stars", [_grounded(58.9)], max_results=5
    )
    assert out[0].confidence_note is None


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
    out = p._maybe_add_freeform(FakeDB(), FakeCategory(), "count the stars", results, max_results=5)
    assert out == results
    assert llm.json_calls == 0  # never called the LLM


def test_weak_grounded_result_triggers_freeform_as_primary():
    llm = FakeLLM(_identify_payload())
    p = _pipeline(llm)
    out = p._maybe_add_freeform(
        FakeDB(), FakeCategory(), "count the stars", [_grounded(58.9)], max_results=5
    )
    assert llm.json_calls == 1
    assert out[0].title == "Counting Stars"  # freeform is now the top result
    assert out[0].metadata.get("source") == "gpt-knowledge"
    assert out[0].image_url is None
    assert out[1].title == "Viva la Vida"  # weak catalog match kept as alternative


def test_greyzone_grounded_overridden_when_freeform_names_different_title():
    # 67 is above the 65 floor but inside the 8-pt grey margin. The catalog match is
    # "Viva la Vida"; the LLM names "Counting Stars" — a different title, so the wrong
    # grounded pick is displaced.
    llm = FakeLLM(_identify_payload())
    p = _pipeline(llm)
    out = p._maybe_add_freeform(
        FakeDB(), FakeCategory(), "count the stars", [_grounded(67.0)], max_results=5
    )
    assert llm.json_calls == 1
    assert out[0].title == "Counting Stars"
    assert out[1].title == "Viva la Vida"


def test_greyzone_grounded_promoted_when_freeform_names_same_title():
    # Grey zone and the LLM confirms the same title — keep the grounded row
    # (poster/src/rich description) but lift its confidence by the agreement.
    llm = FakeLLM(_identify_payload(title="Viva la Vida"))
    p = _pipeline(llm)
    grounded = _grounded(67.0)
    out = p._maybe_add_freeform(
        FakeDB(), FakeCategory(), "viva la vida", [grounded], max_results=5
    )
    assert llm.json_calls == 1  # LLM consulted...
    assert out == [grounded]  # ...no gpt duplicate added
    assert out[0].confidence == 82.0  # lifted to the (capped) free-form level
    assert out[0].breakdown["ai_agreement"] == 15.0


def test_weak_grounded_same_title_promoted_not_duplicated():
    # Below the floor the AI names a title the catalog ALREADY has (even not first):
    # promote that grounded row to the top instead of showing Titanic twice.
    llm = FakeLLM(_identify_payload(title="Counting Stars"))
    p = _pipeline(llm)
    other = _grounded(58.9)  # "Viva la Vida"
    match = ResultItem(item_id=9, title="Counting Stars", description="rich catalog text", confidence=52.0)
    out = p._maybe_add_freeform(
        FakeDB(), FakeCategory(), "count the stars", [other, match], max_results=5
    )
    assert len(out) == 2  # no third gpt row
    assert out[0] is match  # grounded row promoted to Best Match
    assert out[0].description == "rich catalog text"  # catalog detail preserved
    assert out[0].confidence == 82.0
    assert out[0].breakdown["ai_agreement"] == 30.0
    assert out[0].confidence_note == "Lyrics match exactly."  # borrowed from the AI
    assert out[1] is other


def test_freeform_description_used_when_present():
    llm = FakeLLM(_identify_payload(description="A 2013 anthem by OneRepublic about dreaming past money worries."))
    p = _pipeline(llm)
    out = p._maybe_add_freeform(FakeDB(), FakeCategory(), "count the stars", [], max_results=5)
    assert out[0].description.startswith("A 2013 anthem")


def test_freeform_description_language_slip_falls_back_to_detail():
    # Non-ASCII description to an ASCII memory → scrubbed, terse detail shown instead.
    llm = FakeLLM(_identify_payload(description="Uma música de 2013 sobre sonhos…"))
    p = _pipeline(llm)
    out = p._maybe_add_freeform(FakeDB(), FakeCategory(), "count the stars", [], max_results=5)
    assert out[0].description == "OneRepublic, 2013"


def test_confident_grounded_above_grey_margin_skips_llm():
    # 74 ≥ 65 + 8 → trust the catalog, never call the LLM.
    llm = FakeLLM(_identify_payload())
    p = _pipeline(llm)
    results = [_grounded(74.0)]
    out = p._maybe_add_freeform(FakeDB(), FakeCategory(), "count the stars", results, max_results=5)
    assert out == results
    assert llm.json_calls == 0


def test_no_results_triggers_freeform():
    llm = FakeLLM(_identify_payload())
    p = _pipeline(llm)
    out = p._maybe_add_freeform(FakeDB(), FakeCategory(), "count the stars", [], max_results=5)
    assert out and out[0].title == "Counting Stars"


def test_empty_title_not_added():
    llm = FakeLLM(_identify_payload(title=""))
    p = _pipeline(llm)
    out = p._maybe_add_freeform(FakeDB(), FakeCategory(), "mystery", [], max_results=5)
    assert out == []


def test_confidence_capped_below_certainty():
    llm = FakeLLM(_identify_payload(conf=1.0))
    p = _pipeline(llm)
    out = p._maybe_add_freeform(FakeDB(), FakeCategory(), "count the stars", [], max_results=5)
    assert out[0].confidence <= 90.0


def test_freeform_disabled_returns_unchanged():
    llm = FakeLLM(_identify_payload())
    p = _pipeline(llm, enabled=False)
    out = p._maybe_add_freeform(FakeDB(), FakeCategory(), "count the stars", [], max_results=5)
    assert out == []
    assert llm.json_calls == 0


# --- materialization ------------------------------------------------------


def test_freeform_materializes_a_real_catalog_row():
    """A free-form answer becomes a saveable catalog row: real item_id, a Google
    'View source', gpt-knowledge source, and NO embedding created."""
    db = FakeDB()
    p = _pipeline(FakeLLM(_identify_payload()))
    out = p._maybe_add_freeform(db, FakeCategory(), "count the stars", [], max_results=5)
    hero = out[0]

    assert hero.item_id > 0  # no longer the un-saveable item_id=0
    assert hero.source_url.startswith("https://www.google.com/search?q=")
    assert "Counting+Stars" in hero.source_url

    assert len(db.added) == 1
    row = db.added[0]
    assert isinstance(row, Item)
    assert row.external_id == "gpt:counting-stars"
    assert row.item_metadata["source"] == "gpt-knowledge"
    assert row.image_url is None  # songs → no OMDb poster
    assert row.embedding is None  # inert for retrieval


def test_freeform_reuses_existing_row_no_duplicate():
    existing = Item(id=42, category_id=1, external_id="gpt:counting-stars", title="Counting Stars")
    db = FakeDB(existing=existing)
    p = _pipeline(FakeLLM(_identify_payload()))
    out = p._maybe_add_freeform(db, FakeCategory(), "count the stars", [], max_results=5)

    assert out[0].item_id == 42  # reused the existing row
    assert db.added == []  # no duplicate inserted


def test_materialize_failure_falls_back_to_unsaveable():
    """If the DB write blows up, the search still returns the answer as item_id=0."""

    class BoomDB(FakeDB):
        def execute(self, _stmt):
            raise RuntimeError("db down")

    p = _pipeline(FakeLLM(_identify_payload()))
    out = p._maybe_add_freeform(BoomDB(), FakeCategory(), "count the stars", [], max_results=5)
    assert out[0].item_id == 0
    assert out[0].title == "Counting Stars"
