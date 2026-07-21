"""Attendance domain entities and teacher confirmation flow."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.students.entities import Enrolment


class AttendanceStatus(StrEnum):
    """Lifecycle of a lesson attendance record."""

    PENDING_CONFIRMATION = "pending_confirmation"
    PRESENT = "present"
    ABSENT = "absent"


@dataclass(slots=True)
class AttendanceRecord:
    """Check-in for a scheduled lesson; lessons consume on teacher confirm."""

    tenant_id: UUID
    schedule_id: UUID
    student_id: UUID
    enrolment_id: UUID
    status: AttendanceStatus = AttendanceStatus.PENDING_CONFIRMATION
    id: UUID = field(default_factory=uuid4)

    def confirm_present(self, enrolment: Enrolment) -> None:
        """Teacher confirms presence and consumes one enrolment lesson."""
        if self.status != AttendanceStatus.PENDING_CONFIRMATION:
            raise ValueError("Only pending attendance can be confirmed")
        if enrolment.id != self.enrolment_id:
            raise ValueError("Enrolment does not match this attendance record")
        if enrolment.student_id != self.student_id:
            raise ValueError("Enrolment student does not match attendance")
        enrolment.complete_lesson()
        self.status = AttendanceStatus.PRESENT

    def confirm_absent(self) -> None:
        """Teacher confirms absence without consuming a lesson."""
        if self.status != AttendanceStatus.PENDING_CONFIRMATION:
            raise ValueError("Only pending attendance can be confirmed")
        self.status = AttendanceStatus.ABSENT
