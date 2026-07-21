"""Integration tests for student CRUD and tenant isolation."""

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
from tests.factories import StudentFactory, TenantFactory

SECRET = "student-crud-integration-secret-32ch!"


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set; skipping student CRUD integration tests")

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
    """GET /students for tenant A must not include tenant B students."""
    tenant_a = TenantFactory.build(slug="students-tenant-a")
    tenant_b = TenantFactory.build(slug="students-tenant-b")
    student_a = StudentFactory.build(
        tenant_id=tenant_a.id,
        email="a-student@example.com",
    )
    student_b = StudentFactory.build(
        tenant_id=tenant_b.id,
        email="b-student@example.com",
    )
    db_session.add_all([tenant_a, tenant_b, student_a, student_b])
    await db_session.commit()

    response = await client.get(
        "/api/v1/students",
        headers=_staff_headers(tenant_a.id),
    )
    assert response.status_code == 200
    emails = {item["email"] for item in response.json()["items"]}
    assert "a-student@example.com" in emails
    assert "b-student@example.com" not in emails


@pytest.mark.integration
@pytest.mark.asyncio
async def test_student_crud_flow_on_live_db(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """POST/GET/PUT/DELETE students against Postgres."""
    tenant = TenantFactory.build(slug="students-crud")
    db_session.add(tenant)
    await db_session.commit()
    headers = _staff_headers(tenant.id, role=Role.ADMIN)

    created = await client.post(
        "/api/v1/students",
        headers=headers,
        json={"full_name": "Jamie Learner", "email": "jamie@example.com"},
    )
    assert created.status_code == 201
    student_id = created.json()["id"]

    listed = await client.get("/api/v1/students?page=1&page_size=20", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1

    fetched = await client.get(f"/api/v1/students/{student_id}", headers=headers)
    assert fetched.status_code == 200

    updated = await client.put(
        f"/api/v1/students/{student_id}",
        headers=headers,
        json={
            "full_name": "Jamie Updated",
            "email": "jamie@example.com",
            "is_active": False,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["is_active"] is False

    deleted = await client.delete(f"/api/v1/students/{student_id}", headers=headers)
    assert deleted.status_code == 204
