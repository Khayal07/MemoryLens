"""Query cleaning + validation. Runs before anything touches retrieval or the LLM:
normalizes whitespace, enforces length, and scrubs obvious prompt-injection so a
memory fragment can't hijack the reasoning step."""

import re

MIN_LEN = 3
MAX_LEN = 1000

_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+|the\s+)?(previous|above|prior)\s+instructions", re.I),
    re.compile(r"disregard\s+(all\s+|the\s+)?(previous|above)\b", re.I),
    re.compile(r"system\s+prompt", re.I),
    re.compile(r"you\s+are\s+now\b", re.I),
]


class QueryError(ValueError):
    """Raised when a query fails validation."""


def validate_query(raw: str) -> None:
    text = (raw or "").strip()
    if len(text) < MIN_LEN:
        raise QueryError(f"Query must be at least {MIN_LEN} characters.")
    if len(text) > MAX_LEN:
        raise QueryError(f"Query must be at most {MAX_LEN} characters.")


def clean_query(raw: str) -> str:
    text = (raw or "").strip()
    text = re.sub(r"\s+", " ", text)
    for pattern in _INJECTION_PATTERNS:
        text = pattern.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_LEN]
