"""Authentication service."""

import re

from app.core.auth import create_access_token
from app.core.exceptions import bad_request
from app.repositories.user_repository import UserRepository

PHONE_PATTERN = re.compile(r"^1\d{10}$")


class AuthService:
    """Handle MVP login with a mock SMS code."""

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def login(self, *, phone: str, sms_code: str):
        if not PHONE_PATTERN.match(phone):
            raise bad_request("手机号格式不正确")

        if sms_code != "8888":
            raise bad_request("验证码错误")

        user = await self.user_repository.get_by_phone(phone)
        is_new_user = user is None
        if user is None:
            user = await self.user_repository.create_default_user(phone)

        token = create_access_token(user_id=str(user.id), phone=user.phone or "")
        return user, token, is_new_user
