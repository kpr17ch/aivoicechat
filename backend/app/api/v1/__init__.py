"""Versioned API router."""

from fastapi import APIRouter

from app.api.v1 import assistant, conversations, settings

api_router = APIRouter()
api_router.include_router(assistant.router, prefix="/assistant", tags=["assistant"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])

__all__ = ["api_router"]
