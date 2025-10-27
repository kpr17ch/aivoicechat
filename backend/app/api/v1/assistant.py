"""Assistant CRUD endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.assistant import AssistantSettingsResponse, AssistantSettingsUpdate
from app.schemas.instruction_template import InstructionTemplateResponse
from app.services import (
    get_assistant_settings,
    get_instruction_templates,
    update_assistant_settings,
)

router = APIRouter()

AVAILABLE_VOICES = [
    {
        "id": "alloy",
        "name": "Alloy",
        "description": "Neutral und ausgewogen, professionelle Stimme",
    },
    {
        "id": "ash",
        "name": "Ash",
        "description": "Klar und präzise, sachlich und bestimmt",
    },
    {
        "id": "ballad",
        "name": "Ballad",
        "description": "Melodisch und warm, angenehm und beruhigend",
    },
    {
        "id": "cedar",
        "name": "Cedar",
        "description": "Tief und kraftvoll, selbstbewusst und stabil",
    },
    {
        "id": "coral",
        "name": "Coral",
        "description": "Lebhaft und freundlich, energetisch und einladend",
    },
    {
        "id": "echo",
        "name": "Echo",
        "description": "Glatt und modern, zeitgemäß und elegant",
    },
    {
        "id": "marin",
        "name": "Marin",
        "description": "Sanft und einfühlsam, mitfühlend und zugänglich",
    },
    {
        "id": "sage",
        "name": "Sage",
        "description": "Weise und ruhig, gelassen und vertrauensvoll",
    },
    {
        "id": "shimmer",
        "name": "Shimmer",
        "description": "Hell und fröhlich, optimistisch und beschwingt",
    },
    {
        "id": "verse",
        "name": "Verse",
        "description": "Ausdrucksstark und dynamisch, vielseitig",
    },
]


@router.get("/settings", response_model=AssistantSettingsResponse)
async def read_settings(
    session: AsyncSession = Depends(get_session),
) -> AssistantSettingsResponse:
    settings = await get_assistant_settings(session)
    return AssistantSettingsResponse.model_validate(settings)


@router.patch("/settings", response_model=AssistantSettingsResponse)
async def patch_settings(
    payload: AssistantSettingsUpdate,
    session: AsyncSession = Depends(get_session),
) -> AssistantSettingsResponse:
    settings = await get_assistant_settings(session)
    try:
        updated = await update_assistant_settings(session, settings.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return AssistantSettingsResponse.model_validate(updated)


@router.get("/templates", response_model=List[InstructionTemplateResponse])
async def list_templates(
    session: AsyncSession = Depends(get_session),
) -> List[InstructionTemplateResponse]:
    templates = await get_instruction_templates(session)
    return [InstructionTemplateResponse.model_validate(row) for row in templates]


@router.get("/voices")
async def list_voices() -> List[dict]:
    return AVAILABLE_VOICES
