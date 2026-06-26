"""Reciprocal Rank Fusion — merges several ranked lists into one without needing
the underlying scores to be comparable. This is why we can blend pgvector cosine
distance (vector) and ts_rank (keyword) cleanly: only positions matter.

score(item) = Σ over lists 1 / (k + rank), rank 0-based. Larger k softens the
weight of top positions; 60 is the canonical default."""


def reciprocal_rank_fusion(
    ranked_lists: list[list[int]], k: int = 60
) -> list[tuple[int, float]]:
    """Fuse ranked id lists. Returns (item_id, score) pairs, highest score first."""
    scores: dict[int, float] = {}
    for ranked in ranked_lists:
        for rank, item_id in enumerate(ranked):
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
