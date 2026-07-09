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


# A conservative policy for a self-hosted SPA + API. `img-src` allows the external
# poster/cover art (https) and inline data URIs; `style-src` allows the inline styles
# the Vite/Tailwind build injects. Tighten further once a nonce pipeline exists.
_CSP = (
    "default-src 'self'; "
    "img-src 'self' data: https:; "
    "style-src 'self' 'unsafe-inline'; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "base-uri 'self'"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach hardening headers to every response. HSTS is only emitted outside
    development (it requires HTTPS and would break plain-HTTP local dev)."""

    def __init__(self, app, production: bool = False) -> None:
        super().__init__(app)
        self.production = production

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = _CSP
        if self.production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains"
            )
        return response
