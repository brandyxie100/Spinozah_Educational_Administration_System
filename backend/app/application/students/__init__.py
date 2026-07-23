"""Students & teachers application services."""

from app.application.students.enrolment_service import (
    EnrolmentNotFoundError,
    EnrolmentService,
    EnrolmentStudentNotFoundError,
)
from app.application.students.student_service import (
    StudentEmailConflictError,
    StudentNotFoundError,
    StudentPage,
    StudentService,
)
from app.application.students.teacher_service import (
    TeacherEmailConflictError,
    TeacherNotFoundError,
    TeacherPage,
    TeacherService,
    TeacherUserLinkError,
)

__all__ = [
    "EnrolmentNotFoundError",
    "EnrolmentService",
    "EnrolmentStudentNotFoundError",
    "StudentEmailConflictError",
    "StudentNotFoundError",
    "StudentPage",
    "StudentService",
    "TeacherEmailConflictError",
    "TeacherNotFoundError",
    "TeacherPage",
    "TeacherService",
    "TeacherUserLinkError",
]
