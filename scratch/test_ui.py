import requests
import time
import subprocess
import os
import sys

# Start the UI server in a separate process
env = os.environ.copy()
env["PYTHONPATH"] = "."
# Use sys.executable to ensure we use the same python
process = subprocess.Popen([sys.executable, "-m", "src.ui.app"], env=env)

time.sleep(3)  # Wait for server to start

try:
    print("Checking / ...")
    r = requests.get("http://127.0.0.1:8080/")
    print(f"Status: {r.status_code}")
    
    print("Checking /favicon.ico ...")
    r = requests.get("http://127.0.0.1:8080/favicon.ico")
    print(f"Favicon Status: {r.status_code}")
    
    print("Checking /ws ...")
    # GET on a websocket endpoint usually returns 400 or 426
    r = requests.get("http://127.0.0.1:8080/ws")
    print(f"WS path Status: {r.status_code}")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    process.terminate()
