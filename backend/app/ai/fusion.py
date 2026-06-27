"""Reciprocal Rank Fusion — merges several ranked lists into one without needing
the underlying scores to be comparable. This is why we can blend pgvector cosine
distance (vector) and ts_rank (keyword) cleanly: only positions matter.

score(item) = Σ over lists w_list / (k + rank), rank 0-based. Larger k softens the
weight of top positions; 60 is the canonical default. Per-list `weights` let one
leg (e.g. the semantic vector leg) count for more than another."""


def reciprocal_rank_fusion(
    ranked_lists: list[list[int]],
    k: int = 60,
    weights: list[float] | None = None,
) -> list[tuple[int, float]]:
    """Fuse ranked id lists. Returns (item_id, score) pairs, highest score first.
    `weights`, if given, must align with `ranked_lists` and scale each leg."""
    if weights is not None and len(weights) != len(ranked_lists):
        raise ValueError("weights must match ranked_lists in length")
    scores: dict[int, float] = {}
    for idx, ranked in enumerate(ranked_lists):
        weight = weights[idx] if weights is not None else 1.0
        for rank, item_id in enumerate(ranked):
            scores[item_id] = scores.get(item_id, 0.0) + weight / (k + rank + 1)
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
