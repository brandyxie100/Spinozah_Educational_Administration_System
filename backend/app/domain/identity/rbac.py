"""Pure RBAC helpers used by API dependencies."""

from __future__ import annotations

from collections.abc import Iterable

from app.domain.identity.exceptions import InsufficientPermissionsError
from app.domain.identity.roles import Role


def assert_role_allowed(role: str, allowed: Iterable[Role | str]) -> None:
    """Raise when ``role`` is not in the allowed set.

    Args:
        role: Role claim from the access JWT.
        allowed: Roles permitted for the route.

    Raises:
        InsufficientPermissionsError: When the role is not allowed.
    """
    allowed_values = {
        item.value if isinstance(item, Role) else str(item) for item in allowed
    }
    if role not in allowed_values:
        raise InsufficientPermissionsError(
            f"Role '{role}' is not permitted for this resource",
        )
