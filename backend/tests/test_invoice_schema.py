"""Schema tests for invoices table registration."""

from app.infrastructure.persistence.base import Base
from app.infrastructure.persistence.invoice_models import InvoiceModel, PaymentStatusDB


def test_invoices_table_registered() -> None:
    assert "invoices" in Base.metadata.tables


def test_invoice_has_final_amount_column() -> None:
    assert "final_amount" in InvoiceModel.__table__.c
    assert InvoiceModel.__table__.c.final_amount.nullable is False


def test_payment_status_enum_values() -> None:
    assert {status.value for status in PaymentStatusDB} == {
        "unpaid",
        "partial",
        "paid",
        "void",
    }


def test_invoice_semester_unique_constraint() -> None:
    names = {constraint.name for constraint in InvoiceModel.__table__.constraints}
    assert "uq_invoices_tenant_student_semester" in names
