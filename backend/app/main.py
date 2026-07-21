"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.v1.attendance import router as attendance_router
from app.api.v1.auth import router as auth_router
from app.api.v1.invoices import router as invoices_router
from app.api.v1.rbac_routes import router as rbac_router
from app.api.v1.schedules import router as schedules_router
from app.api.v1.students import router as students_router
from app.api.v1.teachers import router as teachers_router
from app.api.v1.users import router as users_router
from app.core.settings import get_settings


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    origins = [
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ]
    if origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    application.include_router(health_router)
    application.include_router(auth_router)
    application.include_router(rbac_router)
    application.include_router(users_router)
    application.include_router(students_router)
    application.include_router(teachers_router)
    application.include_router(schedules_router)
    application.include_router(attendance_router)
    application.include_router(invoices_router)
    return application



app = create_app()
