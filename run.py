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
from sqlalchemy.exc import SQLAlchemyError

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
DIALOG_360_API_KEY = os.environ.get('DIALOG_360_API_KEY')
DIALOG_360_URL = "https://waba.360dialog.io/v1/messages"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
CLIENT_PLATFORM_FEE = Decimal('10.00')

# --- Initialize Extensions ---
from app.models import db, User, Fixer, Job, DataInsight
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

# --- 360Dialog WhatsApp Service (MODIFIED based on feedback) ---
def send_whatsapp_message(to_number, message_body):
    """
    Sends a WhatsApp message using the 360Dialog API.
    Includes 'recipient_type' and improved error handling as per feedback.
    """
    if not DIALOG_360_API_KEY:
        print("ERROR: DIALOG_360_API_KEY is not set. Cannot send message.")
        return False

    # 360Dialog requires the 'whatsapp:' prefix to be removed.
    if to_number.startswith("whatsapp:+"):
        to_number = to_number.replace("whatsapp:+", "")

    headers = {
        "D360-API-KEY": DIALOG_360_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "to": to_number,
        "recipient_type": "individual",  # FIXED: Added as per 360Dialog requirement.
        "type": "text",
        "text": {
            "body": message_body
        }
    }
    try:
        response = requests.post(DIALOG_360_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        print(f"[{datetime.now()}] Successfully sent message to {to_number}. Response: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        # BEST PRACTICE: Log the full error for troubleshooting.
        print(f"[{datetime.now()}] ERROR: Failed to send WhatsApp message to {to_number}.")
        print(f"Payload: {json.dumps(payload)}")
        if e.response:
            print(f"Status Code: {e.response.status_code}, Response Body: {e.response.text}")
        else:
            print(f"Exception: {e}")
        return False


# --- AI & Helper Functions ---
def transcribe_audio(media_url, media_type):
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY not set."); return None
    try:
        headers = {'D360-API-KEY': DIALOG_360_API_KEY}
        r = requests.get(media_url, headers=headers)
        r.raise_for_status()
        
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
    except requests.exceptions.RequestException as e:
        print(f"Error downloading audio from 360dialog: {e}"); return None
    except Exception as e:
        print(f"An error occurred during transcription: {e}"); return None

def generate_and_act_on_insight():
    if not GEMINI_API_KEY:
        return "Insight generation failed: GEMINI_API_KEY not set."
    completed_jobs = Job.query.filter_by(status='complete').all()
    if not completed_jobs:
        return "Not enough job data to analyze."
    job_data = [{'description': job.description, 'area': job.area} for job in completed_jobs]
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        prompt = f"""
        You are a business analyst for FixMate-SA. Analyze the following list of jobs.
        Identify a single high-demand skill in a specific area.
        Your response MUST be a JSON object with two keys: "skill" and "area".
        For example: {{"skill": "plumbing", "area": "Pretoria"}}
        Job Data: {json.dumps(job_data, indent=2)}
        """
        response = model.generate_content(prompt)
        clean_response = response.text.strip().replace("```json", "").replace("```", "")
        insight_data = json.loads(clean_response)
        skill_in_demand = insight_data.get("skill")
        area_in_demand = insight_data.get("area")
        if not all([skill_in_demand, area_in_demand]):
            return "AI could not determine a specific skill/area insight."
        insight_text = f"High demand for '{skill_in_demand}' services identified in '{area_in_demand}'."
        new_insight = DataInsight(insight_text=insight_text)
        db.session.add(new_insight)
        target_fixer = Fixer.query.filter(
            Fixer.is_active==True,
            Fixer.skills.ilike('%general%'),
            ~Fixer.skills.ilike(f'%{skill_in_demand}%')
        ).first()
        if target_fixer:
            suggestion_message = (
                f"Hi {target_fixer.full_name}, this is FixMate-SA with a business tip!\n\n"
                f"Our system has noticed a high demand for '{skill_in_demand}' services in the {area_in_demand} area. "
                "You could increase your earnings by adding this skill to your profile.\n\n"
                "Consider looking into local accredited courses to get certified."
            )
            send_whatsapp_message(to_number=target_fixer.phone_number, message_body=suggestion_message)
            insight_text += f" Proactively notified {target_fixer.full_name}."
            print(f"Notified {target_fixer.full_name} about upskilling opportunity.")
        db.session.commit()
        return insight_text
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"ERROR: Database error during insight generation: {e}")
        return "Database error prevented insight generation."
    except Exception as e:
        print(f"An error occurred during insight generation: {e}")
        return "Could not generate an insight at this time."

def analyze_feedback_sentiment(comment):
    if not GEMINI_API_KEY:
        print("WARN: GEMINI_API_KEY not set. Cannot analyze sentiment.")
        return "Unknown"
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        prompt = f"""
        Analyze the sentiment of the following customer feedback.
        Classify it as one of these three categories: 'Positive', 'Negative', or 'Neutral'.
        Return ONLY the category name as a single word and nothing else.
        Feedback: "{comment}"
        Sentiment:
        """
        response = model.generate_content(prompt)
        sentiment = response.text.strip().capitalize()
        return sentiment if sentiment in ['Positive', 'Negative', 'Neutral'] else 'Neutral'
    except Exception as e:
        print(f"ERROR: Gemini API call failed during sentiment analysis: {e}")
        return "Unknown"

def classify_service_request(service_description):
    if not GEMINI_API_KEY:
        print("WARN: GEMINI_API_KEY not set. Falling back to keyword matching.")
        desc = service_description.lower()
        if any(k in desc for k in ['plumb', 'pipe', 'leak', 'geyser', 'tap', 'toilet']): return 'plumbing'
        if any(k in desc for k in ['light', 'electr', 'plug', 'wiring', 'switch']): return 'electrical'
        return 'general'
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        prompt = f"""
        Analyze the following home repair request from a South African user.
        Classify it into one of these three categories: 'plumbing', 'electrical', or 'general'.
        Return ONLY the category name as a single word and nothing else.
        Request: "{service_description}"
        Category:
        """
        response = model.generate_content(prompt)
        classification = response.text.strip().lower()
        return classification if classification in ['plumbing', 'electrical', 'general'] else 'general'
    except Exception as e:
        print(f"ERROR: Gemini API call failed during classification: {e}. Defaulting to 'general'.")
        return 'general'

def get_or_create_user(phone_number):
    try:
        if not phone_number.startswith("whatsapp:"):
            phone_number = f"whatsapp:{phone_number}"
        user = User.query.filter_by(phone_number=phone_number).first()
        if not user:
            user = User(phone_number=phone_number)
            db.session.add(user)
            db.session.commit()
        return user
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"ERROR: Could not get or create user due to database error: {e}")
        return None

