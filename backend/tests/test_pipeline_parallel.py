"""The three per-search LLM calls (reason, free-form identify, clarify) must run
CONCURRENTLY, not back-to-back — that overlap is the main search-latency win. A fake
LLM that sleeps on every call lets us prove the fan-out by wall-clock time without a
network."""

import time

from app.ai.pipeline import SearchPipeline
from app.ai.types import Candidate


class SleepyLLM:
    """Sleeps on each JSON call so sequential vs concurrent execution is timeable. The
    payload is deliberately un-parseable — the pipeline swallows each parse error and
    returns None; this test only cares that all three calls happened and overlapped."""

    def __init__(self, delay: float = 0.25) -> None:
        self.delay = delay
        self.json_calls = 0

    def complete_json(self, system, user, temperature=0.2, model=None) -> str:
        self.json_calls += 1
        time.sleep(self.delay)
        return "{}"

    def complete_text(self, system, user, temperature=0.3) -> str:
        return ""


class FakeCategory:
    id = 1
    display_name = "Movies"
    key = "misc"  # outside every image-source set — no network


def _candidates():
    return [
        Candidate(item_id=1, title="Inception", description="a heist in dreams"),
        Candidate(item_id=2, title="Memento", description="a man with no short-term memory"),
    ]


def _pipeline(llm):
    return SearchPipeline(
        retriever=None,
        reranker=None,
        llm=llm,
        freeform_enabled=True,
        clarify_enabled=True,
    )


def test_reason_identify_clarify_run_concurrently():
    delay = 0.25
    llm = SleepyLLM(delay)
    p = _pipeline(llm)

    start = time.perf_counter()
    p._reason_identify_clarify(FakeCategory(), "a dream heist movie", _candidates())
    elapsed = time.perf_counter() - start

    assert llm.json_calls == 3  # reason + identify + clarify all fired
    # Sequential would be ~3*delay; concurrent should finish in well under 2*delay.
    assert elapsed < delay * 2, f"calls did not overlap: {elapsed:.3f}s for 3x{delay}s"


def test_disabled_features_are_not_submitted():
    llm = SleepyLLM(0.0)
    p = SearchPipeline(
        retriever=None,
        reranker=None,
        llm=llm,
        freeform_enabled=False,
        clarify_enabled=False,
    )
    reasoning, ident, question = p._reason_identify_clarify(
        FakeCategory(), "a dream heist movie", _candidates()
    )
    assert llm.json_calls == 1  # only reason ran
    assert ident is None and question is None
