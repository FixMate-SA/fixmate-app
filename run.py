# run.py
import os
import re
import hashlib
import requests
import io
import json
from decimal import Decimal
from urllib.parse import urlencode
from flask import Flask, request, Response, render_template, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
import click
import google.generativeai as genai
from geopy.distance import geodesic
from datetime import datetime, timezone

# --- App Initialization & Config ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-very-secret-key-that-is-long-and-random')
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- API Keys & Constants Configuration ---
PAYFAST_MERCHANT_ID = os.environ.get('PAYFAST_MERCHANT_ID')
PAYFAST_MERCHANT_KEY = os.environ.get('PAYFAST_MERCHANT_KEY')
PAYFAST_URL = 'https://sandbox.payfast.co.za/eng/process'
DIALOG_360_URL = 'https://waba-v2.360dialog.io' # Base URL for 360dialog
D360_API_KEY = os.environ.get('D360_API_KEY') # Store your 360dialog API key
CLIENT_PLATFORM_FEE = Decimal('10.00')

# --- Initialize Extensions ---
from app.models import db, User, Fixer, Job, DataInsight
from app.services import send_whatsapp_message
# Import helpers
from app.helpers import format_sa_phone_number, get_gemini_model, admin_required, fixer_required

db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    if session.get('user_type') == 'fixer':
        return db.session.get(Fixer, int(user_id))
    return db.session.get(User, int(user_id))

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# --- AI & Helper Functions (Single Source of Truth) ---
def transcribe_audio(audio_bytes, mime_type="audio/ogg"):
    try:
        gemini_file = genai.upload_file(file_data=audio_bytes, mime_type=mime_type)
        model = get_gemini_model()
        prompt = "Please transcribe the following voice note. The speaker may use English, Sepedi, Xitsonga, or isiZulu."
        result = model.generate_content([prompt, gemini_file])
        genai.delete_file(gemini_file.name)
        return result.text.strip() if result.text else "Transcription failed."
    except Exception as e:
        print(f"[Transcription Error] {e}")
        return "Sorry, transcription failed."

def classify_service_request(service_description):
    try:
        model = get_gemini_model()
        prompt = f"""
        Analyze the following home repair request from a South African user.
        Classify it into one of these three categories: 'plumbing', 'electrical', or 'general'.
        Return ONLY the category name as a single word and nothing else.
        Request: "{service_description}"
        Category:
        """
        response = model.generate_content(prompt)
        classification = response.text.strip().lower()
        if classification in ['plumbing', 'electrical', 'general']:
            return classification
        return 'general'
    except Exception as e:
        print(f"WARN: Gemini API call failed during classification: {e}. Falling back to keyword matching.")
        desc = service_description.lower()
        if any(k in desc for k in ['plumb', 'pipe', 'leak', 'geyser', 'tap', 'toilet']): return 'plumbing'
        if any(k in desc for k in ['light', 'electr', 'plug', 'wiring', 'switch']): return 'electrical'
        return 'general'

# ... (Other AI functions like analyze_feedback_sentiment, generate_and_act_on_insight, etc., go here)

# === FIX: USER AND STATE MANAGEMENT FUNCTIONS MUST BE DEFINED BEFORE THE WEBHOOK ===
# --- User & State Management (Single Source of Truth) ---
def get_or_create_user(phone_number):
    """Gets a user by phone number or creates them if they don't exist."""
    # Ensure phone_number is in the correct format before querying
    whatsapp_number = phone_number
    if not phone_number.startswith("whatsapp:"):
        whatsapp_number = f"whatsapp:{phone_number}"

    user = User.query.filter_by(phone_number=whatsapp_number).first()
    if not user:
        user = User(phone_number=whatsapp_number)
        db.session.add(user)
        db.session.commit()
    return user

def set_user_state(user, new_state, data=None):
    """Sets the user's conversation state and caches related data."""
    cached_data = json.loads(user.service_request_cache) if user.service_request_cache else {}
    if data:
        cached_data.update(data)
    user.conversation_state = new_state
    user.service_request_cache = json.dumps(cached_data)
    db.session.commit()

def get_user_cache(user):
    """Retrieves cached data for a user."""
    return json.loads(user.service_request_cache) if user.service_request_cache else {}

def clear_user_state(user):
    """Clears a user's conversation state and cache."""
    user.conversation_state = None
    user.service_request_cache = None
    db.session.commit()

# ... (Other helper functions like find_fixer_for_job and create_new_job_in_db go here)
# Make sure they are also defined before the whatsapp_webhook if they are called inside it.

def find_fixer_for_job(job):
    """Finds the best-matched fixer for a job using a scoring system."""
    skill_needed = classify_service_request(job.description)
    query_filters = [Fixer.is_active == True, Fixer.vetting_status == 'approved']
    
    eligible_fixers = Fixer.query.filter(*query_filters, Fixer.skills.ilike(f'%{skill_needed}%')).all()
    if not eligible_fixers:
        eligible_fixers = Fixer.query.filter(*query_filters, Fixer.skills.ilike('%general%')).all()

    if not eligible_fixers:
        print("No eligible fixers found for this job.")
        return None

    # ... (rest of the find_fixer_for_job logic)
    scored_fixers = []
    for fixer in eligible_fixers:
        score = 0
        if all([fixer.current_latitude, fixer.current_longitude, job.latitude, job.longitude]):
            distance_km = geodesic((job.latitude, job.longitude), (fixer.current_latitude, fixer.current_longitude)).km
            score += max(0, 50 - (distance_km * 2))
        avg_rating = db.session.query(db.func.avg(Job.rating)).filter(Job.fixer_id == fixer.id, Job.rating.isnot(None)).scalar() or 3.5
        score += (avg_rating / 5) * 30
        if fixer.last_assigned_at:
            hours_since_last = (datetime.now(timezone.utc) - fixer.last_assigned_at).total_seconds() / 3600
            score += min(20, hours_since_last)
        else:
            score += 20
        scored_fixers.append({'fixer': fixer, 'score': score})
    if not scored_fixers:
        return None
    best_fixer = max(scored_fixers, key=lambda x: x['score'])['fixer']
    best_fixer.last_assigned_at = datetime.now(timezone.utc)
    db.session.commit()
    return best_fixer

