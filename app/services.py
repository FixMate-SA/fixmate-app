# app/services.py
import os
import requests
import json

DIALOG_360_API_KEY = os.environ.get('DIALOG_360_API_KEY')
DIALOG_360_URL = "https://waba-v2.360dialog.io/v1/messages"

def send_whatsapp_message(to_number, message_body):
    print("--- Attempting to send WhatsApp message ---")

    if not DIALOG_360_API_KEY:
        print("❌ API key not set.")
        return None

    headers = {
        "D360-API-KEY": DIALOG_360_API_KEY,
        "Content-Type": "application/json"
    }

    recipient_number = to_number.replace("whatsapp:+", "").replace("+", "")

    payload = {
        "to": recipient_number,
        "type": "text",
        "text": {
            "body": message_body
        }
    }

    print(f"🔁 Payload: {json.dumps(payload)}")

    try:
        response = requests.post(DIALOG_360_URL, headers=headers, json=payload)
        print(f"✅ HTTP Status Code: {response.status_code}")
        print(f"🔽 Response: {response.text}")

        response.raise_for_status()

        data = response.json()
        message_id = data.get("messages", [{}])[0].get("id", "N/A")
        print(f"✅ Message sent! ID: {message_id}")
        return message_id

    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR sending WhatsApp message: {e}")
        return None
