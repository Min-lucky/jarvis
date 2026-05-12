import json
import uuid
from datetime import datetime

def make_envelope(messages, user_id="default", extra_context=None):
    """Wrap a list of message dicts (role/content) into an MCP envelope.
    `messages` should be a list like [{"role": "user", "content": "..."}, ...].
    Returns a JSON string.
    """
    envelope = {
        "metadata": {
            "uid": user_id,
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "model": "gpt-oss-120b",
            "context": extra_context or {}
        },
        "payload": {
            "messages": messages
        }
    }
    return json.dumps(envelope)

def parse_response(envelope_str):
    """Extract the assistant's reply from an MCP response envelope.
    Returns the content string.
    """
    data = json.loads(envelope_str)
    msgs = data.get("payload", {}).get("messages", [])
    if not msgs:
        return ""
    # Assume last message is assistant response
    return msgs[-1].get("content", "")

def parse_intent(envelope_str):
    """Extract a structured intent from the assistant's response.
    The LLM is instructed to return a JSON object under `payload.intent`.
    Returns a dict or None.
    """
    data = json.loads(envelope_str)
    intent = data.get("payload", {}).get("intent")
    return intent
