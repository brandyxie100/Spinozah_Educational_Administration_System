"""Pydantic schemas for parent portal magic-link and dashboard APIs."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class MagicLinkRequest(BaseModel):
    """Payload to request a parent magic-link email."""

    tenant_slug: str = Field(min_length=1, max_length=100)
    email: EmailStr


class MagicLinkRequestResponse(BaseModel):
    """Generic acceptance response (does not leak account existence)."""

    detail: str = "If a parent account exists, a magic link has been sent"
    magic_url: str | None = None


class MagicLinkConsumeRequest(BaseModel):
    """Payload to exchange a magic-link token for JWTs."""

    token: str = Field(min_length=16, max_length=256)


class ParentStudentLinkCreate(BaseModel):
    """Payload for frontdesk/admin to link a parent to a student."""

    parent_user_id: UUID
    student_id: UUID


class ParentStudentLinkOut(BaseModel):
    """Public representation of a parent↔student link."""

    id: UUID
    tenant_id: UUID
    parent_user_id: UUID
    student_id: UUID


class LinkedStudentOut(BaseModel):
    """Student summary visible to a linked parent."""

    id: UUID
    full_name: str
    email: str | None
    is_active: bool


class ParentEnrolmentOut(BaseModel):
    """Active enrolment with remaining lesson balance for a linked student."""

    id: UUID
    student_id: UUID
    status: str
    total_lessons: int
    completed_lessons: int
    remaining_lessons: int
    extension_days: int


class ParentAttendanceOut(BaseModel):
    """Attendance history row visible to a linked parent."""

    id: UUID
    schedule_id: UUID
    student_id: UUID
    enrolment_id: UUID
    status: str


class ParentInvoiceOut(BaseModel):
    """Invoice summary for a linked student."""

    id: UUID
    student_id: UUID
    semester_label: str
    subtotal: Decimal
    credit: Decimal
    final_amount: Decimal
    status: str


class ParentDashboardReportOut(BaseModel):
    """Aggregate dashboard report for one linked student."""

    student_id: UUID
    remaining_lessons: int | None
    total_lessons: int | None
    completed_lessons: int | None
    attendance_count: int
    invoice_count: int
    unpaid_invoice_count: int
