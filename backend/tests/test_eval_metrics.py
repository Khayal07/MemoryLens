"""Unit tests for the eval harness's pure metric functions (scripts/run_eval.py)."""

from scripts.run_eval import find_rank, mean_reciprocal_rank, recall_at_k


class TestFindRank:
    def test_exact_title_first(self):
        assert find_rank(["Titanic"], ["Titanic", "The Matrix"]) == 1

    def test_match_deeper_in_list(self):
        assert find_rank(["Inception"], ["Titanic", "Dark", "Inception"]) == 3

    def test_miss_returns_none(self):
        assert find_rank(["Zombie"], ["Creep", "Imagine"]) is None

    def test_loose_franchise_match(self):
        # same_title containment: a remaster/sequel row still counts as a hit.
        assert find_rank(["The Last Of Us"], ["The Last Of Us Remastered"]) == 1

    def test_any_expected_alias_counts(self):
        assert (
            find_rank(
                ["Harry Potter and the Philosopher's Stone", "Harry Potter (series) 1-7"],
                ["Harry Potter (series) 1-7"],
            )
            == 1
        )

    def test_empty_results(self):
        assert find_rank(["Dune"], []) is None


class TestRecallAtK:
    def test_all_hits_at_one(self):
        assert recall_at_k([1, 1, 1], 1) == 1.0

    def test_rank_beyond_k_is_a_miss(self):
        assert recall_at_k([1, 4, None], 3) == 1 / 3

    def test_wider_k_recovers_it(self):
        assert recall_at_k([1, 4, None], 5) == 2 / 3

    def test_empty_is_zero(self):
        assert recall_at_k([], 5) == 0.0


class TestMRR:
    def test_perfect(self):
        assert mean_reciprocal_rank([1, 1]) == 1.0

    def test_mixed_ranks(self):
        # 1/1, 1/2, miss=0 → (1 + 0.5 + 0) / 3
        assert mean_reciprocal_rank([1, 2, None]) == (1 + 0.5) / 3

    def test_empty_is_zero(self):
        assert mean_reciprocal_rank([]) == 0.0
