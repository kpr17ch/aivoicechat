"""Database session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.core.config import get_settings
from app.models import AssistantSettings  # noqa: F401
from app.models import ConversationSession  # noqa: F401
from app.models import InstructionTemplate  # noqa: F401

settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False, future=True)

AsyncSessionMaker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession, autoflush=False
)


async def init_db() -> None:
    """Create database schema."""
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a request-scoped session."""
    async with AsyncSessionMaker() as session:
        yield session
