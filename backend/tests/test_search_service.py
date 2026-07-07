"""Unit tests for search_service helpers — pure, no DB."""

from app.services.search_service import _top_result


def test_top_result_from_snapshot():
    snapshot = {
        "results": [
            {"title": "12 Angry Men", "image_url": "http://img", "confidence": 90.0},
            {"title": "Other", "image_url": None, "confidence": 60.0},
        ]
    }
    assert _top_result(snapshot) == ("12 Angry Men", "http://img", 90.0)


def test_top_result_handles_missing_snapshot():
    assert _top_result(None) == (None, None, None)
    assert _top_result({}) == (None, None, None)
    assert _top_result({"results": []}) == (None, None, None)
    assert _top_result({"results": ["junk"]}) == (None, None, None)
