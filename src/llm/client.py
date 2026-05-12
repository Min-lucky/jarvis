import aiohttp
import json
import asyncio
from ..mcp.protocol import make_envelope

class LLMClient:
    """
    Client for interacting with a real LLM (Gemma/Qwen/Ollama).
    """
    def __init__(
        self,
        endpoint: str = "http://127.0.0.1:11434/v1/chat/completions",
        model: str = "minicpm-v"
    ):
        self.endpoint = endpoint
        self.model = model
        self.system_prompt = (
            "You are Jarvis, a highly advanced AI assistant for a Windows computer. "
            "You are helpful, witty, and efficient. You can control the laptop via tools. "
            "When asked to do something, provide a structured 'intent' in your JSON response. "
            "If you need to open an app, use 'open_app'. If you need system stats, use 'get_system_info'. "
            "Always explain what you are doing in your 'content' field before providing the intent."
        )

    async def query(self, messages: list) -> str:
        """
        Sends messages to the LLM and returns the full JSON response.
        """
        # Inject system prompt
        formatted_messages = [{"role": "system", "content": self.system_prompt}] + messages
        
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "response_format": {"type": "json_object"}
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.endpoint, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Extract the content from the typical OpenAI response format
                        content = data['choices'][0]['message']['content']
                        if isinstance(content, dict):
                            return json.dumps(content)
                        if content is None:
                            return json.dumps({"content": "", "intent": None})
                        return content
                    else:
                        error_text = await response.text()
                        return json.dumps({"error": f"LLM Server Error {response.status}: {error_text}"})
            except Exception as e:
                return json.dumps({"error": f"Failed to connect to LLM: {str(e)}"})

    def make_envelope(self, messages, user_id="default"):
        # Not used with real LLM but kept for backward compatibility if needed
        return messages
