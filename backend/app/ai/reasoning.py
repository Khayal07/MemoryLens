"""Schema + parser for the LLM's structured output. The model returns strict JSON;
we validate it with Pydantic and tolerate common wrapping (code fences, prose
around the object) before failing. Keeping parsing here makes it unit-testable
without any network call."""

import json
import re

from pydantic import BaseModel, Field, ValidationError


class LLMMatch(BaseModel):
    item_id: int
    reason: str
    rating: float = Field(ge=0.0, le=1.0)


class LLMMismatch(BaseModel):
    suspected_category: str
    message: str


class LLMReasoning(BaseModel):
    matches: list[LLMMatch] = Field(default_factory=list)
    category_mismatch: LLMMismatch | None = None


class ReasoningParseError(ValueError):
    """Raised when the LLM output can't be parsed into LLMReasoning."""


_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


def parse_reasoning(raw: str) -> LLMReasoning:
    """Parse raw LLM text into a validated LLMReasoning, extracting the JSON object
    even if wrapped in code fences or surrounding prose."""
    if not raw or not raw.strip():
        raise ReasoningParseError("Empty LLM response.")

    candidate = raw.strip()
    if candidate.startswith("```"):
        candidate = candidate.strip("`")
        candidate = re.sub(r"^json\s*", "", candidate, flags=re.I).strip()

    try:
        return LLMReasoning.model_validate_json(candidate)
    except (ValidationError, ValueError):
        pass

    match = _JSON_OBJECT.search(candidate)
    if not match:
        raise ReasoningParseError("No JSON object found in LLM response.")
    try:
        data = json.loads(match.group(0))
        return LLMReasoning.model_validate(data)
    except (ValidationError, json.JSONDecodeError) as exc:
        raise ReasoningParseError(str(exc)) from exc
