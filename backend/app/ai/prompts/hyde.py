"""HyDE (Hypothetical Document Embeddings) prompt. The LLM writes a short, plausible
catalog-style description for the user's fuzzy memory; we embed that hypothetical text
so the semantic leg matches against descriptions instead of against raw question-shaped
queries. Purely a recall aid — the hypothesis is never shown and never invents a result."""

PROMPT_VERSION = "hyde_v1"

SYSTEM_PROMPT = """You expand a vague memory into the kind of catalog description it \
would match. Given a CATEGORY and a fuzzy MEMORY, write 1-2 plain sentences describing \
the most likely {category}-style item — its plot, theme, or subject. Do NOT name a real \
title, do NOT ask questions, do NOT add commentary. Output only the description."""


def build_user_prompt(category_display: str, query: str) -> str:
    return f"CATEGORY: {category_display}\nMEMORY: {query}"
