"""Chat endpoints."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.content_package_repository import ContentPackageRepository
from app.repositories.daily_problem_repository import DailyProblemRepository
from app.repositories.knowledge_point_repository import KnowledgePointRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_behavior_event_repository import UserBehaviorEventRepository
from app.schemas.chat import ChatHistoryMessageResponse, ChatMessageRequest, ChatSessionResponse
from app.services.chat_service import ChatService
from app.services.content_generation_service import ContentGenerationService
from app.services.daily_clearance_service import DailyClearanceService
from app.services.intent_service import IntentService
from app.services.llm import LLMService

router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_service(db: AsyncSession) -> ChatService:
    llm_service = LLMService()
    knowledge_point_repository = KnowledgePointRepository(db)
    daily_problem_repository = DailyProblemRepository(db)
    plan_repository = PlanRepository(db)
    task_repository = TaskRepository(db)
    content_generation_service = ContentGenerationService(
        llm_service=llm_service,
        knowledge_point_repository=knowledge_point_repository,
        content_package_repository=ContentPackageRepository(db),
    )
    return ChatService(
        llm_service=llm_service,
        intent_service=IntentService(
            llm_service=llm_service,
            knowledge_point_repository=knowledge_point_repository,
        ),
        event_repository=UserBehaviorEventRepository(db),
        daily_clearance_service=DailyClearanceService(
            daily_problem_repository=daily_problem_repository,
            knowledge_point_repository=knowledge_point_repository,
            plan_repository=plan_repository,
            task_repository=task_repository,
            content_generation_service=content_generation_service,
        ),
    )


def _format_sse(event_name: str, payload: dict) -> str:
    return f"event: {event_name}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/message")
async def send_message(
    payload: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Send a user message and stream assistant reply."""
    service = get_chat_service(db)

    async def event_stream():
        async for event in service.stream_message(
            current_user=current_user,
            message=payload.message,
            session_id=payload.session_id,
        ):
            yield _format_sse(event["event"], event["data"])

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ChatSessionResponse]:
    """List chat sessions for current user."""
    return await get_chat_service(db).list_sessions(current_user=current_user)


@router.get("/sessions/{session_id}/messages", response_model=list[ChatHistoryMessageResponse])
async def list_session_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ChatHistoryMessageResponse]:
    """List one session's message history."""
    return await get_chat_service(db).list_messages(
        current_user=current_user,
        session_id=session_id,
    )
