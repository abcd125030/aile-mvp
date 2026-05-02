"""User ORM model."""

import uuid
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.learning_plan import LearningPlan


class User(Base):
    """用户表."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    nickname: Mapped[str] = mapped_column(String(50), nullable=False, server_default="''")
    grade: Mapped[str] = mapped_column(String(10), nullable=False)
    textbook_version: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="'人教版A版'"
    )
    settings: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="'{}'")
    current_plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learning_plans.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    plans: Mapped[list["LearningPlan"]] = relationship(
        "LearningPlan",
        back_populates="user",
        foreign_keys="LearningPlan.user_id",
        cascade="all, delete-orphan",
    )
    current_plan: Mapped["LearningPlan | None"] = relationship(
        "LearningPlan",
        foreign_keys=[current_plan_id],
        post_update=True,
    )
