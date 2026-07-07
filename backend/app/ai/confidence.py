"""Confidence is *computed*, not taken from the model's word. We blend three
signals so a single over-confident source can't dominate:

- the LLM's own rating of the match   (semantic judgement)
- the cross-encoder rerank score       (sharp relevance, squashed via sigmoid)
- the hybrid retrieval/fusion score    (did both legs surface it)

The result is a calibrated 0–100 estimate shown to the user as a percentage."""

import math

W_LLM = 0.50
W_RERANK = 0.35
W_RETRIEVAL = 0.15


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _signals(
    llm_rating: float,
    rerank_score: float | None,
    retrieval_score: float,
    max_retrieval: float,
) -> tuple[float, float, float]:
    """Normalize the three raw signals into 0–1 each."""
    rating = _clamp01(llm_rating)
    rerank = _sigmoid(rerank_score) if rerank_score is not None else 0.5
    retrieval = _clamp01(retrieval_score / max_retrieval) if max_retrieval > 0 else 0.0
    return rating, rerank, retrieval


def compute_confidence(
    llm_rating: float,
    rerank_score: float | None,
    retrieval_score: float,
    max_retrieval: float,
) -> float:
    """Blend signals into a 0–100 confidence. `max_retrieval` is the best fusion
    score among the candidates, used to normalize retrieval into 0–1."""
    rating, rerank, retrieval = _signals(llm_rating, rerank_score, retrieval_score, max_retrieval)
    blended = W_LLM * rating + W_RERANK * rerank + W_RETRIEVAL * retrieval
    return round(_clamp01(blended) * 100.0, 1)


def compute_breakdown(
    llm_rating: float,
    rerank_score: float | None,
    retrieval_score: float,
    max_retrieval: float,
) -> dict[str, float]:
    """Per-signal contribution to the blended confidence, in percentage points —
    the same weighted terms compute_confidence sums, kept separate so the UI can
    show WHY the number is what it is. (Any later feedback nudge is added to the
    dict under its own key, not folded into these.)"""
    rating, rerank, retrieval = _signals(llm_rating, rerank_score, retrieval_score, max_retrieval)
    return {
        "llm": round(W_LLM * rating * 100.0, 1),
        "rerank": round(W_RERANK * rerank * 100.0, 1),
        "retrieval": round(W_RETRIEVAL * retrieval * 100.0, 1),
    }
