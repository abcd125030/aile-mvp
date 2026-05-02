"""Helpers for converting ORM objects into API schemas."""

from collections.abc import Sequence
from typing import Any

from app.models.content_package import ContentPackage
from app.models.exercise_item import ExerciseItem
from app.models.knowledge_point import KnowledgePoint
from app.models.learning_plan import LearningPlan
from app.models.learning_task import LearningTask
from app.schemas.exercises import ExerciseItemResponse
from app.schemas.knowledge_points import KnowledgePointResponse
from app.schemas.plans import LearningPlanResponse
from app.schemas.tasks import ContentPackageResponse, LearningTaskResponse


def _ensure_list(value: Any) -> list:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return list(value)
    return []


def build_plan_response(plan: LearningPlan) -> LearningPlanResponse:
    return LearningPlanResponse(
        id=str(plan.id),
        user_id=str(plan.user_id),
        title=plan.title,
        status=plan.status,
        version=plan.version,
        snapshot=plan.snapshot,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


def build_task_response(task: LearningTask) -> LearningTaskResponse:
    return LearningTaskResponse(
        id=str(task.id),
        plan_id=str(task.plan_id),
        title=task.title,
        type=task.type,
        status=task.status,
        source=task.source,
        source_problem_id=str(task.source_problem_id) if task.source_problem_id else None,
        knowledge_point_ids=[str(value) for value in _ensure_list(task.knowledge_point_ids)],
        metadata=task.metadata_ or {},
        due_at=task.due_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        created_at=task.created_at,
    )


def build_content_package_response(content_package: ContentPackage) -> ContentPackageResponse:
    return ContentPackageResponse(
        id=str(content_package.id),
        status=content_package.status,
        manifest=content_package.manifest,
        created_at=content_package.created_at,
        updated_at=content_package.updated_at,
    )


def build_knowledge_point_response(knowledge_point: KnowledgePoint) -> KnowledgePointResponse:
    return KnowledgePointResponse(
        id=knowledge_point.id,
        name=knowledge_point.name,
        description=knowledge_point.description,
        prerequisite_ids=[str(value) for value in _ensure_list(knowledge_point.prerequisite_ids)],
        difficulty=float(knowledge_point.difficulty),
        subject=knowledge_point.subject,
    )


def build_exercise_response(exercise: ExerciseItem) -> ExerciseItemResponse:
    return ExerciseItemResponse(
        id=exercise.id,
        stem=exercise.stem,
        options=[str(value) for value in _ensure_list(exercise.options)] or None,
        knowledge_point_ids=[str(value) for value in _ensure_list(exercise.knowledge_point_ids)],
        difficulty=float(exercise.difficulty),
        metadata=exercise.metadata_ or {},
    )
