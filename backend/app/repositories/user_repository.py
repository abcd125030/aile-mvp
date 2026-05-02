"""User repository helpers."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User


class UserRepository:
    """Data access layer for users."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.current_plan))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        stmt = (
            select(User)
            .where(User.phone == phone)
            .options(selectinload(User.current_plan))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_default_user(self, phone: str) -> User:
        user = User(
            phone=phone,
            nickname="",
            grade="高一",
            textbook_version="人教版A版",
            settings={},
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def save(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
