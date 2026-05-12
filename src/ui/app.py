from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import asyncio
import json
import uvicorn
from pathlib import Path

app = FastAPI()

# Setup paths and templates
BASE_DIR = Path(__file__).resolve().parent
static_dir = BASE_DIR / "static"
templates_dir = BASE_DIR / "templates"

# Ensure directories exist
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# Global list to track connected websockets
connected_clients = []

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = BASE_DIR / "templates" / "index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Handle favicon requests to prevent 404s."""
    return Response(status_code=204)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            # Just keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in connected_clients:
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
        if client in connected_clients:
            connected_clients.remove(client)

def run_ui(port=8080):
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

if __name__ == "__main__":
    run_ui()
