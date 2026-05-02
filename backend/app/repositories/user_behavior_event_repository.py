"""Chat storage based on user behavior events."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_behavior_event import UserBehaviorEvent

CHAT_EVENT_TYPES = ("utterance_sent", "assistant_replied")


@dataclass(slots=True)
class ChatSessionSummary:
    session_id: str
    last_message: str
    last_active_at: object
    message_count: int


class UserBehaviorEventRepository:
    """Persist and query chat events."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_message_event(
        self,
        *,
        user_id: uuid.UUID,
        session_id: str,
        role: str,
        content: str,
        event_type: str,
        intent: str | None = None,
        knowledge_point_ids: list[str] | None = None,
    ) -> UserBehaviorEvent:
        payload: dict = {"role": role, "content": content}
        if intent:
            payload["intent"] = intent
        if knowledge_point_ids:
            payload["knowledge_point_ids"] = knowledge_point_ids

        event = UserBehaviorEvent(
            user_id=user_id,
            session_id=session_id,
            event_type=event_type,
            event_data=payload,
        )
        self.session.add(event)
        await self.session.flush()
        return event

    async def list_sessions(self, *, user_id: uuid.UUID) -> list[ChatSessionSummary]:
        stmt = (
            select(UserBehaviorEvent)
            .where(
                UserBehaviorEvent.user_id == user_id,
                UserBehaviorEvent.event_type.in_(CHAT_EVENT_TYPES),
            )
            .order_by(UserBehaviorEvent.created_at.desc(), UserBehaviorEvent.id.desc())
        )
        rows = (await self.session.execute(stmt)).scalars().all()

        session_map: dict[str, ChatSessionSummary] = {}
        for event in rows:
            summary = session_map.get(event.session_id)
            content = str((event.event_data or {}).get("content") or "")
            if summary is None:
                session_map[event.session_id] = ChatSessionSummary(
                    session_id=event.session_id,
                    last_message=content,
                    last_active_at=event.created_at,
                    message_count=1,
                )
            else:
                summary.message_count += 1
        return list(session_map.values())

    async def list_messages(self, *, user_id: uuid.UUID, session_id: str) -> list[UserBehaviorEvent]:
        stmt = (
            select(UserBehaviorEvent)
            .where(
                UserBehaviorEvent.user_id == user_id,
                UserBehaviorEvent.session_id == session_id,
                UserBehaviorEvent.event_type.in_(CHAT_EVENT_TYPES),
            )
            .order_by(UserBehaviorEvent.created_at.asc(), UserBehaviorEvent.id.asc())
        )
        return list((await self.session.execute(stmt)).scalars().all())
