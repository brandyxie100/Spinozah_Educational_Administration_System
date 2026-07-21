"""Schema tests for attendance_records table."""

from app.infrastructure.persistence.attendance_models import (
    AttendanceModel,
    AttendanceStatusDB,
)
from app.infrastructure.persistence.base import Base


def test_attendance_table_registered_on_metadata() -> None:
    """Attendance table is present on declarative metadata."""
    assert "attendance_records" in Base.metadata.tables


def test_attendance_status_enum_values() -> None:
    """Persisted status enum matches domain lifecycle."""
    assert {status.value for status in AttendanceStatusDB} == {
        "pending_confirmation",
        "present",
        "absent",
    }


def test_attendance_requires_schedule_and_enrolment() -> None:
    """Core foreign keys are required."""
    columns = AttendanceModel.__table__.c
    assert columns.schedule_id.nullable is False
    assert columns.enrolment_id.nullable is False
    assert columns.student_id.nullable is False
