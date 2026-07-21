"""Shared repository contracts for multi-tenant aggregates."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID


class TenantScopedRepository(ABC):
    """Contract: every query through this repository is bound to one tenant.

    Concrete infrastructure repositories MUST filter by ``tenant_id`` on every
    read and write. Cross-tenant access is a security defect, not a feature.
    """

    @property
    @abstractmethod
    def tenant_id(self) -> UUID:
        """Identifier of the tenant that owns visible rows."""
