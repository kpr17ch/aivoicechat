from datetime import datetime
from typing import Any


def log_event(event_type: str, data: dict[str, Any], level: str = "INFO") -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    emoji = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "DEBUG": "🔍"
    }.get(level, "📝")

    print(f"\n{emoji} [{timestamp}] {event_type}")

    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'turn_stats':
                print(f"   {key}:")
                turn_stats = value
                print(f"      🔢 Turn #{turn_stats['turn_number']}")
                print("      📊 THIS TURN:")
                this_turn = turn_stats['this_turn']
                print(f"         Total: {this_turn['total']} tokens")
                print(f"         Input: {this_turn['input']} (text: {this_turn['input_text']}, audio: {this_turn['input_audio']}, cached: {this_turn['cached']})")
                print(f"         Output: {this_turn['output']} (text: {this_turn['output_text']}, audio: {this_turn['output_audio']})")
                print("      📈 CONVERSATION TOTAL:")
                conv_total = turn_stats['conversation_total']
                print(f"         Total: {conv_total['total']} tokens")
                print(f"         Input: {conv_total['input']} (text: {conv_total['input_text']}, audio: {conv_total['input_audio']}, cached: {conv_total['cached']})")
                print(f"         Output: {conv_total['output']} (text: {conv_total['output_text']}, audio: {conv_total['output_audio']})")
            elif isinstance(value, str) and len(value) > 100:
                print(f"   {key}: {value[:100]}...")
            elif isinstance(value, dict) and key == 'tokens':
                continue
            else:
                print(f"   {key}: {value}")
    else:
        print(f"   {data}")


def format_openai_event(response: dict) -> dict[str, Any]:
    event_type = response.get('type', 'unknown')
    formatted = {
        'event_type': event_type,
        'event_id': response.get('event_id', 'N/A')
    }

    if event_type == 'response.done':
        resp_data = response.get('response', {})
        usage = resp_data.get('usage', {})
        output = resp_data.get('output', [])

        transcript = None
        if output and len(output) > 0:
            content = output[0].get('content', [])
            if content:
                for item in content:
                    if item.get('type') == 'audio' and 'transcript' in item:
                        transcript = item['transcript']
                        break

        formatted.update({
            'response_id': resp_data.get('id', 'N/A'),
            'status': resp_data.get('status', 'N/A'),
            'voice': resp_data.get('voice', 'N/A'),
            'temperature': resp_data.get('temperature', 'N/A'),
            'transcript': transcript or 'N/A',
            'tokens': {
                'total': usage.get('total_tokens', 0),
                'input': usage.get('input_tokens', 0),
                'output': usage.get('output_tokens', 0),
                'input_details': {
                    'text': usage.get('input_token_details', {}).get('text_tokens', 0),
                    'audio': usage.get('input_token_details', {}).get('audio_tokens', 0),
                    'cached': usage.get('input_token_details', {}).get('cached_tokens', 0),
                },
                'output_details': {
                    'text': usage.get('output_token_details', {}).get('text_tokens', 0),
                    'audio': usage.get('output_token_details', {}).get('audio_tokens', 0),
                }
            }
        })

    elif event_type == 'response.audio.delta':
        delta_size = len(response.get('delta', ''))
        formatted.update({
            'response_id': response.get('response_id', 'N/A'),
            'item_id': response.get('item_id', 'N/A'),
            'audio_chunk_size': f"{delta_size} bytes"
        })

    elif event_type == 'input_audio_buffer.speech_started':
        formatted.update({
            'audio_start_ms': response.get('audio_start_ms', 'N/A'),
            'item_id': response.get('item_id', 'N/A')
        })

    elif event_type == 'input_audio_buffer.speech_stopped':
        formatted.update({
            'audio_end_ms': response.get('audio_end_ms', 'N/A'),
            'item_id': response.get('item_id', 'N/A')
        })

    elif event_type == 'input_audio_buffer.committed':
        formatted.update({
            'previous_item_id': response.get('previous_item_id', 'N/A'),
            'item_id': response.get('item_id', 'N/A')
        })

    elif event_type == 'session.created':
        session = response.get('session', {})
        formatted.update({
            'session_id': session.get('id', 'N/A'),
            'model': session.get('model', 'N/A'),
            'voice': session.get('voice', 'N/A')
        })

    elif event_type == 'session.updated':
        session = response.get('session', {})
        formatted.update({
            'session_id': session.get('id', 'N/A'),
            'model': session.get('model', 'N/A'),
            'voice': session.get('voice', 'N/A'),
            'instructions_preview': session.get('instructions', 'N/A')[:80]
        })

    elif event_type == 'error':
        error = response.get('error', {})
        formatted.update({
            'error_type': error.get('type', 'N/A'),
            'error_code': error.get('code', 'N/A'),
            'error_message': error.get('message', 'N/A')
        })

    return formatted
