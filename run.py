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
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

CLIENT_PLATFORM_FEE = Decimal('10.00')

# --- Initialize Extensions ---
from app.models import db, User, Fixer, Job, DataInsight
from app.services import send_whatsapp_message
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    if session.get('user_type') == 'fixer':
        return db.session.get(Fixer, int(user_id))
    return db.session.get(User, int(user_id))

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# --- AI & Helper Functions ---
# (All functions from transcribe_audio to create_new_job_in_db are unchanged)
def transcribe_audio(media_url, media_type):
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY not set."); return None
    try:
        headers = {'D360-API-KEY': os.environ.get('DIALOG_360_API_KEY')}
        r = requests.get(media_url, headers=headers)
        if r.status_code == 200:
            gemini_file = genai.upload_file(io.BytesIO(r.content), mime_type=media_type)
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            prompt = [
                "Please transcribe the following audio. The user is in South Africa and might be speaking in English, Sepedi, Xitsonga, Tshivenda, or Afrikaans.",
                gemini_file
            ]
            response = model.generate_content(prompt)
            genai.delete_file(gemini_file.name)
            if response.text:
                print(f"Transcription successful: '{response.text}'")
                return response.text
            return None
        else:
            print(f"Error downloading audio from 360dialog: {r.status_code}"); return None
    except Exception as e:
        print(f"An error occurred during transcription: {e}"); return None

# [All other helper functions remain unchanged - generate_and_act_on_insight, analyze_feedback_sentiment, etc.]

# --- Main WhatsApp Webhook (FIXED FOR 360DIALOG) ---
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Endpoint to receive incoming WhatsApp messages from 360dialog."""
    # Return 200 immediately as per best practices
    try:
        data = request.json
        print(f"[{datetime.now()}] Received 360dialog webhook: {json.dumps(data, indent=2)}")
        
        # Process webhook asynchronously
        process_webhook_data(data)
        
    except Exception as e:
        print(f"ERROR: Could not parse 360dialog payload. Error: {e}")
    
    return Response(status=200)

def process_webhook_data(data):
    """Process webhook data asynchronously"""
    # Initialize variables
    from_number = None
    incoming_msg = ""
    latitude = None
    longitude = None
    
    try:
        # Parse 360dialog webhook structure
        if 'entry' in data and data['entry']:
            entry = data['entry'][0]
            changes = entry.get('changes', [])
            
            if changes:
                value = changes[0].get('value', {})
                messages = value.get('messages', [])
                
                if messages:
                    message = messages[0]
                    
                    # Extract sender's number
                    from_number = f"whatsapp:+{message.get('from')}"
                    
                    # Determine message type and extract content
                    msg_type = message.get('type')
                    if msg_type == 'text':
                        incoming_msg = message.get('text', {}).get('body', '').strip()
                    elif msg_type == 'location':
                        latitude = message.get('location', {}).get('latitude')
                        longitude = message.get('location', {}).get('longitude')
                    elif msg_type == 'audio':
                        audio_id = message.get('audio', {}).get('id')
                        print(f"Received audio message with ID: {audio_id}. Media URL retrieval needs to be implemented.")
                        send_whatsapp_message(from_number, "Sorry, audio message processing is not yet enabled.")
                        return
                    else:
                        print(f"Received unhandled message type: {msg_type}")
                        return
                        
    except Exception as e:
        print(f"ERROR: Could not parse 360dialog payload. Error: {e}. Payload: {data}")
        return
    
    # If we couldn't parse a valid sender number, exit
    if not from_number:
        print("No valid sender number found in webhook")
        return
    
    # --- Start Conversation State Machine ---
    user = get_or_create_user(from_number)
    current_state = user.conversation_state
    response_message = ""
    
    # [Rest of conversation logic remains exactly the same]
    if current_state == 'awaiting_rating':
        job_id_to_rate_str = get_user_cache(user).get('job_id')
        job = db.session.get(Job, int(job_id_to_rate_str)) if job_id_to_rate_str else None
        if job and incoming_msg.isdigit() and 1 <= int(incoming_msg) <= 5:
            job.rating = int(incoming_msg)
            db.session.commit()
            response_message = "Thank you for the rating! Could you please share a brief comment about your experience?"
            set_user_state(user, 'awaiting_rating_comment', data={'job_id': job.id})
        else:
            response_message = "Thank you for your feedback!"
            clear_user_state(user)