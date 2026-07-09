"""Liveness + readiness probes. /readyz verifies the API can reach Postgres and
Redis; it returns 503 if a dependency is down so orchestrators hold traffic."""

import redis
from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse, Response
from sqlalchemy import text

from app.core import metrics
from app.core.config import get_settings
from app.core.errors import UnauthorizedError
from app.infra.db import engine
from app.infra.redis import get_redis

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz")
def readyz() -> JSONResponse:
    checks = {"db": _check_db(), "redis": _check_redis()}
    ok = all(v == "ok" for v in checks.values())
    return JSONResponse(
        status_code=200 if ok else 503,
        content={"status": "ready" if ok else "degraded", "checks": checks},
    )


@router.get("/metrics")
def prometheus_metrics(x_metrics_token: str | None = Header(default=None)) -> Response:
    # When a metrics token is configured (production), require it; a blank token
    # (development) leaves the endpoint open for local scraping.
    expected = get_settings().metrics_token
    if expected and x_metrics_token != expected:
        raise UnauthorizedError("Invalid or missing metrics token.")
    payload, content_type = metrics.render()
    return Response(content=payload, media_type=content_type)


def _check_db() -> str:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "down"


def _check_redis() -> str:
    try:
        get_redis().ping()
        return "ok"
    except (redis.RedisError, OSError):
        return "down"
