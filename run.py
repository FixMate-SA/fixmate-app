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
        # Note: genai.upload_file expects 'file_data' not 'file_bytes'
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

def analyze_feedback_sentiment(comment):
    try:
        model = get_gemini_model()
        prompt = f"""
        Analyze the sentiment of the following customer feedback.
        Classify it as one of these three categories: 'Positive', 'Negative', or 'Neutral'.
        Return ONLY the category name as a single word.
        Feedback: "{comment}"
        Sentiment:
        """
        response = model.generate_content(prompt)
        sentiment = response.text.strip().capitalize()
        if sentiment in ['Positive', 'Negative', 'Neutral']:
            return sentiment
        return 'Neutral'
    except Exception as e:
        print(f"ERROR: Gemini API call failed during sentiment analysis: {e}")
        return "Unknown"

def generate_and_act_on_insight(proactive_notification=False):
    """Analyzes job data, generates an insight, and optionally notifies a fixer."""
    try:
        model = get_gemini_model()
        completed_jobs = Job.query.filter(Job.area.isnot(None), Job.status == 'complete').all()
        if not completed_jobs:
            return "Not enough completed job data to generate an insight."

        job_data = [{'description': job.description, 'area': job.area} for job in completed_jobs]
        prompt = f"""
        You are a business analyst for FixMate-SA. Analyze the list of jobs.
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

        if proactive_notification:
            target_fixer = Fixer.query.filter(
                Fixer.is_active==True,
                Fixer.skills.ilike('%general%'),
                ~Fixer.skills.ilike(f'%{skill_in_demand}%')
            ).first()

            if target_fixer:
                suggestion_message = (
                    f"Hi {target_fixer.full_name}, this is FixMate-SA with a business tip!\n\n"
                    f"Our system has noticed a high demand for '{skill_in_demand}' services in the {area_in_demand} area. "
                    "You could increase your earnings by adding this skill to your profile."
                )
                send_whatsapp_message(to_number=target_fixer.phone_number, message_body=suggestion_message)
                insight_text += f" Proactively notified {target_fixer.full_name}."
                print(f"Notified {target_fixer.full_name} about upskilling opportunity.")

        db.session.commit()
        return insight_text
    except Exception as e:
        print(f"An error occurred during insight generation: {e}")
        return "Could not generate an insight at this time."


# --- User & State Management (Single Source of Truth) ---
def get_or_create_user(phone_number):
    """Gets a user by phone number or creates them if they don't exist."""
    whatsapp_number = format_sa_phone_number(phone_number) or f"whatsapp:{phone_number}"
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

def find_fixer_for_job(job):
    """Finds the best-matched fixer for a job using a scoring system."""
    skill_needed = classify_service_request(job.description)
    query_filters = [Fixer.is_active == True, Fixer.vetting_status == 'approved']
    
    # Prioritize fixers with the specific skill
    eligible_fixers = Fixer.query.filter(*query_filters, Fixer.skills.ilike(f'%{skill_needed}%')).all()
    if not eligible_fixers:
        # Fallback to 'general' fixers if no specialists are found
        eligible_fixers = Fixer.query.filter(*query_filters, Fixer.skills.ilike('%general%')).all()

    if not eligible_fixers:
        print("No eligible fixers found for this job.")
        return None

    scored_fixers = []
    for fixer in eligible_fixers:
        score = 0
        # Proximity score (up to 50 points)
        if all([fixer.current_latitude, fixer.current_longitude, job.latitude, job.longitude]):
            distance_km = geodesic((job.latitude, job.longitude), (fixer.current_latitude, fixer.current_longitude)).km
            score += max(0, 50 - (distance_km * 2))
        
        # Rating score (up to 30 points)
        avg_rating = db.session.query(db.func.avg(Job.rating)).filter(Job.fixer_id == fixer.id, Job.rating.isnot(None)).scalar() or 3.5
        score += (avg_rating / 5) * 30

        # Recency score (up to 20 points)
        if fixer.last_assigned_at:
            hours_since_last = (datetime.now(timezone.utc) - fixer.last_assigned_at).total_seconds() / 3600
            score += min(20, hours_since_last)
        else:
            score += 20  # Max points for new fixers

        scored_fixers.append({'fixer': fixer, 'score': score})
        print(f"Scored Fixer: {fixer.full_name}, Score: {score:.2f}")

    if not scored_fixers:
        return None

    best_fixer = max(scored_fixers, key=lambda x: x['score'])['fixer']
    best_fixer.last_assigned_at = datetime.now(timezone.utc)
    db.session.commit()
    print(f"Best match found: {best_fixer.full_name}")
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
@app.cli.command("add-fixer")
@click.argument("name")
@click.argument("phone")
@click.argument("skills")
def add_fixer(name, phone, skills):
    whatsapp_phone = format_sa_phone_number(phone)
    if not whatsapp_phone:
        print("Error: Invalid phone number format.")
        return
    if Fixer.query.filter_by(phone_number=whatsapp_phone).first():
        print(f"Error: Fixer with phone number {whatsapp_phone} already exists.")
        return
    new_fixer = Fixer(full_name=name, phone_number=whatsapp_phone, skills=skills)
    db.session.add(new_fixer)
    db.session.commit()
    print(f"Successfully added fixer: '{name}' with number {whatsapp_phone}")


