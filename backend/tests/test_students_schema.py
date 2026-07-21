"""Schema tests for students and enrolments tables."""

from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.student_models import (
    EnrolmentModel,
    EnrolmentStatusDB,
    StudentModel,
)


def test_students_and_enrolments_tables_registered_on_metadata() -> None:
    """Student schema tables are present on declarative metadata."""
    table_names = set(Base.metadata.tables.keys())
    assert "students" in table_names
    assert "enrolments" in table_names


def test_student_and_enrolment_models_use_uuid_primary_keys() -> None:
    """Both tables use UUID primary keys."""
    assert str(StudentModel.__table__.c.id.type) == "UUID"
    assert str(EnrolmentModel.__table__.c.id.type) == "UUID"


def test_student_and_enrolment_require_tenant_id() -> None:
    """Multi-tenant columns are required on both tables."""
    assert StudentModel.__table__.c.tenant_id.nullable is False
    assert EnrolmentModel.__table__.c.tenant_id.nullable is False


def test_enrolment_tracks_total_and_completed_lessons() -> None:
    """Enrolment stores lesson balance columns."""
    columns = EnrolmentModel.__table__.c
    assert "total_lessons" in columns
    assert "completed_lessons" in columns
    assert columns.total_lessons.nullable is False
    assert columns.completed_lessons.nullable is False


def test_enrolment_status_enum_values() -> None:
    """Persisted status enum matches domain lifecycle."""
    assert {status.value for status in EnrolmentStatusDB} == {
        "active",
        "completed",
        "cancelled",
    }
