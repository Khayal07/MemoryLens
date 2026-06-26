"""Unit tests for confidence blending — pure, no models."""

from app.ai.confidence import compute_confidence


def test_confidence_bounded_0_100() -> None:
    c = compute_confidence(1.0, 100.0, 10.0, 10.0)
    assert 0.0 <= c <= 100.0
    assert c == 100.0


def test_zero_signals_floor() -> None:
    c = compute_confidence(0.0, -100.0, 0.0, 10.0)
    assert c >= 0.0
    assert c < 20.0  # only the sigmoid(rerank)->~0 contributes nothing meaningful


def test_higher_llm_rating_raises_confidence() -> None:
    low = compute_confidence(0.2, 0.0, 5.0, 10.0)
    high = compute_confidence(0.9, 0.0, 5.0, 10.0)
    assert high > low


def test_higher_rerank_raises_confidence() -> None:
    low = compute_confidence(0.5, -2.0, 5.0, 10.0)
    high = compute_confidence(0.5, 5.0, 5.0, 10.0)
    assert high > low


def test_missing_rerank_uses_neutral() -> None:
    c = compute_confidence(0.5, None, 5.0, 10.0)
    assert 0.0 <= c <= 100.0


def test_zero_max_retrieval_is_safe() -> None:
    c = compute_confidence(0.5, 0.0, 5.0, 0.0)
    assert 0.0 <= c <= 100.0
