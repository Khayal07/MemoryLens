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
