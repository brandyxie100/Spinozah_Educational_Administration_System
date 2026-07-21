"""Parent portal application services."""

from app.application.parent_portal.dashboard_models import (
    EnrolmentNotFoundError,
    ParentEnrolmentView,
    ParentInvoiceNotFoundError,
    ParentStudentNotLinkedError,
    StudentDashboardReport,
)
from app.application.parent_portal.magic_link_service import (
    CaptureMagicLinkMailer,
    LinkedStudentSummary,
    MagicLinkRequestResult,
    NotAParentError,
    ParentNotFoundError,
    ParentPortalService,
    StudentNotFoundError,
)

__all__ = [
    "CaptureMagicLinkMailer",
    "EnrolmentNotFoundError",
    "LinkedStudentSummary",
    "MagicLinkRequestResult",
    "NotAParentError",
    "ParentEnrolmentView",
    "ParentInvoiceNotFoundError",
    "ParentNotFoundError",
    "ParentPortalService",
    "ParentStudentNotLinkedError",
    "StudentDashboardReport",
    "StudentNotFoundError",
]
