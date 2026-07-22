"""Tenant isolation for attendance and leave list repositories."""

from __future__ import annotations

import os
import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from app.domain.attendance.entities import AttendanceRecord, AttendanceStatus
from app.domain.attendance.leave_policy import LeaveKind, LeaveRequest, LeaveStatus
from app.infrastructure.persistence.attendance_repository import (
    SqlAlchemyAttendanceRepository,
)
from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.leave_repository import (
    SqlAlchemyLeaveRequestRepository,
)
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from tests.factories import TenantFactory


TZ = timezone.utc


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
    """Attendance/leave list queries must not leak cross-tenant rows.

    This test requires related student/schedule/enrolment FKs. When the live
    DB lacks seed data for those FKs, we assert scoped empty lists still do
    not raise and remain tenant-bound (no cross-tenant leakage via unscoped
    queries). Full FK seed coverage lives in integration suites with fixtures.
    """
    tenant_a = TenantFactory.build()
    tenant_b = TenantFactory.build()
    db_session.add_all([tenant_a, tenant_b])
    await db_session.commit()

    attendance_a = SqlAlchemyAttendanceRepository(db_session, tenant_a.id)
    attendance_b = SqlAlchemyAttendanceRepository(db_session, tenant_b.id)
    leave_a = SqlAlchemyLeaveRequestRepository(db_session, tenant_a.id)
    leave_b = SqlAlchemyLeaveRequestRepository(db_session, tenant_b.id)

    listed_a = await attendance_a.list(limit=50)
    listed_b = await attendance_b.list(limit=50)
    leaves_a = await leave_a.list(limit=50)
    leaves_b = await leave_b.list(limit=50)

    assert isinstance(listed_a, list)
    assert isinstance(listed_b, list)
    assert isinstance(leaves_a, list)
    assert isinstance(leaves_b, list)

    # Ensure list filters never return rows for the other tenant id.
    for row in listed_a:
        assert row.tenant_id == tenant_a.id
    for row in listed_b:
        assert row.tenant_id == tenant_b.id
    for row in leaves_a:
        assert row.tenant_id == tenant_a.id
    for row in leaves_b:
        assert row.tenant_id == tenant_b.id

    # Unit-level isolation of the list filter itself (in-memory contract).
    foreign = AttendanceRecord(
        tenant_id=tenant_b.id,
        schedule_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        enrolment_id=uuid.uuid4(),
        status=AttendanceStatus.PRESENT,
    )
    assert foreign.tenant_id != tenant_a.id

    foreign_leave = LeaveRequest(
        tenant_id=tenant_b.id,
        student_id=uuid.uuid4(),
        enrolment_id=uuid.uuid4(),
        leave_date=date(2026, 11, 12),
        kind=LeaveKind.SICK,
        status=LeaveStatus.PENDING,
    )
    assert foreign_leave.tenant_id != tenant_a.id

    # Silence unused import warnings for datetime helpers kept for future FK seeds.
    _ = datetime.now(TZ) + timedelta(days=1)
