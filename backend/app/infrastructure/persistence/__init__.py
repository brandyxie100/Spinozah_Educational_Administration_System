"""Persistence adapters (SQLAlchemy models and session factory)."""

from app.infrastructure.persistence.analysis_models import (
    AnalysisKindDB,
    AnalysisRecordModel,
)
from app.infrastructure.persistence.analysis_repository import (
    SqlAlchemyAnalysisRepository,
)
from app.infrastructure.persistence.attendance_models import (
    AttendanceModel,
    AttendanceStatusDB,
)
from app.infrastructure.persistence.attendance_repository import (
    SqlAlchemyAttendanceRepository,
    SqlAlchemyEnrolmentRepository,
)
from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.invoice_models import (
    InvoiceModel,
    PaymentStatusDB,
)
from app.infrastructure.persistence.invoice_repository import (
    SqlAlchemyInvoiceRepository,
)
from app.infrastructure.persistence.leave_models import (
    LeaveKindDB,
    LeaveRequestModel,
    LeaveStatusDB,
)
from app.infrastructure.persistence.leave_repository import (
    SqlAlchemyLeaveRequestRepository,
)
from app.infrastructure.persistence.models import TenantModel, UserModel, UserRole
from app.infrastructure.persistence.parent_portal_models import (
    MagicLinkTokenModel,
    ParentStudentLinkModel,
)
from app.infrastructure.persistence.parent_portal_repository import (
    SqlAlchemyMagicLinkTokenRepository,
    SqlAlchemyParentStudentLinkRepository,
)
from app.infrastructure.persistence.schedule_models import (
    ScheduleModel,
    ScheduleStatusDB,
)
from app.infrastructure.persistence.schedule_repository import (
    SqlAlchemyScheduleRepository,
)
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
    "AnalysisKindDB",
    "AnalysisRecordModel",
    "AttendanceModel",
    "AttendanceStatusDB",
    "Base",
    "EnrolmentModel",
    "EnrolmentStatusDB",
    "InvoiceModel",
    "LeaveKindDB",
    "LeaveRequestModel",
    "LeaveStatusDB",
    "MagicLinkTokenModel",
    "ParentStudentLinkModel",
    "PaymentStatusDB",
    "ScheduleModel",
    "ScheduleStatusDB",
    "SqlAlchemyAnalysisRepository",
    "SqlAlchemyAttendanceRepository",
    "SqlAlchemyEnrolmentRepository",
    "SqlAlchemyInvoiceRepository",
    "SqlAlchemyLeaveRequestRepository",
    "SqlAlchemyMagicLinkTokenRepository",
    "SqlAlchemyParentStudentLinkRepository",
    "SqlAlchemyScheduleRepository",
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
