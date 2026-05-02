"""Learning task repository helpers."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.learning_task import LearningTask


class TaskRepository:
    """Data access layer for learning tasks."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, task_id: uuid.UUID) -> LearningTask | None:
        stmt = (
            select(LearningTask)
            .where(LearningTask.id == task_id)
            .options(
                joinedload(LearningTask.plan),
                joinedload(LearningTask.content_package),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_plan_id(self, plan_id: uuid.UUID, *, status: str | None = None) -> list[LearningTask]:
        stmt = (
            select(LearningTask)
            .where(LearningTask.plan_id == plan_id)
            .options(joinedload(LearningTask.content_package))
        )
        if status is not None:
            stmt = stmt.where(LearningTask.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def save(self, task: LearningTask) -> LearningTask:
        self.session.add(task)
        await self.session.flush()
        return task
