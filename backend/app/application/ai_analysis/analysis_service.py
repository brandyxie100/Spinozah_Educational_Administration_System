"""Application service for persisting exam/essay analyses."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.domain.ai_analysis.entities import AnalysisKind, AnalysisRecord
from app.infrastructure.persistence.analysis_repository import (
    SqlAlchemyAnalysisRepository,
)
from app.infrastructure.persistence.student_repository import (
    SqlAlchemyStudentRepository,
)


class AnalysisNotFoundError(Exception):
    """Raised when a tenant-scoped analysis id does not exist."""


class AnalysisStudentNotFoundError(Exception):
    """Raised when create references an unknown student in the tenant."""


def _string_field(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def derive_labels(
    kind: AnalysisKind,
    payload: dict[str, Any],
) -> tuple[str | None, str | None]:
    """Extract display labels from a camelCase analysis payload."""
    student_name = _string_field(payload, "studentName")
    if kind is AnalysisKind.EXAM:
        title = _string_field(payload, "subject")
    else:
        title = _string_field(payload, "title")
    return student_name, title


class AnalysisService:
    """Create, list, and fetch analysis records for one tenant."""

    def __init__(
        self,
        analysis_repository: SqlAlchemyAnalysisRepository,
        student_repository: SqlAlchemyStudentRepository,
    ) -> None:
        """Bind tenant-scoped analysis and student repositories."""
        self._analyses = analysis_repository
        self._students = student_repository

    async def create_analysis(
        self,
        *,
        kind: AnalysisKind,
        payload: dict[str, Any],
        student_id: UUID | None = None,
    ) -> AnalysisRecord:
        """Persist an analysis report; optionally attach a student."""
        if student_id is not None:
            student = await self._students.get_by_id(student_id)
            if student is None:
                raise AnalysisStudentNotFoundError(
                    f"Student not found: {student_id}",
                )
        student_name, title = derive_labels(kind, payload)
        record = AnalysisRecord(
            tenant_id=self._students.tenant_id,
            kind=kind,
            payload=payload,
            student_id=student_id,
            student_name=student_name,
            title=title,
        )
        return await self._analyses.add(record)

    async def list_analyses(
        self,
        *,
        kind: AnalysisKind | None = None,
        student_id: UUID | None = None,
    ) -> list[AnalysisRecord]:
        """List analyses with optional kind/student filters."""
        return await self._analyses.list_all(kind=kind, student_id=student_id)

    async def get_analysis(self, analysis_id: UUID) -> AnalysisRecord:
        """Load one analysis or raise if missing in this tenant."""
        record = await self._analyses.get_by_id(analysis_id)
        if record is None:
            raise AnalysisNotFoundError(f"Analysis not found: {analysis_id}")
        return record
