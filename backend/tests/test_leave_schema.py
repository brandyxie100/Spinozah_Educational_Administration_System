"""Schema tests for leave_requests and enrolment extension_days."""

from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.leave_models import LeaveRequestModel, LeaveStatusDB
from app.infrastructure.persistence.student_models import EnrolmentModel


def test_leave_requests_table_registered() -> None:
    assert "leave_requests" in Base.metadata.tables


def test_enrolment_has_extension_days_column() -> None:
    assert "extension_days" in EnrolmentModel.__table__.c
    assert EnrolmentModel.__table__.c.extension_days.nullable is False


def test_leave_status_enum_values() -> None:
    assert {status.value for status in LeaveStatusDB} == {
        "pending",
        "approved",
        "rejected",
    }


def test_leave_request_requires_enrolment() -> None:
    assert LeaveRequestModel.__table__.c.enrolment_id.nullable is False
