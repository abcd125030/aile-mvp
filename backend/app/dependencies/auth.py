"""Authentication dependencies."""

import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import decode_access_token
from app.core.exceptions import unauthorized
from app.db.session import get_db
from app.repositories.user_repository import UserRepository

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Resolve the current user from a bearer token."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized("未提供有效的访问令牌")

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("JWT 缺少 sub")
        parsed_user_id = uuid.UUID(user_id)
    except (JWTError, ValueError) as exc:
        raise unauthorized("访问令牌无效或已过期") from exc

    user = await UserRepository(db).get_by_id(parsed_user_id)
    if user is None:
        raise unauthorized("访问令牌无效或已过期")

    return user
