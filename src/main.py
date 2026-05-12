import asyncio
import yaml
import os
import threading
import webbrowser
from pathlib import Path

# Run this from the project root using: python -m src.main
# This ensures that 'src' is treated as a package and imports work correctly.

from src.audio.capture import AudioCapture
from src.audio.clap import ClapDetector
from src.stt.stt_interface import STTInterface
from src.tts.tts_engine import TTSEngine
from src.llm.client import LLMClient
from src.dialog.manager import DialogManager
from src.ui.app import run_ui, broadcast

def start_ui_server():
    run_ui(port=8080)

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
    
    # Start UI server in background thread
    ui_thread = threading.Thread(target=start_ui_server, daemon=True)
    ui_thread.start()
    
    # Give it a moment to start then open browser
    await asyncio.sleep(2)
    webbrowser.open("http://127.0.0.1:8080")
    
    # Load settings
    config_path = Path("config/settings.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Initialize components
    audio = AudioCapture(rate=config['sample_rate'], chunk=config['chunk_size'])
    
    # Get device info for UI log
    try:
        dev_info = audio.p.get_default_input_device_info()
        await log_ui(f"Using Audio Device: {dev_info['name']}")
    except:
        pass
        
    clap_detector = ClapDetector(threshold=config['clap_threshold'], max_interval=config['clap_max_interval'])
    stt = STTInterface(backend=config['stt_backend'])
    tts = TTSEngine()
    llm_client = LLMClient(endpoint=config['mcp_endpoint'])
    dialog_manager = DialogManager(user_id="user_1")
    
    print("--- Jarvis is Online and Listening for Double Clap ---")
    await log_ui("Jarvis is online and listening for double clap.")
    await update_ui("idle", "Standby Mode", "Awaiting Double Clap")
    
    try:
        while True:
            # Read audio chunk
            samples = audio.read()
            
            # Check for double clap
            if clap_detector.feed(samples):
                print("\n[Jarvis] Double clap detected! How can I help you?")
                await log_ui("Double clap detected!")
                await update_ui("listening", "Listening...", "How can I help you?")
                
                await tts.speak("Yes, I am here. How can I help you?")
                
                # Transcribe speech
                user_text = await stt.transcribe(samples)
                
                if user_text:
                    await log_ui(f"User: {user_text}")
                    if user_text.lower() in ["exit", "stop", "shutdown"]:
                        await update_ui("active", "Shutting Down", "Goodbye")
                        await tts.speak("Shutting down. Goodbye.")
                        break
                    
                    # Handle utterance
                    try:
                        await update_ui("active", "Processing...", user_text)
                        response = await dialog_manager.handle_user_utterance(user_text, llm_client)
                        
                        if isinstance(response, str) and "Failed to connect to LLM server" in response:
                            await log_ui("Error: LLM server offline.")
                            await update_ui("idle", "Connection Error", "AI Core is offline")
                            await tts.speak("I'm sorry, I'm having trouble connecting to my core systems.")
                        else:
                            await log_ui(f"Jarvis: {response}")
                            await update_ui("active", "Jarvis Speaking", response)
                            await tts.speak(response)
                    except Exception as e:
                        print(f"[Jarvis] System Error: {str(e)}")
                        await log_ui(f"System Error: {str(e)}")
                        await tts.speak("I've encountered a system error.")
                
                # Back to idle
                await update_ui("idle", "Standby Mode", "Awaiting Double Clap")
                
            # Yield to other tasks
            await asyncio.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n--- Jarvis Shutting Down ---")
    finally:
        audio.close()

if __name__ == "__main__":
    asyncio.run(main())
