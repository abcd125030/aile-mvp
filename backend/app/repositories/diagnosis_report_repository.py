"""Diagnosis report repository helpers."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnosis_report import DiagnosisReport


class DiagnosisReportRepository:
    """Data access layer for diagnosis reports."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        title: str,
        summary: dict,
        detailed_analysis: dict,
        original_file_url: str | None = None,
        generated_plan_id: uuid.UUID | None = None,
    ) -> DiagnosisReport:
        report = DiagnosisReport(
            user_id=user_id,
            title=title,
            original_file_url=original_file_url,
            summary=summary,
            detailed_analysis=detailed_analysis,
            generated_plan_id=generated_plan_id,
        )
        self.session.add(report)
        await self.session.flush()
        return report

    async def get_by_id(self, report_id: uuid.UUID) -> DiagnosisReport | None:
        stmt = select(DiagnosisReport).where(DiagnosisReport.id == report_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, report: DiagnosisReport) -> DiagnosisReport:
        self.session.add(report)
        await self.session.flush()
        return report
