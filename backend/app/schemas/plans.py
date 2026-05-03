"""Plan schemas."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel

from app.schemas.tasks import LearningTaskResponse


class PlanStatus(str, Enum):
    """Allowed Day 2 plan states."""

    active = "active"
    completed = "completed"
    archived = "archived"


class LearningPlanResponse(BaseModel):
    """Plan summary response."""

    id: str
    user_id: str
    title: str
    status: PlanStatus
    version: int
    snapshot: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime


class CreatePlanRequest(BaseModel):
    """Plan creation request."""

    title: str
    status: PlanStatus = PlanStatus.active
    snapshot: dict[str, Any] | None = None
    set_as_current: bool = True


class GeneratePlanRequest(BaseModel):
    """Auto-generate one executable plan from weak knowledge points."""

    title: str = "智能巩固计划"
    source: str = "manual_generate"
    knowledge_point_ids: list[str]
    set_as_current: bool = True


class UpdatePlanStatusRequest(BaseModel):
    """Plan status update request."""

    status: PlanStatus


class PlanDetailResponse(BaseModel):
    """Plan detail with tasks."""

    plan: LearningPlanResponse
    tasks: list[LearningTaskResponse]
