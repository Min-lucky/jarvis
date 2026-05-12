import aiohttp
import json
from ..mcp.protocol import make_envelope

class LLMClient:
    """
    Client for interacting with an MCP-enabled LLM server.
    """
    def __init__(self, endpoint: str = "http://localhost:5000/v1/chat/completions"):
        self.endpoint = endpoint

    async def query(self, envelope: str) -> str:
        """
        Sends an MCP envelope to the LLM server and returns the response.
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.endpoint, data=envelope, headers={'Content-Type': 'application/json'}) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        error_text = await response.text()
                        return json.dumps({"error": f"Server returned status {response.status}: {error_text}"})
            except Exception as e:
                return json.dumps({"error": f"Failed to connect to LLM server: {str(e)}"})

    def make_envelope(self, messages, user_id="default"):
        return make_envelope(messages, user_id=user_id)
