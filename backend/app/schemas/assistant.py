"""Assistant settings schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AssistantSettingsBase(BaseModel):
    voice: str = Field(default="sage")
    system_instructions: str = Field(default="")
    greeting_message: Optional[str] = Field(default=None)
    template_name: str = Field(default="allgemein")
    phone_number: Optional[str] = Field(default=None)


class AssistantSettingsCreate(AssistantSettingsBase):
    pass


class AssistantSettingsUpdate(BaseModel):
    voice: Optional[str] = None
    system_instructions: Optional[str] = None
    greeting_message: Optional[str] = None
    template_name: Optional[str] = None
    phone_number: Optional[str] = None


class AssistantSettingsResponse(AssistantSettingsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
