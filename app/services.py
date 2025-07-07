import os  # Add this import at the top of the file
import requests
import json

def send_whatsapp_message(to_number, message_body):
    print("--- Attempting to send WhatsApp message ---")
    
    # Get API key from environment variables
    DIALOG_360_API_KEY = os.environ.get('DIALOG_360_API_KEY')
    DIALOG_360_URL = os.environ.get('DIALOG_360_URL')  # Also get URL from env

    if not DIALOG_360_API_KEY:
        print("❌ API key not set.")
        return None

    if not DIALOG_360_URL:  # Add URL validation
        print("❌ DIALOG_360_URL not set.")
        return None

    headers = {
        "D360-API-KEY": "fAZcu5FIR9j4xexivP2sry3gAK"
        "Content-Type": "application/json"
    }

    recipient_number = to_number.replace("whatsapp:+", "").replace("+", "").strip()

    payload = {
        "messaging_product": "whatsapp",
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
        if hasattr(e, 'response') and e.response is not None:
            try:
                print("🔽 Error Details:", e.response.json())
            except:
                pass
        return None