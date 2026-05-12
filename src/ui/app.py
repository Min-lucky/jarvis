from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import asyncio
import json
import uvicorn
from pathlib import Path

app = FastAPI()

# Setup templates
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Global list to track connected websockets
connected_clients = []

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open(BASE_DIR / "templates" / "index.html", "r") as f:
        return f.read()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            # Just keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def broadcast(message: dict):
    """Send a message to all connected UI clients."""
    if not connected_clients:
        return
    
    dead_clients = []
    msg_str = json.dumps(message)
    for client in connected_clients:
        try:
            await client.send_text(msg_str)
        except Exception:
            dead_clients.append(client)
    
    for client in dead_clients:
        connected_clients.remove(client)

def run_ui(port=8080):
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

if __name__ == "__main__":
    run_ui()
