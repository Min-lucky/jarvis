import asyncio
import yaml
import os
import threading
import webbrowser
import time
import numpy as np
import socket
from pathlib import Path

# Run this from the project root using: python -m src.main
# This ensures that 'src' is treated as a package and imports work correctly.

from src.audio.capture import AudioCapture
from src.stt.stt_interface import STTInterface
from src.tts.tts_engine import TTSEngine
from src.llm.client import LLMClient
from src.dialog.manager import DialogManager
from src.persistence.logger import init_db
from src.ui.app import run_ui, broadcast

async def log_terminal(text):
    """Send a message to the UI terminal section."""
    await broadcast({
        "type": "terminal",
        "text": text
    })

def find_free_port(preferred: int = 8080) -> int:
    for port in [preferred, 8081, 8082, 8083, 8090]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return preferred

def start_ui_server(port: int):
    run_ui(port=port)

async def update_ui(state, text, subtext=None):
    await broadcast({
        "type": "status",
        "state": state,
        "text": text,
        "subtext": subtext
    })

async def log_ui(text):
    await broadcast({
        "type": "log",
        "text": text
    })

async def main():
    print("--- Jarvis System Initializing ---")
    init_db() # Setup logging database
    
    # Start UI server in background thread
    ui_port = find_free_port(8080)
    ui_thread = threading.Thread(target=start_ui_server, args=(ui_port,), daemon=True)
    ui_thread.start()
    
    # Give it a moment to start then open browser
    await asyncio.sleep(2)
    webbrowser.open(f"http://127.0.0.1:{ui_port}")
    
    # Load settings
    config_path = Path("config/settings.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Initialize components
    audio = AudioCapture(rate=config['sample_rate'], chunk=config['chunk_size'])
    
    # Get device info for UI log
    try:
        dev_info = audio.p.get_default_input_device_info()
        await log_terminal(f"Audio Initialized: {dev_info['name']}")
        await log_ui(f"Using Audio Device: {dev_info['name']}")
    except:
        pass
        
    stt = STTInterface(backend=config['stt_backend'])
    tts = TTSEngine()
    llm_client = LLMClient(
        endpoint=config['mcp_endpoint'],
        model=config.get('llm_model', 'minicpm-v')
    )
    dialog_manager = DialogManager(user_id="user_1")
    
    print("--- Jarvis is Online and Listening for Voice ---")
    await log_ui("Jarvis is online and listening for voice.")
    await update_ui("idle", "Standby Mode", "Awaiting Voice")

    # Mic warm-up/permission verification: if this fails, audio capture is unavailable.
    try:
        warmup = audio.read_seconds(0.2)
        warmup_peak = float(np.max(np.abs(warmup))) if len(warmup) else 0.0
        await log_terminal(f"Mic check OK (peak={warmup_peak:.3f})")
    except Exception as e:
        await log_terminal(f"Mic check failed: {e}")
        print("CRITICAL: Microphone access failed. Enable Windows microphone access for desktop apps.")
        return
    
    # Startup greeting
    try:
        await tts.speak("All systems online. Jarvis is ready and listening for your voice.")
    except Exception as e:
        print(f"Greeting error: {e}")
    
    last_meter_time = time.time()
    last_term_time = time.time()
    
    try:
        while True:
            # Read audio chunk
            samples = audio.read()
            
            # Volume meter (every 0.1s for smoothness in UI)
            now = time.time()
            if now - last_meter_time > 0.1:
                peak = float(np.max(np.abs(samples)))
                # Broadcast to UI for visualizer
                asyncio.create_task(broadcast({"type": "volume", "value": peak}))
                
                # Terminal bars (less frequent to avoid flicker)
                if now - last_term_time > 0.5:
                    bars = "|" * int(peak * 50)
                    print(f"\rVolume: [{bars:<50}] {peak:.4f}", end="", flush=True)
                    last_term_time = now
                last_meter_time = now
            
            # Voice wake: begin capture when speech-level audio is detected.
            wake_threshold = float(config.get("voice_wake_threshold", 0.02))
            peak_now = float(np.max(np.abs(samples)))
            if peak_now >= wake_threshold:
                print("\n[Jarvis] Voice detected. How can I help you?")
                await log_ui("Voice detected.")
                await update_ui("listening", "Listening...", "How can I help you?")
                
                await tts.speak("Yes, I am here. How can I help you?")
                
                # Capture a full phrase after wake and transcribe it.
                speech_samples = audio.capture_utterance(
                    max_seconds=6.0,
                    silence_seconds=1.0,
                    energy_threshold=0.015
                )
                user_text = await stt.transcribe(speech_samples, sample_rate=audio.rate)
                
                if user_text:
                    await log_ui(f"User: {user_text}")
                    await log_terminal(f"Processing input: {user_text}")
                    
                    if user_text.lower() in ["exit", "stop", "shutdown"]:
                        await update_ui("active", "Shutting Down", "Goodbye")
                        await tts.speak("Shutting down. Goodbye.")
                        break
                    
                    # Handle utterance
                    try:
                        await update_ui("active", "Thinking...", user_text)
                        response = await dialog_manager.handle_user_utterance(user_text, llm_client)
                        
                        if isinstance(response, str) and "error" in response.lower():
                            await log_terminal(f"System Error: {response}")
                            await update_ui("idle", "Error", "Something went wrong")
                            await tts.speak("I'm sorry, I encountered a system error.")
                        else:
                            await log_ui(f"Jarvis: {response}")
                            await update_ui("active", "Jarvis Speaking", response)
                            await tts.speak(response)
                    except Exception as e:
                        print(f"[Jarvis] System Error: {str(e)}")
                        await log_terminal(f"Exception: {str(e)}")
                        await tts.speak("I've encountered a critical system error.")
                
                # Back to idle
                await update_ui("idle", "Standby Mode", "Awaiting Voice")
                await asyncio.sleep(0.35)
                
            # Yield to other tasks
            await asyncio.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n--- Jarvis Shutting Down ---")
    finally:
        audio.close()

if __name__ == "__main__":
    asyncio.run(main())
