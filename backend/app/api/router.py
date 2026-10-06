"""API router — aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.endpoints.health import router as health_router
from app.api.endpoints.analyze import router as analyze_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(analyze_router, tags=["analysis"])
