from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional, Any
import uvicorn
import uuid
from datetime import datetime, timezone

app = FastAPI(title="Mock Jarvis LLM Server")

class Message(BaseModel):
    role: str
    content: str

class MCPPayload(BaseModel):
    messages: List[Message]
    intent: Optional[Any] = None

class MCPMetadata(BaseModel):
    uid: str = "default"
    request_id: Optional[str] = None
    timestamp: Optional[str] = None
    model: str = "mock-jarvis-model"

class MCPEnvelope(BaseModel):
    metadata: MCPMetadata
    payload: MCPPayload

@app.get("/")
async def root():
    return {"status": "Jarvis Mock LLM Server is running", "endpoints": ["/v1/chat/completions"]}

@app.post("/v1/chat/completions", response_model=MCPEnvelope)
async def chat_completions(envelope: MCPEnvelope):
    messages = envelope.payload.messages
    user_text = messages[-1].content.lower() if messages else ""
    
    # Simple logic to generate intents for testing
    intent = None
    answer = "I'm not sure how to do that yet."
    
    if "open chrome" in user_text:
        intent = {"action": "open_app", "target": "chrome.exe", "args": []}
        answer = "Opening Chrome for you."
    elif "open notepad" in user_text:
        intent = {"action": "open_app", "target": "notepad.exe", "args": []}
        answer = "Opening Notepad."
    elif "hello" in user_text:
        answer = "Hello! I am Jarvis. How can I assist you today?"
    
    # Create response
    response_messages = messages + [Message(role="assistant", content=answer)]
    
    response = MCPEnvelope(
        metadata=MCPMetadata(
            uid=envelope.metadata.uid,
            request_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            model="mock-jarvis-model"
        ),
        payload=MCPPayload(
            messages=response_messages,
            intent=intent
        )
    )
    
    return response

if __name__ == "__main__":
    print("Starting Mock Jarvis LLM Server on http://localhost:5000")
    # Using 127.0.0.1 is often more reliable on Windows than 0.0.0.0
    uvicorn.run(app, host="127.0.0.1", port=5000)
