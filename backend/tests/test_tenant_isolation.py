"""Tenant isolation: repository queries must never leak cross-tenant rows."""

from __future__ import annotations

import os

import pytest
from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.user_repository import SqlAlchemyUserRepository
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from tests.factories import TenantFactory, UserFactory


@pytest.fixture
async def db_session() -> AsyncSession:
    """Yield a Postgres session; skip when DATABASE_URL is unset."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set; skipping live tenant isolation test")

    engine = create_async_engine(database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()

    async with engine.begin() as connection:
        await connection.execute(text("TRUNCATE TABLE tenants CASCADE"))
    await engine.dispose()


@pytest.mark.tenant_isolation
@pytest.mark.integration
@pytest.mark.asyncio
async def test_tenant_a_cannot_see_tenant_b_data(db_session: AsyncSession) -> None:
    """Users of tenant B must be invisible when querying as tenant A."""
    tenant_a = TenantFactory.build()
    tenant_b = TenantFactory.build()
    user_a = UserFactory.build(tenant_id=tenant_a.id, email="a@example.com")
    user_b = UserFactory.build(tenant_id=tenant_b.id, email="b@example.com")

    db_session.add_all([tenant_a, tenant_b, user_a, user_b])
    await db_session.commit()

    repo_a = SqlAlchemyUserRepository(db_session, tenant_a.id)
    listed = await repo_a.list_users()
    listed_ids = {user.id for user in listed}

    assert user_a.id in listed_ids
    assert user_b.id not in listed_ids
    assert await repo_a.get_by_id(user_a.id) is not None
    assert await repo_a.get_by_id(user_b.id) is None
