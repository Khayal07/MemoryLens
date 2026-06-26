"""Unit tests for Reciprocal Rank Fusion — pure, no DB or models."""

from app.ai.fusion import reciprocal_rank_fusion


def test_item_in_both_lists_outranks_item_in_one() -> None:
    vector = [1, 2, 3]
    keyword = [2, 4, 5]
    fused = dict(reciprocal_rank_fusion([vector, keyword]))
    # 2 appears in both lists → must beat 1 (top of only one list).
    assert fused[2] > fused[1]


def test_preserves_order_within_single_list() -> None:
    fused = reciprocal_rank_fusion([[10, 20, 30]])
    ids = [item_id for item_id, _ in fused]
    assert ids == [10, 20, 30]


def test_empty_input_returns_empty() -> None:
    assert reciprocal_rank_fusion([]) == []
    assert reciprocal_rank_fusion([[], []]) == []


def test_higher_rank_means_higher_score() -> None:
    fused = dict(reciprocal_rank_fusion([[1, 2]], k=60))
    assert fused[1] > fused[2]


def test_k_softens_top_positions() -> None:
    top_small_k = dict(reciprocal_rank_fusion([[1, 2]], k=1))
    top_large_k = dict(reciprocal_rank_fusion([[1, 2]], k=1000))
    gap_small = top_small_k[1] - top_small_k[2]
    gap_large = top_large_k[1] - top_large_k[2]
    assert gap_small > gap_large


def test_result_sorted_descending() -> None:
    fused = reciprocal_rank_fusion([[1, 2, 3], [3, 2, 1]])
    scores = [s for _, s in fused]
    assert scores == sorted(scores, reverse=True)
