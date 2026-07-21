"""Domain unit tests for Schedule and weekly recurrence expansion."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta

import pytest
from app.domain.scheduling import (
    Schedule,
    ScheduleStatus,
    Weekday,
    WeeklyRecurrence,
)

TZ = UTC


def _wednesday_slot() -> tuple[datetime, datetime]:
    """Fixed Wednesday 16:00–17:00 UTC (2026-10-14 is a Wednesday)."""
    starts = datetime(2026, 10, 14, 16, 0, tzinfo=TZ)
    ends = starts + timedelta(hours=1)
    return starts, ends


def test_schedule_rejects_inverted_time_window() -> None:
    """ends_at must be after starts_at."""
    starts, ends = _wednesday_slot()
    with pytest.raises(ValueError, match="ends_at"):
        Schedule(
            tenant_id=uuid.uuid4(),
            teacher_id=uuid.uuid4(),
            student_id=uuid.uuid4(),
            starts_at=ends,
            ends_at=starts,
        )


def test_recurring_schedule_requires_matching_weekday() -> None:
    """Recurrence weekday must match the first occurrence's ISO weekday."""
    starts, ends = _wednesday_slot()
    with pytest.raises(ValueError, match="weekday"):
        Schedule(
            tenant_id=uuid.uuid4(),
            teacher_id=uuid.uuid4(),
            student_id=uuid.uuid4(),
            starts_at=starts,
            ends_at=ends,
            recurrence=WeeklyRecurrence(weekday=Weekday.MONDAY),
        )


def test_one_off_expand_occurrences_within_range() -> None:
    """One-off schedule yields a single slot when the day is in range."""
    starts, ends = _wednesday_slot()
    schedule = Schedule(
        tenant_id=uuid.uuid4(),
        teacher_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        starts_at=starts,
        ends_at=ends,
    )
    slots = schedule.expand_occurrences(date(2026, 10, 1), date(2026, 10, 31))
    assert len(slots) == 1
    assert slots[0].starts_at == starts


def test_weekly_expand_occurrences_across_month() -> None:
    """Weekly Wednesday series expands to each matching weekday in range."""
    starts, ends = _wednesday_slot()
    schedule = Schedule(
        tenant_id=uuid.uuid4(),
        teacher_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        starts_at=starts,
        ends_at=ends,
        recurrence=WeeklyRecurrence(weekday=Weekday.WEDNESDAY),
    )
    slots = schedule.expand_occurrences(date(2026, 10, 14), date(2026, 10, 28))
    assert [slot.starts_at.date() for slot in slots] == [
        date(2026, 10, 14),
        date(2026, 10, 21),
        date(2026, 10, 28),
    ]
    assert all(
        (slot.ends_at - slot.starts_at) == timedelta(hours=1) for slot in slots
    )


def test_weekly_expand_respects_until_date() -> None:
    """recurrence.until caps generated occurrences."""
    starts, ends = _wednesday_slot()
    schedule = Schedule(
        tenant_id=uuid.uuid4(),
        teacher_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        starts_at=starts,
        ends_at=ends,
        recurrence=WeeklyRecurrence(
            weekday=Weekday.WEDNESDAY,
            until=date(2026, 10, 21),
        ),
    )
    slots = schedule.expand_occurrences(date(2026, 10, 1), date(2026, 11, 30))
    assert [slot.starts_at.date() for slot in slots] == [
        date(2026, 10, 14),
        date(2026, 10, 21),
    ]


def test_schedule_cancel_and_reschedule_status() -> None:
    """cancel/reschedule mutate status with guardrails."""
    starts, ends = _wednesday_slot()
    schedule = Schedule(
        tenant_id=uuid.uuid4(),
        teacher_id=uuid.uuid4(),
        student_id=uuid.uuid4(),
        starts_at=starts,
        ends_at=ends,
    )
    assert schedule.is_recurring is False
    schedule.mark_rescheduled()
    assert schedule.status == ScheduleStatus.RESCHEDULED
    schedule.cancel()
    assert schedule.status == ScheduleStatus.CANCELLED
    with pytest.raises(ValueError, match="cancelled"):
        schedule.mark_rescheduled()
