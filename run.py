# run.py
import os
import re
import hashlib
import requests
import io # New import
from urllib.parse import urlencode
from flask import Flask, request, Response, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
import click
import openai # New import for OpenAI

# --- App Initialization & Config ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-very-secret-key-that-is-long-and-random')
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- API Keys Configuration ---
PAYFAST_MERCHANT_ID = os.environ.get('PAYFAST_MERCHANT_ID')
PAYFAST_MERCHANT_KEY = os.environ.get('PAYFAST_MERCHANT_KEY')
PAYFAST_URL = 'https://sandbox.payfast.co.za/eng/process'
# UPDATED: Replaced Gemini key with OpenAI key
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# --- Initialize Extensions ---
from app.models import db, User, Fixer, Job
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    if session.get('user_type') == 'fixer': return db.session.get(Fixer, int(user_id))
    return db.session.get(User, int(user_id))
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


# --- NEW: Speech-to-Text Function using OpenAI Whisper ---
def transcribe_audio(media_url):
    """Downloads audio from a Twilio URL and transcribes it using the Whisper API."""
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set. Cannot transcribe audio.")
        return None
        
    try:
        auth = (os.environ.get('TWILIO_ACCOUNT_SID'), os.environ.get('TWILIO_AUTH_TOKEN'))
        r = requests.get(media_url, auth=auth)
        
        if r.status_code == 200:
            # We need to present the audio data as a file-like object to the API.
            # The name is important for the API to recognize the file type.
            audio_data = io.BytesIO(r.content)
            audio_data.name = 'voice_note.ogg' 

            print("Audio downloaded. Transcribing with OpenAI Whisper...")
            
            # Call the OpenAI Audio endpoint
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_data
            )
            
            if transcript.text:
                print(f"Transcription successful: '{transcript.text}'")
                return transcript.text
            else:
                print("Transcription failed: No text in response.")
                return None
        else:
            print(f"Error downloading audio: {r.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return None


# --- Admin Commands (Unchanged) ---
@app.cli.command("add-fixer")
@click.argument("name")
@click.argument("phone")
@click.argument("skills")
def add_fixer(name, phone, skills):
    if phone.startswith('0') and len(phone) == 10: formatted_phone = f"+27{phone[1:]}"
    elif phone.startswith('+') and len(phone) == 12: formatted_phone = phone
    else: print(f"Error: Invalid phone number format."); return
    whatsapp_phone = f"whatsapp:{formatted_phone}"
    if Fixer.query.filter_by(phone_number=whatsapp_phone).first():
        print(f"Error: Fixer with phone number {whatsapp_phone} already exists."); return
    new_fixer = Fixer(full_name=name, phone_number=whatsapp_phone, skills=skills)
    db.session.add(new_fixer); db.session.commit()
    print(f"Successfully added fixer: '{name}' with number {whatsapp_phone}")

@app.cli.command("promote-admin")
@click.argument("phone")
def promote_admin(phone):
    if not (phone.startswith('0') and len(phone) == 10):
        print("Error: Please provide a valid 10-digit SA number (e.g., 0821234567)."); return
    formatted_phone = f"whatsapp:+27{phone[1:]}"
    user = User.query.filter_by(phone_number=formatted_phone).first()
    if not user: print(f"Error: User with phone number {formatted_phone} not found."); return
    user.is_admin = True; db.session.commit()
    print(f"Successfully promoted '{user.full_name or user.phone_number}' to admin.")


# --- Helper & Service Functions (Unchanged) ---
from app.services import send_whatsapp_message
def get_or_create_user(phone_number):
    if not phone_number.startswith("whatsapp:"): phone_number = f"whatsapp:{phone_number}"
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user: user = User(phone_number=phone_number); db.session.add(user); db.session.commit()
    return user
def set_user_state(user, new_state, data=None):
    user.conversation_state = new_state
    if data is not None: user.service_request_cache = str(data.get('job_id')) if data.get('job_id') else None
    db.session.commit()
def clear_user_state(user):
    user.conversation_state, user.service_request_cache = None, None; db.session.commit()
def find_fixer_for_job(service_description):
    desc = service_description.lower()
    skill_needed = None
    if any(k in desc for k in ['plumb', 'pipe', 'leak', 'geyser', 'tap']): skill_needed = 'plumbing'
    elif any(k in desc for k in ['light', 'electr', 'plug', 'wiring']): skill_needed = 'electrical'
    if skill_needed:
        fixer = Fixer.query.filter(Fixer.is_active==True, Fixer.skills.ilike(f'%{skill_needed}%')).first()
        if fixer: return fixer
    return Fixer.query.filter(Fixer.is_active==True, Fixer.skills.ilike('%general%')).first()
def get_quote_for_service(service_description):
    desc = service_description.lower()
    if any(k in desc for k in ['plumb', 'pipe', 'leak', 'geyser', 'tap', 'toilet']): return 450.00
    if any(k in desc for k in ['light', 'electr', 'plug', 'wiring', 'switch']): return 400.00
    return 350.00
def create_new_job_in_db(user, service, lat, lon, contact):
    job = Job(description=service, latitude=lat, longitude=lon, client_contact_number=contact, client_id=user.id)
    matched_fixer = find_fixer_for_job(service)
    if matched_fixer:
        job.assigned_fixer = matched_fixer; job.status = 'assigned'
        send_whatsapp_message(to_number=matched_fixer.phone_number, message_body=f"New FixMate Job Alert!\n\nService: {service}\nClient Contact: {contact}\n\nPlease go to your Fixer Portal to accept this job:\n{url_for('fixer_login', _external=True)}")
    db.session.add(job); db.session.commit()
    return job.id, matched_fixer is not None
def create_user_account_in_db(user, name):
    user.full_name = name; db.session.commit(); return True


# --- Main Web Routes (Unchanged) ---
@app.route('/')
def index(): return "<h1>FixMate-SA Bot is running.</h1>"
# --- Authentication Routes (Unchanged) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    # ... code ...
    pass
# ... and so on for all other web routes ...


# --- Main WhatsApp Webhook ---
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Endpoint to receive incoming WhatsApp messages."""
    from_number = request.values.get('From', '')
    media_url = request.values.get('MediaUrl0')
    media_type = request.values.get('MediaContentType0', '')
    incoming_msg = request.values.get('Body', '').strip()
    
    # UPDATED: Logic to call new transcribe_audio function
    if media_url and 'audio' in media_type:
        print(f"Received audio message from {from_number}.")
        transcribed_text = transcribe_audio(media_url) # No longer needs media_type
        if transcribed_text:
            incoming_msg = transcribed_text
        else:
            send_whatsapp_message(from_number, "Sorry, I had trouble understanding that audio. Please try sending a text message instead.")
            return Response(status=200)

    # (The rest of the conversation logic is UNCHANGED)
    # ...
    
    return Response(status=200)
