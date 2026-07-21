"""ReportLab PDF renderer for semester invoices."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from app.domain.finance.entities import Invoice


class InvoicePdfGenerator:
    """Render an ``Invoice`` domain object to PDF bytes via ReportLab."""

    def render(self, invoice: Invoice, *, student_name: str) -> bytes:
        """Return a simple one-page PDF invoice document."""
        buffer = BytesIO()
        canvas = Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 25 * mm

        canvas.setFont("Helvetica-Bold", 16)
        canvas.drawString(20 * mm, y, "Spinozah AI Education — Invoice")
        y -= 12 * mm

        canvas.setFont("Helvetica", 11)
        canvas.drawString(20 * mm, y, f"Invoice ID: {invoice.id}")
        y -= 7 * mm
        canvas.drawString(20 * mm, y, f"Student: {student_name}")
        y -= 7 * mm
        canvas.drawString(20 * mm, y, f"Semester: {invoice.semester_label}")
        y -= 7 * mm
        canvas.drawString(20 * mm, y, f"Payment status: {invoice.status.value}")
        y -= 12 * mm

        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(20 * mm, y, "Line items")
        y -= 7 * mm
        canvas.setFont("Helvetica", 10)
        if not invoice.line_items:
            canvas.drawString(22 * mm, y, "(no line items)")
            y -= 7 * mm
        else:
            for item in invoice.line_items:
                canvas.drawString(
                    22 * mm,
                    y,
                    f"{item.description}: {item.amount:.2f}",
                )
                y -= 6 * mm

        y -= 8 * mm
        canvas.setFont("Helvetica", 11)
        canvas.drawString(20 * mm, y, f"Subtotal: {invoice.subtotal:.2f}")
        y -= 7 * mm
        canvas.drawString(20 * mm, y, f"Credit: {invoice.credit:.2f}")
        y -= 7 * mm
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(20 * mm, y, f"Final amount: {invoice.final_amount:.2f}")
        # Keep formula visible for ops/manual verification.
        y -= 7 * mm
        canvas.setFont("Helvetica", 9)
        canvas.drawString(20 * mm, y, "final_amount = subtotal - credit")

        canvas.showPage()
        canvas.save()
        return buffer.getvalue()
