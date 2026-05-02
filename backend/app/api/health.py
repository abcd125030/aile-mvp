"""Health check endpoint for verifying infrastructure connectivity."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_db

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    """Check PostgreSQL and Redis connectivity.

    Returns 200 if all services are healthy, 503 if any service is unreachable.
    """
    services: dict[str, str] = {}
    healthy = True

    # Check PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        services["postgres"] = "ok"
    except Exception as e:
        services["postgres"] = f"error: {e}"
        healthy = False

    # Check Redis
    try:
        redis = Redis.from_url(settings.REDIS_URL)
        try:
            pong = await redis.ping()
            if pong:
                services["redis"] = "ok"
            else:
                services["redis"] = "error: PING returned False"
                healthy = False
        finally:
            await redis.aclose()
    except Exception as e:
        services["redis"] = f"error: {e}"
        healthy = False

    payload = {
        "status": "healthy" if healthy else "unhealthy",
        "services": services,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    status_code = 200 if healthy else 503
    return JSONResponse(content=payload, status_code=status_code)
