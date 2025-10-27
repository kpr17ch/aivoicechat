"""Instruction template model."""

from typing import Optional

from sqlmodel import Field, SQLModel


class InstructionTemplate(SQLModel, table=True):
    """Reusable prompt template."""

    __tablename__ = "instruction_templates"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True, unique=True)
    description: str = Field(max_length=500)
    default_instructions: str
    category: str = Field(default="general", max_length=50)
