"""Health check endpoint."""

from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint — verifies the service is running.

    Returns:
        Basic health status and version info.
    """
    return {
        "status": "ok",
        "version": settings.app_version,
        "environment": settings.app_env,
    }
