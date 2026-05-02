"""User profile endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.users import UpdateUserRequest, UserProfileResponse
from app.services.user_service import UserService, build_user_profile_response

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserProfileResponse:
    """Return the authenticated user's profile."""
    return build_user_profile_response(current_user)


@router.put("/me", response_model=UserProfileResponse)
async def update_me(
    payload: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    """Update the authenticated user's profile."""
    service = UserService(UserRepository(db))
    return await service.update_me(current_user=current_user, payload=payload)
