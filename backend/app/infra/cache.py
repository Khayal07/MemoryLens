"""Search response cache (Redis). Identical fragments re-asked within the TTL skip
the whole pipeline (retrieval + rerank + LLM). Keyed by category + normalized
query. Fails open: any Redis problem just means a cache miss."""

import hashlib

import redis
import structlog

from app.ai.cleaning import clean_query
from app.infra.redis import get_redis, note_redis_failure, redis_unavailable
from app.schemas.search import SearchResponse

log = structlog.get_logger()
TTL_SECONDS = 600


def _key(category: str, query: str, language: str | None = None) -> str:
    norm = clean_query(query).lower()
    digest = hashlib.sha256(norm.encode("utf-8")).hexdigest()[:24]
    # The answer language is part of the identity: the same memory answered in AZ vs EN
    # is a different cached response. `auto` (None) keeps the old key so pre-existing
    # entries don't need invalidating.
    lang = language or "auto"
    return f"search:{category}:{lang}:{digest}"


def get_cached(category: str, query: str, language: str | None = None) -> SearchResponse | None:
    if redis_unavailable():
        return None
    try:
        raw = get_redis().get(_key(category, query, language))
    except redis.RedisError as exc:
        note_redis_failure()
        log.warning("cache.read_failed", error=str(exc))
        return None
    if not raw:
        return None
    return SearchResponse.model_validate_json(raw)


def set_cached(
    category: str, query: str, response: SearchResponse, language: str | None = None
) -> None:
    if redis_unavailable():
        return
    try:
        get_redis().set(
            _key(category, query, language), response.model_dump_json(), ex=TTL_SECONDS
        )
    except redis.RedisError as exc:
        note_redis_failure()
        log.warning("cache.write_failed", error=str(exc))
