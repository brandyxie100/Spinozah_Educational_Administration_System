"""Unit tests for AnalysisService with in-memory repository doubles."""

from __future__ import annotations

import uuid
from typing import Any

import pytest
from app.application.ai_analysis.analysis_service import (
    AnalysisNotFoundError,
    AnalysisService,
    AnalysisStudentNotFoundError,
    derive_labels,
)
from app.domain.ai_analysis.entities import AnalysisKind, AnalysisRecord
from app.infrastructure.persistence.student_models import StudentModel


class _MemoryStudentRepo:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self.tenant_id = tenant_id
        self._rows: dict[uuid.UUID, StudentModel] = {}

    async def get_by_id(self, student_id: uuid.UUID) -> StudentModel | None:
        return self._rows.get(student_id)

    def seed(self, student: StudentModel) -> None:
        self._rows[student.id] = student


class _MemoryAnalysisRepo:
    def __init__(self, tenant_id: uuid.UUID) -> None:
        self.tenant_id = tenant_id
        self._rows: dict[uuid.UUID, AnalysisRecord] = {}

    async def get_by_id(self, analysis_id: uuid.UUID) -> AnalysisRecord | None:
        return self._rows.get(analysis_id)

    async def list_all(
        self,
        *,
        kind: AnalysisKind | None = None,
        student_id: uuid.UUID | None = None,
    ) -> list[AnalysisRecord]:
        rows = list(self._rows.values())
        if kind is not None:
            rows = [row for row in rows if row.kind is kind]
        if student_id is not None:
            rows = [row for row in rows if row.student_id == student_id]
        return rows

    async def add(self, record: AnalysisRecord) -> AnalysisRecord:
        self._rows[record.id] = record
        return record


@pytest.fixture
def tenant_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def service(
    tenant_id: uuid.UUID,
) -> tuple[AnalysisService, _MemoryStudentRepo]:
    students: Any = _MemoryStudentRepo(tenant_id)
    analyses: Any = _MemoryAnalysisRepo(tenant_id)
    return AnalysisService(analyses, students), students


def test_derive_labels_from_exam_and_essay_payloads() -> None:
    assert derive_labels(
        AnalysisKind.EXAM,
        {"studentName": "Ada", "subject": "Physics"},
    ) == ("Ada", "Physics")
    assert derive_labels(
        AnalysisKind.ESSAY,
        {"studentName": "Bob", "title": "My Trip"},
    ) == ("Bob", "My Trip")


@pytest.mark.asyncio
async def test_create_list_get_analysis(
    service: tuple[AnalysisService, _MemoryStudentRepo],
    tenant_id: uuid.UUID,
) -> None:
    analysis_service, students = service
    student = StudentModel(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        full_name="Casey",
        email=None,
        is_active=True,
    )
    students.seed(student)

    created = await analysis_service.create_analysis(
        kind=AnalysisKind.ESSAY,
        student_id=student.id,
        payload={
            "studentName": "Casey",
            "title": "Holiday",
            "summary": "Good",
        },
    )
    assert created.student_id == student.id
    assert created.title == "Holiday"

    listed = await analysis_service.list_analyses(kind=AnalysisKind.ESSAY)
    assert len(listed) == 1

    fetched = await analysis_service.get_analysis(created.id)
    assert fetched.id == created.id


@pytest.mark.asyncio
async def test_create_rejects_unknown_student(
    service: tuple[AnalysisService, _MemoryStudentRepo],
) -> None:
    analysis_service, _students = service
    with pytest.raises(AnalysisStudentNotFoundError):
        await analysis_service.create_analysis(
            kind=AnalysisKind.EXAM,
            student_id=uuid.uuid4(),
            payload={"studentName": "X", "subject": "Math"},
        )


@pytest.mark.asyncio
async def test_get_rejects_missing(
    service: tuple[AnalysisService, _MemoryStudentRepo],
) -> None:
    analysis_service, _students = service
    with pytest.raises(AnalysisNotFoundError):
        await analysis_service.get_analysis(uuid.uuid4())
