import requests
import json

url = "http://localhost:5000/v1/chat/completions"
payload = {
    "metadata": {"uid": "test-user"},
    "payload": {
        "messages": [{"role": "user", "content": "hello"}]
    }
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
