"""User profile service."""

from copy import deepcopy

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.users import CurrentPlanSnapshot, UpdateUserRequest, UserProfileResponse


def build_user_profile_response(user: User) -> UserProfileResponse:
    """Convert a user ORM object into the API response model."""
    settings = deepcopy(user.settings or {})
    target_university = settings.get("target_university")

    current_plan_snapshot = None
    if user.current_plan is not None:
        current_plan_snapshot = CurrentPlanSnapshot(
            title=user.current_plan.title,
            status=user.current_plan.status,
        )

    return UserProfileResponse(
        id=str(user.id),
        phone=user.phone,
        nickname=user.nickname,
        grade=user.grade,
        textbook_version=user.textbook_version,
        target_university=target_university,
        settings=settings,
        current_plan_id=str(user.current_plan_id) if user.current_plan_id else None,
        current_plan_snapshot=current_plan_snapshot,
    )


class UserService:
    """User profile reads and updates."""

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def get_me(self, current_user: User) -> UserProfileResponse:
        return build_user_profile_response(current_user)

    async def update_me(
        self,
        *,
        current_user: User,
        payload: UpdateUserRequest,
    ) -> UserProfileResponse:
        if payload.nickname is not None:
            current_user.nickname = payload.nickname
        if payload.grade is not None:
            current_user.grade = payload.grade
        if payload.textbook_version is not None:
            current_user.textbook_version = payload.textbook_version

        merged_settings = deepcopy(current_user.settings or {})
        if payload.settings is not None:
            merged_settings.update(payload.settings)
        if payload.target_university is not None:
            merged_settings["target_university"] = payload.target_university
        current_user.settings = merged_settings

        saved_user = await self.user_repository.save(current_user)
        refreshed_user = await self.user_repository.get_by_id(saved_user.id)
        return build_user_profile_response(refreshed_user or saved_user)
