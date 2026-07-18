"""Answer-language override: the directive helper, the relaxed language-slip guard, the
cache-key split, and the request schema. No network."""

from app.ai.pipeline import SearchPipeline, _is_language_slip
from app.ai.prompts.language import language_directive, normalize_language
from app.ai.prompts import clarify, identify
from app.ai.prompts.reasoning import build_user_prompt
from app.infra.cache import _key
from app.schemas.search import SearchRequest


# --- normalize + directive -------------------------------------------------


def test_normalize_language():
    assert normalize_language("az") == "az"
    assert normalize_language("EN") == "en"
    assert normalize_language(" Az ") == "az"
    assert normalize_language("fr") is None
    assert normalize_language(None) is None
    assert normalize_language("") is None


def test_directive_names_language():
    assert "Azerbaijani" in language_directive("az")
    assert "English" in language_directive("en")
    assert language_directive(None) == ""
    assert language_directive("fr") == ""


def test_prompt_builders_embed_directive():
    assert "Azerbaijani" in build_user_prompt("Movies", ["movies"], "a memory", [], "az")
    assert "Azerbaijani" in identify.build_user_prompt("Movies", "a memory", "az")
    assert "Azerbaijani" in clarify.build_user_prompt("Movies", "a memory", [], "az")
    # No language ⇒ default reminder, no override directive.
    assert "LANGUAGE OVERRIDE" not in build_user_prompt("Movies", ["movies"], "m", [], None)


# --- relaxed language-slip guard ------------------------------------------


def test_slip_guard_auto_mode_unchanged():
    # Non-ASCII reply to an English (ASCII) memory is a slip when auto-detecting.
    assert _is_language_slip("é uma série", "an english memory") is True
    # In-language answer to a non-ASCII memory is fine.
    assert _is_language_slip("Azərbaycan cavabı", "qəribə xatirə") is False


def test_slip_guard_forced_az_keeps_azerbaijani():
    # Forcing AZ: an Azerbaijani reply to an English memory is INTENDED, not a slip.
    assert _is_language_slip("Bu, məhz həmin filmdir", "a jury in a room", "az") is False
    # ...but Cyrillic is still always scrubbed.
    assert _is_language_slip("Это фильм", "a jury in a room", "az") is True


def test_slip_guard_forced_en_scrubs_non_ascii():
    # Forcing EN: a non-ASCII reply is a slip.
    assert _is_language_slip("é uma série", "qəribə xatirə", "en") is True
    assert _is_language_slip("A courtroom drama", "qəribə xatirə", "en") is False


# --- cache key -------------------------------------------------------------


def test_cache_key_splits_by_language():
    en = _key("movies", "twelve jurors", "en")
    az = _key("movies", "twelve jurors", "az")
    auto = _key("movies", "twelve jurors", None)
    assert en != az != auto and en != auto
    assert ":en:" in en and ":az:" in az and ":auto:" in auto


# --- request schema --------------------------------------------------------


def test_search_request_accepts_language():
    assert SearchRequest(category="movies", query="a memory", language="az").language == "az"
    # Optional — omitted defaults to None (auto-detect).
    assert SearchRequest(category="movies", query="a memory").language is None


# --- pipeline threading (no network: gate skips the LLM) -------------------


def test_build_results_forced_az_leaves_blank_reason_not_english_fallback():
    from app.ai.reasoning import LLMMatch, LLMReasoning
    from app.ai.types import Candidate

    p = SearchPipeline(retriever=None, reranker=None, llm=None)
    cand = Candidate(item_id=1, title="12 Angry Men", description="jury room drama")
    reasoning = LLMReasoning(matches=[LLMMatch(item_id=1, reason="", rating=0.9)],
                             category_mismatch=None)
    # Forced AZ + empty reason ⇒ no English fallback injected (would be a language mix).
    results, _ = p._build_results("movies", "a jury in a room", [cand], reasoning, 5, "az")
    assert not results[0].reason  # blank, not the English fallback line
    # Forced EN + empty reason ⇒ English fallback is fine.
    results_en, _ = p._build_results("movies", "a jury in a room", [cand], reasoning, 5, "en")
    assert results_en[0].reason == "A close match in the catalog for your memory."
