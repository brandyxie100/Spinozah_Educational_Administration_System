"""Application service for creating schedules with conflict checks."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from uuid import UUID

from app.domain.scheduling.conflict_detection import (
    ConflictDetectionService,
    ScheduleConflict,
)
from app.domain.scheduling.entities import (
    Schedule,
    Weekday,
    WeeklyRecurrence,
)
from app.infrastructure.persistence.schedule_repository import (
    SqlAlchemyScheduleRepository,
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


class ScheduleService:
    """Create schedules after running domain conflict detection."""

    def __init__(
        self,
        repository: SqlAlchemyScheduleRepository,
        conflict_detector: ConflictDetectionService | None = None,
    ) -> None:
        """Bind repository and optional detector (defaults to domain service)."""
        self._repository = repository
        self._detector = conflict_detector or ConflictDetectionService()

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
