"""JWT helpers for Day 2 authentication."""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


def create_access_token(*, user_id: str, phone: str) -> str:
    """Create a signed JWT for the authenticated user."""
    expire_at = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "phone": phone,
        "exp": expire_at,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])


def is_token_invalid(token: str) -> bool:
    """Lightweight helper used by callers that need a boolean result."""
    try:
        decode_access_token(token)
    except JWTError:
        return True
    return False
