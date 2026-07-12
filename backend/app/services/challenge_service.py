"""Daily challenge: reverse MemoryLens. One secret catalog item per day; the player
guesses from up to three progressively revealing clues. The pick is deterministic
(hash of the ISO date, rotating category) so every player gets the same item; the
LLM writes the clues once when the day's row is created and they are stored.

Guess checking reuses the pipeline's loose title matching (app/ai/matching.py)."""

import hashlib
import json
import re
from datetime import date, datetime, timezone

import structlog
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai.llm import LLMError
from app.ai.matching import same_title
from app.ai.prompts import challenge as challenge_prompt
from app.core.errors import NotFoundError, ValidationError
from app.infra.models import Category, ChallengeAttempt, DailyChallenge, Item
from app.schemas.challenge import ChallengeAnswer, ChallengeState

log = structlog.get_logger()

GUESS_LIMIT = 3
_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)
# Title words shorter than this, or in this set, don't count as an answer leak.
_STOPWORDS = {"the", "and", "of", "a", "an", "in", "on", "for", "with", "to"}


def get_state(db: Session, user_id: int, llm=None) -> ChallengeState:
    ch = _get_or_create_today(db, llm)
    attempt = _get_attempt(db, user_id, ch.id)
    return _to_state(db, ch, attempt)


def submit_guess(db: Session, user_id: int, guess: str, llm=None) -> ChallengeState:
    guess = guess.strip()
    if not guess:
        raise ValidationError("Guess cannot be empty.")
    ch = _get_or_create_today(db, llm)
    attempt = _get_attempt(db, user_id, ch.id)
    if attempt is None:
        # Explicit zeros: column defaults only apply at INSERT, not at construction.
        attempt = ChallengeAttempt(
            user_id=user_id, challenge_id=ch.id, guesses_used=0, solved=False
        )
        db.add(attempt)
    if attempt.solved or attempt.guesses_used >= GUESS_LIMIT:
        raise ValidationError("Today's challenge is already finished.")

    attempt.guesses_used += 1
    correct = same_title(guess, ch.item.title)
    if correct:
        attempt.solved = True
    db.commit()
    return _to_state(db, ch, attempt, correct=correct)


# --- state assembly ---------------------------------------------------------


def _to_state(
    db: Session,
    ch: DailyChallenge,
    attempt: ChallengeAttempt | None,
    correct: bool | None = None,
) -> ChallengeState:
    guesses_used = attempt.guesses_used if attempt else 0
    solved = bool(attempt and attempt.solved)
    finished = solved or guesses_used >= GUESS_LIMIT
    clues = list(ch.clues or [])
    # One clue up front; each wrong guess earns the next. Finished shows everything.
    revealed = len(clues) if finished else min(guesses_used + 1, len(clues))
    category = db.get(Category, ch.item.category_id)
    return ChallengeState(
        number=ch.id,
        date=ch.challenge_date.isoformat(),
        category=category.display_name if category else "",
        clues=clues[:revealed],
        clues_total=len(clues),
        guesses_used=guesses_used,
        guess_limit=GUESS_LIMIT,
        solved=solved,
        finished=finished,
        correct=correct,
        answer=(
            ChallengeAnswer(
                title=ch.item.title,
                image_url=ch.item.image_url,
                source_url=ch.item.source_url,
            )
            if finished
            else None
        ),
    )


def _get_attempt(db: Session, user_id: int, challenge_id: int) -> ChallengeAttempt | None:
    return db.execute(
        select(ChallengeAttempt).where(
            ChallengeAttempt.user_id == user_id,
            ChallengeAttempt.challenge_id == challenge_id,
        )
    ).scalar_one_or_none()


# --- challenge creation -------------------------------------------------------


