from app.ai.pipeline import _is_foreign_script


def test_cyrillic_reply_to_latin_query_is_foreign():
    # nano slipped into Russian on an English memory — scrub it.
    assert _is_foreign_script("Вы упомянули фильм о хакере", "a film about a hacker")


def test_cyrillic_reply_to_azerbaijani_query_is_foreign():
    # Azerbaijani is Latin script, so a Cyrillic reply is still a slip.
    assert _is_foreign_script("Это фильм", "hakker haqqında film")


def test_cyrillic_reply_to_cyrillic_query_is_allowed():
    # A genuine Russian memory should keep its Russian answer.
    assert not _is_foreign_script("Это фильм о хакере", "фильм о хакере")


def test_latin_reply_is_never_foreign():
    assert not _is_foreign_script("A film about a hacker", "a film about a hacker")


def test_empty_text_is_never_foreign():
    assert not _is_foreign_script("", "фильм")
    assert not _is_foreign_script(None, "фильм")
