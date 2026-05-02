"""KnowledgePoint ORM model."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KnowledgePoint(Base):
    """知识点表 — 无外键依赖."""

    __tablename__ = "knowledge_points"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    prerequisite_ids: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="'[]'")
    difficulty: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False, server_default="0.5")
    subject: Mapped[str] = mapped_column(String(20), nullable=False, server_default="'math'")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
