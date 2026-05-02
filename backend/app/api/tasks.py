"""Learning task endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.exercise_repository import ExerciseRepository
from app.repositories.knowledge_point_repository import KnowledgePointRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.tasks import (
    LearningTaskResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    TaskDetailResponse,
    TaskStatus,
    UpdateTaskStatusRequest,
)
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(db: AsyncSession) -> TaskService:
    return TaskService(
        task_repository=TaskRepository(db),
        plan_repository=PlanRepository(db),
        knowledge_point_repository=KnowledgePointRepository(db),
        exercise_repository=ExerciseRepository(db),
    )


@router.get("", response_model=list[LearningTaskResponse])
async def list_tasks(
    plan_id: str | None = Query(default=None),
    status: TaskStatus | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[LearningTaskResponse]:
    """List tasks for the current user."""
    return await get_task_service(db).list_tasks(
        current_user=current_user,
        plan_id=plan_id,
        status_filter=status.value if status else None,
    )


@router.get("/{task_id}", response_model=TaskDetailResponse)
async def get_task_detail(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskDetailResponse:
    """Return one task with related resources."""
    return await get_task_service(db).get_task_detail(task_id=task_id, current_user=current_user)


@router.put("/{task_id}/status", response_model=LearningTaskResponse)
async def update_task_status(
    task_id: str,
    payload: UpdateTaskStatusRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LearningTaskResponse:
    """Update one task's status."""
    return await get_task_service(db).update_task_status(
        current_user=current_user,
        task_id=task_id,
        payload=payload,
    )


@router.post("/{task_id}/submit-answer", response_model=SubmitAnswerResponse)
async def submit_answer(
    task_id: str,
    payload: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SubmitAnswerResponse:
    """Submit an answer for one exercise in a task."""
    return await get_task_service(db).submit_answer(
        current_user=current_user,
        task_id=task_id,
        payload=payload,
    )
