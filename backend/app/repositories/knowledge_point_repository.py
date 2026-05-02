from __future__ import annotations

"""Knowledge point repository helpers."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_point import KnowledgePoint


class KnowledgePointRepository:
    """Data access layer for knowledge points."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self, *, subject: str | None = None) -> list[KnowledgePoint]:
        stmt = select(KnowledgePoint)
        if subject is not None:
            stmt = stmt.where(KnowledgePoint.subject == subject)
        stmt = stmt.order_by(KnowledgePoint.id.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, knowledge_point_id: str) -> KnowledgePoint | None:
        stmt = select(KnowledgePoint).where(KnowledgePoint.id == knowledge_point_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, knowledge_point_ids: list[str]) -> list[KnowledgePoint]:
        if not knowledge_point_ids:
            return []
        stmt = (
            select(KnowledgePoint)
            .where(KnowledgePoint.id.in_(knowledge_point_ids))
            .order_by(KnowledgePoint.id.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
