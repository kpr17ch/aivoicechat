"""Versioned API router."""

from fastapi import APIRouter

from app.api.v1 import assistant, settings

api_router = APIRouter()
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])

__all__ = ["api_router"]
