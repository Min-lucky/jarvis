import json
import datetime
from ..mcp.protocol import parse_response
from ..action.executor import execute_intent
from ..persistence.permissions import is_granted, grant

class DialogManager:
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.history = []  # list of dict(role, content)

    async def handle_user_utterance(self, text: str, llm_client):
        """Send user text to LLM, parse intent, check permissions, and execute.
        llm_client must expose an async method `query(envelope: str) -> str` returning MCP JSON.
        """
        self.history.append({"role": "user", "content": text})
        # Build MCP envelope via llm client (or external helper)
        envelope = llm_client.make_envelope(self.history, self.user_id)
        response_envelope = await llm_client.query(envelope)
        intent = json.loads(response_envelope).get("intent")
        if not intent:
            # fallback: treat whole response as plain answer
            answer = parse_response(response_envelope)
            self.history.append({"role": "assistant", "content": answer})
            return answer
        # Permission check
        action = intent.get("action")
        target = intent.get("target")
        if not is_granted(self.user_id, action, target):
            # ask for permission (simplified: assume user says yes)
            # In real implementation you would invoke TTS + STT to get yes/no
            # Here we auto‑grant for demo purposes
            grant(self.user_id, action, target, datetime.datetime.utcnow().isoformat())
        success, log_entry = execute_intent(self.user_id, intent)
        reply = f"Done – {action.replace('_', ' ')} {target}." if success else f"Failed to {action} {target}."
        self.history.append({"role": "assistant", "content": reply})
        return reply
