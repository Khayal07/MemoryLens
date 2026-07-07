"""Unit tests for constellation edge trimming — fake DB rows, no Postgres."""

from app.services.constellation_service import _EDGES_PER_NODE, _similarity_edges


class _Rows:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class FakeDB:
    def __init__(self, rows):
        self.rows = rows

    def execute(self, *_args, **_kwargs):
        return _Rows(self.rows)


def test_no_edges_for_single_node():
    assert _similarity_edges(FakeDB([]), [1]) == []


def test_edges_built_from_rows():
    edges = _similarity_edges(FakeDB([(1, 2, 0.83), (2, 3, 0.61)]), [1, 2, 3])
    assert [(e.a, e.b, e.weight) for e in edges] == [(1, 2, 0.83), (2, 3, 0.61)]


def test_per_node_cap_keeps_strongest():
    # Node 1 appears in more pairs than the cap allows — strongest kept (rows arrive
    # sorted by similarity desc, as the SQL orders them).
    rows = [(1, n, 0.9 - n * 0.01) for n in range(2, 2 + _EDGES_PER_NODE + 3)]
    edges = _similarity_edges(FakeDB(rows), list(range(1, 12)))
    assert len(edges) == _EDGES_PER_NODE
    assert all(e.a == 1 for e in edges)
    assert edges[0].weight >= edges[-1].weight


def test_weight_clamped_0_1():
    edges = _similarity_edges(FakeDB([(1, 2, 1.0000004)]), [1, 2])
    assert edges[0].weight == 1.0
