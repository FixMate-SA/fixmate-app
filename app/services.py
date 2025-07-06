# app/services.py
import os
import requests
import json

# --- NEW: Define necessary variables at the top of the file ---
DIALOG_360_API_KEY = os.environ.get('DIALOG_360_API_KEY')
# Using the correct v2 endpoint for production
DIALOG_360_URL = "https://waba-v2.360dialog.io/v1/messages" 


def send_whatsapp_message(to_number, message_body):
    print("\n--- Attempting to send WhatsApp message ---")

    if not DIALOG_360_API_KEY:
        print("❌ ERROR: Missing DIALOG_360_API_KEY. Cannot send message.")
        return None

    # Clean recipient number
    recipient_number = to_number.replace("whatsapp:+", "").replace("+", "").strip()

    print(f"🟡 Preparing to send message to: {recipient_number}")
    print(f"📦 Message Body: {message_body}")

    headers = {
        "D360-API-KEY": DIALOG_360_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_number,
        "type": "text",
        "recipient_type": "individual",
        "text": {
            "body": message_body
        }
    }

    print(f"🔁 Payload: {json.dumps(payload)}")

    try:
        response = requests.post(DIALOG_360_URL, json=payload, headers=headers, timeout=15)
        print(f"✅ HTTP Status Code: {response.status_code}")
        print(f"🔽 Response: {response.text}")
        response.raise_for_status()

        data = response.json()
        message_id = data.get('messages', [{}])[0].get('id')
        print(f"✅ Message sent! ID: {message_id}")
        return message_id

    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR sending WhatsApp message: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                print("🔽 Error Details:", e.response.json())
            except:
                pass
        return None
