"""Guardrails that keep the domain layer free of infrastructure imports."""

from __future__ import annotations

from pathlib import Path

FORBIDDEN_IMPORT_TOKENS = (
    "sqlalchemy",
    "fastapi",
    "starlette",
    "httpx",
    "psycopg",
    "alembic",
)

DOMAIN_ROOT = Path(__file__).resolve().parents[1] / "app" / "domain"


def test_domain_layer_has_no_forbidden_infrastructure_imports() -> None:
    """Domain Python modules must not import FastAPI, SQLAlchemy, or HTTP clients."""
    assert DOMAIN_ROOT.is_dir(), f"Expected domain package at {DOMAIN_ROOT}"

    violations: list[str] = []
    for path in DOMAIN_ROOT.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            lowered = stripped.lower()
            if not (lowered.startswith("import ") or lowered.startswith("from ")):
                continue
            for token in FORBIDDEN_IMPORT_TOKENS:
                if token in lowered:
                    rel = path.relative_to(DOMAIN_ROOT.parent.parent)
                    violations.append(f"{rel}:{line_number}: {stripped}")

    message = "Forbidden imports in domain layer:\n" + "\n".join(violations)
    assert not violations, message



def test_domain_package_exposes_shared_marker() -> None:
    """Domain shared package is importable without infrastructure deps."""
    from app.domain.shared import DOMAIN_LAYER_MARKER

    assert DOMAIN_LAYER_MARKER == "domain"
