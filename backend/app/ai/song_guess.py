"""Schema + tolerant parser for the songs-only guess expansion. Mirrors identify.py
so it's unit-testable without any network call. An empty title is a valid result
(the model saying "I don't know") — the caller then falls back to plain expansion."""

import json
import re

from pydantic import BaseModel, ValidationError


class SongGuess(BaseModel):
    title: str = ""
    artist: str = ""
    description: str = ""


class SongGuessParseError(ValueError):
    """Raised when the LLM output can't be parsed into a SongGuess."""


_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


def parse_song_guess(raw: str) -> SongGuess:
    """Parse raw LLM text into a SongGuess, extracting the JSON object even if wrapped
    in code fences or surrounding prose. An empty/whitespace response raises."""
    if not raw or not raw.strip():
        raise SongGuessParseError("Empty LLM response.")

    candidate = raw.strip()
    if candidate.startswith("```"):
        candidate = candidate.strip("`")
        candidate = re.sub(r"^json\s*", "", candidate, flags=re.I).strip()

    try:
        return SongGuess.model_validate_json(candidate)
    except (ValidationError, ValueError):
        pass

    match = _JSON_OBJECT.search(candidate)
    if not match:
        raise SongGuessParseError("No JSON object found in LLM response.")
    try:
        data = json.loads(match.group(0))
        return SongGuess.model_validate(data)
    except (ValidationError, json.JSONDecodeError) as exc:
        raise SongGuessParseError(str(exc)) from exc
