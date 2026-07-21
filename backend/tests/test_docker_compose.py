"""Validate docker-compose.yml structure for the local stack."""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = REPO_ROOT / "docker-compose.yml"


def test_compose_defines_postgres_15_db_service() -> None:
    """db service uses Postgres 15 and exposes 5432."""
    payload = yaml.safe_load(COMPOSE_FILE.read_text(encoding="utf-8"))
    db = payload["services"]["db"]

    assert db["image"] == "postgres:15"
    assert "5432:5432" in db["ports"]
    assert db["environment"]["POSTGRES_DB"] == "spinozah"


def test_compose_api_is_optional_profile() -> None:
    """API service is opt-in via compose profile so db-only start works."""
    payload = yaml.safe_load(COMPOSE_FILE.read_text(encoding="utf-8"))
    api = payload["services"]["api"]

    assert "api" in api["profiles"]
    assert api["depends_on"]["db"]["condition"] == "service_healthy"
