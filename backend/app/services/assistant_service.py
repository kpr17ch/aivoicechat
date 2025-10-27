"""Assistant service for persistence operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import AssistantSettings, InstructionTemplate
from app.schemas.assistant import AssistantSettingsUpdate


async def get_instruction_templates(session: AsyncSession) -> list[InstructionTemplate]:
    result = await session.execute(select(InstructionTemplate))
    return list(result.scalars().all())


async def get_instruction_template_by_name(
    session: AsyncSession, name: str
) -> Optional[InstructionTemplate]:
    result = await session.execute(
        select(InstructionTemplate).where(InstructionTemplate.name == name)
    )
    return result.scalar_one_or_none()


async def initialize_default_templates(session: AsyncSession) -> None:
    templates = [
        {
            "name": "allgemein",
            "description": "Allgemeiner AI-Assistent",
            "default_instructions": (
                "Du bist ein hilfreicher und vielseitiger AI-Assistent. "
                "Passe dich flexibel an die Bedürfnisse deines Gesprächspartners an."
            ),
            "category": "general",
        },
        {
            "name": "sales",
            "description": "Sales-Assistent",
            "default_instructions": (
                "Du bist ein enthusiastischer Sales-Assistent. "
                "Erkenne Bedürfnisse und hebe Vorteile hervor."
            ),
            "category": "sales",
        },
        {
            "name": "support",
            "description": "Support-Assistent",
            "default_instructions": (
                "Du bist ein technischer Support-Assistent. "
                "Analysiere Probleme und leite Schritt für Schritt an."
            ),
            "category": "support",
        },
    ]

    for template in templates:
        existing = await get_instruction_template_by_name(session, template["name"])
        if not existing:
            session.add(InstructionTemplate(**template))
    await session.commit()


async def get_assistant_settings(
    session: AsyncSession, phone_number: Optional[str] = None
) -> AssistantSettings:
    query = select(AssistantSettings)
    if phone_number:
        query = query.where(AssistantSettings.phone_number == phone_number)
    result = await session.execute(query)
    settings = result.scalar_one_or_none()
    if settings:
        return settings

    template = await get_instruction_template_by_name(session, "allgemein")
    config = get_settings()
    default_instructions = (
        template.default_instructions if template else config.default_system_instructions
    )
    settings = AssistantSettings(
        voice=config.default_voice,
        system_instructions=default_instructions,
        greeting_message=config.default_greeting_message,
        template_name="allgemein",
        phone_number=phone_number,
    )
    session.add(settings)
    await session.commit()
    await session.refresh(settings)
    return settings


async def update_assistant_settings(
    session: AsyncSession,
    settings_id: int,
    payload: AssistantSettingsUpdate,
) -> AssistantSettings:
    result = await session.execute(
        select(AssistantSettings).where(AssistantSettings.id == settings_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        raise ValueError("Assistant settings not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings, key, value)
    settings.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(settings)
    return settings
