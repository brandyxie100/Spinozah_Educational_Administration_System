"""Map between Schedule domain entities and ORM rows."""

from __future__ import annotations

from app.domain.scheduling.entities import (
    Schedule,
    ScheduleStatus,
    Weekday,
    WeeklyRecurrence,
)
from app.infrastructure.persistence.schedule_models import (
    ScheduleModel,
    ScheduleStatusDB,
)


def schedule_to_model(schedule: Schedule) -> ScheduleModel:
    """Convert a domain Schedule into a persistence model."""
    recurrence = schedule.recurrence
    return ScheduleModel(
        id=schedule.id,
        tenant_id=schedule.tenant_id,
        teacher_id=schedule.teacher_id,
        student_id=schedule.student_id,
        classroom=schedule.classroom,
        starts_at=schedule.starts_at,
        ends_at=schedule.ends_at,
        status=ScheduleStatusDB(schedule.status.value),
        is_recurring=recurrence is not None,
        recurrence_weekday=int(recurrence.weekday) if recurrence else None,
        recurrence_until=recurrence.until if recurrence else None,
    )


def model_to_schedule(model: ScheduleModel) -> Schedule:
    """Convert a persistence row into a domain Schedule."""
    recurrence: WeeklyRecurrence | None = None
    if model.is_recurring and model.recurrence_weekday is not None:
        recurrence = WeeklyRecurrence(
            weekday=Weekday(model.recurrence_weekday),
            until=model.recurrence_until,
        )
    return Schedule(
        id=model.id,
        tenant_id=model.tenant_id,
        teacher_id=model.teacher_id,
        student_id=model.student_id,
        classroom=model.classroom,
        starts_at=model.starts_at,
        ends_at=model.ends_at,
        status=ScheduleStatus(model.status.value),
        recurrence=recurrence,
    )