def _get_or_create_today(db: Session, llm=None) -> DailyChallenge:
    today = datetime.now(timezone.utc).date()
    ch = db.execute(
        select(DailyChallenge).where(DailyChallenge.challenge_date == today)
    ).scalar_one_or_none()
    if ch is not None:
        return ch
    item = _pick_item(db, today)
    ch = DailyChallenge(challenge_date=today, item_id=item.id, clues=_clues_for(item, llm))
    db.add(ch)
    db.commit()
    db.refresh(ch)
    return ch


def _pick_item(db: Session, day: date) -> Item:
    """Deterministic daily pick: the date hash chooses a category (rotating) and an
    index into that category's eligible items — with an image, and never a gpt:*
    free-form row (those are unverified AI answers)."""
    seed = int(hashlib.sha256(day.isoformat().encode()).hexdigest(), 16)
    categories = db.execute(select(Category).order_by(Category.key)).scalars().all()
    if not categories:
        raise NotFoundError("No categories available for a challenge.")
    for offset in range(len(categories)):
        cat = categories[(seed + offset) % len(categories)]
        eligible = (
            (Item.category_id == cat.id)
            & Item.image_url.is_not(None)
            & Item.external_id.notlike("gpt:%")
        )
        count = db.execute(select(func.count(Item.id)).where(eligible)).scalar_one()
        if not count:
            continue
        item = db.execute(
            select(Item).where(eligible).order_by(Item.id).offset(seed % count).limit(1)
        ).scalar_one()
        return item
    raise NotFoundError("No eligible catalog items for a challenge.")


# --- clue generation ----------------------------------------------------------


def _clues_for(item: Item, llm=None) -> list[str]:
    """Three stored clues: LLM-written when possible, with any clue that leaks the
    title dropped, topped up from a deterministic masked-description fallback."""
    category = item.category
    clues: list[str] = []
    if llm is None:
        from app.ai.llm import LLMClient

        llm = LLMClient()
    try:
        raw = llm.complete_json(
            challenge_prompt.SYSTEM_PROMPT.format(category=category.display_name),
            challenge_prompt.build_user_prompt(
                category.display_name, item.title, item.description
            ),
        )
        clues = [c for c in _parse_clues(raw) if c.strip() and not _leaks_title(c, item.title)]
    except (LLMError, ValueError) as exc:
        log.warning("challenge.clues_failed", error=str(exc))
    # Top up positionally so a dropped clue 3 is replaced by the MOST revealing
    # fallback, keeping the cryptic→giveaway progression.
    fallback = _fallback_clues(item)
    return (clues + fallback[len(clues):])[:3]


def _parse_clues(raw: str) -> list[str]:
    match = _JSON_OBJECT.search(raw or "")
    if not match:
        raise ValueError("No JSON object in clue response.")
    data = json.loads(match.group(0))
    clues = data.get("clues")
    if not isinstance(clues, list):
        raise ValueError("Clue response missing a 'clues' list.")
    return [str(c) for c in clues][:3]


def _title_tokens(title: str) -> set[str]:
    return {
        t
        for t in re.findall(r"[a-z0-9]+", title.lower())
        if len(t) >= 3 and t not in _STOPWORDS
    }


def _leaks_title(clue: str, title: str) -> bool:
    words = set(re.findall(r"[a-z0-9]+", clue.lower()))
    return bool(_title_tokens(title) & words)


def _mask_title(text: str, title: str) -> str:
    for token in _title_tokens(title):
        text = re.sub(rf"(?i)\b{re.escape(token)}\b", "▮▮▮", text)
    return text


def _fallback_clues(item: Item) -> list[str]:
    """Network-free clues from the item's own description with the title masked out,
    split into progressively longer reveals."""
    display = item.category.display_name if item.category else "catalog"
    masked = _mask_title(item.description or "", item.title).strip()
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", masked) if s.strip()]
    first = sentences[0] if sentences else "Its description is a mystery even to us."
    rest = " ".join(sentences[1:3]) or first
    return [
        f"Today's secret hides in the {display} shelf of the catalog.",
        first[:160],
        rest[:220],
    ]
