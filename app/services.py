# app/services.py
import os
import requests
import json

# --- 360dialog Configuration ---
DIALOG_360_API_KEY = os.environ.get('DIALOG_360_API_KEY')
DIALOG_360_URL = "https://waba-v2.360dialog.io/v1/messages"


def send_whatsapp_message(to_number, message_body):
    """
    Sends a WhatsApp message using the 360dialog API with detailed logging.
    """
    print("--- Attempting to send WhatsApp message ---")
    
    if not DIALOG_360_API_KEY:
        print("DEBUG: FATAL - DIALOG_360_API_KEY is not set or not found. Cannot send message.")
        return None
    
    # Let's print a part of the key to confirm it's loaded correctly
    print(f"DEBUG: API Key found, starting with: {DIALOG_360_API_KEY[:4]}...")

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
    
    print(f"DEBUG: Sending payload to {recipient_number}: {json.dumps(payload)}")

    try:
        response = requests.post(DIALOG_360_URL, json=payload, headers=headers, timeout=15) # Added timeout
        
        # Log the response regardless of status code
        print(f"DEBUG: Received HTTP status code: {response.status_code}")
        print(f"DEBUG: Full response content: {response.text}")
        
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        response_data = response.json()
        message_id = response_data.get('messages', [{}])[0].get('id')
        
        print(f"SUCCESS: Message sent to {recipient_number} via 360dialog: ID {message_id}")
        print("--- WhatsApp message process finished ---")
        return message_id
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR: An exception occurred while sending message via 360dialog: {e}")
        print("--- WhatsApp message process finished with error ---")
        return None

