"""Exercise endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.repositories.exercise_repository import ExerciseRepository
from app.repositories.knowledge_point_repository import KnowledgePointRepository
from app.schemas.exercises import ExerciseItemResponse
from app.services.learning_resource_service import LearningResourceService

router = APIRouter(prefix="/exercises", tags=["exercises"])


def get_learning_resource_service(db: AsyncSession) -> LearningResourceService:
    return LearningResourceService(
        knowledge_point_repository=KnowledgePointRepository(db),
        exercise_repository=ExerciseRepository(db),
    )


@router.get("", response_model=list[ExerciseItemResponse])
async def list_exercises(
    knowledge_point_id: str | None = Query(default=None),
    difficulty_min: float | None = Query(default=None),
    difficulty_max: float | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    _current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ExerciseItemResponse]:
    """List exercises with optional filters."""
    return await get_learning_resource_service(db).list_exercises(
        knowledge_point_id=knowledge_point_id,
        difficulty_min=difficulty_min,
        difficulty_max=difficulty_max,
        limit=limit,
    )
