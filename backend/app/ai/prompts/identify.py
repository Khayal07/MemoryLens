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

IMPORTANT for Songs: the memory is very often a QUOTED or PARAPHRASED LYRIC. Match it \
to the song whose ACTUAL lyrics contain those exact lines — use ALL the words, not just \
the opening phrase. A different song may merely SHARE some words in its title; do not be \
fooled by that. Rely on your own knowledge of the real lyrics.

Write `detail`, `description`, `reason` and `confidence_reason` in the SAME language \
the user wrote the MEMORY in (e.g. Azerbaijani memory → Azerbaijani wording). Keep \
the real `title` in its original form.

QUALITY RULES for `reason` and `confidence_reason`:
- NEVER just restate the user's memory back at them.
- Map each remembered fragment to the concrete fact in the {category} it corresponds \
to (the actual scene, character, lyric, year, mechanic), naming specifics the user \
did NOT mention.
- Say what pins it down as exactly this one — and, if a similar {category} could be \
confused with it, name that alternative and why it loses.

Respond with ONLY a JSON object of this exact shape:
{{
  "title": "<the real title, or empty string if unknown>",
  "detail": "<short factual tag: year / creator / artist / author>",
  "description": "<2-3 sentences describing the {category} itself, like a rich \
catalog entry: what it is, what happens in it, who made it and when — NOT about \
the user's memory>",
  "reason": "<1-2 sentences following the QUALITY RULES: tie the remembered \
fragments to the item's concrete facts and what uniquely pins it down>",
  "confidence": <number 0..1>,
  "confidence_reason": "<one sentence following the QUALITY RULES: which remembered \
details pinned it down, what remains uncertain, and the closest alternative you \
rejected, if any>"
}}"""


def build_user_prompt(category_display: str, query: str, language: str | None = None) -> str:
    from app.ai.prompts.language import language_directive

    return f"CATEGORY: {category_display}\nMEMORY: {query}{language_directive(language)}"
