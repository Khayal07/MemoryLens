"""Clarifying-question prompt (Akinator mode). Used only when the grounded search
comes back weak: the LLM asks ONE short question whose answer would best split the
likely candidates. Stateless — the frontend folds the answer back into a new query."""

SYSTEM_PROMPT = """You help narrow down a vague memory of a {category}.
The catalog search was inconclusive. Ask exactly ONE short clarifying question whose \
answer would best help identify the {category} — pick the detail that most cleanly \
separates the likely candidates (era, country or language, genre, a plot element, \
a person involved, where the user encountered it…).

Rules: one question only, under 15 words, no lists of options, and never mention or \
suggest any specific title. Write the question in the SAME language the MEMORY is \
written in (e.g. Azerbaijani memory → Azerbaijani question).

Respond with ONLY a JSON object of this exact shape:
{{"question": "<the one clarifying question, or empty string if nothing useful to ask>"}}"""


def build_user_prompt(
    category_display: str, query: str, candidate_titles: list[str], language: str | None = None
) -> str:
    from app.ai.prompts.language import language_directive

    titles = "; ".join(candidate_titles) if candidate_titles else "none"
    return (
        f"CATEGORY: {category_display}\nMEMORY: {query}\nWEAK CANDIDATES: {titles}"
        f"{language_directive(language)}"
    )
