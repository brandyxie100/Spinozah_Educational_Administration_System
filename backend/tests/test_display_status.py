"""Unit tests for timetable display status resolution."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.domain.scheduling.display_status import DisplayStatus, resolve_display_status
from app.domain.scheduling.entities import ScheduleStatus, TimeSlot

TZ = UTC


def _slot(hour: int) -> TimeSlot:
    starts = datetime(2026, 10, 14, hour, 0, tzinfo=TZ)
    return TimeSlot(starts, starts + timedelta(hours=1))


def test_display_status_in_progress_during_window() -> None:
    slot = _slot(16)
    now = datetime(2026, 10, 14, 16, 30, tzinfo=TZ)
    assert (
        resolve_display_status(slot, ScheduleStatus.NOT_STARTED, now=now)
        == DisplayStatus.IN_PROGRESS
    )


def test_display_status_starting_soon() -> None:
    slot = _slot(16)
    now = datetime(2026, 10, 14, 15, 50, tzinfo=TZ)
    assert (
        resolve_display_status(slot, ScheduleStatus.NOT_STARTED, now=now)
        == DisplayStatus.STARTING_SOON
    )


def test_display_status_absent_when_cancelled() -> None:
    slot = _slot(16)
    now = datetime(2026, 10, 14, 15, 0, tzinfo=TZ)
    assert (
        resolve_display_status(slot, ScheduleStatus.CANCELLED, now=now)
        == DisplayStatus.ABSENT
    )


def test_display_status_upcoming_when_far_away() -> None:
    slot = _slot(16)
    now = datetime(2026, 10, 14, 10, 0, tzinfo=TZ)
    assert (
        resolve_display_status(slot, ScheduleStatus.NOT_STARTED, now=now)
        == DisplayStatus.UPCOMING
    )


def test_display_status_respects_domain_in_progress_and_completed() -> None:
    slot = _slot(16)
    early = datetime(2026, 10, 14, 10, 0, tzinfo=TZ)
    assert (
        resolve_display_status(slot, ScheduleStatus.IN_PROGRESS, now=early)
        == DisplayStatus.IN_PROGRESS
    )
    assert (
        resolve_display_status(slot, ScheduleStatus.COMPLETED, now=early)
        == DisplayStatus.COMPLETED
    )


def test_display_status_completed_after_window() -> None:
    slot = _slot(16)
    now = datetime(2026, 10, 14, 18, 0, tzinfo=TZ)
    assert (
        resolve_display_status(slot, ScheduleStatus.NOT_STARTED, now=now)
        == DisplayStatus.COMPLETED
    )
