"""Chat orchestration service."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator

from app.core.exceptions import not_found
from app.models.user import User
from app.repositories.user_behavior_event_repository import UserBehaviorEventRepository
from app.schemas.chat import ChatHistoryMessageResponse, ChatSessionResponse
from app.services.daily_clearance_service import DailyClearanceService
from app.services.intent_service import IntentService
from app.services.llm import LLMMessage, LLMService

SYSTEM_PROMPT = (
    '你是"艾乐"，一个温暖、耐心的AI学习伙伴（不是老师）。'
    "你帮助高中生理解数学知识、解决学习困惑。"
    "说话风格亲切、鼓励式、简洁。"
)


class ChatService:
    """Handle message, stream response, and persistence."""

    def __init__(
        self,
        *,
        llm_service: LLMService,
        intent_service: IntentService,
        event_repository: UserBehaviorEventRepository,
        daily_clearance_service: DailyClearanceService,
    ) -> None:
        self.llm_service = llm_service
        self.intent_service = intent_service
        self.event_repository = event_repository
        self.daily_clearance_service = daily_clearance_service
        self.session = daily_clearance_service.session

    async def list_sessions(self, *, current_user: User) -> list[ChatSessionResponse]:
        sessions = await self.event_repository.list_sessions(user_id=current_user.id)
        return [
            ChatSessionResponse(
                session_id=item.session_id,
                last_message=item.last_message,
                last_active_at=item.last_active_at,
                message_count=item.message_count,
            )
            for item in sessions
        ]

    async def list_messages(
        self,
        *,
        current_user: User,
        session_id: str,
    ) -> list[ChatHistoryMessageResponse]:
        events = await self.event_repository.list_messages(user_id=current_user.id, session_id=session_id)
        if not events:
            raise not_found("会话不存在")
        return [
            ChatHistoryMessageResponse(
                role=str((item.event_data or {}).get("role") or ""),
                content=str((item.event_data or {}).get("content") or ""),
                created_at=item.created_at,
                intent=(item.event_data or {}).get("intent"),
                knowledge_point_ids=list((item.event_data or {}).get("knowledge_point_ids") or []),
            )
            for item in events
        ]

    async def stream_message(
        self,
        *,
        current_user: User,
        message: str,
        session_id: str | None,
    ) -> AsyncIterator[dict]:
        resolved_session_id = session_id or str(uuid.uuid4())
        try:
            resolved_session_id = str(uuid.UUID(resolved_session_id))
        except ValueError:
            resolved_session_id = str(uuid.uuid4())
        intent = await self.intent_service.classify(message=message)
        kp_ids = list(intent.slots.get("knowledge_point_ids") or [])

        await self.event_repository.create_message_event(
            user_id=current_user.id,
            session_id=resolved_session_id,
            role="user",
            content=message,
            event_type="utterance_sent",
            intent=intent.primary_intent,
            knowledge_point_ids=kp_ids,
        )

        _, task = await self.daily_clearance_service.record_problem_and_generate_task(
            current_user=current_user,
            session_id=resolved_session_id,
            utterance=message,
            intent=intent,
        )

        history = await self.event_repository.list_messages(
            user_id=current_user.id,
            session_id=resolved_session_id,
        )
        messages = [LLMMessage(role="system", content=SYSTEM_PROMPT)]
        for item in history[-8:]:
            role = str((item.event_data or {}).get("role") or "user")
            content = str((item.event_data or {}).get("content") or "")
            if role in {"user", "assistant"} and content:
                messages.append(LLMMessage(role=role, content=content))

        assistant_text_parts: list[str] = []
        async for chunk in self.llm_service.stream_chat(messages=messages):
            assistant_text_parts.append(chunk)
            yield {"event": "token", "data": {"text": chunk}}

        assistant_text = "".join(assistant_text_parts).strip()
        if not assistant_text:
            assistant_text = "我在这儿，咱们一步一步来。你先告诉我最卡的是哪一步。"

        await self.event_repository.create_message_event(
            user_id=current_user.id,
            session_id=resolved_session_id,
            role="assistant",
            content=assistant_text,
            event_type="assistant_replied",
        )
        await self.session.commit()

        yield {
            "event": "metadata",
            "data": {
                "session_id": resolved_session_id,
                "intent": intent.primary_intent,
                "knowledge_point_ids": kp_ids,
                "task_created": task is not None,
                "task_id": str(task.id) if task else None,
            },
        }
        yield {
            "event": "done",
            "data": {
                "session_id": resolved_session_id,
                "assistant_message": assistant_text,
            },
        }
