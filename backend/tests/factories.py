"""factory_boy builders for persistence models — never hardcode entities in tests."""

from __future__ import annotations

import uuid

import factory
from app.infrastructure.persistence.models import TenantModel, UserModel, UserRole
from app.infrastructure.persistence.student_models import StudentModel
from app.infrastructure.persistence.teacher_models import TeacherModel


class TenantFactory(factory.Factory):

    """Build a TenantModel with unique slug for multi-tenant tests."""

    class Meta:
        model = TenantModel

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Tenant {n}")
    slug = factory.LazyFunction(lambda: f"tenant-{uuid.uuid4().hex[:12]}")


class UserFactory(factory.Factory):
    """Build a UserModel; caller must set tenant_id before persistence."""

    class Meta:
        model = UserModel

    id = factory.LazyFunction(uuid.uuid4)
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    full_name = factory.Sequence(lambda n: f"User {n}")
    hashed_password = "hashed-password-placeholder"
    role = UserRole.TEACHER
    is_active = True


class StudentFactory(factory.Factory):
    """Build a StudentModel; caller must set tenant_id before persistence."""

    class Meta:
        model = StudentModel

    id = factory.LazyFunction(uuid.uuid4)
    full_name = factory.Sequence(lambda n: f"Student {n}")
    email = factory.Sequence(lambda n: f"student{n}@example.com")
    is_active = True


class TeacherFactory(factory.Factory):
    """Build a TeacherModel; caller must set tenant_id before persistence."""

    class Meta:
        model = TeacherModel

    id = factory.LazyFunction(uuid.uuid4)
    full_name = factory.Sequence(lambda n: f"Teacher {n}")
    email = factory.Sequence(lambda n: f"teacher{n}@example.com")
    user_id = None
    is_active = True
