"""Search response cache (Redis). Identical fragments re-asked within the TTL skip
the whole pipeline (retrieval + rerank + LLM). Keyed by category + normalized
query. Fails open: any Redis problem just means a cache miss."""

import hashlib

import redis
import structlog

from app.ai.cleaning import clean_query
from app.infra.redis import get_redis
from app.schemas.search import SearchResponse

log = structlog.get_logger()
TTL_SECONDS = 600


def _key(category: str, query: str) -> str:
    norm = clean_query(query).lower()
    digest = hashlib.sha256(norm.encode("utf-8")).hexdigest()[:24]
    return f"search:{category}:{digest}"


def get_cached(category: str, query: str) -> SearchResponse | None:
    try:
        raw = get_redis().get(_key(category, query))
    except redis.RedisError as exc:
        log.warning("cache.read_failed", error=str(exc))
        return None
    if not raw:
        return None
    return SearchResponse.model_validate_json(raw)


def set_cached(category: str, query: str, response: SearchResponse) -> None:
    try:
        get_redis().set(_key(category, query), response.model_dump_json(), ex=TTL_SECONDS)
    except redis.RedisError as exc:
        log.warning("cache.write_failed", error=str(exc))
