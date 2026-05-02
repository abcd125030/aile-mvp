"""Authentication endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth_service import AuthService
from app.services.user_service import build_user_profile_response

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> LoginResponse:
    """Login with phone number and a mock SMS code."""
    service = AuthService(UserRepository(db))
    user, token, is_new_user = await service.login(phone=payload.phone, sms_code=payload.sms_code)
    return LoginResponse(
        user=build_user_profile_response(user),
        token=token,
        is_new_user=is_new_user,
    )
