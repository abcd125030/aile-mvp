"""ExerciseItem ORM model."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ExerciseItem(Base):
    """练习题表 — 无外键依赖."""

    __tablename__ = "exercise_items"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    stem: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    correct_answer: Mapped[str] = mapped_column(String(500), nullable=False)
    solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    knowledge_point_ids: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="'[]'")
    difficulty: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False, server_default="0.5")
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, server_default="'{}'")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
