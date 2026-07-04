"""Schema + parser for the free-form identification step. Same tolerant JSON
extraction as reasoning.py, kept here so it's unit-testable without any network call."""

import json
import re

from pydantic import BaseModel, Field, ValidationError


class Identification(BaseModel):
    title: str
    detail: str = ""
    reason: str = ""
    confidence: float = Field(ge=0.0, le=1.0)


class IdentifyParseError(ValueError):
    """Raised when the LLM output can't be parsed into an Identification."""


_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


def parse_identification(raw: str) -> Identification:
    """Parse raw LLM text into a validated Identification, extracting the JSON object
    even if wrapped in code fences or surrounding prose."""
    if not raw or not raw.strip():
        raise IdentifyParseError("Empty LLM response.")

    candidate = raw.strip()
    if candidate.startswith("```"):
        candidate = candidate.strip("`")
        candidate = re.sub(r"^json\s*", "", candidate, flags=re.I).strip()

    try:
        return Identification.model_validate_json(candidate)
    except (ValidationError, ValueError):
        pass

    match = _JSON_OBJECT.search(candidate)
    if not match:
        raise IdentifyParseError("No JSON object found in LLM response.")
    try:
        data = json.loads(match.group(0))
        return Identification.model_validate(data)
    except (ValidationError, json.JSONDecodeError) as exc:
        raise IdentifyParseError(str(exc)) from exc
