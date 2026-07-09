"""Unit tests for feedback_service.record_vote ownership handling, with a fake
Session (no DB). Focus: a vote may only be linked to the voter's own search."""

import pytest

from app.core.errors import NotFoundError, ValidationError
from app.infra.models import Item, ResultFeedback, Search
from app.services import feedback_service


class _Result:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class _FakeSession:
    def __init__(self, items, searches, existing_vote=None):
        self._items = items
        self._searches = searches
        self._existing_vote = existing_vote
        self.added = []
        self.committed = False

    def get(self, model, pk):
        if model is Item:
            return self._items.get(pk)
        if model is Search:
            return self._searches.get(pk)
        return None

    def execute(self, _stmt):
        return _Result(self._existing_vote)

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed = True


def _session(existing_vote=None, search_owner=None):
    searches = {99: Search(id=99, user_id=search_owner)} if search_owner is not None else {}
    return _FakeSession(items={5: Item(id=5)}, searches=searches, existing_vote=existing_vote)


def test_vote_links_to_own_search():
    db = _session(search_owner=1)
    feedback_service.record_vote(db, user_id=1, search_id=99, item_id=5, vote=1)
    assert db.added[0].search_id == 99  # own search kept


def test_vote_detaches_foreign_search():
    # search 99 belongs to user 2; user 1 must not attach their vote to it.
    db = _session(search_owner=2)
    feedback_service.record_vote(db, user_id=1, search_id=99, item_id=5, vote=1)
    assert db.added[0].search_id is None  # foreign search dropped
    assert db.added[0].vote == 1  # vote itself still recorded


def test_vote_detaches_unknown_search():
    db = _session(search_owner=None)  # no search rows at all
    feedback_service.record_vote(db, user_id=1, search_id=99, item_id=5, vote=1)
    assert db.added[0].search_id is None


def test_existing_vote_is_updated_not_duplicated():
    prior = ResultFeedback(user_id=1, item_id=5, search_id=None, vote=1)
    db = _session(existing_vote=prior, search_owner=1)
    feedback_service.record_vote(db, user_id=1, search_id=99, item_id=5, vote=-1)
    assert db.added == []  # no new row
    assert prior.vote == -1 and prior.search_id == 99


def test_invalid_vote_rejected():
    with pytest.raises(ValidationError):
        feedback_service.record_vote(_session(), user_id=1, search_id=None, item_id=5, vote=0)


def test_missing_item_rejected():
    db = _FakeSession(items={}, searches={})
    with pytest.raises(NotFoundError):
        feedback_service.record_vote(db, user_id=1, search_id=None, item_id=404, vote=1)
