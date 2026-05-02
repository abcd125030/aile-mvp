"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_v1_router
from app.api.health import router as health_router
from app.core.exceptions import AppHTTPException

app = FastAPI(title="艾乐学伴 MVP", version="0.1.0")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router)
app.include_router(api_v1_router)


@app.exception_handler(AppHTTPException)
async def app_http_exception_handler(_, exc: AppHTTPException) -> JSONResponse:
    """Ensure custom app exceptions always return the same response shape."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
