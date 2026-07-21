"""Map attendance and enrolment domain entities to ORM rows."""

from __future__ import annotations

from app.domain.attendance.entities import AttendanceRecord, AttendanceStatus
from app.domain.students.entities import Enrolment, EnrolmentStatus
from app.infrastructure.persistence.attendance_models import (
    AttendanceModel,
    AttendanceStatusDB,
)
from app.infrastructure.persistence.student_models import (
    EnrolmentModel,
    EnrolmentStatusDB,
)


def attendance_to_model(record: AttendanceRecord) -> AttendanceModel:
    """Convert a domain attendance record into a persistence model."""
    return AttendanceModel(
        id=record.id,
        tenant_id=record.tenant_id,
        schedule_id=record.schedule_id,
        student_id=record.student_id,
        enrolment_id=record.enrolment_id,
        status=AttendanceStatusDB(record.status.value),
    )


def model_to_attendance(model: AttendanceModel) -> AttendanceRecord:
    """Convert a persistence row into a domain attendance record."""
    return AttendanceRecord(
        id=model.id,
        tenant_id=model.tenant_id,
        schedule_id=model.schedule_id,
        student_id=model.student_id,
        enrolment_id=model.enrolment_id,
        status=AttendanceStatus(model.status.value),
    )


def enrolment_to_model(enrolment: Enrolment) -> EnrolmentModel:
    """Convert a domain enrolment into a persistence model."""
    return EnrolmentModel(
        id=enrolment.id,
        tenant_id=enrolment.tenant_id,
        student_id=enrolment.student_id,
        total_lessons=enrolment.total_lessons,
        completed_lessons=enrolment.completed_lessons,
        extension_days=enrolment.extension_days,
        status=EnrolmentStatusDB(enrolment.status.value),
    )


def model_to_enrolment(model: EnrolmentModel) -> Enrolment:
    """Convert a persistence enrolment row into a domain entity."""
    return Enrolment(
        id=model.id,
        tenant_id=model.tenant_id,
        student_id=model.student_id,
        total_lessons=model.total_lessons,
        completed_lessons=model.completed_lessons,
        extension_days=model.extension_days,
        status=EnrolmentStatus(model.status.value),
    )


def apply_enrolment_to_model(model: EnrolmentModel, enrolment: Enrolment) -> None:
    """Copy mutable enrolment fields onto an existing ORM row."""
    model.total_lessons = enrolment.total_lessons
    model.completed_lessons = enrolment.completed_lessons
    model.extension_days = enrolment.extension_days
    model.status = EnrolmentStatusDB(enrolment.status.value)
