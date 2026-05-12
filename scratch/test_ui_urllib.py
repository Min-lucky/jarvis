import urllib.request
import time
import subprocess
import os
import sys

# Start the UI server in a separate process
env = os.environ.copy()
env["PYTHONPATH"] = "."
process = subprocess.Popen([sys.executable, "-m", "src.ui.app"], env=env)

time.sleep(3)  # Wait for server to start

try:
    print("Checking / ...")
    with urllib.request.urlopen("http://127.0.0.1:8080/") as response:
        print(f"Status: {response.getcode()}")
        print(f"Headers: {response.info()['Content-Type']}")
    
    print("Checking /favicon.ico ...")
    try:
        with urllib.request.urlopen("http://127.0.0.1:8080/favicon.ico") as response:
            print(f"Favicon Status: {response.getcode()}")
    except urllib.error.HTTPError as e:
        print(f"Favicon Status (Error): {e.code}")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    process.terminate()