@app.cli.command("promote-admin")
@click.argument("phone")
def promote_admin(phone):
    formatted_phone = format_sa_phone_number(phone)
    if not formatted_phone:
        print("Error: Please provide a valid 10-digit SA number.")
        return
    user = User.query.filter_by(phone_number=formatted_phone).first()
    if not user:
        user = User(phone_number=formatted_phone, is_admin=True)
        db.session.add(user)
        print(f"Successfully created and promoted new admin: {user.phone_number}")
    else:
        user.is_admin = True
        print(f"Successfully promoted existing user '{user.full_name or user.phone_number}' to admin.")
    db.session.commit()
    
# (Other CLI commands like demote-admin, remove-fixer, remove-client, etc. would be updated similarly)
# ...

@app.cli.command("analyze-data")
@click.option('--notify', is_flag=True, help='Proactively notify a fixer about the insight.')
def analyze_data(notify):
    """Generates a business insight and can proactively message a fixer."""
    print("Starting data analysis...")
    insight = generate_and_act_on_insight(proactive_notification=notify)
    print(f"Insight & Action: {insight}")

# --- Web Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form.get('phone')
        formatted_number = format_sa_phone_number(phone_number)
        if not formatted_number:
            flash('Please enter a valid 10-digit South African cell number.', 'danger')
            return redirect(url_for('login'))
        
        user = get_or_create_user(formatted_number)
        token = serializer.dumps({'id': user.id, 'type': 'user'}, salt='login-salt')
        login_url = url_for('authenticate', token=token, _external=True)
        send_whatsapp_message(to_number=formatted_number, message_body=f"Hi! To log in to your FixMate-SA dashboard, please click this link:\n\n{login_url}")
        flash('A login link has been sent to your WhatsApp number.', 'success')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/fixer/login', methods=['GET', 'POST'])
def fixer_login():
    if request.method == 'POST':
        phone_number = request.form.get('phone')
        formatted_number = format_sa_phone_number(phone_number)
        if not formatted_number:
            flash('Please enter a valid 10-digit SA cell number.', 'danger')
            return redirect(url_for('fixer_login'))

        fixer = Fixer.query.filter_by(phone_number=formatted_number).first()
        if not fixer:
            flash('This phone number is not registered as a Fixer.', 'danger')
            return redirect(url_for('fixer_login'))
            
        token = serializer.dumps({'id': fixer.id, 'type': 'fixer'}, salt='login-salt')
        login_url = url_for('authenticate', token=token, _external=True)
        send_whatsapp_message(to_number=fixer.phone_number, message_body=f"Hi {fixer.full_name}! To log in to your Fixer Portal, please click this link:\n\n{login_url}")
        flash('A login link has been sent to your WhatsApp number.', 'success')
        return redirect(url_for('fixer_login'))
    return render_template('login.html', fixer_login=True)


@app.route('/authenticate/<token>')
def authenticate(token):
    try:
        data = serializer.loads(token, salt='login-salt', max_age=3600)
        user_id, user_type = data['id'], data['type']
        
        if user_type == 'fixer':
            user = db.session.get(Fixer, user_id)
            redirect_to = 'fixer_dashboard'
        else:
            user = db.session.get(User, user_id)
            redirect_to = 'admin_dashboard' if user and user.is_admin else 'dashboard'
            
        if user:
            session['user_type'] = user_type
            login_user(user)
            flash('You have been logged in successfully!', 'success')
            return redirect(url_for(redirect_to))
        else:
            flash('Login failed. User not found.', 'danger')
    except Exception:
        flash('Invalid or expired login link. Please try again.', 'danger')
    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# --- Dashboards & Protected Routes ---
@app.route('/dashboard')
@login_required
def dashboard():
    jobs = Job.query.filter_by(client_id=current_user.id).order_by(Job.id.desc()).all()
    return render_template('dashboard.html', jobs=jobs)

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    all_users = User.query.order_by(User.id.desc()).all()
    all_fixers = Fixer.query.order_by(Fixer.id.desc()).all()
    all_jobs = Job.query.order_by(Job.id.desc()).all()
    all_insights = DataInsight.query.order_by(DataInsight.id.desc()).all()
    return render_template('admin_dashboard.html', users=all_users, fixers=all_fixers, jobs=all_jobs, insights=all_insights)

