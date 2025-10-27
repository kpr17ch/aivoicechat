"""Alembic configuration for async SQLModel migrations."""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel

from app.core.config import get_settings
from app.models import AssistantSettings, InstructionTemplate  # noqa: F401

settings = get_settings()
config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def do_run_migrations() -> None:
        async with connectable.connect() as connection:  # type: ignore[call-arg]
            await connection.run_sync(
                lambda sync_connection: context.configure(
                    connection=sync_connection,
                    target_metadata=target_metadata,
                )
            )
            await connection.run_sync(lambda sync_connection: context.run_migrations())

    import asyncio

    asyncio.run(do_run_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
