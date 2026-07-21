"""Unit tests for ScheduleService.get_teacher_schedule."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any

import pytest
from app.application.scheduling.schedule_service import (
    ScheduleService,
    TeacherNotFoundForScheduleError,
)
from app.domain.scheduling.display_status import DisplayStatus
from app.domain.scheduling.entities import Schedule, ScheduleStatus
from app.infrastructure.persistence.student_models import StudentModel
from app.infrastructure.persistence.teacher_models import TeacherModel

TZ = UTC


class _MemoryScheduleRepo:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self.tenant_id = tenant_id
        self._rows: list[Schedule] = []

    async def list_all(self) -> list[Schedule]:
        return list(self._rows)

    async def list_by_teacher_id(self, teacher_id: uuid.UUID) -> list[Schedule]:
        return [row for row in self._rows if row.teacher_id == teacher_id]

    async def add(self, schedule: Schedule) -> Schedule:
        self._rows.append(schedule)
        return schedule


class _MemoryTeacherRepo:
    def __init__(self, teacher: TeacherModel | None) -> None:
        self._teacher = teacher

    async def get_by_id(self, teacher_id: uuid.UUID) -> TeacherModel | None:
        if self._teacher is not None and self._teacher.id == teacher_id:
            return self._teacher
        return None


class _MemoryStudentRepo:
    def __init__(self, student: StudentModel) -> None:
        self._student = student

    async def get_by_id(self, student_id: uuid.UUID) -> StudentModel | None:
        if self._student.id == student_id:
            return self._student
        return None


@pytest.mark.asyncio
async def test_get_teacher_schedule_expands_slots_with_display_status() -> None:
    tenant_id = uuid.uuid4()
    teacher_id = uuid.uuid4()
    student_id = uuid.uuid4()
    starts = datetime(2026, 10, 14, 16, 0, tzinfo=TZ)
    schedule = Schedule(
        tenant_id=tenant_id,
        teacher_id=teacher_id,
        student_id=student_id,
        starts_at=starts,
        ends_at=starts + timedelta(hours=1),
        status=ScheduleStatus.CANCELLED,
    )
    repo: Any = _MemoryScheduleRepo(tenant_id)
    await repo.add(schedule)

    teacher = TeacherModel(
        id=teacher_id,
        tenant_id=tenant_id,
        full_name="Max",
        email=None,
        user_id=None,
        is_active=True,
    )
    student = StudentModel(
        id=student_id,
        tenant_id=tenant_id,
        full_name="Charlotte",
        email=None,
        is_active=True,
    )
    service = ScheduleService(
        repository=repo,
        teacher_repository=_MemoryTeacherRepo(teacher),  # type: ignore[arg-type]
        student_repository=_MemoryStudentRepo(student),  # type: ignore[arg-type]
    )

    slots = await service.get_teacher_schedule(
        teacher_id,
        range_start=date(2026, 10, 14),
        range_end=date(2026, 10, 14),
        now=datetime(2026, 10, 14, 15, 0, tzinfo=TZ),
    )
    assert len(slots) == 1
    assert slots[0].student_name == "Charlotte"
    assert slots[0].display_status == DisplayStatus.ABSENT


@pytest.mark.asyncio
async def test_get_teacher_schedule_raises_when_teacher_missing() -> None:
    tenant_id = uuid.uuid4()
    repo: Any = _MemoryScheduleRepo(tenant_id)
    service = ScheduleService(
        repository=repo,
        teacher_repository=_MemoryTeacherRepo(None),  # type: ignore[arg-type]
    )
    with pytest.raises(TeacherNotFoundForScheduleError):
        await service.get_teacher_schedule(
            uuid.uuid4(),
            range_start=date(2026, 10, 14),
            range_end=date(2026, 10, 14),
        )
