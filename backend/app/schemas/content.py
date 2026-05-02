"""Content generation schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ContentGenerateRequest(BaseModel):
    """Request payload for AI content generation."""

    knowledge_point_ids: list[str] = Field(min_length=1)
    style: str = "encouraging"
    target_minutes: int = Field(default=8, ge=3, le=60)


class ContentSection(BaseModel):
    """One generated content section."""

    type: Literal["text", "example"]
    content: str


class ContentGenerateResponse(BaseModel):
    """Generated content package payload."""

    content_package_id: str
    status: str
    sections: list[ContentSection]
