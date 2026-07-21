"""Schema tests for schedules table."""

from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.schedule_models import (
    ScheduleModel,
    ScheduleStatusDB,
)


def test_schedules_table_registered_on_metadata() -> None:
    """Schedules table is present on declarative metadata."""
    assert "schedules" in Base.metadata.tables


def test_schedule_model_uses_uuid_primary_key() -> None:
    """Schedules table uses a UUID primary key."""
    assert str(ScheduleModel.__table__.c.id.type) == "UUID"


def test_schedule_requires_tenant_teacher_student() -> None:
    """Core foreign keys are required."""
    columns = ScheduleModel.__table__.c
    assert columns.tenant_id.nullable is False
    assert columns.teacher_id.nullable is False
    assert columns.student_id.nullable is False


def test_schedule_status_enum_values() -> None:
    """Persisted status enum matches domain lifecycle."""
    assert {status.value for status in ScheduleStatusDB} == {
        "not_started",
        "in_progress",
        "completed",
        "cancelled",
        "rescheduled",
    }


def test_schedule_supports_weekly_recurrence_columns() -> None:
    """Weekly recurrence fields exist on the table."""
    columns = ScheduleModel.__table__.c
    assert "is_recurring" in columns
    assert "recurrence_weekday" in columns
    assert "recurrence_until" in columns
    assert columns.recurrence_weekday.nullable is True
    assert columns.recurrence_until.nullable is True
