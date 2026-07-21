"""Application service for creating schedules with conflict checks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from app.domain.scheduling.conflict_detection import (
    ConflictDetectionService,
    ScheduleConflict,
)
from app.domain.scheduling.display_status import (
    DisplayStatus,
    resolve_display_status,
)
from app.domain.scheduling.entities import (
    Schedule,
    Weekday,
    WeeklyRecurrence,
)
from app.infrastructure.persistence.schedule_repository import (
    SqlAlchemyScheduleRepository,
)
from app.infrastructure.persistence.student_repository import (
    SqlAlchemyStudentRepository,
)
from app.infrastructure.persistence.teacher_repository import (
    SqlAlchemyTeacherRepository,
)

# Horizon used when a weekly series has no until date.
_DEFAULT_RECURRENCE_WEEKS = 16


class ScheduleConflictError(Exception):
    """Raised when a proposed booking overlaps an existing resource."""

    def __init__(self, conflicts: list[ScheduleConflict]) -> None:
        """Attach conflict details for API mapping to HTTP 409."""
        self.conflicts = conflicts
        kinds = sorted({conflict.kind.value for conflict in conflicts})
        super().__init__(f"Schedule conflict: {', '.join(kinds)}")


class TeacherNotFoundForScheduleError(Exception):
    """Raised when the teacher id is missing in the tenant."""


@dataclass(frozen=True, slots=True)
class TeacherScheduleSlot:
    """Expanded occurrence for a teacher timetable view."""

    schedule_id: UUID
    student_id: UUID
    student_name: str | None
    classroom: str | None
    starts_at: datetime
    ends_at: datetime
    status: str
    display_status: DisplayStatus


class ScheduleService:
    """Create schedules and load teacher timetables."""

    def __init__(
        self,
        repository: SqlAlchemyScheduleRepository,
        conflict_detector: ConflictDetectionService | None = None,
        teacher_repository: SqlAlchemyTeacherRepository | None = None,
        student_repository: SqlAlchemyStudentRepository | None = None,
    ) -> None:
        """Bind repositories and optional detector."""
        self._repository = repository
        self._detector = conflict_detector or ConflictDetectionService()
        self._teacher_repository = teacher_repository
        self._student_repository = student_repository

    def _expansion_window(self, schedule: Schedule) -> tuple[date, date]:
        start = schedule.starts_at.date()
        if schedule.recurrence is None:
            return start, start
        if schedule.recurrence.until is not None:
            return start, schedule.recurrence.until
        return start, start + timedelta(weeks=_DEFAULT_RECURRENCE_WEEKS)

    async def create_schedule(
        self,
        *,
        teacher_id: UUID,
        student_id: UUID,
        starts_at: datetime,
        ends_at: datetime,
        classroom: str | None = None,
        is_recurring: bool = False,
        recurrence_until: date | None = None,
    ) -> Schedule:
        """Create a schedule or raise ``ScheduleConflictError`` on overlap."""
        recurrence: WeeklyRecurrence | None = None
        if is_recurring:
            recurrence = WeeklyRecurrence(
                weekday=Weekday(starts_at.isoweekday()),
                until=recurrence_until,
            )
        proposed = Schedule(
            tenant_id=self._repository.tenant_id,
            teacher_id=teacher_id,
            student_id=student_id,
            starts_at=starts_at,
            ends_at=ends_at,
            classroom=classroom,
            recurrence=recurrence,
        )
        range_start, range_end = self._expansion_window(proposed)
        existing = await self._repository.list_all()
        conflicts = self._detector.find_conflicts(
            proposed,
            existing,
            range_start=range_start,
            range_end=range_end,
        )
        if conflicts:
            raise ScheduleConflictError(conflicts)
        return await self._repository.add(proposed)

    async def get_teacher_schedule(
        self,
        teacher_id: UUID,
        *,
        range_start: date,
        range_end: date,
        now: datetime | None = None,
    ) -> list[TeacherScheduleSlot]:
        """Expand a teacher's bookings into display slots for a date range."""
        if range_end < range_start:
            raise ValueError("range_end must be on or after range_start")
        if self._teacher_repository is not None:
            teacher = await self._teacher_repository.get_by_id(teacher_id)
            if teacher is None:
                raise TeacherNotFoundForScheduleError(
                    f"Teacher not found: {teacher_id}",
                )

        clock = now or datetime.now(UTC)
        schedules = await self._repository.list_by_teacher_id(teacher_id)
        name_by_student: dict[UUID, str | None] = {}
        slots: list[TeacherScheduleSlot] = []

        for schedule in schedules:
            if schedule.student_id not in name_by_student:
                name_by_student[schedule.student_id] = await self._student_name(
                    schedule.student_id,
                )
            for occurrence in schedule.expand_occurrences(range_start, range_end):
                display = resolve_display_status(
                    occurrence,
                    schedule.status,
                    now=clock,
                )
                slots.append(
                    TeacherScheduleSlot(
                        schedule_id=schedule.id,
                        student_id=schedule.student_id,
                        student_name=name_by_student[schedule.student_id],
                        classroom=schedule.classroom,
                        starts_at=occurrence.starts_at,
                        ends_at=occurrence.ends_at,
                        status=schedule.status.value,
                        display_status=display,
                    ),
                )

        slots.sort(key=lambda item: item.starts_at)
        return slots

    async def _student_name(self, student_id: UUID) -> str | None:
        if self._student_repository is None:
            return None
        student = await self._student_repository.get_by_id(student_id)
        return student.full_name if student is not None else None
