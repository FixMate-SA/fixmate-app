# app/routes.py
import re
import json
from flask import Blueprint, request, Response
from .state_manager import get_user_state, set_user_state, clear_user_state
from .services import send_whatsapp_message, create_user_account, create_new_job

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def index():
    """A simple homepage to confirm the app is running."""
    print("--- ROOT / ENDPOINT WAS HIT ---")
    return "<h1>FixMate WhatsApp Bot is running.</h1>", 200

@main.route('/ping', methods=['GET'])
def ping():
    """A simple endpoint to test if the server is reachable and logging."""
    print("--- PING ENDPOINT WAS HIT SUCCESSFULLY ---")
    return "Pong! The server is running.", 200

@main.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Endpoint to receive incoming WhatsApp messages from 360dialog."""
    print("--- /WHATSAPP ENDPOINT WAS HIT SUCCESSFULLY ---")

    data = request.get_json()
    print(f"Received data: {json.dumps(data, indent=2)}")

    # --- Start of 360dialog Message Processing ---
    
    # 360dialog sends messages in a 'messages' array
    if 'messages' not in data or not data['messages']:
        print("No messages found in the payload.")
        return Response(status=200)

    message = data['messages'][0]
    from_number = message.get('from')
    message_type = message.get('type')
    
    incoming_msg = ""
    latitude = None
    longitude = None

    if message_type == 'text':
        incoming_msg = message.get('text', {}).get('body', '').strip()
    elif message_type == 'location':
        location_data = message.get('location', {})
        latitude = location_data.get('latitude')
        longitude = location_data.get('longitude')
    else:
        print(f"Unsupported message type: {message_type}")
        # Optionally send a message back to the user
        send_whatsapp_message(from_number, "Sorry, I can only process text and location messages.")
        return Response(status=200)

    # --- End of 360dialog Message Processing ---

    user = get_user_state(from_number)
    current_state = user.get('state')
    response_message = ""

    # --- Start of Conversational Logic ---

    if current_state == 'awaiting_location' and latitude and longitude:
        response_message = (
            "Thank you for sharing your location.\n\n"
            "Lastly, please provide a contact number (e.g., 082 123 4567) that the fixer can call to confirm the address if needed."
        )
        user['data']['latitude'] = latitude
        user['data']['longitude'] = longitude
        set_user_state(from_number, 'awaiting_contact_number', data=user['data'])

    elif current_state == 'awaiting_contact_number':
        potential_number = incoming_msg
        # Basic validation for a phone number
        if any(char.isdigit() for char in potential_number) and len(potential_number) >= 10:
            service_details = user['data'].get('service', 'a service')
            lat = user['data'].get('latitude')
            lon = user['data.get']('longitude')
            job_id = create_new_job(from_number, service_details, lat, lon, potential_number)
            response_message = (
                f"Perfect! We have logged your request for '{service_details}' under contact number {potential_number}.\n\n"
                f"Your job ID is {job_id}. We are finding a qualified fixer near you and will send a confirmation shortly."
            )
            clear_user_state(from_number)
        else:
            response_message = "That doesn't seem to be a valid phone number. Please enter a valid South African contact number."

    elif current_state == 'awaiting_location':
        # This handles the case where they are supposed to send a location but send text instead.
        response_message = (
            "I'm sorry, I can't understand a typed address yet.\n\n"
            "Please use the WhatsApp location sharing feature (the paperclip icon 📎) to send your pin location."
        )

    elif current_state is None:
        if 'hello' in incoming_msg.lower() or 'hi' in incoming_msg.lower():
            response_message = (
                "Welcome to FixMate! Your reliable help is a message away. \n\n"
                "What would you like to do? \n"
                "1. Request a Service 🛠️\n"
                "2. Register an Account 📝"
            )
            set_user_state(from_number, 'awaiting_initial_choice')
        else:
            response_message = "Sorry, I didn't understand. Please say 'Hello' to get started."

    elif current_state == 'awaiting_initial_choice':
        if '1' in incoming_msg or 'request' in incoming_msg.lower():
            response_message = "Great! What service do you need? (e.g., 'Leaking pipe', 'Broken light switch')"
            set_user_state(from_number, 'awaiting_service_request')
        elif '2' in incoming_msg or 'register' in incoming_msg.lower():
            response_message = "Let's get you registered. What is your full name?"
            set_user_state(from_number, 'awaiting_name_for_registration')
        else:
            response_message = "Invalid choice. Please reply with '1' to request a service or '2' to register."

    elif current_state == 'awaiting_name_for_registration':
        user_name = incoming_msg
        create_user_account(user_name, from_number)
        response_message = f"Thanks, {user_name}! You are now registered with FixMate."
        clear_user_state(from_number)

    elif current_state == 'awaiting_service_request':
        service_details = incoming_msg
        response_message = (
            f"Got it: '{service_details}'.\n\n"
            "Now, please share your location pin using the WhatsApp location feature so we can dispatch a fixer.\n\n"
            "Tap the paperclip icon 📎, then choose 'Location'."
        )
        set_user_state(from_number, 'awaiting_location', data={'service': service_details})

    # --- End of Conversational Logic ---

    if response_message:
        send_whatsapp_message(from_number, response_message)

    # Acknowledge receipt of the message to 360dialog
    return Response(status=200)
