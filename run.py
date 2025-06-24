# run.py
import os
import re
from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# --- Database and App Initialization ---

# Create the Flask app instance
app = Flask(__name__)

# Configure the database connection using the Heroku environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import and initialize the database with our app
from app.models import db, User
db.init_app(app)

# Initialize Flask-Migrate for handling database schema changes
migrate = Migrate(app, db)


# --- State Management (Now uses the database) ---

def get_or_create_user(phone_number):
    """Finds a user by phone number or creates a new one if not found."""
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user:
        user = User(phone_number=phone_number)
        db.session.add(user)
        db.session.commit()
    return user

def set_user_state(user, new_state, data=None):
    """Sets a new state for a user in the database."""
    user.conversation_state = new_state
    if data:
        user.service_request_cache = data.get('service')
        user.latitude_cache = data.get('latitude')
        user.longitude_cache = data.get('longitude')
    db.session.commit()
    print(f"State for {user.phone_number} set to {new_state}")

def clear_user_state(user):
    """Clears the state for a user in the database."""
    user.conversation_state = None
    user.service_request_cache = None
    user.latitude_cache = None
    user.longitude_cache = None
    db.session.commit()
    print(f"State for {user.phone_number} cleared.")


# --- Service Functions ---
# Note: These could be in services.py, but are here for simplicity in this refactor.

def create_user_account_in_db(user, name):
    """Updates the user's name in the database."""
    user.full_name = name
    db.session.commit()
    print(f"Updated user: {name} with number {user.phone_number}")
    return True

def create_new_job_in_db(user, service, lat, lon, contact):
    """Placeholder for creating a job. This will eventually create a Job record."""
    print(f"User {user.phone_number} requested a job for: '{service}'")
    print(f"Location: {lat}, {lon} | Contact: {contact}")
    # In the future, this will be: new_job = Job(...)
    return "JOB-DB-001"


# --- Twilio Integration ---
from app.services import send_whatsapp_message


# --- Main Webhook Route ---

@app.route('/', methods=['GET'])
def index():
    return "<h1>FixMate WhatsApp Bot is running.</h1>", 200

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Endpoint to receive incoming WhatsApp messages."""
    print("--- /WHATSAPP ENDPOINT WAS HIT ---")
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')

    latitude = request.values.get('Latitude')
    longitude = request.values.get('Longitude')

    # Get or create the user from the database
    user = get_or_create_user(from_number)
    current_state = user.conversation_state
    response_message = ""

    # --- Conversational Logic ---
    if current_state == 'awaiting_location' and latitude and longitude:
        response_message = (
            "Thank you for sharing your location.\n\n"
            "Lastly, please provide a contact number (e.g., 082 123 4567) that the fixer can call to confirm the address if needed."
        )
        set_user_state(user, 'awaiting_contact_number', data={
            'service': user.service_request_cache,
            'latitude': latitude,
            'longitude': longitude
        })

    elif current_state == 'awaiting_contact_number':
        potential_number = incoming_msg
        if any(char.isdigit() for char in potential_number) and len(potential_number) >= 10:
            job_id = create_new_job_in_db(
                user,
                user.service_request_cache,
                user.latitude_cache,
                user.longitude_cache,
                potential_number
            )
            response_message = (
                f"Perfect! We have logged your request for '{user.service_request_cache}' under contact number {potential_number}.\n\n"
                f"Your job ID is {job_id}. We are finding a qualified fixer near you and will send a confirmation shortly."
            )
            clear_user_state(user)
        else:
            response_message = "That doesn't seem to be a valid phone number. Please enter a valid South African contact number."

    elif current_state == 'awaiting_location':
        response_message = "Please use the WhatsApp location sharing feature (the paperclip icon 📎) to send your pin location."

    elif current_state is None:
        if 'hello' in incoming_msg.lower() or 'hi' in incoming_msg.lower():
            response_message = (
                "Welcome to FixMate! Your reliable help is a message away. \n\n"
                "What would you like to do? \n"
                "1. Request a Service 🛠️\n"
                "2. Register an Account 📝"
            )
            set_user_state(user, 'awaiting_initial_choice')
        else:
            response_message = "Sorry, I didn't understand. Please say 'Hello' to get started."

    elif current_state == 'awaiting_initial_choice':
        if '1' in incoming_msg or 'request' in incoming_msg.lower():
            response_message = "Great! What service do you need? (e.g., 'Leaking pipe', 'Broken light switch')"
            set_user_state(user, 'awaiting_service_request')
        elif '2' in incoming_msg or 'register' in incoming_msg.lower():
            response_message = "Let's get you registered. What is your full name?"
            set_user_state(user, 'awaiting_name_for_registration')
        else:
            response_message = "Invalid choice. Please reply with '1' to request a service or '2' to register."

    elif current_state == 'awaiting_name_for_registration':
        user_name = incoming_msg
        create_user_account_in_db(user, user_name)
        response_message = f"Thanks, {user_name}! You are now registered with FixMate."
        clear_user_state(user)

    elif current_state == 'awaiting_service_request':
        service_details = incoming_msg
        response_message = (
            f"Got it: '{service_details}'.\n\n"
            "Now, please share your location pin using the WhatsApp location feature so we can dispatch a fixer.\n\n"
            "Tap the paperclip icon 📎, then choose 'Location'."
        )
        set_user_state(user, 'awaiting_location', data={'service': service_details})
    
    if response_message:
        send_whatsapp_message(from_number, response_message)

    return Response(status=200)