def set_user_state(user, new_state, data=None):
    try:
        cached_data = json.loads(user.service_request_cache) if user.service_request_cache else {}
        if data:
            cached_data.update(data)
        user.conversation_state = new_state
        user.service_request_cache = json.dumps(cached_data)
        db.session.commit()
        print(f"State for {user.phone_number} set to {new_state} with data: {cached_data}")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"ERROR: Database error setting user state: {e}")

def get_user_cache(user):
    if user.service_request_cache:
        try:
            return json.loads(user.service_request_cache)
        except json.JSONDecodeError:
            return {}
    return {}

def clear_user_state(user):
    try:
        user.conversation_state = None
        user.service_request_cache = None
        db.session.commit()
        print(f"State for {user.phone_number} cleared.")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"ERROR: Database error clearing user state: {e}")

def find_fixer_for_job(job):
    # This function logic remains unchanged.
    skill_needed = classify_service_request(job.description)
    eligible_fixers = Fixer.query.filter(
        Fixer.is_active==True,
        Fixer.vetting_status=='approved',
        Fixer.skills.ilike(f'%{skill_needed}%')
    ).all()
    if not eligible_fixers:
        eligible_fixers = Fixer.query.filter(
            Fixer.is_active==True,
            Fixer.vetting_status=='approved',
            Fixer.skills.ilike('%general%')
        ).all()
    if not eligible_fixers:
        print("No eligible fixers found for this job.")
        return None
    scored_fixers = []
    for fixer in eligible_fixers:
        score = 0
        if fixer.current_latitude and fixer.current_longitude and job.latitude and job.longitude:
            client_location = (job.latitude, job.longitude)
            fixer_location = (fixer.current_latitude, fixer.current_longitude)
            distance_km = geodesic(client_location, fixer_location).km
            proximity_score = max(0, 50 - (distance_km * 2))
            score += proximity_score
        avg_rating = db.session.query(db.func.avg(Job.rating)).filter(Job.fixer_id==fixer.id, Job.rating != None).scalar() or 3.5
        score += (avg_rating / 5) * 30
        if fixer.last_assigned_at:
            hours_since_last_job = (datetime.now(timezone.utc) - fixer.last_assigned_at).total_seconds() / 3600
            score += min(20, hours_since_last_job)
        else:
            score += 20
        scored_fixers.append({'fixer': fixer, 'score': score})
        print(f"Fixer: {fixer.full_name}, Score: {score:.2f}")
    if not scored_fixers:
        return None
    best_fixer_data = max(scored_fixers, key=lambda x: x['score'])
    best_fixer = best_fixer_data['fixer']
    try:
        best_fixer.last_assigned_at = datetime.now(timezone.utc)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"ERROR: DB error updating fixer last_assigned_at: {e}")
    print(f"Best match found: {best_fixer.full_name} with score {best_fixer_data['score']:.2f}")
    return best_fixer

