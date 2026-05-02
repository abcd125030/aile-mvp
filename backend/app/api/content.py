"""Content generation endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.repositories.content_package_repository import ContentPackageRepository
from app.repositories.knowledge_point_repository import KnowledgePointRepository
from app.schemas.content import ContentGenerateRequest, ContentGenerateResponse
from app.services.content_generation_service import ContentGenerationService
from app.services.llm import LLMService

router = APIRouter(prefix="/content", tags=["content"])


def get_content_generation_service(db: AsyncSession) -> ContentGenerationService:
    return ContentGenerationService(
        llm_service=LLMService(),
        knowledge_point_repository=KnowledgePointRepository(db),
        content_package_repository=ContentPackageRepository(db),
    )


@router.post("/generate", response_model=ContentGenerateResponse)
async def generate_content(
    payload: ContentGenerateRequest,
    _: object = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ContentGenerateResponse:
    """Generate explain content sections for knowledge points."""
    return await get_content_generation_service(db).generate(payload=payload)
