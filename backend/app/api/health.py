"""Health and readiness HTTP endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Payload returned by the liveness probe."""

    status: str = Field(description="Service health status")
    service: str = Field(description="Logical service name")


class ReadyResponse(BaseModel):
    """Payload returned by the readiness probe."""

    status: str = Field(description="Service readiness status")


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return liveness status for load balancers and CI smoke checks."""
    return HealthResponse(status="ok", service="spinozah-backend")


@router.get("/ready", response_model=ReadyResponse)
def get_ready() -> ReadyResponse:
    """Return readiness status (expanded when DB deps are added)."""
    return ReadyResponse(status="ready")
