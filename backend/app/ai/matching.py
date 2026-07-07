"""Loose title matching shared by the search pipeline (grey-zone freeform vs grounded
comparison) and the daily challenge (guess checking)."""

import re


def slug(title: str) -> str:
    """Lowercase, keep [a-z0-9], collapse everything else to single hyphens, and cap
    length so `gpt:<slug>` stays inside the external_id String(128) column."""
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:120] or "untitled"


def same_title(a: str, b: str) -> bool:
    """Loose title equality: slug-normalize and treat one being contained in the other
    as a match (so "Hello" ≈ "Hello from the Other Side", but "We Will Rock You" ≠
    "Don't Stop Believin'")."""
    sa, sb = slug(a), slug(b)
    return sa == sb or sa in sb or sb in sa
