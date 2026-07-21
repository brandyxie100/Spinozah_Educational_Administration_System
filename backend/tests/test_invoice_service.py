"""Unit tests for InvoiceService create and payment status workflow."""

from __future__ import annotations

import uuid
from decimal import Decimal
from types import SimpleNamespace

import pytest
from app.application.finance.invoice_service import (
    InvoiceNotFoundError,
    InvoiceService,
    InvoiceStudentNotFoundError,
)
from app.domain.finance import Invoice, PaymentStatus


class _FakeInvoiceRepo:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self.tenant_id = tenant_id
        self._rows: dict[uuid.UUID, Invoice] = {}

    async def get_by_id(self, invoice_id: uuid.UUID) -> Invoice | None:
        return self._rows.get(invoice_id)

    async def add(self, invoice: Invoice) -> Invoice:
        self._rows[invoice.id] = invoice
        return invoice

    async def save(self, invoice: Invoice) -> Invoice:
        self._rows[invoice.id] = invoice
        return invoice


class _FakeStudentRepo:
    def __init__(self, student_id: uuid.UUID) -> None:
        self._student_id = student_id

    async def get_by_id(self, student_id: uuid.UUID) -> SimpleNamespace | None:
        if student_id != self._student_id:
            return None
        return SimpleNamespace(id=student_id, full_name="Ada Lovelace")


@pytest.mark.asyncio
async def test_create_invoice_computes_final_amount() -> None:
    tenant_id = uuid.uuid4()
    student_id = uuid.uuid4()
    service = InvoiceService(
        invoice_repository=_FakeInvoiceRepo(tenant_id),
        student_repository=_FakeStudentRepo(student_id),
    )
    invoice = await service.create_invoice(
        student_id=student_id,
        semester_label="2026-S2",
        subtotal=Decimal("1000.00"),
        credit=Decimal("200.00"),
        line_items=[{"description": "Piano", "amount": "1000.00"}],
    )
    assert invoice.final_amount == Decimal("800.00")
    assert invoice.status == PaymentStatus.UNPAID


@pytest.mark.asyncio
async def test_create_invoice_missing_student_raises() -> None:
    service = InvoiceService(
        invoice_repository=_FakeInvoiceRepo(uuid.uuid4()),
        student_repository=_FakeStudentRepo(uuid.uuid4()),
    )
    with pytest.raises(InvoiceStudentNotFoundError):
        await service.create_invoice(
            student_id=uuid.uuid4(),
            semester_label="2026-S2",
            subtotal=Decimal("100.00"),
        )


@pytest.mark.asyncio
async def test_update_payment_status_to_paid() -> None:
    tenant_id = uuid.uuid4()
    student_id = uuid.uuid4()
    invoices = _FakeInvoiceRepo(tenant_id)
    service = InvoiceService(
        invoice_repository=invoices,
        student_repository=_FakeStudentRepo(student_id),
    )
    created = await service.create_invoice(
        student_id=student_id,
        semester_label="2026-S2",
        subtotal=Decimal("100.00"),
    )
    updated = await service.update_payment_status(
        created.id,
        status=PaymentStatus.PAID,
    )
    assert updated.status == PaymentStatus.PAID


@pytest.mark.asyncio
async def test_get_invoice_missing_raises() -> None:
    service = InvoiceService(
        invoice_repository=_FakeInvoiceRepo(uuid.uuid4()),
        student_repository=_FakeStudentRepo(uuid.uuid4()),
    )
    with pytest.raises(InvoiceNotFoundError):
        await service.get_invoice(uuid.uuid4())


@pytest.mark.asyncio
async def test_render_pdf_returns_pdf_bytes() -> None:
    tenant_id = uuid.uuid4()
    student_id = uuid.uuid4()
    service = InvoiceService(
        invoice_repository=_FakeInvoiceRepo(tenant_id),
        student_repository=_FakeStudentRepo(student_id),
    )
    created = await service.create_invoice(
        student_id=student_id,
        semester_label="2026-S2",
        subtotal=Decimal("100.00"),
    )
    pdf = await service.render_pdf(created.id)
    assert pdf.startswith(b"%PDF")
