# Umgebungsvariablen Setup

## Gmail SMTP E-Mail-Tool

Um das E-Mail-Versand-Feature zu nutzen, müssen folgende Umgebungsvariablen gesetzt werden:

### Erforderliche Variablen

Füge diese Variablen zu deiner `.env` Datei hinzu:

```env
# Gmail SMTP für E-Mail-Versand
GMAIL_EMAIL=kaiperich@gmail.com
GMAIL_APP_PASSWORD=dein_16_zeichen_app_passwort
ENABLE_EMAIL_TOOL=true
```

### Gmail App-Passwort erstellen

1. **Google Account öffnen**: [myaccount.google.com](https://myaccount.google.com)
2. **Sicherheit** → **2-Faktor-Authentifizierung aktivieren** (falls nicht bereits aktiv)
3. **Sicherheit** → **App-Passwörter**
4. App auswählen: **Mail**
5. Gerät auswählen: **Sonstiges** (z.B. "AI Voice Assistant")
6. **16-stelliges Passwort** wird angezeigt
7. Passwort kopieren und in `.env` als `GMAIL_APP_PASSWORD` einfügen

### Komplettes .env Beispiel

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_azure_openai_api_key_here
OPENAI_REALTIME_URL=https://ai-voicebot-gpt.openai.azure.com/openai/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime-mini
OPENAI_REALTIME_MODEL=gpt-realtime-mini

# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/assistants

# Assistant Configuration
DEFAULT_VOICE=sage
DEFAULT_SYSTEM_INSTRUCTIONS=Du bist ein hilfreicher KI-Assistent.
DEFAULT_GREETING_MESSAGE=
CONVERSATION_TEMPERATURE=0.8
TEMPERATURE=0.8

# Audio Recording
ENABLE_AUDIO_RECORDING=false
RECORDINGS_DIR=recordings

# Frontend CORS
FRONTEND_ORIGINS=http://localhost:3000

# Gmail SMTP für E-Mail-Versand
GMAIL_EMAIL=kaiperich@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
ENABLE_EMAIL_TOOL=true

# Server Configuration
PORT=8000
LOG_LEVEL=INFO
```

## E-Mail-Tool deaktivieren

Falls du das E-Mail-Tool temporär deaktivieren möchtest:

```env
ENABLE_EMAIL_TOOL=false
```

## Testing

1. Server starten: `uvicorn app.main:app --reload`
2. Twilio-Anruf tätigen
3. Beispiel-Command: "Schicke eine E-Mail an test@gmail.com, Betreff ist Test, und der Inhalt ist Hallo Welt"
4. Check Logs für:
   - `Email Tool Call` Event
   - `Email Sent` Event
5. Prüfe dein E-Mail-Postfach

## Troubleshooting

### Fehler: "Username and Password not accepted"

- Stelle sicher, dass 2FA aktiviert ist
- Verwende ein App-Passwort, nicht dein normales Gmail-Passwort
- App-Passwort sollte 16 Zeichen haben (mit oder ohne Leerzeichen)

### Fehler: "SMTP connection failed"

- Prüfe deine Internetverbindung
- Port 587 muss offen sein
- Firewall-Einstellungen prüfen

### E-Mails kommen nicht an

- Prüfe Spam-Ordner
- Stelle sicher, dass die E-Mail-Adresse korrekt ist
- Check Gmail Sent-Ordner zur Bestätigung





