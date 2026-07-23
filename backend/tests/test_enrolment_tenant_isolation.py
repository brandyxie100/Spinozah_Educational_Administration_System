"""Tenant isolation for enrolments (skipped without DATABASE_URL)."""

from __future__ import annotations

import os

import pytest
from app.domain.students.entities import Enrolment
from app.infrastructure.persistence.attendance_repository import (
    SqlAlchemyEnrolmentRepository,
)
from app.infrastructure.persistence.base import Base
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from tests.factories import EnrolmentFactory, StudentFactory, TenantFactory


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
    """Enrolments for tenant B must be invisible when querying as tenant A."""
    tenant_a = TenantFactory.build()
    tenant_b = TenantFactory.build()
    student_a = StudentFactory.build(tenant_id=tenant_a.id)
    student_b = StudentFactory.build(tenant_id=tenant_b.id)
    db_session.add_all([tenant_a, tenant_b, student_a, student_b])
    await db_session.commit()

    repo_a = SqlAlchemyEnrolmentRepository(db_session, tenant_a.id)
    repo_b = SqlAlchemyEnrolmentRepository(db_session, tenant_b.id)

    enr_a = await repo_a.add(
        Enrolment(
            tenant_id=tenant_a.id,
            student_id=student_a.id,
            total_lessons=10,
        ),
    )
    enr_b = await repo_b.add(
        Enrolment(
            tenant_id=tenant_b.id,
            student_id=student_b.id,
            total_lessons=20,
        ),
    )

    listed_a = await repo_a.list_all()
    assert len(listed_a) == 1
    assert listed_a[0].id == enr_a.id
    assert await repo_a.list_by_student_id(student_b.id) == []
    assert await repo_a.get_by_id(enr_b.id) is None

    # factory_boy model builder remains available for ORM seeding helpers.
    assert EnrolmentFactory.build(
        tenant_id=tenant_a.id,
        student_id=student_a.id,
    ).total_lessons == 10