def create_new_job_in_db(user, job_data):
    """Creates a job, finds a fixer, and sends notifications."""
    job = Job(
        description=job_data.get('service'),
        latitude=job_data.get('latitude'),
        longitude=job_data.get('longitude'),
        client_contact_number=job_data.get('contact'),
        client_id=user.id
    )
    matched_fixer = find_fixer_for_job(job)
    if matched_fixer:
        job.assigned_fixer = matched_fixer
        job.status = 'assigned'
        notification_message = (
            f"New FixMate-SA Job Alert!\n\n"
            f"Service: {job.description}\n"
            f"Client Contact: {job.client_contact_number}\n\n"
            f"Please go to your Fixer Portal to accept this job:\n{url_for('fixer_login', _external=True)}"
        )
        send_whatsapp_message(to_number=matched_fixer.phone_number, message_body=notification_message)
    else:
        job.status = 'unassigned'
    
    db.session.add(job)
    db.session.commit()
    return job.id, matched_fixer is not None

# --- CLI Commands ---
# (Your CLI commands go here)

# --- Web Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

# (Login, Auth, Dashboard, and other routes go here)
# ...

# === WHATSAPP WEBHOOK ===
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    data = request.json
    print(f"Received 360dialog webhook: {json.dumps(data, indent=2)}")

    try:
        value = data['entry'][0]['changes'][0]['value']

        # Ignore status updates
        if 'statuses' in value:
            print("Received a status update. Ignoring.")
            return Response(status=200)
        
        # Process incoming messages
        if 'messages' in value:
            message = value['messages'][0]
            from_number = f"whatsapp:+{message['from']}"
            user = get_or_create_user(from_number)
            
            msg_type = message.get('type')
            incoming_msg = ""
            location = None
            
            if msg_type == 'text':
                incoming_msg = message['text']['body'].strip()

            elif msg_type == 'audio':
                audio_id = message['audio']['id']
                media_url_endpoint = f"{DIALOG_360_URL}/v1/media/{audio_id}"
                headers = {'API-KEY': D360_API_KEY}
                
                media_info_response = requests.get(media_url_endpoint, headers=headers)
                
                if media_info_response.status_code != 200:
                    print(f"Error fetching media info: {media_info_response.text}")
                    send_whatsapp_message(from_number, "Sorry, I couldn't process the voice note.")
                    return Response(status=200)

                media_info = media_info_response.json()
                audio_download_url = media_info.get('url')

                if not audio_download_url:
                    print(f"Could not find 'url' key in media info response: {media_info}")
                    send_whatsapp_message(from_number, "Sorry, an error occurred while trying to get the voice note.")
                    return Response(status=200)

                audio_content_response = requests.get(audio_download_url)
                
                if audio_content_response.status_code == 200:
                    audio_bytes = audio_content_response.content
                    mime_type = message['audio'].get('mime_type', 'audio/ogg')
                    incoming_msg = transcribe_audio(audio_bytes, mime_type)
                    
                    if "failed" in incoming_msg.lower():
                        send_whatsapp_message(from_number, incoming_msg)
                        return Response(status=200)
                else:
                    print(f"Error downloading audio content. Status: {audio_content_response.status_code}")
                    send_whatsapp_message(from_number, "Sorry, I had trouble downloading the voice note.")
                    return Response(status=200)

            elif msg_type == 'location':
                location = message['location']
            
            # --- Conversation State Machine ---
            current_state = user.conversation_state
            response_message = ""

            if current_state == 'awaiting_location' and location:
                 response_message = "Thank you for sharing your location.\n\nLastly, please provide a contact number (e.g., 082 123 4567) that the fixer can call if needed."
                 set_user_state(user, 'awaiting_contact_number', data={'latitude': str(location.get('latitude')), 'longitude': str(location.get('longitude'))})

            elif incoming_msg:
                if current_state == 'awaiting_service_request':
                    response_message = "Got it. To help us find the nearest fixer, please share your location pin.\n\nTap the paperclip icon 📎, then choose 'Location'."
                    set_user_state(user, 'awaiting_location', data={'service': incoming_msg})
                
                elif current_state == 'awaiting_contact_number':
                    # (Contact number logic here)
                    pass

                elif current_state == 'awaiting_terms_approval':
                    # (Terms approval logic here)
                    pass
                
                else: 
                    clear_user_state(user)
                    if incoming_msg.lower() in ['hi', 'hello', 'hallo', 'dumela', 'sawubona', 'molo']:
                        response_message = "Welcome to FixMate-SA! To request a service, please describe what you need (e.g., 'Leaking pipe') or send a voice note."
                        set_user_state(user, 'awaiting_service_request')
                    else:
                        response_message = "Got it. To help us find the nearest fixer, please share your location pin.\n\nTap the paperclip icon 📎, then choose 'Location'."
                        set_user_state(user, 'awaiting_location', data={'service': incoming_msg})
            
            if response_message:
                send_whatsapp_message(from_number, response_message)

    except (IndexError, KeyError) as e:
        print(f"Error parsing 360dialog payload or processing message: {e}")

    return Response(status=200)