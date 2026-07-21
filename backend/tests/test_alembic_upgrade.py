"""Integration: apply Alembic migrations against a live PostgreSQL database."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

BACKEND_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_alembic_upgrade_head_succeeds_on_clean_db() -> None:
    """`alembic upgrade head` creates tenants/users on a clean database."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set; skipping live migration test")

    env = {**os.environ, "DATABASE_URL": database_url}
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=BACKEND_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout

    engine = create_async_engine(database_url)
    async with engine.connect() as connection:
        tenants = await connection.execute(
            text("SELECT to_regclass('public.tenants')"),
        )
        users = await connection.execute(text("SELECT to_regclass('public.users')"))
        assert tenants.scalar() == "tenants"
        assert users.scalar() == "users"
    await engine.dispose()
