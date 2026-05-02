"""Task schemas."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.exercises import ExerciseItemResponse
from app.schemas.knowledge_points import KnowledgePointResponse


class TaskStatus(str, Enum):
    """Allowed Day 2 task states."""

    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class ContentPackageResponse(BaseModel):
    """Content package summary embedded in task detail."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    manifest: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class LearningTaskResponse(BaseModel):
    """Task summary response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    plan_id: str
    title: str
    type: str
    status: TaskStatus
    source: str
    source_problem_id: str | None
    knowledge_point_ids: list[str]
    metadata: dict[str, Any]
    due_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime


class UpdateTaskStatusRequest(BaseModel):
    """Task status transition request."""

    status: TaskStatus


class SubmitAnswerRequest(BaseModel):
    """Exercise answer submission."""

    exercise_id: str
    answer: str


class SubmitAnswerResponse(BaseModel):
    """Exercise answer result."""

    task_id: str
    exercise_id: str
    is_correct: bool
    correct_answer: str
    solution: str | None
    task_status: TaskStatus


class TaskDetailResponse(BaseModel):
    """Full task detail for execution view."""

    task: LearningTaskResponse
    knowledge_points: list[KnowledgePointResponse]
    content_package: ContentPackageResponse | None
    exercises: list[ExerciseItemResponse]
