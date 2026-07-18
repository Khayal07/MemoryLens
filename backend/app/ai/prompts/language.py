"""Optional answer-language override shared by the reasoning / identify / clarify
prompts. When the user has explicitly picked a UI language, every explanatory field the
model writes must come back in THAT language regardless of what language the memory was
typed in. When no language is forced (``None``), the prompts keep their default behaviour
of matching the memory's own language."""

_LANG_NAMES = {"az": "Azerbaijani", "en": "English"}


def normalize_language(language: str | None) -> str | None:
    """Coerce an incoming value to a supported code or None (unknown ⇒ auto-detect)."""
    if not language:
        return None
    code = language.strip().lower()
    return code if code in _LANG_NAMES else None


def language_directive(language: str | None) -> str:
    """A directive appended to a user prompt to force the answer language, or "" for the
    default detect-from-memory behaviour."""
    name = _LANG_NAMES.get(normalize_language(language) or "")
    if not name:
        return ""
    return (
        f"\n\nLANGUAGE OVERRIDE: Write every explanation, reason, message, description "
        f"and question in {name}, regardless of the language the memory was written in. "
        f"Keep real titles in their original form. This affects only the wording, never "
        f"which item you pick."
    )
