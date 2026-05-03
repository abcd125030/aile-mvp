"""API route registration."""

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.content import router as content_router
from app.api.diagnosis_reports import router as diagnosis_reports_router
from app.api.exercises import router as exercises_router
from app.api.users import router as users_router
from app.api.knowledge_points import router as knowledge_points_router
from app.api.plans import router as plans_router
from app.api.tasks import router as tasks_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(content_router)
api_v1_router.include_router(diagnosis_reports_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(plans_router)
api_v1_router.include_router(tasks_router)
api_v1_router.include_router(knowledge_points_router)
api_v1_router.include_router(exercises_router)

__all__ = ["api_v1_router"]
