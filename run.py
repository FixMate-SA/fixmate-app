# run.py
import os
import re
from flask import Flask, request, Response, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import click

# --- App Initialization ---
app = Flask(__name__)

# --- Database Configuration ---
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import models and initialize db
from app.models import db, User, Fixer, Job
db.init_app(app)

# Initialize Flask-Migrate for managing database schema changes
migrate = Migrate(app, db)


# --- Admin Commands ---
@app.cli.command("add-fixer")
@click.argument("name")
@click.argument("phone")
@click.argument("skills")
def add_fixer(name, phone, skills):
    """Creates a new fixer in the database."""
    if not phone.startswith("whatsapp:"):
        phone = f"whatsapp:{phone}"
        
    new_fixer = Fixer(full_name=name, phone_number=phone, skills=skills)
    db.session.add(new_fixer)
    db.session.commit()
    print(f"Successfully added fixer: {name} with number {phone}")


# --- State Management (Uses the database) ---
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
from app.services import send_whatsapp_message

def create_user_account_in_db(user, name):
    """Updates the user's name in the database."""
    user.full_name = name
    db.session.commit()
    print(f"Updated user: {name} with number {user.phone_number}")
    return True

def find_fixer_for_job(service_description):
    """
    Finds an available fixer based on skills.
    """
    if 'plumb' in service_description.lower() or 'pipe' in service_description.lower() or 'leak' in service_description.lower():
        skill_needed = 'plumbing'
    elif 'light' in service_description.lower() or 'electr' in service_description.lower():
        skill_needed = 'electrical'
    else:
        return None
        
    fixer = Fixer.query.filter(Fixer.is_active==True, Fixer.skills.ilike(f'%{skill_needed}%')).first()
    return fixer

def create_new_job_in_db(user, service, lat, lon, contact):
    """Creates a Job record, finds a fixer, and notifies them."""
    new_job = Job(
        description=service,
        latitude=lat,
        longitude=lon,
        client_contact_number=contact,
        client_id=user.id
    )

    matched_fixer = find_fixer_for_job(service)
    
    if matched_fixer:
        new_job.assigned_fixer = matched_fixer
        new_job.status = 'assigned'
        print(f"Job {new_job.id} assigned to {matched_fixer.full_name}")
        
        notification_message = (
            f"New FixMate Job Alert!\n\n"
            f"Service Needed: {service}\n"
            f"Client Contact: {contact}\n\n"
            f"Please go to your Fixer dashboard to accept this job."
        )
        send_whatsapp_message(to_number=matched_fixer.phone_number, message_body=notification_message)
    else:
        print(f"No suitable fixer found for job with description: {service}")

    db.session.add(new_job)
    db.session.commit()
    
    return new_job.id, matched_fixer is not None


# --- Web and WhatsApp Routes ---

@app.route('/', methods=['GET'])
def index():
    return "<h1>FixMate WhatsApp Bot is running.</h1>", 200

# --- NEW: Web Login Route ---
@app.route('/login', methods=['GET'])
def login():
    """Displays the login page."""
    return render_template('login.html')

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Endpoint to receive incoming WhatsApp messages."""
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    latitude = request.values.get('Latitude')
    longitude = request.values.get('Longitude')

    user = get_or_create_user(from_number)
    current_state = user.conversation_state
    response_message = ""

    # (The conversational logic block remains unchanged)
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
            job_id, fixer_found = create_new_job_in_db(
                user,
                user.service_request_cache,
                user.latitude_cache,
                user.longitude_cache,
                potential_number
            )
            
            if fixer_found:
                response_message = (
                    f"Perfect! Your request has been logged (Job #{job_id}) and we have assigned a fixer.\n\n"
                    f"They will contact you on {potential_number} shortly."
                )
            else:
                 response_message = (
                    f"Thank you. Your request has been logged (Job #{job_id}).\n\n"
                    f"All our qualified fixers are currently busy. We will notify you as soon as one becomes available."
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

