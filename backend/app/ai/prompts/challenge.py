"""Daily-challenge clue prompt. Runs ONCE per day when the challenge row is created;
the three clues are stored and every player reads the stored copy (no per-user LLM
cost). Clues are progressively revealing and must never contain the answer itself."""

SYSTEM_PROMPT = """You write clues for a daily guessing game about a secret {category}.
Write exactly THREE clues in English about the given {category}, progressively more
revealing: clue 1 is cryptic and atmospheric, clue 2 adds a concrete plot/content
detail, clue 3 is almost a giveaway (era, a famous person involved, a signature scene
or line paraphrased).

HARD RULES: never use any word from the title itself, never name the title, and never
quote text that contains it. Each clue is one sentence, under 25 words.

Respond with ONLY a JSON object of this exact shape:
{{"clues": ["<clue 1>", "<clue 2>", "<clue 3>"]}}"""


def build_user_prompt(category_display: str, title: str, description: str | None) -> str:
    about = description or "(no description available)"
    return f"CATEGORY: {category_display}\nSECRET TITLE: {title}\nABOUT IT: {about}"
