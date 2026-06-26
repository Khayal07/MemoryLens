"""Request middleware: assign a request id, time the request, emit one structured
log line, and feed metrics. The route *template* (not the raw path) is used as a
metric label to avoid unbounded cardinality."""

import time
from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core import metrics

log = structlog.get_logger()


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = uuid4().hex[:12]
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start

        route = _route_template(request)
        metrics.observe(request.method, route, response.status_code, elapsed)
        log.info(
            "request",
            method=request.method,
            route=route,
            status=response.status_code,
            duration_ms=round(elapsed * 1000, 1),
        )
        response.headers["X-Request-ID"] = request_id
        return response


def _route_template(request: Request) -> str:
    route = request.scope.get("route")
    return getattr(route, "path", request.url.path)
