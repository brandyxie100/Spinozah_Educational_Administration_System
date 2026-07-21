"""Schedule domain entities and weekly recurrence expansion."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import IntEnum, StrEnum
from uuid import UUID, uuid4


class ScheduleStatus(StrEnum):
    """Lifecycle state of a scheduled lesson slot."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class Weekday(IntEnum):
    """ISO weekday numbers (Monday=1 … Sunday=7)."""

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


@dataclass(frozen=True, slots=True)
class TimeSlot:
    """Concrete lesson window on the calendar."""

    starts_at: datetime
    ends_at: datetime

    def __post_init__(self) -> None:
        """Require a positive duration."""
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")


@dataclass(frozen=True, slots=True)
class WeeklyRecurrence:
    """Weekly recurrence rule anchored to an ISO weekday.

    Occurrence clock times come from the parent schedule's first slot.
    """

    weekday: Weekday
    until: date | None = None

    def __post_init__(self) -> None:
        """Reject invalid weekday values."""
        if int(self.weekday) not in range(1, 8):
            raise ValueError("weekday must be ISO 1–7")


@dataclass(slots=True)
class Schedule:
    """Tenant-scoped lesson booking; optionally repeats weekly."""

    tenant_id: UUID
    teacher_id: UUID
    student_id: UUID
    starts_at: datetime
    ends_at: datetime
    status: ScheduleStatus = ScheduleStatus.NOT_STARTED
    classroom: str | None = None
    recurrence: WeeklyRecurrence | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        """Validate slot duration and recurrence weekday alignment."""
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        if self.recurrence is not None:
            if self.starts_at.isoweekday() != int(self.recurrence.weekday):
                raise ValueError(
                    "recurrence weekday must match starts_at ISO weekday",
                )

    @property
    def is_recurring(self) -> bool:
        """True when a weekly recurrence rule is attached."""
        return self.recurrence is not None

    def cancel(self) -> None:
        """Mark the schedule cancelled."""
        if self.status == ScheduleStatus.COMPLETED:
            raise ValueError("Cannot cancel a completed schedule")
        self.status = ScheduleStatus.CANCELLED

    def mark_rescheduled(self) -> None:
        """Mark the schedule as rescheduled (replacement booked elsewhere)."""
        if self.status == ScheduleStatus.CANCELLED:
            raise ValueError("Cannot reschedule a cancelled schedule")
        self.status = ScheduleStatus.RESCHEDULED

    def expand_occurrences(
        self,
        range_start: date,
        range_end: date,
    ) -> list[TimeSlot]:
        """Return concrete slots overlapping ``[range_start, range_end]`` inclusive.

        One-off schedules yield at most one slot. Weekly schedules walk each
        matching weekday until ``recurrence.until`` (if set).
        """
        if range_end < range_start:
            raise ValueError("range_end must be on or after range_start")

        if self.recurrence is None:
            slot_day = self.starts_at.date()
            if range_start <= slot_day <= range_end:
                return [TimeSlot(self.starts_at, self.ends_at)]
            return []

        if self.starts_at.tzinfo:
            start_clock = self.starts_at.timetz()
        else:
            start_clock = self.starts_at.time()
        duration = self.ends_at - self.starts_at

        until = self.recurrence.until
        first_day = self.starts_at.date()
        cursor = max(range_start, first_day)
        # Advance to the first matching weekday on/after cursor.
        target = int(self.recurrence.weekday)
        while cursor.isoweekday() != target:
            cursor += timedelta(days=1)

        slots: list[TimeSlot] = []
        while cursor <= range_end:
            if until is not None and cursor > until:
                break
            if cursor >= first_day:
                starts = datetime.combine(
                    cursor,
                    time(
                        start_clock.hour,
                        start_clock.minute,
                        start_clock.second,
                        start_clock.microsecond,
                        tzinfo=self.starts_at.tzinfo,
                    ),
                )
                slots.append(TimeSlot(starts, starts + duration))
            cursor += timedelta(days=7)
        return slots
