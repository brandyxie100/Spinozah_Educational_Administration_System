"""Tenant isolation for parent-student links (skipped without DATABASE_URL)."""

from __future__ import annotations

import os
import uuid

import pytest
from app.domain.parent_portal import ParentStudentLink
from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.models import UserModel, UserRole
from app.infrastructure.persistence.parent_portal_repository import (
    SqlAlchemyParentStudentLinkRepository,
)
from app.infrastructure.persistence.student_models import StudentModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from tests.factories import TenantFactory


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
    """Parent links for tenant B must be invisible when querying as tenant A."""
    tenant_a = TenantFactory.build()
    tenant_b = TenantFactory.build()
    parent_a = UserModel(
        id=uuid.uuid4(),
        tenant_id=tenant_a.id,
        email="a@example.com",
        full_name="A",
        hashed_password="x",
        role=UserRole.PARENT,
        is_active=True,
    )
    parent_b = UserModel(
        id=uuid.uuid4(),
        tenant_id=tenant_b.id,
        email="b@example.com",
        full_name="B",
        hashed_password="x",
        role=UserRole.PARENT,
        is_active=True,
    )
    student_a = StudentModel(
        id=uuid.uuid4(),
        tenant_id=tenant_a.id,
        full_name="Student A",
        email=None,
        is_active=True,
    )
    student_b = StudentModel(
        id=uuid.uuid4(),
        tenant_id=tenant_b.id,
        full_name="Student B",
        email=None,
        is_active=True,
    )
    db_session.add_all(
        [tenant_a, tenant_b, parent_a, parent_b, student_a, student_b],
    )
    await db_session.commit()

    repo_a = SqlAlchemyParentStudentLinkRepository(db_session, tenant_a.id)
    repo_b = SqlAlchemyParentStudentLinkRepository(db_session, tenant_b.id)
    await repo_a.add(
        ParentStudentLink(
            tenant_id=tenant_a.id,
            parent_user_id=parent_a.id,
            student_id=student_a.id,
        ),
    )
    await repo_b.add(
        ParentStudentLink(
            tenant_id=tenant_b.id,
            parent_user_id=parent_b.id,
            student_id=student_b.id,
        ),
    )

    assert await repo_a.list_student_ids_for_parent(parent_a.id) == [student_a.id]
    assert await repo_a.list_student_ids_for_parent(parent_b.id) == []
