"""Unit tests for ScheduleService conflict gatekeeping."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from app.application.scheduling.schedule_service import (
    ScheduleConflictError,
    ScheduleService,
)
from app.domain.scheduling.entities import Schedule

TZ = UTC


class _MemoryScheduleRepo:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self.tenant_id = tenant_id
        self._rows: list[Schedule] = []

    async def list_all(self) -> list[Schedule]:
        return list(self._rows)

    async def add(self, schedule: Schedule) -> Schedule:
        self._rows.append(schedule)
        return schedule


@pytest.fixture
def service() -> ScheduleService:
    repo: Any = _MemoryScheduleRepo(uuid.uuid4())
    return ScheduleService(repository=repo)


@pytest.mark.asyncio
async def test_schedule_service_creates_when_no_conflict(
    service: ScheduleService,
) -> None:
    starts = datetime(2026, 10, 14, 16, 0, tzinfo=TZ)
    created = await service.create_schedule(
        teacher_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        starts_at=starts,
        ends_at=starts + timedelta(hours=1),
    )
    assert created.id is not None


@pytest.mark.asyncio
async def test_schedule_service_raises_on_teacher_conflict(
    service: ScheduleService,
) -> None:
    teacher = uuid.uuid4()
    starts = datetime(2026, 10, 14, 16, 0, tzinfo=TZ)
    ends = starts + timedelta(hours=1)
    await service.create_schedule(
        teacher_id=teacher,
        student_id=uuid.uuid4(),
        starts_at=starts,
        ends_at=ends,
    )
    with pytest.raises(ScheduleConflictError) as exc_info:
        await service.create_schedule(
            teacher_id=teacher,
            student_id=uuid.uuid4(),
            starts_at=starts,
            ends_at=ends,
        )
    assert exc_info.value.conflicts
