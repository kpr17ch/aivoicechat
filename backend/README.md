# Voice Assistant Backend

FastAPI service that stores AI assistant settings (voice, system instructions, greeting) and
provides APIs for the frontend dashboard and the realtime Twilio bridge.

## Features

- Assistant settings persisted in PostgreSQL (SQLModel/SQLAlchemy)
- Instruction templates with default copy seeded on startup
- REST endpoints for fetching/updating the active assistant, listing templates and available
  voices
- Lightweight defaults endpoint consumed by the realtime gateway
- Complete conversation transcripts as JSON/TXT in `backend/transcripts/`

## Tooling

- Python 3.11+
- FastAPI + SQLModel + Alembic
- PostgreSQL (via Docker Compose)

Install dependencies locally:

```bash
pip install -r requirements.txt
```

> Tipp: Im Projekt-Root steht mit `npm start` ein kompletter Dev-Launcher bereit,
> der automatisch ein Virtualenv erstellt, die Datenbank vorbereitet und das
> Backend (plus Frontend) startet.

Run the API during development:

```bash
uvicorn app.main:app --reload
```

## Environment

Environment variables are consolidated at the repository root. Copy `.env.example` to `.env`
and adjust the values you need:

- `OPENAI_API_KEY` – secret used for all OpenAI requests (required)
- `OPENAI_REALTIME_URL` – realtime endpoint (set to your Azure deployment if applicable)
- `DATABASE_URL` – async SQLAlchemy URL for Postgres (defaults to the Docker service)
- `FRONTEND_ORIGINS` – CORS allow list for the dashboard (defaults to `http://localhost:3000`)

## API Overview

- `GET /api/v1/assistant/settings` – fetch current assistant settings
- `PATCH /api/v1/assistant/settings` – update assistant settings
- `GET /api/v1/assistant/templates` – list instruction templates
- `GET /api/v1/assistant/voices` – list available realtime voices
- `GET /api/v1/settings/` – returns voice/instructions/greeting for realtime bridge

## Docker Compose

Use `docker-compose.yml` to spin up backend, frontend, and Postgres:

```bash
docker compose up --build
```

This will expose the backend at `http://localhost:8000` and the frontend at
`http://localhost:3000`.
