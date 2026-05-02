"""Authentication schemas."""

from pydantic import BaseModel, Field

from app.schemas.users import UserProfileResponse


class LoginRequest(BaseModel):
    """Phone login request."""

    phone: str = Field(..., examples=["13800000001"])
    sms_code: str = Field(..., examples=["8888"])


class LoginResponse(BaseModel):
    """Phone login response."""

    user: UserProfileResponse
    token: str
    is_new_user: bool
