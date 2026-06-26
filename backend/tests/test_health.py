from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_readyz() -> None:
    resp = client.get("/api/v1/readyz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"
