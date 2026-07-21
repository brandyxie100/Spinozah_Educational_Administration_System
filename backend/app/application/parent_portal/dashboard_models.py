"""Parent portal dashboard read models and access errors."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.domain.attendance.entities import AttendanceRecord
from app.domain.finance.entities import Invoice
from app.domain.students.entities import Enrolment


class ParentStudentNotLinkedError(Exception):
    """Raised when a parent requests a student they are not linked to."""


class EnrolmentNotFoundError(Exception):
    """Raised when the linked student has no active enrolment."""


class ParentInvoiceNotFoundError(Exception):
    """Raised when an invoice is missing or not owned by the linked student."""


@dataclass(frozen=True, slots=True)
class StudentDashboardReport:
    """Aggregate parent-facing report for one linked student."""

    student_id: UUID
    remaining_lessons: int | None
    total_lessons: int | None
    completed_lessons: int | None
    attendance_count: int
    invoice_count: int
    unpaid_invoice_count: int


@dataclass(frozen=True, slots=True)
class ParentEnrolmentView:
    """Enrolment snapshot with remaining lesson balance."""

    enrolment: Enrolment
    remaining_lessons: int


__all__ = [
    "AttendanceRecord",
    "EnrolmentNotFoundError",
    "Invoice",
    "ParentEnrolmentView",
    "ParentInvoiceNotFoundError",
    "ParentStudentNotLinkedError",
    "StudentDashboardReport",
]
