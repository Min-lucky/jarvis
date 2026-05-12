import json
import datetime
from ..persistence.logger import log_interaction
from ..action.executor import execute_intent
from ..persistence.permissions import is_granted, grant

class DialogManager:
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.history = []  # list of dict(role, content)

    async def handle_user_utterance(self, text: str, llm_client):
        """Send user text to LLM, parse intent, execute, and log."""
        self.history.append({"role": "user", "content": text})
        
        # Query LLM (using the updated client)
        response_json = await llm_client.query(self.history)
        
        try:
            data = json.loads(response_json)
        except:
            # Fallback for plain text response
            data = {"content": response_json, "intent": None}
            
        content = data.get("content", "I'm not sure how to respond to that.")
        intent = data.get("intent")
        
        # 1. First, Jarvis speaks his natural language response
        final_reply = content
        
        # 2. Execute intent if present
        tool_output = None
        if intent:
            action = intent.get("action")
            target = intent.get("target", "")
            
            # Simple permission check (Auto-grant for now as per project goal)
            if not is_granted(self.user_id, action, target):
                grant(self.user_id, action, target, datetime.datetime.now().isoformat())
            
            success, tool_output = execute_intent(self.user_id, intent)
            
            if success:
                if action == "get_system_info":
                    final_reply = f"{content} I've checked the systems for you: {json.dumps(tool_output)}"
                else:
                    final_reply = f"{content} I've successfully initiated the {action} for {target}."
            else:
                final_reply = f"{content} However, I encountered an issue: {tool_output.get('error', 'unknown error')}"

        self.history.append({"role": "assistant", "content": final_reply})
        
        # 3. Log everything to the server-side database
        log_interaction(self.user_id, text, final_reply, intent, tool_output)
        
        return final_reply
