"""Daily-challenge DTOs. The state never carries the answer until the attempt is
finished (solved or out of guesses) — clue gating is enforced server-side."""

from pydantic import BaseModel, Field


class ChallengeAnswer(BaseModel):
    title: str
    image_url: str | None = None
    source_url: str | None = None


class ChallengeState(BaseModel):
    number: int
    date: str
    category: str
    # Only the clues the player has earned so far (finished → all of them).
    clues: list[str] = Field(default_factory=list)
    clues_total: int = 3
    guesses_used: int = 0
    guess_limit: int = 3
    solved: bool = False
    finished: bool = False
    # Set only on the response to a guess; None on plain state reads.
    correct: bool | None = None
    # Revealed only when finished.
    answer: ChallengeAnswer | None = None


class GuessRequest(BaseModel):
    guess: str = Field(min_length=1, max_length=200)
