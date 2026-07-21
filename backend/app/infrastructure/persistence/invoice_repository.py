"""Tenant-scoped SQLAlchemy repository for invoices."""

from __future__ import annotations

from decimal import Decimal
from typing import cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.finance.entities import Invoice
from app.infrastructure.persistence.invoice_mapper import (
    apply_invoice_to_model,
    invoice_to_model,
    model_to_invoice,
)
from app.infrastructure.persistence.invoice_models import InvoiceModel, PaymentStatusDB
from app.infrastructure.persistence.tenant_scoped import (
    SqlAlchemyTenantScopedRepository,
)


class SqlAlchemyInvoiceRepository(SqlAlchemyTenantScopedRepository):
    """Load and mutate invoices within the bound tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        """Create an invoice repository scoped to ``tenant_id``."""
        super().__init__(session, tenant_id)

    async def get_by_id(self, invoice_id: UUID) -> Invoice | None:
        """Return an invoice by id for this tenant."""
        statement = self._scoped(
            select(InvoiceModel).where(InvoiceModel.id == invoice_id),
            InvoiceModel,
        )
        result = await self._session.scalar(statement)
        model = cast(InvoiceModel | None, result)
        return model_to_invoice(model) if model is not None else None

    async def list_by_student_id(self, student_id: UUID) -> list[Invoice]:
        """Return invoices for a student in this tenant (newest first)."""
        statement = self._scoped(
            select(InvoiceModel)
            .where(InvoiceModel.student_id == student_id)
            .order_by(InvoiceModel.created_at.desc()),
            InvoiceModel,
        )
        result = await self._session.scalars(statement)
        return [model_to_invoice(model) for model in result.all()]

    async def list_all(self) -> list[Invoice]:
        """Return all invoices for the bound tenant (newest first)."""
        statement = self._scoped(
            select(InvoiceModel).order_by(InvoiceModel.created_at.desc()),
            InvoiceModel,
        )
        result = await self._session.scalars(statement)
        return [model_to_invoice(model) for model in result.all()]

    async def count_by_status(self, status: PaymentStatusDB) -> int:
        """Count invoices with the given payment status in this tenant."""
        statement = self._scoped(
            select(func.count())
            .select_from(InvoiceModel)
            .where(InvoiceModel.status == status),
            InvoiceModel,
        )
        return int(await self._session.scalar(statement) or 0)

    async def sum_final_amount_by_status(self, status: PaymentStatusDB) -> Decimal:
        """Sum ``final_amount`` for invoices in the given status."""
        statement = self._scoped(
            select(func.coalesce(func.sum(InvoiceModel.final_amount), 0))
            .select_from(InvoiceModel)
            .where(InvoiceModel.status == status),
            InvoiceModel,
        )
        result = await self._session.scalar(statement)
        return Decimal(str(result or 0))

    async def add(self, invoice: Invoice) -> Invoice:
        """Persist a new invoice."""
        if invoice.tenant_id != self._tenant_id:
            raise ValueError("Cannot add invoice for a different tenant")
        model = invoice_to_model(invoice)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return model_to_invoice(model)

    async def save(self, invoice: Invoice) -> Invoice:
        """Persist updates to an existing invoice."""
        if invoice.tenant_id != self._tenant_id:
            raise ValueError("Cannot save invoice for a different tenant")
        statement = self._scoped(
            select(InvoiceModel).where(InvoiceModel.id == invoice.id),
            InvoiceModel,
        )
        model = cast(InvoiceModel | None, await self._session.scalar(statement))
        if model is None:
            raise ValueError(f"Invoice not found: {invoice.id}")
        apply_invoice_to_model(model, invoice)
        await self._session.commit()
        await self._session.refresh(model)
        return model_to_invoice(model)
