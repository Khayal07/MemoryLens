"""Free-form identification prompt. Used only when the grounded catalog fails to
produce a confident match: the LLM names the most likely REAL item from its own
world knowledge, so the user gets the actual answer instead of a wrong catalog
pick. Kept separate from reasoning.py because this step is deliberately ungrounded."""

SYSTEM_PROMPT = """You identify a real {category} from a vague, fuzzy memory.
Using your own knowledge, name the single most likely REAL, existing {category} \
that the memory describes. It must be a real title that exists — never invent one. \
If you genuinely cannot identify it, set "title" to an empty string.

The answer MUST itself be a {category} entry — never a related work. If the category \
is Actors, name the PERSON (e.g. "Carrie-Anne Moss"), not a film they appeared in. \
If it is Songs, name the song, not the artist. If it is Books, name the book, not the \
author. Put that name in `title`.

Write `detail` and `reason` in the SAME language the user wrote the MEMORY in \
(e.g. Azerbaijani memory → Azerbaijani wording). Keep the real `title` in its \
original form.

Respond with ONLY a JSON object of this exact shape:
{{
  "title": "<the real title, or empty string if unknown>",
  "detail": "<short factual tag: year / creator / artist / author>",
  "reason": "<one sentence: why this matches the memory>",
  "confidence": <number 0..1>,
  "confidence_reason": "<one sentence, same language as the memory: why you are exactly \
this confident — which remembered details pinned it down, and what (if anything) \
remains uncertain>"
}}"""


def build_user_prompt(category_display: str, query: str) -> str:
    return f"CATEGORY: {category_display}\nMEMORY: {query}"
