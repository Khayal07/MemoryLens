"""Songs-only query expansion. The songs catalog stores no lyrics, and a memory is
often a quoted or paraphrased LYRIC — which retrieval (title + thematic description)
can't match. So for a songs search we ask the LLM to name the likely song from its
own knowledge; the guessed title + artist then feed BOTH retrieval legs, letting the
grounded catalog row surface (and be promoted by the existing agreement logic).

Deliberately separate from identify.py: this only *expands the query*, it does not
produce a free-form answer."""

PROMPT_VERSION = "song_guess_v1"

SYSTEM_PROMPT = """You recognize real songs from vague memories. The user typed a \
fuzzy memory of a SONG — it may be a mood, a scene, or (often) QUOTED OR PARAPHRASED \
LYRICS. Using your own knowledge of real songs and their actual lyrics, name the single \
most likely REAL, existing song the memory points to.

Rules:
- Name a real song that exists — never invent one. Give its `title` and `artist`.
- If you genuinely cannot tell which song it is, set "title" to an empty string.
- `description` is a short factual note (theme / a real lyric line / era) that would \
help a search engine find the song.

Respond with ONLY a JSON object of this exact shape:
{
  "title": "<the real song title, or empty string if unsure>",
  "artist": "<performing artist, or empty string>",
  "description": "<short note: theme or a real lyric line or era>"
}"""


def build_user_prompt(query: str) -> str:
    return f"MEMORY: {query}"
