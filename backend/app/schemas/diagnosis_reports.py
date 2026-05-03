"""Diagnosis report schemas."""

from datetime import datetime

from pydantic import BaseModel


class SimplifiedWeakPointItem(BaseModel):
    """One weak point item in simplified diagnosis report."""

    id: str
    name: str
    pending_task_count: int


class SaveSimplifiedDiagnosisReportRequest(BaseModel):
    """Persist simplified diagnosis report built from current tasks."""

    title: str = "诊断报告（简化版）"
    source: str | None = None
    weak_points: list[SimplifiedWeakPointItem]


class BindDiagnosisReportPlanRequest(BaseModel):
    """Bind generated plan to an existing diagnosis report."""

    generated_plan_id: str


class DiagnosisReportResponse(BaseModel):
    """Diagnosis report persistence result."""

    id: str
    user_id: str
    title: str
    original_file_url: str | None
    summary: dict
    detailed_analysis: dict
    generated_plan_id: str | None
    created_at: datetime
