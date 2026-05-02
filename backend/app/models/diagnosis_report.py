"""DiagnosisReport ORM model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DiagnosisReport(Base):
    """诊断报告表 — 依赖 users, learning_plans."""

    __tablename__ = "diagnosis_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    original_file_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[dict] = mapped_column(JSONB, nullable=False)
    detailed_analysis: Mapped[dict] = mapped_column(JSONB, nullable=False)
    generated_plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learning_plans.id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
