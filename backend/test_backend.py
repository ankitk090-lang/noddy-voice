import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_chat():
    url = "http://localhost:8000/api/chat"
    payload = {
        "message": "Hello Noddy! Who are you?",
        "history": []
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("✅ Chat Endpoint Success")
            print("Response:", response.json())
        else:
            print(f"❌ Chat Endpoint Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_chat()
