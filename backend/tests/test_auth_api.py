"""Integration tests for JWT login and refresh cookie flow."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.models import UserModel, UserRole
from app.infrastructure.persistence.session import get_session
from app.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from app.main import create_app
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from tests.factories import TenantFactory, UserFactory

REFRESH_COOKIE = "refresh_token"


@pytest.fixture
async def auth_db_session() -> AsyncIterator[AsyncSession]:
    """Yield a Postgres session seeded for auth tests; skip without DATABASE_URL."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set; skipping auth integration tests")

    engine = create_async_engine(database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()

    async with engine.begin() as connection:
        await connection.execute(text("TRUNCATE TABLE tenants CASCADE"))
    await engine.dispose()


@pytest.fixture
async def auth_client(auth_db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """Async HTTP client with DB session override for auth routes."""
    app = create_app()

    async def _override_session() -> AsyncIterator[AsyncSession]:
        yield auth_db_session

    app.dependency_overrides[get_session] = _override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_returns_access_jwt_and_sets_httponly_refresh_cookie(
    auth_client: AsyncClient,
    auth_db_session: AsyncSession,
) -> None:
    """POST /api/v1/auth/login returns access JWT and httpOnly refresh cookie."""
    plain_password = "Str0ng-Pass!"
    tenant = TenantFactory.build(slug="acme-tutoring")
    user = UserFactory.build(
        tenant_id=tenant.id,
        email="admin@acme.example",
        role=UserRole.ADMIN,
        hashed_password=BcryptPasswordHasher().hash(plain_password),
    )
    auth_db_session.add_all([tenant, user])
    await auth_db_session.commit()

    response = await auth_client.post(
        "/api/v1/auth/login",
        json={
            "tenant_slug": "acme-tutoring",
            "email": "admin@acme.example",
            "password": plain_password,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "access_token" in payload
    assert payload["token_type"] == "bearer"
    assert payload["user"]["email"] == "admin@acme.example"
    assert payload["user"]["role"] == "admin"

    assert REFRESH_COOKIE in response.cookies
    set_cookie = response.headers.get("set-cookie", "")
    assert "httponly" in set_cookie.lower()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_rejects_invalid_password(
    auth_client: AsyncClient,
    auth_db_session: AsyncSession,
) -> None:
    """Wrong password returns 401 without setting a refresh cookie."""
    tenant = TenantFactory.build(slug="beta-center")
    user = UserFactory.build(
        tenant_id=tenant.id,
        email="teacher@beta.example",
        hashed_password=BcryptPasswordHasher().hash("real-password"),
    )
    auth_db_session.add_all([tenant, user])
    await auth_db_session.commit()

    response = await auth_client.post(
        "/api/v1/auth/login",
        json={
            "tenant_slug": "beta-center",
            "email": "teacher@beta.example",
            "password": "not-the-password",
        },
    )

    assert response.status_code == 401
    assert REFRESH_COOKIE not in response.cookies


@pytest.mark.integration
@pytest.mark.asyncio
async def test_refresh_returns_new_access_token_from_httponly_cookie(
    auth_client: AsyncClient,
    auth_db_session: AsyncSession,
) -> None:
    """POST /api/v1/auth/refresh mints a new access JWT from the refresh cookie."""
    plain_password = "Refresh-Me-123"
    tenant = TenantFactory.build(slug="gamma-edu")
    user = UserFactory.build(
        tenant_id=tenant.id,
        email="front@gamma.example",
        role=UserRole.FRONTDESK,
        hashed_password=BcryptPasswordHasher().hash(plain_password),
    )
    auth_db_session.add_all([tenant, user])
    await auth_db_session.commit()

    login = await auth_client.post(
        "/api/v1/auth/login",
        json={
            "tenant_slug": "gamma-edu",
            "email": "front@gamma.example",
            "password": plain_password,
        },
    )
    assert login.status_code == 200
    first_access = login.json()["access_token"]

    refresh = await auth_client.post("/api/v1/auth/refresh")
    assert refresh.status_code == 200
    second_access = refresh.json()["access_token"]
    assert second_access
    assert second_access != first_access


@pytest.mark.integration
@pytest.mark.asyncio
async def test_logout_clears_refresh_cookie(
    auth_client: AsyncClient,
    auth_db_session: AsyncSession,
) -> None:
    """POST /api/v1/auth/logout clears the httpOnly refresh cookie."""
    plain_password = "Logout-Pass-9"
    tenant = TenantFactory.build(slug="delta-school")
    user = UserFactory.build(
        tenant_id=tenant.id,
        email="parent@delta.example",
        role=UserRole.PARENT,
        hashed_password=BcryptPasswordHasher().hash(plain_password),
    )
    auth_db_session.add_all([tenant, user])
    await auth_db_session.commit()

    await auth_client.post(
        "/api/v1/auth/login",
        json={
            "tenant_slug": "delta-school",
            "email": "parent@delta.example",
            "password": plain_password,
        },
    )
    logout = await auth_client.post("/api/v1/auth/logout")
    assert logout.status_code == 204

    refreshed = await auth_client.post("/api/v1/auth/refresh")
    assert refreshed.status_code == 401


@pytest.mark.integration
@pytest.mark.asyncio
async def test_seeded_user_password_is_bcrypt_hashed_not_plaintext(
    auth_db_session: AsyncSession,
) -> None:
    """Persisted passwords must be bcrypt digests, never plaintext."""
    hasher = BcryptPasswordHasher()
    tenant = TenantFactory.build()
    user = UserFactory.build(
        tenant_id=tenant.id,
        hashed_password=hasher.hash("never-store-plain"),
    )
    auth_db_session.add_all([tenant, user])
    await auth_db_session.commit()

    loaded = await auth_db_session.scalar(
        select(UserModel).where(UserModel.id == user.id),
    )
    assert loaded is not None
    assert loaded.hashed_password != "never-store-plain"
    assert loaded.hashed_password.startswith("$2")
