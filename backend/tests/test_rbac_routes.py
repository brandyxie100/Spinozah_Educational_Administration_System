"""HTTP tests for RBAC role guards on protected routes."""

from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.infrastructure.security.jwt_token_service import JwtTokenService
from app.main import create_app
from fastapi.testclient import TestClient

SECRET = "rbac-unit-test-secret-at-least-32-chars!"


@pytest.fixture
def client() -> Iterator[TestClient]:
    """App client with a predictable JWT secret."""
    import os

    previous = os.environ.get("JWT_SECRET")
    os.environ["JWT_SECRET"] = SECRET
    # Settings are constructed per request; ensure env is set before create_app.
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
    if previous is None:
        os.environ.pop("JWT_SECRET", None)
    else:
        os.environ["JWT_SECRET"] = previous


def _access_header(role: Role) -> dict[str, str]:
    service = JwtTokenService(
        secret=SECRET,
        access_expire_minutes=15,
        refresh_expire_days=7,
    )
    token = service.create_access_token(
        AccessTokenClaims(
            user_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            email=f"{role.value}@example.com",
            role=role.value,
        ),
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [
        (Role.ADMIN, 200),
        (Role.FRONTDESK, 403),
        (Role.TEACHER, 403),
        (Role.PARENT, 403),
    ],
)
def test_admin_ping_per_role(
    client: TestClient,
    role: Role,
    expected_status: int,
) -> None:
    """Admin-only route: only admin succeeds; others get 403."""
    response = client.get("/api/v1/admin/ping", headers=_access_header(role))
    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json()["resource"] == "admin"
        assert response.json()["role"] == Role.ADMIN.value


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [
        (Role.ADMIN, 200),
        (Role.FRONTDESK, 200),
        (Role.TEACHER, 200),
        (Role.PARENT, 403),
    ],
)
def test_staff_ping_per_role(
    client: TestClient,
    role: Role,
    expected_status: int,
) -> None:
    """Staff route allows admin/frontdesk/teacher; parent is 403."""
    response = client.get("/api/v1/staff/ping", headers=_access_header(role))
    assert response.status_code == expected_status


@pytest.mark.parametrize("role", list(Role))
def test_me_allows_every_authenticated_role(client: TestClient, role: Role) -> None:
    """Any authenticated product role can hit /me."""
    response = client.get("/api/v1/me", headers=_access_header(role))
    assert response.status_code == 200
    assert response.json()["role"] == role.value


def test_protected_route_without_token_returns_401(client: TestClient) -> None:
    """Missing Bearer token yields 401, not 403."""
    response = client.get("/api/v1/admin/ping")
    assert response.status_code == 401
