"""Exercise repository helpers."""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exercise_item import ExerciseItem


class ExerciseRepository:
    """Data access layer for exercises."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, exercise_id: str) -> ExerciseItem | None:
        stmt = select(ExerciseItem).where(ExerciseItem.id == exercise_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, exercise_ids: list[str]) -> list[ExerciseItem]:
        if not exercise_ids:
            return []
        stmt = select(ExerciseItem).where(ExerciseItem.id.in_(exercise_ids))
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        order_map = {exercise_id: index for index, exercise_id in enumerate(exercise_ids)}
        items.sort(key=lambda item: order_map.get(item.id, len(order_map)))
        return items

    async def list_filtered(
        self,
        *,
        knowledge_point_id: str | None = None,
        difficulty_min: float | None = None,
        difficulty_max: float | None = None,
        limit: int = 20,
    ) -> list[ExerciseItem]:
        stmt = select(ExerciseItem)
        if knowledge_point_id is not None:
            stmt = stmt.where(ExerciseItem.knowledge_point_ids.contains([knowledge_point_id]))
        if difficulty_min is not None:
            stmt = stmt.where(ExerciseItem.difficulty >= difficulty_min)
        if difficulty_max is not None:
            stmt = stmt.where(ExerciseItem.difficulty <= difficulty_max)
        stmt = stmt.order_by(ExerciseItem.difficulty.asc(), ExerciseItem.id.asc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_for_knowledge_points(
        self,
        knowledge_point_ids: list[str],
        *,
        limit: int = 10,
    ) -> list[ExerciseItem]:
        if not knowledge_point_ids:
            return []
        conditions = [ExerciseItem.knowledge_point_ids.contains([knowledge_point_id]) for knowledge_point_id in knowledge_point_ids]
        stmt = (
            select(ExerciseItem)
            .where(or_(*conditions))
            .order_by(ExerciseItem.difficulty.asc(), ExerciseItem.id.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
