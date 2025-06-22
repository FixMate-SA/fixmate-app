# app/services.py
from twilio.rest import Client
from .config import Config

client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)

def send_whatsapp_message(to_number, message_body):
    """Sends a message to a user via WhatsApp."""
    try:
        message = client.messages.create(
            from_=Config.TWILIO_WHATSAPP_NUMBER,
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
    In a real app, this would interact with your PostgreSQL DB.
    """
    print(f"Creating user: {name} with number {phone_number}")
    # DATABASE LOGIC GOES HERE
    return True

def create_new_job(user_id, service_requested, latitude, longitude, contact_number):
    """
    Placeholder for creating a new job in the database.
    Now includes location data and a contact number.
    """
    print(f"User {user_id} requested a job for: '{service_requested}'")
    print(f"Location Data -> Latitude: {latitude}, Longitude: {longitude}")
    print(f"Contact Number for Fixer: {contact_number}")
    # DATABASE LOGIC GOES HERE
    # This would involve finding the nearest available fixer and creating a job record.
    return "JOB-12347" # Return a mock job ID