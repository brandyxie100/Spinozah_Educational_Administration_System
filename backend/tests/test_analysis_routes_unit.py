"""Unit tests for analysis persistence routes (dependency overrides, no DB)."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from typing import Any

import pytest
from app.api.v1.analyses import get_analysis_service
from app.application.ai_analysis.analysis_service import (
    AnalysisNotFoundError,
    AnalysisService,
    AnalysisStudentNotFoundError,
)
from app.domain.ai_analysis.entities import AnalysisKind, AnalysisRecord
from app.main import create_app
from fastapi.testclient import TestClient


class _FakeAnalysisService:
    def __init__(self) -> None:
        self.tenant_id = uuid.uuid4()
        self._rows: dict[uuid.UUID, AnalysisRecord] = {}

    async def create_analysis(
        self,
        *,
        kind: AnalysisKind,
        payload: dict[str, Any],
        student_id: uuid.UUID | None = None,
    ) -> AnalysisRecord:
        if student_id is not None and student_id.hex.startswith("dead"):
            raise AnalysisStudentNotFoundError(f"Student not found: {student_id}")
        title_value = (
            payload.get("subject")
            if kind is AnalysisKind.EXAM
            else payload.get("title")
        )
        record = AnalysisRecord(
            tenant_id=self.tenant_id,
            kind=kind,
            payload=payload,
            student_id=student_id,
            student_name=str(payload.get("studentName") or "") or None,
            title=str(title_value or "") or None,
        )
        self._rows[record.id] = record
        return record

    async def list_analyses(
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

    async def get_analysis(self, analysis_id: uuid.UUID) -> AnalysisRecord:
        record = self._rows.get(analysis_id)
        if record is None:
            raise AnalysisNotFoundError(f"Analysis not found: {analysis_id}")
        return record


@pytest.fixture
def client() -> Iterator[TestClient]:
    fake = _FakeAnalysisService()
    app = create_app()

    def _override() -> AnalysisService:
        return fake  # type: ignore[return-value]

    app.dependency_overrides[get_analysis_service] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_analysis_create_list_get_flow(client: TestClient) -> None:
    created = client.post(
        "/api/v1/analyses",
        json={
            "kind": "essay",
            "payload": {
                "studentName": "Ada",
                "title": "Trip",
                "summary": "Nice",
            },
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["kind"] == "essay"
    assert body["title"] == "Trip"
    analysis_id = body["id"]

    listed = client.get("/api/v1/analyses?kind=essay")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = client.get(f"/api/v1/analyses/{analysis_id}")
    assert fetched.status_code == 200
    assert fetched.json()["payload"]["summary"] == "Nice"


def test_create_unknown_student_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/v1/analyses",
        json={
            "kind": "exam",
            "student_id": "dead0000-0000-4000-8000-000000000001",
            "payload": {"studentName": "X", "subject": "Math"},
        },
    )
    assert response.status_code == 404
