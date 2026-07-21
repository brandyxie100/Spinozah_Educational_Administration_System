"""Tenant isolation for invoice repository (skipped without DATABASE_URL)."""

from __future__ import annotations

import os
import uuid
from decimal import Decimal

import pytest
from app.domain.finance import Invoice
from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.invoice_repository import (
    SqlAlchemyInvoiceRepository,
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
    """Invoices of tenant B must be invisible when querying as tenant A."""
    tenant_a = TenantFactory.build()
    tenant_b = TenantFactory.build()
    student_a = StudentModel(
        id=uuid.uuid4(),
        tenant_id=tenant_a.id,
        full_name="A",
        email=None,
        is_active=True,
    )
    student_b = StudentModel(
        id=uuid.uuid4(),
        tenant_id=tenant_b.id,
        full_name="B",
        email=None,
        is_active=True,
    )
    db_session.add_all([tenant_a, tenant_b, student_a, student_b])
    await db_session.commit()

    invoice_a = Invoice(
        tenant_id=tenant_a.id,
        student_id=student_a.id,
        semester_label="2026-S2",
        subtotal=Decimal("100.00"),
    )
    invoice_b = Invoice(
        tenant_id=tenant_b.id,
        student_id=student_b.id,
        semester_label="2026-S2",
        subtotal=Decimal("200.00"),
    )
    repo_a = SqlAlchemyInvoiceRepository(db_session, tenant_a.id)
    repo_b = SqlAlchemyInvoiceRepository(db_session, tenant_b.id)
    saved_a = await repo_a.add(invoice_a)
    saved_b = await repo_b.add(invoice_b)

    assert await repo_a.get_by_id(saved_a.id) is not None
    assert await repo_a.get_by_id(saved_b.id) is None
