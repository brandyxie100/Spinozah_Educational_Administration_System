"""Unit tests for schedule conflict detection edge cases."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta

from app.domain.scheduling import Schedule, ScheduleStatus, Weekday, WeeklyRecurrence
from app.domain.scheduling.conflict_detection import (
    ConflictDetectionService,
    ConflictKind,
    intervals_overlap,
)
from app.domain.scheduling.entities import TimeSlot

TZ = UTC
DETECTOR = ConflictDetectionService()


def _slot(
    day: date,
    hour: int,
    *,
    duration_hours: int = 1,
) -> tuple[datetime, datetime]:
    starts = datetime(day.year, day.month, day.day, hour, 0, tzinfo=TZ)
    return starts, starts + timedelta(hours=duration_hours)


def _schedule(
    *,
    teacher_id: uuid.UUID,
    student_id: uuid.UUID,
    starts_at: datetime,
    ends_at: datetime,
    classroom: str | None = None,
    status: ScheduleStatus = ScheduleStatus.NOT_STARTED,
    recurrence: WeeklyRecurrence | None = None,
    schedule_id: uuid.UUID | None = None,
) -> Schedule:
    return Schedule(
        id=schedule_id or uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        teacher_id=teacher_id,
        student_id=student_id,
        starts_at=starts_at,
        ends_at=ends_at,
        classroom=classroom,
        status=status,
        recurrence=recurrence,
    )


def test_intervals_overlap_true_for_partial_overlap() -> None:
    left = TimeSlot(*_slot(date(2026, 10, 14), 16))
    right = TimeSlot(*_slot(date(2026, 10, 14), 16, duration_hours=2))
    # right starts at same time — overlaps
    assert intervals_overlap(left, right) is True


def test_intervals_adjacent_do_not_overlap() -> None:
    """Back-to-back lessons (end == start) are allowed."""
    first_start, first_end = _slot(date(2026, 10, 14), 16)
    second_start, second_end = first_end, first_end + timedelta(hours=1)
    assert (
        intervals_overlap(
            TimeSlot(first_start, first_end),
            TimeSlot(second_start, second_end),
        )
        is False
    )


def test_detects_teacher_overlap() -> None:
    teacher = uuid.uuid4()
    starts, ends = _slot(date(2026, 10, 14), 16)
    existing = _schedule(
        teacher_id=teacher,
        student_id=uuid.uuid4(),
        starts_at=starts,
        ends_at=ends,
    )
    proposed = _schedule(
        teacher_id=teacher,
        student_id=uuid.uuid4(),
        starts_at=starts,
        ends_at=ends,
    )
    conflicts = DETECTOR.find_conflicts(
        proposed,
        [existing],
        range_start=date(2026, 10, 14),
        range_end=date(2026, 10, 14),
    )
    assert any(c.kind == ConflictKind.TEACHER for c in conflicts)
    assert not any(c.kind == ConflictKind.STUDENT for c in conflicts)


def test_detects_student_overlap() -> None:
    student = uuid.uuid4()
    starts, ends = _slot(date(2026, 10, 14), 16)
    existing = _schedule(
        teacher_id=uuid.uuid4(),
        student_id=student,
        starts_at=starts,
        ends_at=ends,
    )
    proposed = _schedule(
        teacher_id=uuid.uuid4(),
        student_id=student,
        starts_at=starts,
        ends_at=ends,
    )
    conflicts = DETECTOR.find_conflicts(
        proposed,
        [existing],
        range_start=date(2026, 10, 14),
        range_end=date(2026, 10, 14),
    )
    assert any(c.kind == ConflictKind.STUDENT for c in conflicts)


def test_detects_classroom_overlap_when_both_named() -> None:
    starts, ends = _slot(date(2026, 10, 14), 16)
    existing = _schedule(
        teacher_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        starts_at=starts,
        ends_at=ends,
        classroom="Room A",
    )
    proposed = _schedule(
        teacher_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        starts_at=starts,
        ends_at=ends,
        classroom="Room A",
    )
    conflicts = DETECTOR.find_conflicts(
        proposed,
        [existing],
        range_start=date(2026, 10, 14),
        range_end=date(2026, 10, 14),
    )
    assert any(c.kind == ConflictKind.CLASSROOM for c in conflicts)


def test_no_classroom_conflict_when_classroom_missing() -> None:
    starts, ends = _slot(date(2026, 10, 14), 16)
    existing = _schedule(
        teacher_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        starts_at=starts,
        ends_at=ends,
        classroom="Room A",
    )
    proposed = _schedule(
        teacher_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        starts_at=starts,
        ends_at=ends,
        classroom=None,
    )
    conflicts = DETECTOR.find_conflicts(
        proposed,
        [existing],
        range_start=date(2026, 10, 14),
        range_end=date(2026, 10, 14),
    )
    assert conflicts == []


def test_cancelled_schedules_are_ignored() -> None:
    teacher = uuid.uuid4()
    starts, ends = _slot(date(2026, 10, 14), 16)
    existing = _schedule(
        teacher_id=teacher,
        student_id=uuid.uuid4(),
        starts_at=starts,
        ends_at=ends,
        status=ScheduleStatus.CANCELLED,
    )
    proposed = _schedule(
        teacher_id=teacher,
        student_id=uuid.uuid4(),
        starts_at=starts,
        ends_at=ends,
    )
    conflicts = DETECTOR.find_conflicts(
        proposed,
        [existing],
        range_start=date(2026, 10, 14),
        range_end=date(2026, 10, 14),
    )
    assert conflicts == []


def test_exclude_schedule_id_skips_self() -> None:
    teacher = uuid.uuid4()
    schedule_id = uuid.uuid4()
    starts, ends = _slot(date(2026, 10, 14), 16)
    existing = _schedule(
        teacher_id=teacher,
        student_id=uuid.uuid4(),
        starts_at=starts,
        ends_at=ends,
        schedule_id=schedule_id,
    )
    proposed = _schedule(
        teacher_id=teacher,
        student_id=uuid.uuid4(),
        starts_at=starts,
        ends_at=ends,
    )
    conflicts = DETECTOR.find_conflicts(
        proposed,
        [existing],
        range_start=date(2026, 10, 14),
        range_end=date(2026, 10, 14),
        exclude_schedule_id=schedule_id,
    )
    assert conflicts == []


def test_recurring_series_conflicts_on_later_week() -> None:
    """Weekly series overlapping on week 2 is detected within the window."""
    teacher = uuid.uuid4()
    first_start, first_end = _slot(date(2026, 10, 14), 16)  # Wednesday
    existing = _schedule(
        teacher_id=teacher,
        student_id=uuid.uuid4(),
        starts_at=first_start + timedelta(days=7),
        ends_at=first_end + timedelta(days=7),
    )
    proposed = _schedule(
        teacher_id=teacher,
        student_id=uuid.uuid4(),
        starts_at=first_start,
        ends_at=first_end,
        recurrence=WeeklyRecurrence(weekday=Weekday.WEDNESDAY),
    )
    conflicts = DETECTOR.find_conflicts(
        proposed,
        [existing],
        range_start=date(2026, 10, 14),
        range_end=date(2026, 10, 28),
    )
    assert any(c.kind == ConflictKind.TEACHER for c in conflicts)
