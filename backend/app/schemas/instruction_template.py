"""Instruction template schemas."""

from pydantic import BaseModel, Field


class InstructionTemplateResponse(BaseModel):
    id: int
    name: str = Field(description="Template name")
    description: str
    default_instructions: str
    category: str

    model_config = {"from_attributes": True}
