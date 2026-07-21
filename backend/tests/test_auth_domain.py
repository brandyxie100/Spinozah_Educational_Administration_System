"""Domain unit tests for bcrypt password hashing and JWT claims."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from app.domain.identity.exceptions import InvalidCredentialsError
from app.domain.identity.tokens import AccessTokenClaims, TokenType
from app.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from app.infrastructure.security.jwt_token_service import JwtTokenService


def test_bcrypt_hash_password_then_verify_succeeds() -> None:
    """Hashed passwords verify with the same plain text."""
    hasher = BcryptPasswordHasher()
    hashed = hasher.hash("correct-horse-battery")

    assert hashed != "correct-horse-battery"
    assert hasher.verify("correct-horse-battery", hashed) is True


def test_bcrypt_verify_wrong_password_returns_false() -> None:
    """Wrong plain text must not verify against a bcrypt hash."""
    hasher = BcryptPasswordHasher()
    hashed = hasher.hash("correct-horse-battery")

    assert hasher.verify("wrong-password", hashed) is False


def test_jwt_create_and_decode_access_token_roundtrip() -> None:
    """Access JWT encodes user/tenant claims and decodes them back."""
    service = JwtTokenService(
        secret="unit-test-secret-at-least-32-chars!",
        access_expire_minutes=15,
        refresh_expire_days=7,
    )
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    claims = AccessTokenClaims(
        user_id=user_id,
        tenant_id=tenant_id,
        email="teacher@example.com",
        role="teacher",
    )

    token = service.create_access_token(claims)
    decoded = service.decode_access_token(token)

    assert decoded.user_id == user_id
    assert decoded.tenant_id == tenant_id
    assert decoded.email == "teacher@example.com"
    assert decoded.role == "teacher"
    assert decoded.token_type == TokenType.ACCESS


def test_jwt_decode_access_token_rejects_refresh_token() -> None:
    """Access decoder must reject tokens minted as refresh."""
    service = JwtTokenService(
        secret="unit-test-secret-at-least-32-chars!",
        access_expire_minutes=15,
        refresh_expire_days=7,
    )
    claims = AccessTokenClaims(
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        email="a@b.com",
        role="admin",
    )
    refresh = service.create_refresh_token(claims)

    with pytest.raises(InvalidCredentialsError):
        service.decode_access_token(refresh)


def test_jwt_decode_expired_access_token_raises() -> None:
    """Expired access tokens must fail closed."""
    service = JwtTokenService(
        secret="unit-test-secret-at-least-32-chars!",
        access_expire_minutes=15,
        refresh_expire_days=7,
    )
    claims = AccessTokenClaims(
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        email="a@b.com",
        role="admin",
    )
    past = datetime.now(UTC) - timedelta(hours=1)
    token = service.create_access_token(claims, now=past)

    with pytest.raises(InvalidCredentialsError):
        service.decode_access_token(token)
