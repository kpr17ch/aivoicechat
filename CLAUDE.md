# AI Voice Chat Bot - Projekt Kontext

## Überblick
Dies ist ein AI-gestützter Kundenservice-Bot, der über Telefon funktioniert. Anrufer können natürliche Gespräche auf Deutsch führen, wobei das System in Echtzeit antwortet.

## Aktuelle Infrastruktur
- **Twilio**: US-Telefonnummer (Trial) mit TwiML-App
- **FastAPI**: Server mit `/voice` Endpunkt
- **ngrok**: Tunnel für öffentlichen Zugang
- **APIs**: OpenAI (Whisper STT + GPT-4o mini), ElevenLabs (deutsche Stimmen)

## Ziel-Architektur
```
Telefon-Audio → Twilio → WebSocket → FastAPI
                                      ↓
                               Speech-to-Text (Whisper)
                                      ↓
                               LLM Response (GPT-4o mini)
                                      ↓
                               Text-to-Speech (ElevenLabs)
                                      ↓
                        WebSocket → Twilio → zurück zum Anrufer
```

## Technische Implementierung

### 1. Real-time Media Streaming Setup
- **WebSocket Verbindung**: Twilio sendet Live-Audio über WebSocket
- **Audio Format**: Base64-kodiertes Audio in JSON Messages
- **Message Types**: "connected", "start", "media", "closed"
- **Encoding**: μ-law (8kHz) Audio von Twilio

### 2. FastAPI WebSocket Handler
```python
# Benötigt:
from fastapi import FastAPI, WebSocket
import asyncio
import json
import base64
```

### 3. Audio Processing Pipeline
1. **Eingehend**: Base64 → Bytes → Whisper STT → Text
2. **Ausgehend**: Text → ElevenLabs TTS → Audio → Base64 → Twilio

### 4. TwiML Konfiguration
- `<Connect>` Verb für WebSocket-Verbindung
- `<Stream>` für Media-Streaming
- WebSocket URL zeigt auf FastAPI `/media` Endpunkt

## Umgebungsvariablen
```
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
```

## Kritische Implementierungsdetails

### WebSocket Message Handling
```python
# Message Format von Twilio:
{
    "event": "media",
    "sequenceNumber": "4",
    "media": {
        "track": "inbound",
        "chunk": "4",
        "timestamp": "1234",
        "payload": "base64_encoded_audio"
    }
}
```

### Audio Chunks Processing
- Twilio sendet Audio in kleinen Chunks (320 Bytes μ-law)
- Chunks müssen gesammelt werden für Whisper (mindestens 1-2 Sekunden)
- Puffering-Strategie notwendig für kontinuierliche Verarbeitung

### Response Streaming zurück zu Twilio
```python
# Format für ausgehende Audio:
{
    "event": "media",
    "streamSid": stream_sid,
    "media": {
        "payload": base64_encoded_response_audio
    }
}
```

## Entwicklungsphasen

### Phase 1: WebSocket Setup
- FastAPI WebSocket Endpunkt `/media`
- TwiML Update für `<Stream>` 
- Audio-Empfang und -Logging

### Phase 2: STT Integration
- Audio-Chunk-Buffering implementieren
- Whisper API Integration
- Transkription-Logging

### Phase 3: LLM Integration
- GPT-4o mini für deutsche Antworten
- Kontext-Management für Gespräche
- Antwort-Generierung

### Phase 4: TTS & Response
- ElevenLabs deutsche Stimme
- Audio-Format-Konvertierung für Twilio
- WebSocket Response-Streaming

### Phase 5: Optimierung
- Latenz-Reduzierung
- Error Handling
- Qualitäts-Verbesserungen

## Erwartete Herausforderungen

1. **Audio-Format-Konvertierung**: μ-law ↔ WAV/MP3 für APIs
2. **Latenz-Management**: Echtzeit-Gefühl trotz API-Aufrufe
3. **Chunk-Synchronisation**: Audio-Pieces richtig zusammenfügen
4. **Error Recovery**: Robuste Behandlung von API-Fehlern
5. **Conversation State**: Kontext zwischen WebSocket-Messages

## Testingn & Deployment
- **Lokal**: ngrok für Twilio-Webhooks
- **Testing**: Echte Telefonanrufe erforderlich
- **Monitoring**: WebSocket-Verbindungen und API-Latenz
- **Scaling**: Eventuelle Migration von FastAPI zu async Framework

## Hilfreiche Ressourcen
- Twilio Media Streams: https://www.twilio.com/docs/voice/media-streams
- Whisper API: https://platform.openai.com/docs/guides/speech-to-text
- ElevenLabs API: https://elevenlabs.io/docs/api-reference/text-to-speech