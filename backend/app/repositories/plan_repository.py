"""Learning plan repository helpers."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.learning_plan import LearningPlan


class PlanRepository:
    """Data access layer for learning plans."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_user_id(self, user_id: uuid.UUID) -> list[LearningPlan]:
        stmt = select(LearningPlan).where(LearningPlan.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, plan_id: uuid.UUID, *, include_tasks: bool = False) -> LearningPlan | None:
        stmt = select(LearningPlan).where(LearningPlan.id == plan_id)
        if include_tasks:
            stmt = stmt.options(selectinload(LearningPlan.tasks))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active_by_user_id(
        self,
        user_id: uuid.UUID,
        *,
        exclude_plan_id: uuid.UUID | None = None,
    ) -> list[LearningPlan]:
        stmt = select(LearningPlan).where(
            LearningPlan.user_id == user_id,
            LearningPlan.status == "active",
        )
        if exclude_plan_id is not None:
            stmt = stmt.where(LearningPlan.id != exclude_plan_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        title: str,
        status: str,
        snapshot: dict | None,
    ) -> LearningPlan:
        plan = LearningPlan(
            user_id=user_id,
            title=title,
            status=status,
            snapshot=snapshot,
        )
        self.session.add(plan)
        await self.session.flush()
        return plan

    async def save(self, plan: LearningPlan) -> LearningPlan:
        self.session.add(plan)
        await self.session.flush()
        return plan
