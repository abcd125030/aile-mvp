"""Knowledge point and exercise query services."""

from fastapi import HTTPException, status

from app.repositories.exercise_repository import ExerciseRepository
from app.repositories.knowledge_point_repository import KnowledgePointRepository
from app.schemas.exercises import ExerciseItemResponse
from app.schemas.knowledge_points import KnowledgePointDetailResponse, KnowledgePointResponse
from app.services.presenters import build_exercise_response, build_knowledge_point_response


class LearningResourceService:
    """Read-only queries for knowledge points and exercises."""

    def __init__(
        self,
        *,
        knowledge_point_repository: KnowledgePointRepository,
        exercise_repository: ExerciseRepository,
    ) -> None:
        self.knowledge_point_repository = knowledge_point_repository
        self.exercise_repository = exercise_repository

    async def list_knowledge_points(self, *, subject: str | None) -> list[KnowledgePointResponse]:
        knowledge_points = await self.knowledge_point_repository.list(subject=subject)
        return [build_knowledge_point_response(item) for item in knowledge_points]

    async def get_knowledge_point_detail(self, *, knowledge_point_id: str) -> KnowledgePointDetailResponse:
        knowledge_point = await self.knowledge_point_repository.get_by_id(knowledge_point_id)
        if knowledge_point is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="知识点不存在")

        prerequisites = await self.knowledge_point_repository.get_by_ids(
            list(knowledge_point.prerequisite_ids or [])
        )
        return KnowledgePointDetailResponse(
            **build_knowledge_point_response(knowledge_point).model_dump(),
            prerequisites=[build_knowledge_point_response(item) for item in prerequisites],
        )

    async def list_exercises(
        self,
        *,
        knowledge_point_id: str | None,
        difficulty_min: float | None,
        difficulty_max: float | None,
        limit: int,
    ) -> list[ExerciseItemResponse]:
        exercises = await self.exercise_repository.list_filtered(
            knowledge_point_id=knowledge_point_id,
            difficulty_min=difficulty_min,
            difficulty_max=difficulty_max,
            limit=limit,
        )
        return [build_exercise_response(item) for item in exercises]
