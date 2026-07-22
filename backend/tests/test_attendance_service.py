"""Unit tests for AttendanceService check-in and confirm flow."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from app.application.attendance.attendance_service import (
    AttendanceConflictError,
    AttendanceService,
    ConfirmOutcome,
)
from app.domain.attendance import AttendanceRecord, AttendanceStatus
from app.domain.scheduling.entities import Schedule
from app.domain.students import Enrolment

TZ = UTC


class _MemoryAttendanceRepo:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self.tenant_id = tenant_id
        self._rows: dict[uuid.UUID, AttendanceRecord] = {}

    async def get_by_id(self, attendance_id: uuid.UUID) -> AttendanceRecord | None:
        return self._rows.get(attendance_id)

    async def get_by_schedule_id(
        self,
        schedule_id: uuid.UUID,
    ) -> AttendanceRecord | None:
        for row in self._rows.values():
            if row.schedule_id == schedule_id:
                return row
        return None

    async def add(self, record: AttendanceRecord) -> AttendanceRecord:
        self._rows[record.id] = record
        return record

    async def save(self, record: AttendanceRecord) -> AttendanceRecord:
        self._rows[record.id] = record
        return record

    async def list(
        self,
        *,
        status: str | None = None,
        student_id: uuid.UUID | None = None,
        limit: int = 100,
    ) -> list[AttendanceRecord]:
        rows = list(self._rows.values())
        if student_id is not None:
            rows = [row for row in rows if row.student_id == student_id]
        if status is not None:
            rows = [row for row in rows if row.status.value == status]
        return rows[:limit]


class _MemoryEnrolmentRepo:
    def __init__(self, enrolment: Enrolment) -> None:
        self._enrolment = enrolment

    async def get_by_id(self, enrolment_id: uuid.UUID) -> Enrolment | None:
        if self._enrolment.id == enrolment_id:
            return self._enrolment
        return None

    async def get_active_for_student(self, student_id: uuid.UUID) -> Enrolment | None:
        if self._enrolment.student_id == student_id:
            return self._enrolment
        return None

    async def save(self, enrolment: Enrolment) -> Enrolment:
        self._enrolment = enrolment
        return enrolment


class _MemoryScheduleRepo:
    def __init__(self, schedule: Schedule) -> None:
        self._schedule = schedule

    async def get_by_id(self, schedule_id: uuid.UUID) -> Schedule | None:
        if self._schedule.id == schedule_id:
            return self._schedule
        return None


@pytest.mark.asyncio
async def test_check_in_then_confirm_present_decrements_lessons() -> None:
    tenant_id = uuid.uuid4()
    student_id = uuid.uuid4()
    starts = datetime(2026, 11, 4, 16, 0, tzinfo=TZ)
    schedule = Schedule(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        teacher_id=uuid.uuid4(),
        student_id=student_id,
        starts_at=starts,
        ends_at=starts + timedelta(hours=1),
    )
    enrolment = Enrolment(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        student_id=student_id,
        total_lessons=10,
        completed_lessons=1,
    )
    attendance_repo: Any = _MemoryAttendanceRepo(tenant_id)
    service = AttendanceService(
        attendance_repository=attendance_repo,
        enrolment_repository=_MemoryEnrolmentRepo(enrolment),  # type: ignore[arg-type]
        schedule_repository=_MemoryScheduleRepo(schedule),  # type: ignore[arg-type]
    )

    checked_in = await service.check_in(schedule_id=schedule.id)
    assert checked_in.attendance.status == AttendanceStatus.PENDING_CONFIRMATION
    assert checked_in.remaining_lessons == 9

    confirmed = await service.confirm(
        checked_in.attendance.id,
        outcome=ConfirmOutcome.PRESENT,
    )
    assert confirmed.attendance.status == AttendanceStatus.PRESENT
    assert confirmed.remaining_lessons == 8


@pytest.mark.asyncio
async def test_check_in_rejects_duplicate_schedule() -> None:
    tenant_id = uuid.uuid4()
    student_id = uuid.uuid4()
    starts = datetime(2026, 11, 4, 16, 0, tzinfo=TZ)
    schedule = Schedule(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        teacher_id=uuid.uuid4(),
        student_id=student_id,
        starts_at=starts,
        ends_at=starts + timedelta(hours=1),
    )
    enrolment = Enrolment(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        student_id=student_id,
        total_lessons=5,
        completed_lessons=0,
    )
    service = AttendanceService(
        attendance_repository=_MemoryAttendanceRepo(tenant_id),  # type: ignore[arg-type]
        enrolment_repository=_MemoryEnrolmentRepo(enrolment),  # type: ignore[arg-type]
        schedule_repository=_MemoryScheduleRepo(schedule),  # type: ignore[arg-type]
    )
    await service.check_in(schedule_id=schedule.id)
    with pytest.raises(AttendanceConflictError):
        await service.check_in(schedule_id=schedule.id)


@pytest.mark.asyncio
async def test_list_attendance_filters_pending() -> None:
    tenant_id = uuid.uuid4()
    student_id = uuid.uuid4()
    starts = datetime(2026, 11, 4, 16, 0, tzinfo=TZ)
    schedule = Schedule(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        teacher_id=uuid.uuid4(),
        student_id=student_id,
        starts_at=starts,
        ends_at=starts + timedelta(hours=1),
    )
    enrolment = Enrolment(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        student_id=student_id,
        total_lessons=10,
        completed_lessons=0,
    )
    service = AttendanceService(
        attendance_repository=_MemoryAttendanceRepo(tenant_id),  # type: ignore[arg-type]
        enrolment_repository=_MemoryEnrolmentRepo(enrolment),  # type: ignore[arg-type]
        schedule_repository=_MemoryScheduleRepo(schedule),  # type: ignore[arg-type]
    )
    await service.check_in(schedule_id=schedule.id)
    pending = await service.list_attendance(status="pending_confirmation")
    assert len(pending) == 1
    assert pending[0].remaining_lessons == 10
