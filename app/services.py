# app/services.py
from twilio.rest import Client
import os

# Get credentials from environment variables
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER')

# Initialize the client only if credentials are available
client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    print("WARNING: Twilio credentials not found. The app will not be able to send messages.")


def send_whatsapp_message(to_number, message_body):
    """Sends a message to a user via WhatsApp."""
    if not client:
        print(f"ERROR: Cannot send message. Twilio client not initialized.")
        return None
    try:
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message_body,
            to=to_number
        )
        print(f"Message sent to {to_number}: SID {message.sid}")
        return message.sid
    except Exception as e:
        print(f"Error sending message to {to_number}: {e}")
        return None

def create_user_account(name, phone_number):
    """
    Placeholder for creating a user in your database.
    """
    print(f"Creating user: {name} with number {phone_number}")
    # In the future, you will add your database logic here.
    return True

def create_new_job(user_id, service_requested, latitude, longitude, contact_number):
    """
    Placeholder for creating a new job in the database.
    """
    print(f"User {user_id} requested a job for: '{service_requested}'")
    print(f"Location Data -> Latitude: {latitude}, Longitude: {longitude}")
    print(f"Contact Number for Fixer: {contact_number}")
    # In the future, you will add your database logic here.
    return "JOB-12348"