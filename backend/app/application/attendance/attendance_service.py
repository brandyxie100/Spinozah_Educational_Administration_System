"""Application service for attendance check-in and teacher confirmation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.domain.attendance.entities import AttendanceRecord, AttendanceStatus
from app.infrastructure.persistence.attendance_repository import (
    SqlAlchemyAttendanceRepository,
    SqlAlchemyEnrolmentRepository,
)
from app.infrastructure.persistence.schedule_repository import (
    SqlAlchemyScheduleRepository,
)


class AttendanceConflictError(Exception):
    """Raised when check-in already exists for a schedule."""


class AttendanceNotFoundError(Exception):
    """Raised when an attendance id is missing in the tenant."""


class ScheduleNotFoundForAttendanceError(Exception):
    """Raised when check-in references an unknown schedule."""


class EnrolmentNotFoundError(Exception):
    """Raised when no suitable enrolment exists for lesson consumption."""


class ConfirmOutcome(StrEnum):
    """Teacher confirmation outcomes for a pending check-in."""

    PRESENT = "present"
    ABSENT = "absent"


@dataclass(frozen=True, slots=True)
class AttendanceResult:
    """API-facing attendance snapshot including remaining lessons."""

    attendance: AttendanceRecord
    remaining_lessons: int | None


class AttendanceService:
    """Check-in students and confirm attendance with lesson consumption."""

    def __init__(
        self,
        attendance_repository: SqlAlchemyAttendanceRepository,
        enrolment_repository: SqlAlchemyEnrolmentRepository,
        schedule_repository: SqlAlchemyScheduleRepository,
    ) -> None:
        """Bind tenant-scoped attendance, enrolment, and schedule repos."""
        self._attendance = attendance_repository
        self._enrolments = enrolment_repository
        self._schedules = schedule_repository

    async def check_in(
        self,
        *,
        schedule_id: UUID,
        enrolment_id: UUID | None = None,
    ) -> AttendanceResult:
        """Create a pending attendance record for a scheduled lesson."""
        schedule = await self._schedules.get_by_id(schedule_id)
        if schedule is None:
            raise ScheduleNotFoundForAttendanceError(
                f"Schedule not found: {schedule_id}",
            )

        existing = await self._attendance.get_by_schedule_id(schedule_id)
        if existing is not None:
            raise AttendanceConflictError(
                f"Attendance already recorded for schedule: {schedule_id}",
            )

        if enrolment_id is not None:
            enrolment = await self._enrolments.get_by_id(enrolment_id)
        else:
            enrolment = await self._enrolments.get_active_for_student(
                schedule.student_id,
            )
        if enrolment is None:
            raise EnrolmentNotFoundError(
                f"No active enrolment for student: {schedule.student_id}",
            )
        if enrolment.student_id != schedule.student_id:
            raise EnrolmentNotFoundError(
                "Enrolment does not belong to the scheduled student",
            )

        record = AttendanceRecord(
            tenant_id=self._attendance.tenant_id,
            schedule_id=schedule_id,
            student_id=schedule.student_id,
            enrolment_id=enrolment.id,
            status=AttendanceStatus.PENDING_CONFIRMATION,
        )
        saved = await self._attendance.add(record)
        return AttendanceResult(
            attendance=saved,
            remaining_lessons=enrolment.remaining_lessons(),
        )

    async def confirm(
        self,
        attendance_id: UUID,
        *,
        outcome: ConfirmOutcome,
    ) -> AttendanceResult:
        """Teacher confirms present/absent; present consumes one lesson."""
        record = await self._attendance.get_by_id(attendance_id)
        if record is None:
            raise AttendanceNotFoundError(f"Attendance not found: {attendance_id}")

        enrolment = await self._enrolments.get_by_id(record.enrolment_id)
        if enrolment is None:
            raise EnrolmentNotFoundError(
                f"Enrolment not found: {record.enrolment_id}",
            )

        if outcome == ConfirmOutcome.PRESENT:
            record.confirm_present(enrolment)
            enrolment = await self._enrolments.save(enrolment)
        else:
            record.confirm_absent()

        saved = await self._attendance.save(record)
        return AttendanceResult(
            attendance=saved,
            remaining_lessons=enrolment.remaining_lessons(),
        )

    async def list_attendance(
        self,
        *,
        status: str | None = None,
        student_id: UUID | None = None,
        limit: int = 100,
    ) -> list[AttendanceResult]:
        """List attendance records for the tenant with remaining lesson balances."""
        records = await self._attendance.list(
            status=status,
            student_id=student_id,
            limit=limit,
        )
        results: list[AttendanceResult] = []
        for record in records:
            enrolment = await self._enrolments.get_by_id(record.enrolment_id)
            remaining = (
                enrolment.remaining_lessons() if enrolment is not None else None
            )
            results.append(
                AttendanceResult(attendance=record, remaining_lessons=remaining),
            )
        return results