def create_new_job_in_db(user, job_data):
    try:
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
            notification_message = f"New FixMate-SA Job Alert!\n\nService: {job.description}\nClient Contact: {job.client_contact_number}\n\nPlease go to your Fixer Portal to accept this job:\n{url_for('fixer_login', _external=True)}"
            send_whatsapp_message(to_number=matched_fixer.phone_number, message_body=notification_message)
        else:
            job.status = 'unassigned'
        db.session.add(job)
        db.session.commit()
        return job.id, matched_fixer is not None
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"ERROR: Could not create new job due to database error: {e}")
        return None, False


# --- Admin Commands & Web Routes ---
# Note: All Flask CLI commands and web routes remain unchanged as the feedback
# was focused on the WhatsApp API interaction and backend robustness.
# (All commands and routes from @app.cli.command("add-fixer") to @app.route('/payment/notify') are unchanged)
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

# ... (Rest of the CLI commands and Flask routes are identical to the original file)
# ... The provided code for all other routes (@app.cli.command, @app.route) is assumed to be correct
# ... and is not repeated here for brevity. The main change is in the webhook below.


# --- Main WhatsApp Webhook (CORRECTED FOR 360DIALOG) ---
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Endpoint to receive incoming WhatsApp messages from 360dialog."""
    data = request.json
    # BEST PRACTICE: Log the full incoming request with a timestamp for debugging.
    print(f"[{datetime.now()}] Received 360dialog webhook: {json.dumps(data, indent=2)}")

    # Initialize variables
    from_number = None
    incoming_msg = ""
    latitude = None
    longitude = None
    
    # FIXED: More robust validation of the incoming webhook data structure.
    try:
        message = data['messages'][0]
        from_number_raw = message.get('from')
        if not from_number_raw:
            print("Webhook payload missing 'from' number in message object.")
            return Response(status=200)
        from_number = f"whatsapp:+{from_number_raw}"

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
            return Response(status=200)
        else:
            print(f"Received unhandled message type: {msg_type}")
            return Response(status=200)

    except (KeyError, IndexError, TypeError) as e:
        # BEST PRACTICE: Log the specific parsing error.
        print(f"ERROR: Could not parse 360dialog payload. Error: {e}. Payload: {data}")
        return Response(status=200)

    if not from_number:
        print("Could not determine sender number after parsing. Exiting.")
        return Response(status=200)

    # --- Start Conversation State Machine ---
    user = get_or_create_user(from_number)
    if not user:
        # Handle case where user creation failed
        send_whatsapp_message(from_number, "We're sorry, but there was a problem with our system. Please try again in a few moments.")
        return Response(status=200)

    current_state = user.conversation_state
    response_message = ""

    # The conversation flow logic remains the same.
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

    elif current_state == 'awaiting_rating_comment':
        job_id_to_rate_str = get_user_cache(user).get('job_id')
        job = db.session.get(Job, int(job_id_to_rate_str)) if job_id_to_rate_str else None
        if job:
            job.rating_comment = incoming_msg
            job.sentiment = analyze_feedback_sentiment(incoming_msg)
            db.session.commit()
            response_message = "Your feedback has been recorded. We appreciate you helping us improve FixMate-SA!"
            clear_user_state(user)

    elif current_state == 'awaiting_service_request':
        response_message = "Got it. To help us find the nearest fixer, please share your location pin.\n\nTap the paperclip icon 📎, then choose 'Location'."
        set_user_state(user, 'awaiting_location', data={'service': incoming_msg})

    elif current_state == 'awaiting_location' and latitude and longitude:
        response_message = "Thank you for sharing your location.\n\nLastly, please provide a contact number (e.g., 082 123 4567) that the fixer can call if needed."
        set_user_state(user, 'awaiting_contact_number', data={'latitude': str(latitude), 'longitude': str(longitude)})

    elif current_state == 'awaiting_contact_number':
        potential_number = incoming_msg
        if any(char.isdigit() for char in potential_number) and len(potential_number) >= 10:
            terms_url = url_for('terms', _external=True)
            response_message = (
                f"Great! We have all the details.\n\n"
                f"By proceeding, you agree to the FixMate-SA Terms of Service, which states that payment is handled directly between you and the fixer.\n"
                f"View here: {terms_url}\n\n"
                "Reply *YES* to confirm and dispatch a fixer."
            )
            set_user_state(user, 'awaiting_terms_approval', data={'contact': potential_number})
        else:
            response_message = "That doesn't seem to be a valid phone number. Please try again."

    elif current_state == 'awaiting_terms_approval':
        if 'yes' in incoming_msg.lower():
            job_data = get_user_cache(user)
            job_id, fixer_found = create_new_job_in_db(user, job_data)
            if job_id: # Check if job creation was successful
                if fixer_found:
                    response_message = f"Perfect! We have logged your request (Job #{job_id}) and have notified a nearby fixer. They will contact you shortly."
                else:
                    response_message = f"Thank you. We have logged your request (Job #{job_id}), but all our fixers for this skill are currently busy. We will notify you as soon as one becomes available."
            else:
                response_message = "Sorry, there was a system error creating your job. Please try again."
            clear_user_state(user)
        else:
            response_message = "Job request cancelled. Please say 'hello' to start a new request."
            clear_user_state(user)

    else: # Default state / start of conversation
        if incoming_msg:
            clear_user_state(user) # Clear any stale data
            if incoming_msg.lower() in ['hi', 'hello', 'hallo', 'dumela', 'sawubona', 'molo']:
                response_message = "Welcome to FixMate-SA! To request a service, please describe what you need (e.g., 'Leaking pipe') or send a voice note."
                set_user_state(user, 'awaiting_service_request')
            else:
                response_message = "Got it. To help us find the nearest fixer, please share your location pin.\n\nTap the paperclip icon 📎, then choose 'Location'."
                set_user_state(user, 'awaiting_location', data={'service': incoming_msg})

    if response_message:
        send_whatsapp_message(from_number, response_message)

    return Response(status=200)
