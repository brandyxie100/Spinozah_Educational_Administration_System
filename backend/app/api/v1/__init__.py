"""API v1 routers."""

from app.api.v1.attendance import router as attendance_router
from app.api.v1.auth import router as auth_router
from app.api.v1.rbac_routes import router as rbac_router
from app.api.v1.schedules import router as schedules_router
from app.api.v1.students import router as students_router
from app.api.v1.teachers import router as teachers_router
from app.api.v1.users import router as users_router

__all__ = [
    "attendance_router",
    "auth_router",
    "rbac_router",
    "schedules_router",
    "students_router",
    "teachers_router",
    "users_router",
]
