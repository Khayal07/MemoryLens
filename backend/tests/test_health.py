from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_readyz_reports_dependency_checks() -> None:
    # Without live Postgres/Redis (as in CI unit runs) readiness is "degraded" (503);
    # with them it's "ready" (200). Either way the contract holds: a status + checks.
    resp = client.get("/api/v1/readyz")
    assert resp.status_code in (200, 503)
    body = resp.json()
    assert body["status"] in ("ready", "degraded")
    assert set(body["checks"]) == {"db", "redis"}


def test_security_headers_present() -> None:
    resp = client.get("/api/v1/health")
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" in resp.headers
    # HSTS is dev-off (plain HTTP), so it should be absent under the default env.
    assert "Strict-Transport-Security" not in resp.headers


def test_docs_enabled_in_development() -> None:
    # Default env is development, so the schema/docs stay available.
    assert client.get("/openapi.json").status_code == 200


def test_metrics_open_without_token_in_dev() -> None:
    # metrics_token is blank in dev → endpoint is open.
    assert client.get("/api/v1/metrics").status_code == 200
