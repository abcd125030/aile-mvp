"""LearningPlan ORM model."""

import uuid
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.learning_task import LearningTask
    from app.models.user import User


class LearningPlan(Base):
    """学习计划表 — 依赖 users."""

    __tablename__ = "learning_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="'active'")
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="plans",
        foreign_keys=[user_id],
    )
    tasks: Mapped[list["LearningTask"]] = relationship(
        "LearningTask",
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="LearningTask.created_at",
    )
