"""User-facing schemas."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class CurrentPlanSnapshot(BaseModel):
    """Current plan summary embedded in the user profile."""

    title: str
    status: str


class UserProfileResponse(BaseModel):
    """Authenticated user profile."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    phone: str | None
    nickname: str
    grade: str
    textbook_version: str
    target_university: str | None = None
    settings: dict[str, Any]
    current_plan_id: str | None = None
    current_plan_snapshot: CurrentPlanSnapshot | None = None


class UpdateUserRequest(BaseModel):
    """Mutable profile fields for the MVP."""

    nickname: str | None = None
    grade: str | None = None
    textbook_version: str | None = None
    target_university: str | None = None
    settings: dict[str, Any] | None = None
