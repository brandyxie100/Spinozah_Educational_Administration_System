"""Scheduling bounded context domain package."""

from app.domain.scheduling.conflict_detection import (
    ConflictDetectionService,
    ConflictKind,
    ScheduleConflict,
    intervals_overlap,
)
from app.domain.scheduling.entities import (
    Schedule,
    ScheduleStatus,
    TimeSlot,
    Weekday,
    WeeklyRecurrence,
)

__all__ = [
    "ConflictDetectionService",
    "ConflictKind",
    "Schedule",
    "ScheduleConflict",
    "ScheduleStatus",
    "TimeSlot",
    "Weekday",
    "WeeklyRecurrence",
    "intervals_overlap",
]
