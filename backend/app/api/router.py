"""API router — aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.endpoints.health import router as health_router
from app.api.endpoints.analyze import router as analyze_router
from app.api.endpoints.cover_letter import router as cover_letter_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(analyze_router, tags=["analysis"])
api_router.include_router(cover_letter_router, tags=["cover-letter"])
