import json

from app.core.twilio_logging import log_event


async def send_initial_conversation_item(openai_ws, greeting_message: str | None = None):
    if not greeting_message:
        greeting_message = "Hello there! I am an AI voice assistant. How can I help you?"

    initial_conversation_item = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": f"Greet the user with '{greeting_message}'"
                }
            ]
        }
    }
    await openai_ws.send(json.dumps(initial_conversation_item))
    await openai_ws.send(json.dumps({"type": "response.create"}))


async def initialize_session(openai_ws, is_azure: bool, settings: dict, model: str, temperature: float):
    from app.core.config import get_settings
    app_settings = get_settings()
    
    voice = settings.get('voice', 'sage')
    instructions = settings.get('system_instructions', 'Du bist ein hilfreicher KI-Assistent.')
    greeting_message = settings.get('greeting_message')
    transcription_model = app_settings.openai_transcription_model
    transcription_language = app_settings.transcription_language
    transcription_prompt_text = app_settings.transcription_prompt
    phrase_hints = app_settings.transcription_phrase_hints

    if is_azure and not transcription_model:
        transcription_model = "gpt-4o-mini-transcribe"

    number_guidelines = (
        "Achte besonders auf Telefonnummern, Codes und Bestellnummern. "
        "Für deutsche Telefonnummern verwende das Format '+49 …' oder '0 …', wiederhole alle Ziffern einzeln "
        "und bestätige die komplette Nummer mit dem Nutzer. "
        "Wenn eine Vorwahl nicht plausibel klingt oder Ziffern fehlen, bitte aktiv um Wiederholung. "
        "Verwende deutsche Zahlwörter (null, eins, zwo, zwei, drei, vier, fünf, sechs, sieben, acht, neun) "
        "und überführe sie in korrekte Ziffern."
    )

    if app_settings.enable_email_tool:
        instructions += "\n\nWenn der Nutzer eine E-Mail senden möchte, extrahiere Empfänger, Betreff und Inhalt aus der Anfrage und rufe send_email auf. Wenn Informationen fehlen (z.B. nur 'Schick eine E-Mail'), frage gezielt nach den fehlenden Feldern. Nach erfolgreichem Versand bestätige kurz: 'E-Mail an [Empfänger] wurde versendet.'"

    instructions += f"\n\n{number_guidelines}"

    tools = []
    if app_settings.enable_email_tool:
        tools.append({
            "type": "function",
            "name": "send_email",
            "description": "Send an email on behalf of the user. Use this when the user explicitly asks to send an email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line"
                    },
                    "body": {
                        "type": "string",
                        "description": "Plain text email body content"
                    }
                },
                "required": ["to", "subject", "body"],
                "additionalProperties": False
            }
        })

    log_event("OpenAI Session Initialization", {
        "voice": voice,
        "instructions": instructions[:100] + "...",
        "greeting": greeting_message or "None",
        "temperature": temperature,
        "is_azure": is_azure,
        "tools_enabled": len(tools) > 0
    })

    if is_azure:
        session_update = {
            "type": "session.update",
            "session": {
                "modalities": ["audio", "text"],
                "instructions": instructions,
                "voice": voice,
                "input_audio_format": "g711_ulaw",
                "output_audio_format": "g711_ulaw",
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 200
                },
                "temperature": temperature,
                "tools": tools,
                "tool_choice": "auto"
            }
        }
        transcription_payload: dict[str, str] = {}
        if transcription_model:
            transcription_payload["model"] = transcription_model
        if transcription_language:
            transcription_payload["language"] = transcription_language
        if transcription_prompt_text:
            transcription_payload["prompt"] = transcription_prompt_text
        if transcription_payload:
            session_update["session"]["input_audio_transcription"] = transcription_payload
    else:
        session_update = {
            "type": "session.update",
            "session": {
                "type": "realtime",
                "model": model,
                "output_modalities": ["audio"],
                "audio": {
                    "input": {
                        "format": {"type": "audio/pcmu"},
                        "turn_detection": {"type": "server_vad"}
                    },
                    "output": {
                        "format": {"type": "audio/pcmu"},
                        "voice": voice
                    }
                },
                "instructions": instructions,
                "temperature": temperature,
                "tools": tools,
                "tool_choice": "auto"
            }
        }
        if transcription_model:
            transcription_payload = {"model": transcription_model}
            if phrase_hints and not is_azure:
                transcription_payload["phrases"] = phrase_hints
            session_update["session"]["audio"]["input"]["transcription"] = transcription_payload

    if transcription_prompt_text:
        prompt_preview = transcription_prompt_text[:160] + ("…" if len(transcription_prompt_text) > 160 else "")
    else:
        prompt_preview = None

    if is_azure:
        phrase_bias_mode = "prompt" if transcription_prompt_text else "disabled"
    else:
        phrase_bias_mode = "list" if phrase_hints else "default"

    log_event("Session Configuration Sent", {
        "model": session_update['session'].get('model', 'N/A'),
        "voice": voice,
        "temperature": temperature,
        "audio_format": session_update['session'].get('output_audio_format', session_update['session'].get('audio', {}).get('output', {}).get('format', 'N/A')),
        "transcription_model": transcription_model or "disabled",
        "transcription_language": transcription_language or "auto",
        "transcription_prompt": prompt_preview,
        "phrase_bias_mode": phrase_bias_mode
    }, "SUCCESS")

    await openai_ws.send(json.dumps(session_update))

    if greeting_message:
        log_event("Greeting Message", {"message": greeting_message})
        await send_initial_conversation_item(openai_ws, greeting_message)
