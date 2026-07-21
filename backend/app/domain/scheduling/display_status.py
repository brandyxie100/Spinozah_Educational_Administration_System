"""Resolve live timetable display status for a concrete occurrence."""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum

from app.domain.scheduling.entities import ScheduleStatus, TimeSlot

_STARTING_SOON_WINDOW = timedelta(minutes=15)


class DisplayStatus(StrEnum):
    """UI-facing lesson status for teacher timetable views."""

    IN_PROGRESS = "in_progress"
    ABSENT = "absent"
    STARTING_SOON = "starting_soon"
    UPCOMING = "upcoming"
    COMPLETED = "completed"


def resolve_display_status(
    slot: TimeSlot,
    schedule_status: ScheduleStatus,
    *,
    now: datetime,
) -> DisplayStatus:
    """Map domain status + clock to a timetable display status.

    - cancelled → absent (placeholder until attendance check-in lands)
    - within the lesson window → in_progress
    - starting within 15 minutes → starting_soon
    - otherwise upcoming or completed
    """
    if schedule_status == ScheduleStatus.CANCELLED:
        return DisplayStatus.ABSENT
    if schedule_status == ScheduleStatus.IN_PROGRESS:
        return DisplayStatus.IN_PROGRESS
    if schedule_status == ScheduleStatus.COMPLETED:
        return DisplayStatus.COMPLETED
    if slot.starts_at <= now < slot.ends_at:
        return DisplayStatus.IN_PROGRESS
    if now >= slot.ends_at:
        return DisplayStatus.COMPLETED
    if timedelta(0) < (slot.starts_at - now) <= _STARTING_SOON_WINDOW:
        return DisplayStatus.STARTING_SOON
    return DisplayStatus.UPCOMING
