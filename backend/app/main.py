"""FastAPI entrypoint for the voice assistant configuration service."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from structlog.stdlib import BoundLogger, LoggerFactory

from app.api.router import api_router
from app.api.v1 import twilio
from app.core.config import get_settings
from app.core.twilio_logging import log_event
from app.db.session import AsyncSessionMaker, init_db
from app.services import initialize_default_templates
from app.websockets.media_stream import handle_media_stream

settings = get_settings()


def configure_logging() -> None:
    """Configure structlog with standard logging integration."""
    log_level = getattr(logging, settings.logging.level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
    )
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            (
                structlog.processors.JSONRenderer()
                if settings.logging.json_logs
                else structlog.dev.ConsoleRenderer()
            ),
        ],
        wrapper_class=BoundLogger,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup and shutdown routines."""
    configure_logging()
    logger = structlog.get_logger(__name__)
    logger.info("startup.begin")
    await init_db()
    async with AsyncSessionMaker() as session:
        await initialize_default_templates(session)
    logger.info("startup.complete")
    log_event("Configuration", {
        "audio_recording": "enabled" if settings.enable_audio_recording else "disabled",
        "recordings_dir": settings.recordings_dir if settings.enable_audio_recording else "N/A",
        "openai_model": settings.openai_realtime_model,
        "port": settings.port
    }, "INFO")
    yield
    logger.info("shutdown.complete")


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)
app.include_router(twilio.router)


@app.websocket("/media-stream")
async def media_stream_websocket(websocket: WebSocket):
    await handle_media_stream(websocket)
