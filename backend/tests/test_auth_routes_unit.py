"""Unit tests for auth HTTP routes with dependency overrides (no database)."""

from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.v1.auth import get_auth_service
from app.application.identity.auth_service import (
    AuthApplicationService,
    AuthenticatedUser,
    AuthTokens,
)
from app.domain.identity.exceptions import InvalidCredentialsError
from app.main import create_app


class _FakeAuthService:
    """Minimal stand-in for AuthApplicationService in route tests."""

    async def login(
        self,
        *,
        tenant_slug: str,
        email: str,
        password: str,
    ) -> AuthTokens:
        if password != "ok":
            raise InvalidCredentialsError("Invalid email or password")
        user = AuthenticatedUser(
            id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            email=email,
            full_name="Test User",
            role="admin",
        )
        return AuthTokens(
            access_token="access.jwt",
            refresh_token="refresh.jwt",
            user=user,
        )

    async def refresh(self, refresh_token: str) -> AuthTokens:
        if refresh_token != "refresh.jwt":
            raise InvalidCredentialsError("Invalid refresh token")
        user = AuthenticatedUser(
            id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            email="admin@acme.example",
            full_name="Test User",
            role="admin",
        )
        return AuthTokens(
            access_token="access.jwt.new",
            refresh_token="refresh.jwt.rotated",
            user=user,
        )


@pytest.fixture
def client() -> Iterator[TestClient]:
    """TestClient with auth service overridden by a fake."""
    app = create_app()

    def _override() -> AuthApplicationService:
        return _FakeAuthService()  # type: ignore[return-value]

    app.dependency_overrides[get_auth_service] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_login_route_returns_access_token_and_httponly_cookie(
    client: TestClient,
) -> None:
    """Login route maps service success to JSON + Set-Cookie."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "tenant_slug": "acme",
            "email": "admin@acme.example",
            "password": "ok",
        },
    )
    assert response.status_code == 200
    assert response.json()["access_token"] == "access.jwt"
    assert "refresh_token" in response.cookies
    assert "httponly" in response.headers.get("set-cookie", "").lower()


def test_login_route_returns_401_on_invalid_credentials(client: TestClient) -> None:
    """Login route maps InvalidCredentialsError to HTTP 401."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "tenant_slug": "acme",
            "email": "admin@acme.example",
            "password": "nope",
        },
    )
    assert response.status_code == 401


def test_refresh_route_reads_cookie(client: TestClient) -> None:
    """Refresh route uses the httpOnly cookie value."""
    client.cookies.set("refresh_token", "refresh.jwt", path="/api/v1/auth")
    response = client.post("/api/v1/auth/refresh")
    assert response.status_code == 200
    assert response.json()["access_token"] == "access.jwt.new"


def test_logout_route_clears_cookie(client: TestClient) -> None:
    """Logout clears the refresh cookie."""
    client.cookies.set("refresh_token", "refresh.jwt", path="/api/v1/auth")
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 204
