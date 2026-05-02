"""Content package repository helpers."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_package import ContentPackage


class ContentPackageRepository:
    """Data access layer for content packages."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        manifest: dict,
        status: str = "ready",
        associated_task_id: uuid.UUID | None = None,
        associated_problem_id: uuid.UUID | None = None,
    ) -> ContentPackage:
        package = ContentPackage(
            manifest=manifest,
            status=status,
            associated_task_id=associated_task_id,
            associated_problem_id=associated_problem_id,
        )
        self.session.add(package)
        await self.session.flush()
        return package

    async def get_by_id(self, package_id: uuid.UUID) -> ContentPackage | None:
        stmt = select(ContentPackage).where(ContentPackage.id == package_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_associated_task_id(self, task_id: uuid.UUID) -> list[ContentPackage]:
        stmt = (
            select(ContentPackage)
            .where(ContentPackage.associated_task_id == task_id)
            .order_by(ContentPackage.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_associated_problem_id(self, problem_id: uuid.UUID) -> list[ContentPackage]:
        stmt = (
            select(ContentPackage)
            .where(ContentPackage.associated_problem_id == problem_id)
            .order_by(ContentPackage.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
