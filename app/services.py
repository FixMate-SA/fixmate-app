# app/services.py
import os
import requests

# --- 360dialog Configuration ---
DIALOG_360_API_KEY = os.environ.get('DIALOG_360_API_KEY')
DIALOG_360_URL = "https://waba.360dialog.io/v1/messages"


def send_whatsapp_message(to_number, message_body):
    """
    Sends a WhatsApp message using the 360dialog API.
    """
    if not DIALOG_360_API_KEY:
        print("ERROR: DIALOG_360_API_KEY not set. Cannot send message.")
        return None

    # 360dialog requires the number without the 'whatsapp:+' prefix
    recipient_number = to_number.replace("whatsapp:+", "")

    headers = {
        "D360-API-KEY": DIALOG_360_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "to": recipient_number,
        "type": "text",
        "text": {
            "body": message_body
        }
    }

    try:
        response = requests.post(DIALOG_360_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        response_data = response.json()
        message_id = response_data.get('messages', [{}])[0].get('id')
        
        print(f"Message sent to {recipient_number} via 360dialog: ID {message_id}")
        return message_id
    except requests.exceptions.RequestException as e:
        print(f"Error sending message via 360dialog: {e}")
        return None

