"""Pydantic schemas for invoice and finance APIs."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class InvoiceLineItemIn(BaseModel):
    """One subject or fee line on create."""

    description: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(ge=0)


class InvoiceCreate(BaseModel):
    """Payload to generate a semester invoice."""

    student_id: UUID
    semester_label: str = Field(min_length=1, max_length=100)
    subtotal: Decimal = Field(ge=0)
    credit: Decimal = Field(default=Decimal("0.00"), ge=0)
    enrolment_id: UUID | None = None
    line_items: list[InvoiceLineItemIn] = Field(default_factory=list)


class InvoicePaymentStatusUpdate(BaseModel):
    """Payload to update invoice payment tracking status."""

    status: str = Field(pattern="^(unpaid|partial|paid|void)$")


class InvoiceLineItemOut(BaseModel):
    """Public line item representation."""

    description: str
    amount: Decimal


class InvoiceOut(BaseModel):
    """Public invoice representation including computed final amount."""

    id: UUID
    tenant_id: UUID
    student_id: UUID
    enrolment_id: UUID | None
    semester_label: str
    subtotal: Decimal
    credit: Decimal
    final_amount: Decimal
    status: str
    line_items: list[InvoiceLineItemOut]
