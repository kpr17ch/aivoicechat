AI Voice Assistant – Development Shortcuts
=========================================

Lokale Entwicklung ohne Docker
------------------------------

1. Stelle sicher, dass ein lokaler PostgreSQL‐Server läuft (z. B. via `brew services start postgresql@16`).  
   Die Standardverbindung erwartet `postgresql+asyncpg://postgres:postgres@localhost:5432/assistants`.
2. `cp .env.example .env` und alle benötigten Secrets eintragen.
3. Abhängigkeiten installieren: `npm run install:all`.
4. Starte Frontend **und** Backend parallel: `npm start`.

Der Startbefehl führt automatisch folgende Schritte aus:

- Initialisiert bei Bedarf `backend/.venv`.
- Installiert fehlende Python-Abhängigkeiten.
- Legt die Datenbank `assistants` an (falls noch nicht vorhanden) und führt `alembic upgrade head` aus.
- Startet `uvicorn` mit Reload sowie das Next.js-Frontend.

Alternative: Docker Compose
---------------------------

- Kompletten Stack starten: `npm run start:docker`
- Nur Datenbank-Container: `npm run dev:db`

Hinweise
--------

- `backend/scripts/start_local.sh` akzeptiert optional `PYTHON_BIN=/pfad/zu/python`.
- Für spezielle Migrationen oder Daten-Seeding können wie gewohnt Alembic- oder SQLModel-Tools verwendet werden.
- Gesprächstranskripte landen automatisch als `.json` und `.txt` unter `backend/transcripts/<stream>.{json,txt}`; die Logs zeigen dazu `conversation.user`/`conversation.assistant` mit vollständigem Text und Turn-Statistiken.
- Sprachmodell-Biasing und Numeric-Normalisierung sorgen dafür, dass Telefonnummern/Bestellnummern in deutscher Sprache zuverlässiger erkannt, normalisiert (`+49…`) und validiert werden.
- Für Azure-Realtime kannst du `TRANSCRIPTION_PROMPT` / `TRANSCRIPTION_LANGUAGE` setzen; Standard ist ein deutscher Bias-Prompt plus Sprache `de` für korrekte +49-Vorwahlen.
