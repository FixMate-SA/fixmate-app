# app/services.py
import os
import requests
import json

# --- 360dialog Configuration ---
DIALOG_360_API_KEY = os.environ.get('DIALOG_360_API_KEY')
DIALOG_360_URL = "https://waba-v2.360dialog.io/v1/messages"
DIALOG_360_PHONE_NUMBER_ID = os.environ.get('DIALOG_360_PHONE_NUMBER_ID', '702642972933051')

def send_whatsapp_message(to_number, message_body):
    """
    Sends a WhatsApp message using the 360dialog API.
    """
    print("\n--- Attempting to send WhatsApp message ---")

    if not DIALOG_360_API_KEY:
        print("❌ ERROR: Missing DIALOG_360_API_KEY. Cannot send message.")
        return None

    # Extract just the phone number
    if to_number.startswith("whatsapp:+"):
        recipient_number = to_number.replace("whatsapp:+", "")
    elif to_number.startswith("+"):
        recipient_number = to_number.replace("+", "")
    else:
        recipient_number = to_number.strip()

    print(f"🟡 Preparing to send message to: {recipient_number}")
    print(f"📦 Message Body: {message_body}")

    headers = {
        "D360-API-KEY": DIALOG_360_API_KEY,
        "Content-Type": "application/json"
    }

    # Final payload
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_number,
        "type": "text",
        "recipient_type": "individual",
        "from": DIALOG_360_PHONE_NUMBER_ID,
        "text": {
            "body": message_body  # ✅ This sends the actual text content
        }
    }

    print(f"🔁 Payload: {json.dumps(payload)}")

    try:
        response = requests.post(DIALOG_360_URL, json=payload, headers=headers, timeout=15)

        print(f"✅ HTTP Status Code: {response.status_code}")
        print(f"🔽 Response: {response.text}")

        response.raise_for_status()
        response_data = response.json()
        message_id = response_data.get('messages', [{}])[0].get('id')

        print(f"✅ Message sent! ID: {message_id}")
        print("--- WhatsApp message process finished ---")
        return message_id

    except requests.exceptions.RequestException as e:
        error_details = f"❌ ERROR sending WhatsApp message: {e}"
        try:
            if hasattr(e, 'response') and e.response:
                response_json = e.response.json()
                trace_id = response_json.get('meta', {}).get('360dialog_trace_id')
                if trace_id:
                    error_details += f" | 360dialog Trace ID: {trace_id}"
        except:
            pass
        print(error_details)
        print("--- WhatsApp message process finished with error ---")
        return None
