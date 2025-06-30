# run.py
import os
import re
import hashlib
import requests # Needed for downloading audio
from urllib.parse import urlencode
from flask import Flask, request, Response, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
import click
import google.generativeai as genai # New import for Gemini

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
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') # New
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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


# --- NEW: Simplified Speech-to-Text Function (No Conversion) ---
def transcribe_audio(media_url, media_type):
    """Downloads audio and transcribes it using the Gemini API directly."""
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY not set."); return None
        
    try:
        auth = (os.environ.get('TWILIO_ACCOUNT_SID'), os.environ.get('TWILIO_AUTH_TOKEN'))
        r = requests.get(media_url, auth=auth)
        
        if r.status_code == 200:
            print(f"Audio downloaded. Uploading to Gemini with MIME type: {media_type}")
            
            # Upload the raw audio bytes directly to Gemini
            gemini_file = genai.upload_file(r.content, mime_type=media_type)
            
            # Ask the model to transcribe, specifying the languages for better accuracy
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            prompt = "Please transcribe the following audio. The speaker may be using English, Sepedi, Xitsonga, or Venda."
            response = model.generate_content([prompt, gemini_file])
            
            # Clean up the file from the API after use
            genai.delete_file(gemini_file.name)
            
            if response.text:
                print(f"Transcription successful: '{response.text}'")
                return response.text
            return None
        else:
            print(f"Error downloading audio: {r.status_code}"); return None
    except Exception as e:
        print(f"An error occurred during transcription: {e}"); return None


# (The rest of the file, including all Admin commands, Helper Functions, and Web Routes, remains unchanged)
# ...


# --- Main WhatsApp Webhook ---
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Endpoint to receive incoming WhatsApp messages."""
    from_number = request.values.get('From', '')
    
    media_url = request.values.get('MediaUrl0')
    media_type = request.values.get('MediaContentType0', '') # e.g., 'audio/ogg'
    incoming_msg = request.values.get('Body', '').strip()
    
    # Check if the message is a voice note first
    if media_url and 'audio' in media_type:
        print(f"Received audio message from {from_number}.")
        transcribed_text = transcribe_audio(media_url, media_type)
        if transcribed_text:
            incoming_msg = transcribed_text # Overwrite the empty body with the transcription
        else:
            # If transcription fails, inform the user and stop
            send_whatsapp_message(from_number, "Sorry, I had trouble understanding that audio. Please try sending a text message instead.")
            return Response(status=200)

    # The rest of the conversation logic proceeds with `incoming_msg`
    # It doesn't matter if it came from text or a successfully transcribed voice note
    user = get_or_create_user(from_number)
    current_state = user.conversation_state
    response_message = ""
    
    # (The entire conversational logic block remains unchanged from our last working version)
    if current_state == 'awaiting_rating':
        # ... logic to handle rating
        pass
    elif current_state == 'awaiting_service_request':
        # ... logic to handle new service request
        pass
    # ... all other elif blocks for the conversation ...
    else: # Default state
        response_message = "Welcome to FixMate-SA! To request a service, please describe what you need (e.g., 'Leaking pipe') or send a voice note."
        set_user_state(user, 'awaiting_service_request')
    
    if response_message:
        send_whatsapp_message(from_number, response_message)
        
    return Response(status=200)

