"""Integration tests for the FastAPI health endpoint."""

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_get_returns_200_and_ok_status() -> None:
    """GET /health returns HTTP 200 with a healthy payload."""
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "service" in payload


def test_ready_get_returns_200() -> None:
    """GET /ready returns HTTP 200 for readiness probes."""
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
