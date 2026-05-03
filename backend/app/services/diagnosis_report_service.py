"""Diagnosis report service."""

import uuid

from app.core.exceptions import bad_request
from app.core.exceptions import forbidden
from app.core.exceptions import not_found
from app.models.user import User
from app.repositories.diagnosis_report_repository import DiagnosisReportRepository
from app.repositories.plan_repository import PlanRepository
from app.schemas.diagnosis_reports import (
    BindDiagnosisReportPlanRequest,
    DiagnosisReportResponse,
    SaveSimplifiedDiagnosisReportRequest,
)


class DiagnosisReportService:
    """Diagnosis report write operations for current user."""

    def __init__(
        self,
        *,
        diagnosis_report_repository: DiagnosisReportRepository,
        plan_repository: PlanRepository,
    ) -> None:
        self.diagnosis_report_repository = diagnosis_report_repository
        self.plan_repository = plan_repository
        self.session = diagnosis_report_repository.session

    async def save_simplified_report(
        self,
        *,
        current_user: User,
        payload: SaveSimplifiedDiagnosisReportRequest,
    ) -> DiagnosisReportResponse:
        if not payload.weak_points:
            raise bad_request("薄弱知识点不能为空")

        summary = {
            "report_type": "simplified",
            "weak_points": [
                {
                    "id": item.id,
                    "name": item.name,
                    "pending_task_count": item.pending_task_count,
                }
                for item in payload.weak_points
            ],
        }
        detailed_analysis = {
            "source": payload.source or "active_plan_pending_in_progress_tasks",
            "weak_point_count": len(payload.weak_points),
            "total_pending_task_count": sum(item.pending_task_count for item in payload.weak_points),
        }

        report = await self.diagnosis_report_repository.create(
            user_id=current_user.id,
            title=payload.title,
            summary=summary,
            detailed_analysis=detailed_analysis,
        )
        await self.session.commit()

        return DiagnosisReportResponse(
            id=str(report.id),
            user_id=str(report.user_id),
            title=report.title,
            original_file_url=report.original_file_url,
            summary=report.summary,
            detailed_analysis=report.detailed_analysis,
            generated_plan_id=str(report.generated_plan_id) if report.generated_plan_id else None,
            created_at=report.created_at,
        )

    async def bind_generated_plan(
        self,
        *,
        report_id: str,
        current_user: User,
        payload: BindDiagnosisReportPlanRequest,
    ) -> DiagnosisReportResponse:
        parsed_report_id = self._parse_uuid(report_id, "诊断报告不存在")
        parsed_plan_id = self._parse_uuid(payload.generated_plan_id, "学习计划不存在")

        report = await self.diagnosis_report_repository.get_by_id(parsed_report_id)
        if report is None:
            raise not_found("诊断报告不存在")
        if report.user_id != current_user.id:
            raise forbidden("无权修改该诊断报告")

        plan = await self.plan_repository.get_by_id(parsed_plan_id)
        if plan is None:
            raise not_found("学习计划不存在")
        if plan.user_id != current_user.id:
            raise forbidden("无权关联该学习计划")

        report.generated_plan_id = plan.id
        await self.diagnosis_report_repository.save(report)
        await self.session.commit()

        return DiagnosisReportResponse(
            id=str(report.id),
            user_id=str(report.user_id),
            title=report.title,
            original_file_url=report.original_file_url,
            summary=report.summary,
            detailed_analysis=report.detailed_analysis,
            generated_plan_id=str(report.generated_plan_id) if report.generated_plan_id else None,
            created_at=report.created_at,
        )

    @staticmethod
    def _parse_uuid(value: str, error_detail: str) -> uuid.UUID:
        try:
            return uuid.UUID(value)
        except ValueError as exc:
            raise not_found(error_detail) from exc
