"""Daily problem repository helpers."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_problem import DailyProblem


class DailyProblemRepository:
    """Data access layer for daily problems."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        session_id: str,
        original_utterance: str,
        intent: str,
        slots: dict,
    ) -> DailyProblem:
        problem = DailyProblem(
            user_id=user_id,
            session_id=uuid.UUID(session_id),
            original_utterance=original_utterance,
            intent=intent,
            slots=slots,
        )
        self.session.add(problem)
        await self.session.flush()
        return problem

    async def set_resolution_task(
        self,
        *,
        problem_id: uuid.UUID,
        task_id: uuid.UUID,
        resolution_type: str = "practice_task",
    ) -> None:
        stmt = select(DailyProblem).where(DailyProblem.id == problem_id)
        result = await self.session.execute(stmt)
        problem = result.scalar_one_or_none()
        if problem is None:
            return
        problem.resolution_type = resolution_type
        problem.resolution_task_id = task_id
        self.session.add(problem)
        await self.session.flush()
