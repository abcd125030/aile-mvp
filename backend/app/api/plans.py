"""Learning plan endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.knowledge_point_repository import KnowledgePointRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.plans import (
    CreatePlanRequest,
    GeneratePlanRequest,
    LearningPlanResponse,
    PlanDetailResponse,
    UpdatePlanStatusRequest,
)
from app.services.plan_service import PlanService

router = APIRouter(prefix="/plans", tags=["plans"])


def get_plan_service(db: AsyncSession) -> PlanService:
    return PlanService(
        plan_repository=PlanRepository(db),
        user_repository=UserRepository(db),
        task_repository=TaskRepository(db),
        knowledge_point_repository=KnowledgePointRepository(db),
    )


@router.get("", response_model=list[LearningPlanResponse])
async def list_plans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[LearningPlanResponse]:
    """Return all plans owned by the current user."""
    return await get_plan_service(db).list_plans(current_user=current_user)


@router.post("", response_model=LearningPlanResponse, status_code=201)
async def create_plan(
    payload: CreatePlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LearningPlanResponse:
    """Create a new plan for the current user."""
    return await get_plan_service(db).create_plan(current_user=current_user, payload=payload)


@router.post("/generate", response_model=PlanDetailResponse, status_code=201)
async def generate_plan(
    payload: GeneratePlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PlanDetailResponse:
    """Generate one executable plan and tasks from weak knowledge points."""
    return await get_plan_service(db).generate_plan(current_user=current_user, payload=payload)


@router.get("/{plan_id}", response_model=PlanDetailResponse)
async def get_plan_detail(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PlanDetailResponse:
    """Return one plan and its tasks."""
    return await get_plan_service(db).get_plan_detail(plan_id=plan_id, current_user=current_user)


@router.put("/{plan_id}/status", response_model=LearningPlanResponse)
async def update_plan_status(
    plan_id: str,
    payload: UpdatePlanStatusRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LearningPlanResponse:
    """Update one plan's status."""
    return await get_plan_service(db).update_plan_status(
        plan_id=plan_id,
        current_user=current_user,
        payload=payload,
    )
