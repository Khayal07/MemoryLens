"""Prometheus metrics. Kept tiny: a request counter and a latency histogram,
labelled by method/route/status. Exposed at /metrics."""

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUESTS = Counter(
    "memorylens_requests_total",
    "Total HTTP requests",
    ["method", "route", "status"],
)
LATENCY = Histogram(
    "memorylens_request_duration_seconds",
    "HTTP request latency",
    ["method", "route"],
)


def observe(method: str, route: str, status: int, seconds: float) -> None:
    REQUESTS.labels(method=method, route=route, status=str(status)).inc()
    LATENCY.labels(method=method, route=route).observe(seconds)


def render() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
