"""Domain roles for RBAC (AIJOB-36)."""

from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    """Application roles enforced on protected API routes."""

    ADMIN = "admin"
    FRONTDESK = "frontdesk"
    TEACHER = "teacher"
    PARENT = "parent"


ALL_ROLES: frozenset[Role] = frozenset(Role)
