"""Integration tests for teacher CRUD and tenant isolation."""

from __future__ import annotations

import os
import uuid
from collections.abc import AsyncIterator

import pytest
from app.domain.identity.roles import Role
from app.domain.identity.tokens import AccessTokenClaims
from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.session import get_session
from app.infrastructure.security.jwt_token_service import JwtTokenService
from app.main import create_app
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from tests.factories import TeacherFactory, TenantFactory, UserFactory

SECRET = "teacher-crud-integration-secret-32ch!"


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set; skipping teacher CRUD integration tests")

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


def _staff_headers(tenant_id: uuid.UUID, role: Role = Role.FRONTDESK) -> dict[str, str]:
    token = JwtTokenService(
        secret=SECRET,
        access_expire_minutes=15,
        refresh_expire_days=7,
    ).create_access_token(
        AccessTokenClaims(
            user_id=uuid.uuid4(),
            tenant_id=tenant_id,
            email=f"{role.value}@example.com",
            role=role.value,
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
    """GET /teachers for tenant A must not include tenant B teachers."""
    tenant_a = TenantFactory.build(slug="teachers-tenant-a")
    tenant_b = TenantFactory.build(slug="teachers-tenant-b")
    teacher_a = TeacherFactory.build(
        tenant_id=tenant_a.id,
        email="a-teacher@example.com",
    )
    teacher_b = TeacherFactory.build(
        tenant_id=tenant_b.id,
        email="b-teacher@example.com",
    )
    db_session.add_all([tenant_a, tenant_b, teacher_a, teacher_b])
    await db_session.commit()

    response = await client.get(
        "/api/v1/teachers",
        headers=_staff_headers(tenant_a.id),
    )
    assert response.status_code == 200
    emails = {item["email"] for item in response.json()["items"]}
    assert "a-teacher@example.com" in emails
    assert "b-teacher@example.com" not in emails


@pytest.mark.integration
@pytest.mark.asyncio
async def test_teacher_crud_flow_with_optional_user_link(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """POST/GET/PUT/DELETE teachers against Postgres, including user_id."""
    tenant = TenantFactory.build(slug="teachers-crud")
    user = UserFactory.build(tenant_id=tenant.id, email="teach-login@example.com")
    db_session.add_all([tenant, user])
    await db_session.commit()
    headers = _staff_headers(tenant.id, role=Role.ADMIN)

    created = await client.post(
        "/api/v1/teachers",
        headers=headers,
        json={
            "full_name": "Jamie Instructor",
            "email": "jamie-t@example.com",
            "user_id": str(user.id),
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["user_id"] == str(user.id)
    teacher_id = body["id"]

    listed = await client.get("/api/v1/teachers?page=1&page_size=20", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1

    fetched = await client.get(f"/api/v1/teachers/{teacher_id}", headers=headers)
    assert fetched.status_code == 200

    updated = await client.put(
        f"/api/v1/teachers/{teacher_id}",
        headers=headers,
        json={
            "full_name": "Jamie Updated",
            "email": "jamie-t@example.com",
            "is_active": False,
            "user_id": str(user.id),
        },
    )
    assert updated.status_code == 200
    assert updated.json()["is_active"] is False

    deleted = await client.delete(f"/api/v1/teachers/{teacher_id}", headers=headers)
    assert deleted.status_code == 204
