"""Knowledge point endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.repositories.exercise_repository import ExerciseRepository
from app.repositories.knowledge_point_repository import KnowledgePointRepository
from app.schemas.knowledge_points import KnowledgePointDetailResponse, KnowledgePointResponse
from app.services.learning_resource_service import LearningResourceService

router = APIRouter(prefix="/knowledge-points", tags=["knowledge-points"])


def get_learning_resource_service(db: AsyncSession) -> LearningResourceService:
    return LearningResourceService(
        knowledge_point_repository=KnowledgePointRepository(db),
        exercise_repository=ExerciseRepository(db),
    )


@router.get("", response_model=list[KnowledgePointResponse])
async def list_knowledge_points(
    subject: str | None = Query(default=None),
    _current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[KnowledgePointResponse]:
    """List knowledge points with an optional subject filter."""
    return await get_learning_resource_service(db).list_knowledge_points(subject=subject)


@router.get("/{knowledge_point_id}", response_model=KnowledgePointDetailResponse)
async def get_knowledge_point_detail(
    knowledge_point_id: str,
    _current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KnowledgePointDetailResponse:
    """Return one knowledge point and its prerequisites."""
    return await get_learning_resource_service(db).get_knowledge_point_detail(
        knowledge_point_id=knowledge_point_id
    )
