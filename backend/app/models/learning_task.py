"""LearningTask ORM model."""

import uuid
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.content_package import ContentPackage
    from app.models.learning_plan import LearningPlan


class LearningTask(Base):
    """学习任务表 — 依赖 learning_plans, daily_problems, content_packages."""

    __tablename__ = "learning_tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("learning_plans.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="'pending'")
    source: Mapped[str] = mapped_column(String(50), nullable=False, server_default="'scheduled'")
    source_problem_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("daily_problems.id", ondelete="SET NULL"),
        nullable=True,
    )
    knowledge_point_ids: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="'[]'")
    content_package_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content_packages.id", ondelete="SET NULL"),
        nullable=True,
    )
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, server_default="'{}'")
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    plan: Mapped["LearningPlan"] = relationship(
        "LearningPlan",
        back_populates="tasks",
        foreign_keys=[plan_id],
    )
    content_package: Mapped["ContentPackage | None"] = relationship(
        "ContentPackage",
        foreign_keys=[content_package_id],
    )
