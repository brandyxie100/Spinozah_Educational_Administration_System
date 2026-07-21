"""Domain unit tests for RBAC role checks."""

from __future__ import annotations

import pytest
from app.domain.identity.exceptions import InsufficientPermissionsError
from app.domain.identity.rbac import assert_role_allowed
from app.domain.identity.roles import ALL_ROLES, Role


def test_all_roles_contains_four_product_roles() -> None:
    """Product roles are exactly admin, frontdesk, teacher, parent."""
    assert {role.value for role in ALL_ROLES} == {
        "admin",
        "frontdesk",
        "teacher",
        "parent",
    }


def test_assert_role_allowed_accepts_matching_role() -> None:
    """Matching role does not raise."""
    assert_role_allowed(Role.ADMIN.value, (Role.ADMIN, Role.TEACHER))


def test_assert_role_allowed_rejects_insufficient_role() -> None:
    """Non-allowed role raises InsufficientPermissionsError."""
    with pytest.raises(InsufficientPermissionsError):
        assert_role_allowed(Role.PARENT.value, (Role.ADMIN,))
