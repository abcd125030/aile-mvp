"""ContentPackage ORM model."""

import uuid
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.learning_task import LearningTask


class ContentPackage(Base):
    """内容包表 — 延迟外键."""

    __tablename__ = "content_packages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    production_job_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="'generating'")
    manifest: Mapped[dict] = mapped_column(JSONB, nullable=False)
    associated_task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learning_tasks.id"),
        nullable=True,
    )
    associated_problem_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("daily_problems.id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    task: Mapped["LearningTask | None"] = relationship(
        "LearningTask",
        foreign_keys=[associated_task_id],
        viewonly=True,
    )
