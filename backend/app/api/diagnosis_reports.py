"""Diagnosis report endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.diagnosis_report_repository import DiagnosisReportRepository
from app.repositories.plan_repository import PlanRepository
from app.schemas.diagnosis_reports import (
    BindDiagnosisReportPlanRequest,
    DiagnosisReportResponse,
    SaveSimplifiedDiagnosisReportRequest,
)
from app.services.diagnosis_report_service import DiagnosisReportService

router = APIRouter(prefix="/diagnosis-reports", tags=["diagnosis-reports"])


def get_diagnosis_report_service(db: AsyncSession) -> DiagnosisReportService:
    return DiagnosisReportService(
        diagnosis_report_repository=DiagnosisReportRepository(db),
        plan_repository=PlanRepository(db),
    )


@router.post("/simplified", response_model=DiagnosisReportResponse, status_code=201)
async def save_simplified_diagnosis_report(
    payload: SaveSimplifiedDiagnosisReportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DiagnosisReportResponse:
    """Persist one simplified diagnosis report for current user."""
    return await get_diagnosis_report_service(db).save_simplified_report(
        current_user=current_user,
        payload=payload,
    )


@router.put("/{report_id}/generated-plan", response_model=DiagnosisReportResponse)
async def bind_generated_plan(
    report_id: str,
    payload: BindDiagnosisReportPlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DiagnosisReportResponse:
    """Bind one generated plan to the diagnosis report."""
    return await get_diagnosis_report_service(db).bind_generated_plan(
        report_id=report_id,
        current_user=current_user,
        payload=payload,
    )
