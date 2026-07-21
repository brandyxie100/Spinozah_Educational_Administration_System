"""Unit tests for invoice API routes with dependency overrides."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from decimal import Decimal

import pytest
from app.api.v1.invoices import get_invoice_service
from app.application.finance.invoice_service import InvoiceService
from app.domain.finance import Invoice, InvoiceLineItem, PaymentStatus
from app.main import create_app
from fastapi.testclient import TestClient


class _FakeInvoiceService:
    def __init__(self) -> None:
        self.tenant_id = uuid.uuid4()
        self._rows: dict[uuid.UUID, Invoice] = {}

    async def create_invoice(self, **kwargs: object) -> Invoice:
        items = [
            InvoiceLineItem(
                description=str(raw["description"]),
                amount=Decimal(str(raw["amount"])),
            )
            for raw in (kwargs.get("line_items") or [])  # type: ignore[union-attr]
        ]
        invoice = Invoice(
            tenant_id=self.tenant_id,
            student_id=kwargs["student_id"],  # type: ignore[arg-type]
            semester_label=kwargs["semester_label"],  # type: ignore[arg-type]
            subtotal=kwargs["subtotal"],  # type: ignore[arg-type]
            credit=kwargs.get("credit") or Decimal("0.00"),  # type: ignore[arg-type]
            enrolment_id=kwargs.get("enrolment_id"),  # type: ignore[arg-type]
            line_items=items,
        )
        self._rows[invoice.id] = invoice
        return invoice

    async def get_invoice(self, invoice_id: uuid.UUID) -> Invoice:
        return self._rows[invoice_id]

    async def update_payment_status(
        self,
        invoice_id: uuid.UUID,
        *,
        status: PaymentStatus,
    ) -> Invoice:
        invoice = self._rows[invoice_id]
        if status == PaymentStatus.PAID:
            invoice.mark_paid()
        elif status == PaymentStatus.PARTIAL:
            invoice.mark_partial()
        elif status == PaymentStatus.VOID:
            invoice.void()
        else:
            invoice.status = status
        return invoice

    async def render_pdf(self, invoice_id: uuid.UUID) -> bytes:
        _ = self._rows[invoice_id]
        return b"%PDF-1.4 fake-invoice"


@pytest.fixture
def client() -> Iterator[TestClient]:
    fake = _FakeInvoiceService()
    app = create_app()

    def _override() -> InvoiceService:
        return fake  # type: ignore[return-value]

    app.dependency_overrides[get_invoice_service] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_create_invoice_and_download_pdf(client: TestClient) -> None:
    created = client.post(
        "/api/v1/invoices",
        json={
            "student_id": str(uuid.uuid4()),
            "semester_label": "2026-S2",
            "subtotal": "1200.00",
            "credit": "100.00",
            "line_items": [{"description": "Piano", "amount": "1200.00"}],
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["final_amount"] == "1100.00"
    assert body["status"] == "unpaid"
    invoice_id = body["id"]

    pdf = client.get(f"/api/v1/invoices/{invoice_id}/pdf")
    assert pdf.status_code == 200
    assert pdf.headers["content-type"].startswith("application/pdf")
    assert pdf.content.startswith(b"%PDF")

    paid = client.patch(
        f"/api/v1/invoices/{invoice_id}/payment-status",
        json={"status": "paid"},
    )
    assert paid.status_code == 200
    assert paid.json()["status"] == "paid"
