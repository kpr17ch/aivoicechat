"""Ensure the local PostgreSQL database exists and is reachable."""

from __future__ import annotations

import asyncio
import sys
from typing import Any

import asyncpg
from sqlalchemy.engine.url import make_url

from app.core.config import get_settings


async def ensure_database() -> None:
    """Create the configured database if it does not already exist."""
    settings = get_settings()
    url = make_url(settings.database_url)

    if url.get_backend_name() != "postgresql":
        print(
            f"[backend] Skipping database bootstrap for non-postgres URL: {settings.database_url}",
            file=sys.stderr,
        )
        return

    host = url.host or "localhost"
    port = url.port or 5432
    user = url.username or ""
    password = url.password or ""
    database = url.database

    if not database:
        raise SystemExit("[backend] DATABASE_URL must include a database name")

    print(f"[backend] Ensuring database '{database}' exists on {host}:{port}")

    try:
        connection = await asyncpg.connect(
            host=host,
            port=port,
            user=user or None,
            password=password or None,
            database="postgres",
        )
    except (ConnectionError, OSError) as exc:
        raise SystemExit(
            f"[backend] Could not reach Postgres at {host}:{port}. "
            "Start your local server or adjust DATABASE_URL."
        ) from exc
    except asyncpg.InvalidCatalogNameError:
        raise SystemExit(
            "[backend] The control database 'postgres' is not available. "
            "Adjust DATABASE_URL to point at an existing maintenance database."
        )

    try:
        exists = await connection.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            database,
        )
        if not exists:
            db_identifier = database.replace('"', '""')
            try:
                await connection.execute(f'CREATE DATABASE "{db_identifier}"')
                print(f"[backend] Created database '{database}'")
            except asyncpg.InsufficientPrivilegeError as exc:
                raise SystemExit(
                    f"[backend] User '{user}' lacks permission to create database '{database}'. "
                    "Create it manually or update DATABASE_URL credentials."
                ) from exc
    finally:
        await connection.close()

    try:
        probe = await asyncpg.connect(
            host=host,
            port=port,
            user=user or None,
            password=password or None,
            database=database,
        )
    except asyncpg.InvalidCatalogNameError as exc:
        raise SystemExit(
            f"[backend] Database '{database}' is not accessible. "
            "Verify it exists and your credentials are correct."
        ) from exc
    finally:
        if "probe" in locals():
            await probe.close()


def main(args: list[str] | None = None) -> Any:  # noqa: D401 - CLI entry point
    """CLI entry point."""
    return asyncio.run(ensure_database())


if __name__ == "__main__":
    main(sys.argv[1:])
