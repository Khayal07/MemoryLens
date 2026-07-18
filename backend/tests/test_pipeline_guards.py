from app.ai.pipeline import _artist_from, _is_language_slip, _slug


def test_artist_from_picks_name_over_year():
    assert _artist_from("OneRepublic, 2013") == "OneRepublic"
    assert _artist_from("2013, OneRepublic") == "OneRepublic"


def test_artist_from_handles_slashes_and_role_words():
    # Free-form book/song details are often slash-separated with a trailing role label.
    assert _artist_from("1925 / Franz Kafka / author") == "Franz Kafka"
    assert _artist_from("George Orwell / 1949") == "George Orwell"
    assert _artist_from("1977 / Queen / band / song") == "Queen"


def test_artist_from_none_when_empty_or_only_year():
    assert _artist_from(None) is None
    assert _artist_from("2013") is None
    assert _artist_from("1925 / author") is None


def test_cyrillic_reply_to_latin_query_is_slip():
    # nano slipped into Russian on an English memory — scrub it.
    assert _is_language_slip("Вы упомянули фильм о хакере", "a film about a hacker")


def test_cyrillic_reply_to_azerbaijani_query_is_slip():
    # Azerbaijani is Latin script, so a Cyrillic reply is still a slip.
    assert _is_language_slip("Это фильм", "hakker haqqında film")


def test_cyrillic_reply_to_cyrillic_query_is_allowed():
    # A genuine Russian memory should keep its Russian answer.
    assert not _is_language_slip("Это фильм о хакере", "фильм о хакере")


def test_portuguese_reply_to_english_query_is_slip():
    # nano slipped into Portuguese on a plain-English memory — scrub it.
    assert _is_language_slip("Breaking Bad é uma série sobre um professor", "a chemistry teacher")


def test_in_language_reply_to_azerbaijani_query_is_allowed():
    # An Azerbaijani (non-ASCII) memory keeps its Azerbaijani, accented answer.
    assert not _is_language_slip("Bu, kimyagər haqqında serialdır", "kimyaçı müəllim")


def test_latin_reply_is_never_slip():
    assert not _is_language_slip("A film about a hacker", "a film about a hacker")


def test_empty_text_is_never_slip():
    assert not _is_language_slip("", "фильм")
    assert not _is_language_slip(None, "фильм")


def test_slug_basic():
    assert _slug("Mr. Robot") == "mr-robot"
    assert _slug("Counting Stars") == "counting-stars"


def test_slug_collapses_and_trims():
    assert _slug("  V for Vendetta!! ") == "v-for-vendetta"


def test_slug_caps_length_and_never_empty():
    assert len(_slug("x" * 400)) <= 120
    assert _slug("!!!") == "untitled"


def _reasoning_with_mismatch(rating: float):
    from app.ai.reasoning import LLMMatch, LLMMismatch, LLMReasoning

    return LLMReasoning(
        matches=[LLMMatch(item_id=1, reason="fits", rating=rating)],
        category_mismatch=LLMMismatch(
            suspected_category="songs", message="Looks like a song."
        ),
    )


def test_mismatch_suppressed_when_top_match_is_strong():
    # nano flagged "songs" while rating The Matrix 0.95 — contradiction, drop banner.
    from app.ai.pipeline import SearchPipeline

    out = SearchPipeline._validate_mismatch(
        "movies", "red pill hacker", _reasoning_with_mismatch(0.95)
    )
    assert out is None


def test_mismatch_kept_when_matches_are_weak():
    from app.ai.pipeline import SearchPipeline

    out = SearchPipeline._validate_mismatch(
        "movies", "a lyric about rain", _reasoning_with_mismatch(0.4)
    )
    assert out is not None
    assert out.suspected_category == "songs"
