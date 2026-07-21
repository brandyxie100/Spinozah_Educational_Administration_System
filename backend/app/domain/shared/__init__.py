"""Shared domain primitives used across bounded contexts."""

from app.domain.shared.repositories import TenantScopedRepository

DOMAIN_LAYER_MARKER = "domain"
"""Marker confirming this module lives in the domain layer."""

__all__ = ["DOMAIN_LAYER_MARKER", "TenantScopedRepository"]