@app.route('/fixer/dashboard')
@login_required
@fixer_required
def fixer_dashboard():
    latest_insight = DataInsight.query.order_by(DataInsight.id.desc()).first()
    return render_template('fixer_dashboard.html', latest_insight=latest_insight)


@app.route('/job/accept/<int:job_id>')
@login_required
@fixer_required
def accept_job(job_id):
    # ... logic for accepting a job ...
    pass

# --- API Routes ---
@app.route('/api/update_location', methods=['POST'])
@login_required
@fixer_required
def update_location():
    # ... logic for updating location ...
    pass
    
# === WHATSAPP WEBHOOK WITH AUDIO TRANSCRIPTION ===
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
                headers = {'D360-API-KEY': D360_API_KEY}
                
                # Get the direct media URL
                media_response = requests.get(media_url_endpoint, headers=headers)
                if media_response.status_code != 200:
                    print(f"Error fetching media URL: {media_response.text}")
                    send_whatsapp_message(from_number, "Sorry, I couldn't process the voice note.")
                    return Response(status=200)

                # Download the actual audio file
                audio_url = media_response.json().get('url')
                audio_content_response = requests.get(audio_url, headers=headers)
                if audio_content_response.status_code == 200:
                    audio_bytes = audio_content_response.content
                    mime_type = message['audio'].get('mime_type', 'audio/ogg')
                    # Transcribe the audio
                    incoming_msg = transcribe_audio(audio_bytes, mime_type)
                    if "failed" in incoming_msg.lower():
                        send_whatsapp_message(from_number, incoming_msg) # Send failure message
                        return Response(status=200)
                else:
                    print("Error downloading audio content.")
                    send_whatsapp_message(from_number, "Sorry, I had trouble downloading the voice note.")
                    return Response(status=200)

            elif msg_type == 'location':
                location = message['location']
            
            # --- Conversation State Machine ---
            current_state = user.conversation_state
            response_message = "" # Initialize response message

            # Handle location data if the state is awaiting_location
            if current_state == 'awaiting_location' and location:
                 response_message = "Thank you for sharing your location.\n\nLastly, please provide a contact number (e.g., 082 123 4567) that the fixer can call if needed."
                 set_user_state(user, 'awaiting_contact_number', data={'latitude': str(location.get('latitude')), 'longitude': str(location.get('longitude'))})

            # Handle text/transcribed audio messages
            elif incoming_msg:
                if current_state == 'awaiting_service_request':
                    response_message = "Got it. To help us find the nearest fixer, please share your location pin.\n\nTap the paperclip icon 📎, then choose 'Location'."
                    set_user_state(user, 'awaiting_location', data={'service': incoming_msg})
                
                elif current_state == 'awaiting_contact_number':
                    if any(char.isdigit() for char in incoming_msg) and len(incoming_msg) >= 10:
                        terms_url = url_for('terms', _external=True)
                        response_message = (
                            f"Great! We have all the details.\n\n"
                            f"By proceeding, you agree to the FixMate-SA Terms of Service, which states that payment is handled directly between you and the fixer.\n"
                            f"View here: {terms_url}\n\n"
                            "Reply *YES* to confirm and dispatch a fixer."
                        )
                        set_user_state(user, 'awaiting_terms_approval', data={'contact': incoming_msg})
                    else:
                        response_message = "That doesn't seem to be a valid phone number. Please try again."

                elif current_state == 'awaiting_terms_approval':
                    if 'yes' in incoming_msg.lower():
                        job_data = get_user_cache(user)
                        job_id, fixer_found = create_new_job_in_db(user, job_data)
                        if fixer_found:
                            response_message = f"Perfect! We have logged your request (Job #{job_id}) and have notified a nearby fixer. They will contact you shortly."
                        else:
                            response_message = f"Thank you. We have logged your request (Job #{job_id}), but all our fixers for this skill are currently busy. We will notify you as soon as one becomes available."
                        clear_user_state(user)
                    else:
                        response_message = "Job request cancelled. Please say 'hello' to start a new request."
                        clear_user_state(user)
                
                # Default state / New conversation
                else: 
                    clear_user_state(user)
                    if incoming_msg.lower() in ['hi', 'hello', 'hallo', 'dumela', 'sawubona', 'molo']:
                        response_message = "Welcome to FixMate-SA! To request a service, please describe what you need (e.g., 'Leaking pipe') or send a voice note."
                        set_user_state(user, 'awaiting_service_request')
                    else: # Assumed direct service request
                        response_message = "Got it. To help us find the nearest fixer, please share your location pin.\n\nTap the paperclip icon 📎, then choose 'Location'."
                        set_user_state(user, 'awaiting_location', data={'service': incoming_msg})
            
            # Send the determined response message, if any
            if response_message:
                send_whatsapp_message(from_number, response_message)

    except (IndexError, KeyError) as e:
        print(f"Error parsing 360dialog payload or processing message: {e}")

    return Response(status=200)