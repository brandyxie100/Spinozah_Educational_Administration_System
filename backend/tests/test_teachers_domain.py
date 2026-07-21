"""Domain unit tests for Teacher."""

from __future__ import annotations

import uuid

import pytest
from app.domain.students import Teacher


def test_teacher_requires_non_empty_full_name() -> None:
    """Teacher full_name cannot be blank."""
    with pytest.raises(ValueError, match="full_name"):
        Teacher(tenant_id=uuid.uuid4(), full_name="   ")


def test_teacher_link_and_unlink_user() -> None:
    """Optional user account can be linked and cleared."""
    teacher = Teacher(tenant_id=uuid.uuid4(), full_name="Sam Teacher")
    user_id = uuid.uuid4()
    teacher.link_user(user_id)
    assert teacher.user_id == user_id
    teacher.unlink_user()
    assert teacher.user_id is None


def test_teacher_deactivate_sets_inactive() -> None:
    """deactivate() flips is_active to False."""
    teacher = Teacher(tenant_id=uuid.uuid4(), full_name="Sam Teacher")
    teacher.deactivate()
    assert teacher.is_active is False
