"""Persistence adapters (SQLAlchemy models and session factory)."""

from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.models import TenantModel, UserModel, UserRole
from app.infrastructure.persistence.session import (
    create_engine,
    create_session_factory,
    get_session,
)
from app.infrastructure.persistence.student_models import (
    EnrolmentModel,
    EnrolmentStatusDB,
    StudentModel,
)
from app.infrastructure.persistence.student_repository import (
    SqlAlchemyStudentRepository,
)
from app.infrastructure.persistence.teacher_models import TeacherModel
from app.infrastructure.persistence.teacher_repository import (
    SqlAlchemyTeacherRepository,
)
from app.infrastructure.persistence.tenant_scoped import (
    SqlAlchemyTenantScopedRepository,
)
from app.infrastructure.persistence.user_repository import SqlAlchemyUserRepository

__all__ = [
    "Base",
    "EnrolmentModel",
    "EnrolmentStatusDB",
    "SqlAlchemyStudentRepository",
    "SqlAlchemyTeacherRepository",
    "SqlAlchemyTenantScopedRepository",
    "SqlAlchemyUserRepository",
    "StudentModel",
    "TeacherModel",
    "TenantModel",
    "UserModel",
    "UserRole",
    "create_engine",
    "create_session_factory",
    "get_session",
]
