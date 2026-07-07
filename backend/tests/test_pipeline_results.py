"""Unit tests for _build_results reason handling and the _same_title helper —
no network, plain in-memory pipeline with null retriever/reranker/llm."""

from app.ai.pipeline import _FALLBACK_REASON, SearchPipeline, _same_title
from app.ai.reasoning import LLMMatch, LLMReasoning
from app.ai.types import Candidate


def _pipeline() -> SearchPipeline:
    return SearchPipeline(retriever=None, reranker=None, llm=None)


def _cand(item_id=1, title="Robert Downey Jr.") -> Candidate:
    return Candidate(item_id=item_id, title=title, description="Known for: Iron Man.",
                     retrieval_score=1.0, rerank_score=2.0)


# --- empty-reason fallback (Fix 4) ---------------------------------------


def test_empty_reason_on_english_match_gets_template():
    p = _pipeline()
    reasoning = LLMReasoning(matches=[LLMMatch(item_id=1, reason="", rating=0.95)])
    results, _ = p._build_results("actors", "who plays iron man", [_cand()], reasoning, 5)
    assert results[0].reason == _FALLBACK_REASON


def test_present_reason_is_kept():
    p = _pipeline()
    reasoning = LLMReasoning(matches=[LLMMatch(item_id=1, reason="He is Iron Man.", rating=0.9)])
    results, _ = p._build_results("actors", "who plays iron man", [_cand()], reasoning, 5)
    assert results[0].reason == "He is Iron Man."


def test_empty_reason_on_non_ascii_query_stays_blank():
    # An Azerbaijani memory keeps a blank reason rather than an English template.
    p = _pipeline()
    reasoning = LLMReasoning(matches=[LLMMatch(item_id=1, reason="", rating=0.95)])
    results, _ = p._build_results("actors", "dəmir adamı kim oynayır", [_cand()], reasoning, 5)
    assert not results[0].reason  # blank, not an English template


# --- _same_title (Fix 2) --------------------------------------------------


def test_same_title_exact_and_substring():
    assert _same_title("Hello", "Hello from the Other Side")
    assert _same_title("Mr. Robot", "mr robot")


def test_same_title_rejects_different():
    assert not _same_title("We Will Rock You", "Don't Stop Believin'")
