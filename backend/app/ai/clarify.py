"""Schema + parser for the clarifying-question step (Akinator mode). Same tolerant
JSON extraction as identify.py, kept here so it's unit-testable without any network."""

import json
import re

from pydantic import BaseModel, ValidationError


class Clarification(BaseModel):
    question: str = ""


class ClarifyParseError(ValueError):
    """Raised when the LLM output can't be parsed into a Clarification."""


_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


def parse_clarification(raw: str) -> Clarification:
    """Parse raw LLM text into a validated Clarification, extracting the JSON object
    even if wrapped in code fences or surrounding prose."""
    if not raw or not raw.strip():
        raise ClarifyParseError("Empty LLM response.")

    candidate = raw.strip()
    if candidate.startswith("```"):
        candidate = candidate.strip("`")
        candidate = re.sub(r"^json\s*", "", candidate, flags=re.I).strip()

    try:
        return Clarification.model_validate_json(candidate)
    except (ValidationError, ValueError):
        pass

    match = _JSON_OBJECT.search(candidate)
    if not match:
        raise ClarifyParseError("No JSON object found in LLM response.")
    try:
        data = json.loads(match.group(0))
        return Clarification.model_validate(data)
    except (ValidationError, json.JSONDecodeError) as exc:
        raise ClarifyParseError(str(exc)) from exc
