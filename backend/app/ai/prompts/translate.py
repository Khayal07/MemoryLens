"""Retrieval-side translation prompt. The local embedder and reranker are English-only,
so a non-English memory is translated to English *for retrieval only*. The original text
is still what the reasoning stage sees, so explanations come back in the user's language.
Kept deliberately literal — this is a search key, not user-facing copy."""

SYSTEM_PROMPT = """Translate the user's text to English. It is a short, fuzzy memory of \
a movie, show, song, book, game, or person. Output ONLY the plain English translation — \
no quotes, no notes, no explanation. If the text is already English, return it unchanged. \
Keep any real proper names as they are."""
