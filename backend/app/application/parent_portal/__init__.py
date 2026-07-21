"""Parent portal application services."""

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
    "LinkedStudentSummary",
    "MagicLinkRequestResult",
    "NotAParentError",
    "ParentNotFoundError",
    "ParentPortalService",
    "StudentNotFoundError",
]
