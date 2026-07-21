"""Schema tests for teachers table."""

from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.teacher_models import TeacherModel


def test_teachers_table_registered_on_metadata() -> None:
    """Teachers table is present on declarative metadata."""
    assert "teachers" in Base.metadata.tables


def test_teacher_model_uses_uuid_primary_key() -> None:
    """Teachers table uses a UUID primary key."""
    assert str(TeacherModel.__table__.c.id.type) == "UUID"


def test_teacher_requires_tenant_id() -> None:
    """Multi-tenant column is required."""
    assert TeacherModel.__table__.c.tenant_id.nullable is False


def test_teacher_user_id_is_optional() -> None:
    """user_id may be null when teacher has no login account."""
    assert TeacherModel.__table__.c.user_id.nullable is True
