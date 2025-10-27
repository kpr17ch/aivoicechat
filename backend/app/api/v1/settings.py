"""Assistant defaults endpoint for realtime consumers."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.services import get_assistant_settings

router = APIRouter()


async def _payload(session: AsyncSession) -> dict:
    settings = await get_assistant_settings(session)
    return {
        "voice": settings.voice,
        "system_instructions": settings.system_instructions,
        "greeting_message": settings.greeting_message,
    }


@router.get("/")
async def read_defaults(session: AsyncSession = Depends(get_session)) -> dict:
    """Return assistant configuration for external clients."""
    return await _payload(session)


@router.get("/assistant")
async def read_defaults_alias(session: AsyncSession = Depends(get_session)) -> dict:
    """Alias endpoint matching earlier client expectations."""
    return await _payload(session)
