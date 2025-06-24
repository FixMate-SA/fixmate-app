# app/routes.py
import re
from flask import Blueprint, request, Response
from .state_manager import get_user_state, set_user_state, clear_user_state
from .services import send_whatsapp_message, create_user_account, create_new_job

main = Blueprint('main', __name__)

# NEW: Add a root route for health checks
@main.route('/', methods=['GET'])
def index():
    """A simple homepage to confirm the app is running."""
    print("--- ROOT / ENDPOINT WAS HIT ---")
    return "<h1>FixMate WhatsApp Bot is running.</h1>", 200

# This route is for browser testing
@main.route('/ping', methods=['GET'])
def ping():
    """A simple endpoint to test if the server is reachable and logging."""
    print("--- PING ENDPOINT WAS HIT SUCCESSFULLY ---")
    return "Pong! The server is running.", 200

# This is the main webhook route for Twilio
@main.route('/whatsapp', methods=['GET', 'POST'])
def whatsapp_webhook():
    """Endpoint to receive incoming WhatsApp messages."""
    print("--- /WHATSAPP ENDPOINT WAS HIT SUCCESSFULLY ---")

    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')

    # Check for incoming location data
    latitude = request.values.get('Latitude')
    longitude = request.values.get('Longitude')

    # Get the user's current conversation state
    user = get_user_state(from_number)
    current_state = user['state']

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
        if any(char.isdigit() for char in potential_number) and len(potential_number) >= 10:
            service_details = user['data'].get('service', 'a service')
            lat = user['data'].get('latitude')
            lon = user['data'].get('longitude')
            job_id = create_new_job(from_number, service_details, lat, lon, potential_number)
            response_message = (
                f"Perfect! We have logged your request for '{service_details}' under contact number {potential_number}.\n\n"
                f"Your job ID is {job_id}. We are finding a qualified fixer near you and will send a confirmation shortly."
            )
            clear_user_state(from_number)
        else:
            response_message = "That doesn't seem to be a valid phone number. Please enter a valid South African contact number."

    elif current_state == 'awaiting_location':
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

    if response_message:
        send_whatsapp_message(from_number, response_message)

    # Always return a 200 OK for Twilio
    return Response(status=200)

