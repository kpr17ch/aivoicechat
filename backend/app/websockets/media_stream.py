import json
import base64
import asyncio
from pathlib import Path

import websockets
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect

from app.core.config import get_settings
from app.core.twilio_logging import log_event, format_openai_event
from app.services.assistant_service import get_assistant_settings
from app.services.openai_service import initialize_session
from app.services.audio_service import finalize_audio_segment, decode_audio_chunk
from app.db.session import AsyncSessionMaker

settings = get_settings()

LOG_EVENT_TYPES = [
    'error', 'response.content.done', 'rate_limits.updated',
    'response.done', 'input_audio_buffer.committed',
    'input_audio_buffer.speech_stopped', 'input_audio_buffer.speech_started',
    'session.created', 'session.updated'
]
LOG_AUDIO_CHUNKS = False
SHOW_TIMING_MATH = False


async def handle_media_stream(websocket: WebSocket):
    log_event("WebSocket Connection", {"status": "Client connected"}, "SUCCESS")
    await websocket.accept()

    async with AsyncSessionMaker() as session:
        assistant_settings = await get_assistant_settings(session)
        settings_dict = {
            'voice': assistant_settings.voice,
            'system_instructions': assistant_settings.system_instructions,
            'greeting_message': assistant_settings.greeting_message,
            'temperature': settings.conversation_temperature
        }

    realtime_url = settings.openai_realtime_url
    is_azure = "azure.com" in realtime_url
    if realtime_url.startswith("https://"):
        realtime_url = "wss://" + realtime_url[len("https://"):]
    elif realtime_url.startswith("http://"):
        realtime_url = "ws://" + realtime_url[len("http://"):]

    headers = {}
    if is_azure:
        headers["api-key"] = settings.openai_api_key
    else:
        headers["Authorization"] = f"Bearer {settings.openai_api_key}"
        headers["OpenAI-Beta"] = "realtime=v1"

    connect_params = {
        "additional_headers": headers,
        "open_timeout": 10
    }
    if not is_azure:
        connect_params["subprotocols"] = ["openai-realtime-v1"]

    async with websockets.connect(realtime_url, **connect_params) as openai_ws:
        await initialize_session(
            openai_ws,
            is_azure,
            settings_dict,
            settings.openai_realtime_model,
            settings.temperature
        )

        stream_sid = None
        latest_media_timestamp = 0
        last_assistant_item = None
        mark_queue = []
        response_start_timestamp_twilio = None

        conversation_stats = {
            'turn_number': 0,
            'total_tokens': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_input_text_tokens': 0,
            'total_input_audio_tokens': 0,
            'total_output_text_tokens': 0,
            'total_output_audio_tokens': 0,
            'total_cached_tokens': 0,
            'last_response_tokens': {}
        }

        stream_recording_dir: Path | None = None
        current_audio_buffer = bytearray()
        audio_segment_index = 0
        audio_buffer_lock = asyncio.Lock()

        async def finalize_segment(reason: str) -> None:
            nonlocal audio_segment_index
            async with audio_buffer_lock:
                audio_segment_index = await finalize_audio_segment(
                    current_audio_buffer,
                    audio_segment_index,
                    stream_recording_dir,
                    reason,
                    settings.enable_audio_recording
                )

        async def receive_from_twilio():
            nonlocal stream_sid, latest_media_timestamp, stream_recording_dir, audio_segment_index
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data['event'] == 'media' and openai_ws.state.name == 'OPEN':
                        latest_media_timestamp = int(data['media']['timestamp'])
                        audio_append = {
                            "type": "input_audio_buffer.append",
                            "audio": data['media']['payload']
                        }
                        await openai_ws.send(json.dumps(audio_append))

                        if settings.enable_audio_recording and stream_recording_dir is not None:
                            raw_chunk = decode_audio_chunk(data['media']['payload'])
                            if raw_chunk:
                                async with audio_buffer_lock:
                                    current_audio_buffer.extend(raw_chunk)
                    elif data['event'] == 'start':
                        stream_sid = data['start']['streamSid']
                        log_event("Stream Started", {
                            "stream_sid": stream_sid,
                            "status": "Twilio media stream active",
                            "audio_recording": "enabled" if settings.enable_audio_recording else "disabled"
                        }, "SUCCESS")
                        if settings.enable_audio_recording:
                            recordings_base = Path(settings.recordings_dir)
                            stream_recording_dir = recordings_base / stream_sid
                            stream_recording_dir.mkdir(parents=True, exist_ok=True)
                            async with audio_buffer_lock:
                                current_audio_buffer.clear()
                            audio_segment_index = 0
                        else:
                            stream_recording_dir = None
                        response_start_timestamp_twilio = None
                        latest_media_timestamp = 0
                        last_assistant_item = None
                    elif data['event'] == 'mark':
                        if mark_queue:
                            mark_queue.pop(0)
            except WebSocketDisconnect:
                log_event("WebSocket Disconnection", {"status": "Client disconnected"}, "WARNING")
                if openai_ws.state.name == 'OPEN':
                    await openai_ws.close()

        async def send_to_twilio():
            nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio, conversation_stats

            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)

                    if response['type'] in LOG_EVENT_TYPES:
                        formatted = format_openai_event(response)

                        if response['type'] == 'response.done':
                            conversation_stats['turn_number'] += 1

                            resp_data = response.get('response', {})
                            usage = resp_data.get('usage', {})

                            current_total = usage.get('total_tokens', 0)
                            current_input = usage.get('input_tokens', 0)
                            current_output = usage.get('output_tokens', 0)

                            input_details = usage.get('input_token_details', {})
                            output_details = usage.get('output_token_details', {})

                            current_input_text = input_details.get('text_tokens', 0)
                            current_input_audio = input_details.get('audio_tokens', 0)
                            current_cached = input_details.get('cached_tokens', 0)
                            current_output_text = output_details.get('text_tokens', 0)
                            current_output_audio = output_details.get('audio_tokens', 0)

                            turn_input = current_input - conversation_stats['total_input_tokens']
                            turn_output = current_output - conversation_stats['total_output_tokens']
                            turn_total = current_total - conversation_stats['total_tokens']

                            turn_input_text = current_input_text - conversation_stats['total_input_text_tokens']
                            turn_input_audio = current_input_audio - conversation_stats['total_input_audio_tokens']
                            turn_output_text = current_output_text - conversation_stats['total_output_text_tokens']
                            turn_output_audio = current_output_audio - conversation_stats['total_output_audio_tokens']
                            turn_cached = current_cached - conversation_stats['total_cached_tokens']

                            conversation_stats['total_tokens'] = current_total
                            conversation_stats['total_input_tokens'] = current_input
                            conversation_stats['total_output_tokens'] = current_output
                            conversation_stats['total_input_text_tokens'] = current_input_text
                            conversation_stats['total_input_audio_tokens'] = current_input_audio
                            conversation_stats['total_output_text_tokens'] = current_output_text
                            conversation_stats['total_output_audio_tokens'] = current_output_audio
                            conversation_stats['total_cached_tokens'] = current_cached

                            formatted['turn_stats'] = {
                                'turn_number': conversation_stats['turn_number'],
                                'this_turn': {
                                    'total': turn_total,
                                    'input': turn_input,
                                    'output': turn_output,
                                    'input_text': turn_input_text,
                                    'input_audio': turn_input_audio,
                                    'output_text': turn_output_text,
                                    'output_audio': turn_output_audio,
                                    'cached': turn_cached
                                },
                                'conversation_total': {
                                    'total': conversation_stats['total_tokens'],
                                    'input': conversation_stats['total_input_tokens'],
                                    'output': conversation_stats['total_output_tokens'],
                                    'input_text': conversation_stats['total_input_text_tokens'],
                                    'input_audio': conversation_stats['total_input_audio_tokens'],
                                    'output_text': conversation_stats['total_output_text_tokens'],
                                    'output_audio': conversation_stats['total_output_audio_tokens'],
                                    'cached': conversation_stats['total_cached_tokens']
                                }
                            }

                        log_event(f"OpenAI Event: {formatted['event_type']}", formatted)

                    if response.get('type') in ['response.output_audio.delta', 'response.audio.delta'] and 'delta' in response:
                        if LOG_AUDIO_CHUNKS:
                            chunk_info = {
                                'response_id': response.get('response_id', 'N/A'),
                                'item_id': response.get('item_id', 'N/A'),
                                'chunk_size': f"{len(response.get('delta', ''))} bytes"
                            }
                            log_event("Audio Chunk Streaming", chunk_info, "DEBUG")

                        audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
                        audio_delta = {
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {
                                "payload": audio_payload
                            }
                        }
                        await websocket.send_json(audio_delta)

                        if response.get("item_id") and response["item_id"] != last_assistant_item:
                            response_start_timestamp_twilio = latest_media_timestamp
                            last_assistant_item = response["item_id"]
                            if SHOW_TIMING_MATH:
                                log_event("Response Timing", {
                                    "start_timestamp": f"{response_start_timestamp_twilio}ms",
                                    "item_id": last_assistant_item
                                }, "DEBUG")

                        await send_mark(websocket, stream_sid)

                    if response.get('type') == 'input_audio_buffer.speech_started':
                        log_event("User Speech Started", {
                            "audio_start_ms": response.get('audio_start_ms', 'N/A'),
                            "item_id": response.get('item_id', 'N/A')
                        }, "INFO")
                        if last_assistant_item:
                            log_event("Interruption", {
                                "action": "Interrupting assistant response",
                                "interrupted_item_id": last_assistant_item
                            }, "WARNING")
                            await handle_speech_started_event()
                    elif response.get('type') == 'input_audio_buffer.committed':
                        await finalize_segment("input_audio_buffer.committed")
            except Exception as e:
                log_event("Stream Error", {"error": str(e), "type": type(e).__name__}, "ERROR")

        async def handle_speech_started_event():
            nonlocal response_start_timestamp_twilio, last_assistant_item

            if mark_queue and response_start_timestamp_twilio is not None:
                elapsed_time = latest_media_timestamp - response_start_timestamp_twilio

                if last_assistant_item:
                    log_event("Response Truncation", {
                        "item_id": last_assistant_item,
                        "elapsed_time": f"{elapsed_time}ms",
                        "action": "Truncating assistant response due to user interruption"
                    }, "INFO")

                    truncate_event = {
                        "type": "conversation.item.truncate",
                        "item_id": last_assistant_item,
                        "content_index": 0,
                        "audio_end_ms": elapsed_time
                    }
                    await openai_ws.send(json.dumps(truncate_event))

                await websocket.send_json({
                    "event": "clear",
                    "streamSid": stream_sid
                })

                mark_queue.clear()
                last_assistant_item = None
                response_start_timestamp_twilio = None

        async def send_mark(connection, stream_sid):
            if stream_sid:
                mark_event = {
                    "event": "mark",
                    "streamSid": stream_sid,
                    "mark": {"name": "responsePart"}
                }
                await connection.send_json(mark_event)
                mark_queue.append('responsePart')

        try:
            await asyncio.gather(receive_from_twilio(), send_to_twilio())
        finally:
            await finalize_segment("connection_closed")
