"""Domain service: detect teacher/student/classroom schedule overlaps."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from uuid import UUID

from app.domain.scheduling.entities import Schedule, ScheduleStatus, TimeSlot

# Statuses that no longer occupy the timetable.
_INACTIVE_STATUSES = frozenset(
    {
        ScheduleStatus.CANCELLED,
        ScheduleStatus.RESCHEDULED,
    },
)


class ConflictKind(StrEnum):
    """Resource that caused a timetable overlap."""

    TEACHER = "teacher"
    STUDENT = "student"
    CLASSROOM = "classroom"


@dataclass(frozen=True, slots=True)
class ScheduleConflict:
    """One overlapping pair of concrete time slots for a shared resource."""

    kind: ConflictKind
    existing_schedule_id: UUID
    proposed_slot: TimeSlot
    existing_slot: TimeSlot


def intervals_overlap(left: TimeSlot, right: TimeSlot) -> bool:
    """Return True when intervals share open time (adjacent edges do not overlap)."""
    return left.starts_at < right.ends_at and right.starts_at < left.ends_at


class ConflictDetectionService:
    """Pure domain service that finds timetable conflicts for a proposed booking."""

    def find_conflicts(
        self,
        proposed: Schedule,
        existing: Sequence[Schedule],
        *,
        range_start: date,
        range_end: date,
        exclude_schedule_id: UUID | None = None,
    ) -> list[ScheduleConflict]:
        """Compare proposed occurrences against active existing schedules.

        Args:
            proposed: Candidate booking (may be recurring).
            existing: Other schedules in the same tenant.
            range_start: Inclusive expansion window start.
            range_end: Inclusive expansion window end.
            exclude_schedule_id: Skip this id (e.g. when updating a schedule).

        Returns:
            All detected overlaps (teacher, student, and/or classroom).
        """
        if range_end < range_start:
            raise ValueError("range_end must be on or after range_start")

        proposed_slots = proposed.expand_occurrences(range_start, range_end)
        if not proposed_slots:
            return []

        conflicts: list[ScheduleConflict] = []
        for other in existing:
            if exclude_schedule_id is not None and other.id == exclude_schedule_id:
                continue
            if other.id == proposed.id:
                continue
            if other.status in _INACTIVE_STATUSES:
                continue

            other_slots = other.expand_occurrences(range_start, range_end)
            for proposed_slot in proposed_slots:
                for other_slot in other_slots:
                    if not intervals_overlap(proposed_slot, other_slot):
                        continue
                    conflicts.extend(
                        self._resource_conflicts(
                            proposed,
                            other,
                            proposed_slot,
                            other_slot,
                        ),
                    )
        return conflicts

    def _resource_conflicts(
        self,
        proposed: Schedule,
        other: Schedule,
        proposed_slot: TimeSlot,
        other_slot: TimeSlot,
    ) -> list[ScheduleConflict]:
        found: list[ScheduleConflict] = []
        if proposed.teacher_id == other.teacher_id:
            found.append(
                ScheduleConflict(
                    kind=ConflictKind.TEACHER,
                    existing_schedule_id=other.id,
                    proposed_slot=proposed_slot,
                    existing_slot=other_slot,
                ),
            )
        if proposed.student_id == other.student_id:
            found.append(
                ScheduleConflict(
                    kind=ConflictKind.STUDENT,
                    existing_schedule_id=other.id,
                    proposed_slot=proposed_slot,
                    existing_slot=other_slot,
                ),
            )
        # Classroom conflicts only when both bookings name the same room.
        if (
            proposed.classroom is not None
            and other.classroom is not None
            and proposed.classroom == other.classroom
        ):
            found.append(
                ScheduleConflict(
                    kind=ConflictKind.CLASSROOM,
                    existing_schedule_id=other.id,
                    proposed_slot=proposed_slot,
                    existing_slot=other_slot,
                ),
            )
        return found
