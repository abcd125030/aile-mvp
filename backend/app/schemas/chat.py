"""Chat schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """Incoming user message for chat."""

    session_id: str | None = None
    message: str = Field(min_length=1, max_length=4000)
    journey: str = "DAILY_CLEARANCE"


class IntentResult(BaseModel):
    """Intent classification output."""

    primary_intent: str
    slots: dict[str, Any] = Field(default_factory=dict)


class ChatSessionResponse(BaseModel):
    """Session summary for chat list."""

    session_id: str
    last_message: str
    last_active_at: datetime
    message_count: int


class ChatHistoryMessageResponse(BaseModel):
    """One message in a chat session history."""

    role: str
    content: str
    created_at: datetime
    intent: str | None = None
    knowledge_point_ids: list[str] = Field(default_factory=list)
