# app/services.py
import os
import requests

# Get the API key from environment variables
DIALOG_360_API_KEY = os.environ.get('DIALOG_360_API_KEY')
# Using the correct v2 endpoint for production
DIALOG_360_URL = "https://waba.360dialog.io/v1/messages" 

def send_whatsapp_message(to_number, message_body):
    """Sends a message to a user via the 360dialog API."""
    if not DIALOG_360_API_KEY:
        print("ERROR: DIALOG_360_API_KEY not set. Cannot send message.")
        return None

    # 360dialog requires the number without the 'whatsapp:' prefix
    recipient_number = to_number.replace("whatsapp:+", "")

    headers = {
        "D360-API-KEY": DIALOG_360_API_KEY,
        "Content-Type": "application/json"
    }
    
    # --- THIS IS THE CORRECTED PAYLOAD ---
    # The "preview_url" parameter has been removed.
    payload = {
        "to": recipient_number,
        "type": "text",
        "text": {
            "body": message_body
        }
    }

    try:
        print(f"DEBUG: Sending payload to {recipient_number}: {payload}")
        response = requests.post(DIALOG_360_URL, json=payload, headers=headers)
        
        # Check for a successful response (2xx status code)
        if response.status_code >= 200 and response.status_code < 300:
            response_data = response.json()
            message_id = response_data.get('messages', [{}])[0].get('id')
            print(f"Message sent successfully to {recipient_number}: ID {message_id}")
            return message_id
        else:
            # Print more detailed error info if available
            print(f"ERROR: Failed to send message. Status: {response.status_code}, Response: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"ERROR: An exception occurred while sending message via 360dialog: {e}")
        return None
