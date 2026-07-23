"""Tenant-scoped SQLAlchemy repository for analysis records."""

from __future__ import annotations

from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.ai_analysis.entities import AnalysisKind, AnalysisRecord
from app.infrastructure.persistence.analysis_mapper import (
    analysis_to_model,
    model_to_analysis,
)
from app.infrastructure.persistence.analysis_models import (
    AnalysisKindDB,
    AnalysisRecordModel,
)
from app.infrastructure.persistence.tenant_scoped import (
    SqlAlchemyTenantScopedRepository,
)


class SqlAlchemyAnalysisRepository(SqlAlchemyTenantScopedRepository):
    """Load and mutate analysis records within the bound tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        """Create an analysis repository scoped to ``tenant_id``."""
        super().__init__(session, tenant_id)

    async def get_by_id(self, analysis_id: UUID) -> AnalysisRecord | None:
        """Return one analysis by id for this tenant."""
        statement = self._scoped(
            select(AnalysisRecordModel).where(AnalysisRecordModel.id == analysis_id),
            AnalysisRecordModel,
        )
        result = await self._session.scalar(statement)
        model = cast(AnalysisRecordModel | None, result)
        return model_to_analysis(model) if model is not None else None

    async def list_all(
        self,
        *,
        kind: AnalysisKind | None = None,
        student_id: UUID | None = None,
    ) -> list[AnalysisRecord]:
        """Return analyses for this tenant (newest first), with optional filters."""
        statement = select(AnalysisRecordModel)
        if kind is not None:
            statement = statement.where(
                AnalysisRecordModel.kind == AnalysisKindDB(kind.value),
            )
        if student_id is not None:
            statement = statement.where(AnalysisRecordModel.student_id == student_id)
        statement = self._scoped(
            statement.order_by(AnalysisRecordModel.created_at.desc()),
            AnalysisRecordModel,
        )
        result = await self._session.scalars(statement)
        return [model_to_analysis(model) for model in result.all()]

    async def add(self, record: AnalysisRecord) -> AnalysisRecord:
        """Persist a new analysis record."""
        if record.tenant_id != self._tenant_id:
            raise ValueError("Cannot add analysis for a different tenant")
        model = analysis_to_model(record)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return model_to_analysis(model)
