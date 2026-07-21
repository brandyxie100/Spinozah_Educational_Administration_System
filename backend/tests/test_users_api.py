"""Integration tests for admin user CRUD and tenant isolation."""

from __future__ import annotations

import os
import uuid
from collections.abc import AsyncIterator

import pytest
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.models import UserRole
from app.infrastructure.persistence.session import get_session
from app.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from app.infrastructure.security.jwt_token_service import JwtTokenService
from app.main import create_app
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from tests.factories import TenantFactory, UserFactory

SECRET = "user-crud-integration-secret-32chars!!"


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set; skipping user CRUD integration tests")

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
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    previous = os.environ.get("JWT_SECRET")
    os.environ["JWT_SECRET"] = SECRET
    app = create_app()

    async def _override_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = _override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        yield http
    app.dependency_overrides.clear()
    if previous is None:
        os.environ.pop("JWT_SECRET", None)
    else:
        os.environ["JWT_SECRET"] = previous


def _admin_headers(tenant_id: uuid.UUID) -> dict[str, str]:
    token = JwtTokenService(
        secret=SECRET,
        access_expire_minutes=15,
        refresh_expire_days=7,
    ).create_access_token(
        AccessTokenClaims(
            user_id=uuid.uuid4(),
            tenant_id=tenant_id,
            email="admin@example.com",
            role=Role.ADMIN.value,
        ),
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
@pytest.mark.tenant_isolation
@pytest.mark.asyncio
async def test_tenant_a_cannot_see_tenant_b_data(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """GET /users for tenant A must not include tenant B users."""
    tenant_a = TenantFactory.build(slug="tenant-a-users")
    tenant_b = TenantFactory.build(slug="tenant-b-users")
    user_a = UserFactory.build(
        tenant_id=tenant_a.id,
        email="a@example.com",
        role=UserRole.TEACHER,
        hashed_password=BcryptPasswordHasher().hash("password12"),
    )
    user_b = UserFactory.build(
        tenant_id=tenant_b.id,
        email="b@example.com",
        role=UserRole.TEACHER,
        hashed_password=BcryptPasswordHasher().hash("password12"),
    )
    db_session.add_all([tenant_a, tenant_b, user_a, user_b])
    await db_session.commit()

    response = await client.get(
        "/api/v1/users",
        headers=_admin_headers(tenant_a.id),
    )
    assert response.status_code == 200
    emails = {item["email"] for item in response.json()["items"]}
    assert "a@example.com" in emails
    assert "b@example.com" not in emails


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_can_create_update_and_deactivate_user(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Admin CRUD happy path against a live Postgres tenant."""
    tenant = TenantFactory.build(slug="crud-center")
    db_session.add(tenant)
    await db_session.commit()

    headers = _admin_headers(tenant.id)
    created = await client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "email": "new@example.com",
            "full_name": "New User",
            "password": "password12",
            "role": "teacher",
        },
    )
    assert created.status_code == 201
    user_id = created.json()["id"]

    listed = await client.get("/api/v1/users?page=1&page_size=20", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1

    updated = await client.patch(
        f"/api/v1/users/{user_id}",
        headers=headers,
        json={"full_name": "Updated Name"},
    )
    assert updated.status_code == 200
    assert updated.json()["full_name"] == "Updated Name"

    deactivated = await client.post(
        f"/api/v1/users/{user_id}/deactivate",
        headers=headers,
    )
    assert deactivated.status_code == 200
    assert deactivated.json()["is_active"] is False
