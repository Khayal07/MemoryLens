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


def compute_confidence(
    llm_rating: float,
    rerank_score: float | None,
    retrieval_score: float,
    max_retrieval: float,
) -> float:
    """Blend signals into a 0–100 confidence. `max_retrieval` is the best fusion
    score among the candidates, used to normalize retrieval into 0–1."""
    rating = _clamp01(llm_rating)
    rerank = _sigmoid(rerank_score) if rerank_score is not None else 0.5
    retrieval = _clamp01(retrieval_score / max_retrieval) if max_retrieval > 0 else 0.0

    blended = W_LLM * rating + W_RERANK * rerank + W_RETRIEVAL * retrieval
    return round(_clamp01(blended) * 100.0, 1)
