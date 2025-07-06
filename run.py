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

# --- API Keys & Constants Configuration (UPDATED) ---
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
    if session.get('user_type') == 'fixer': return db.session.get(Fixer, int(user_id))
    return db.session.get(User, int(user_id))
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


# --- Speech-to-Text Function (UPDATED) ---
def transcribe_audio(media_url, media_type):
    """
    Downloads audio from a direct URL and transcribes it using the Gemini API.
    """
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY not set."); return None
    try:
        # 360dialog media URLs might require an API key in the header for auth
        headers = {'D360-API-KEY': os.environ.get('DIALOG_360_API_KEY')}
        r = requests.get(media_url, headers=headers) # No longer uses Twilio auth
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

# --- AI Data Analysis & Sentiment Functions ---
def generate_and_act_on_insight():
    # (This function is unchanged)
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
    except Exception as e:
        print(f"An error occurred during insight generation: {e}")
        return "Could not generate an insight at this time."

def analyze_feedback_sentiment(comment):
    # (This function is unchanged)
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
        if sentiment in ['Positive', 'Negative', 'Neutral']:
            return sentiment
        return 'Neutral'
    except Exception as e:
        print(f"ERROR: Gemini API call failed during sentiment analysis: {e}")
        return "Unknown"


# --- Admin Commands ---
# (All admin commands are unchanged and preserved)
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

@app.cli.command("demote-admin")
@click.argument("phone")
def demote_admin(phone):
    if not (phone.startswith('0') and len(phone) == 10):
        print("Error: Please provide a valid 10-digit SA number (e.g., 0821234567)."); return
    formatted_phone = f"whatsapp:+27{phone[1:]}"
    user = User.query.filter_by(phone_number=formatted_phone).first()
    if not user:
        print(f"Error: User with phone number {formatted_phone} not found."); return
    user.is_admin = False
    db.session.commit()
    print(f"Successfully demoted '{user.full_name or user.phone_number}'. They are now a regular client.")

@app.cli.command("remove-fixer")
@click.argument("phone")
def remove_fixer(phone):
    if phone.startswith('0') and len(phone) == 10: formatted_phone = f"+27{phone[1:]}"
    elif phone.startswith('+') and len(phone) == 12: formatted_phone = phone
    else:
        print("Error: Invalid phone number format. Use a 10-digit or international format."); return
    whatsapp_phone = f"whatsapp:{formatted_phone}"
    fixer = Fixer.query.filter_by(phone_number=whatsapp_phone).first()
    if not fixer:
        print(f"Error: Fixer with phone number {whatsapp_phone} not found.")
        return
    if click.confirm(f"Are you sure you want to delete fixer '{fixer.full_name}' ({fixer.phone_number})? This cannot be undone.", abort=True):
        db.session.delete(fixer)
        db.session.commit()
        print(f"Successfully deleted fixer: {fixer.full_name}")

@app.cli.command("remove-client")
@click.argument("phone")
def remove_client(phone):
    if phone.startswith('0') and len(phone) == 10: formatted_phone = f"+27{phone[1:]}"
    elif phone.startswith('+') and len(phone) == 12: formatted_phone = phone
    else:
        print("Error: Invalid phone number format. Use a 10-digit or international format."); return
    whatsapp_phone = f"whatsapp:{formatted_phone}"
    user = User.query.filter_by(phone_number=whatsapp_phone).first()
    if not user:
        print(f"Error: Client with phone number {whatsapp_phone} not found.")
        return
    if click.confirm(f"Are you sure you want to delete client '{user.full_name or user.phone_number}'? This cannot be undone.", abort=True):
        db.session.delete(user)
        db.session.commit()
        print(f"Successfully deleted client: {user.full_name or user.phone_number}")

@app.cli.command("analyze-data")
def analyze_data():
    print("Starting data analysis...")
    insight = generate_and_act_on_insight()
    print(f"Insight & Action: {insight}")

@app.cli.command("stats")
def stats():
    user_count = User.query.count()
    fixer_count = Fixer.query.count()
    print("--- FixMate-SA System Statistics ---")
    print(f"Total Registered Clients: {user_count}")
    print(f"Total Registered Fixers:  {fixer_count}")
    print("------------------------------------")

@app.cli.command("list-admins")
def list_admins():
    admins = User.query.filter_by(is_admin=True).all()
    if not admins:
        print("No administrators found.")
        return
    print("--- Current Administrators ---")
    for admin in admins:
        print(f"- {admin.full_name or 'Unnamed'} ({admin.phone_number})")
    print("----------------------------")

@app.cli.command("toggle-fixer-active")
@click.argument("phone")
def toggle_fixer_active(phone):
    if phone.startswith('0') and len(phone) == 10: formatted_phone = f"+27{phone[1:]}"
    elif phone.startswith('+') and len(phone) == 12: formatted_phone = phone
    else:
        print("Error: Invalid phone number format."); return
    whatsapp_phone = f"whatsapp:{formatted_phone}"
    fixer = Fixer.query.filter_by(phone_number=whatsapp_phone).first()
    if not fixer:
        print(f"Error: Fixer with phone number {whatsapp_phone} not found.")
        return
    fixer.is_active = not fixer.is_active
    db.session.commit()
    status = "ACTIVE" if fixer.is_active else "INACTIVE"
    print(f"Successfully set fixer '{fixer.full_name}' to {status}.")

@app.cli.command("list-jobs")
@click.option('--status', default=None, help='Filter jobs by status (e.g., paid_unassigned, awaiting_payment).')
def list_jobs(status):
    query = Job.query
    if status:
        query = query.filter_by(status=status)
    jobs = query.order_by(Job.id.desc()).all()
    if not jobs:
        print(f"No jobs found" + (f" with status '{status}'." if status else "."))
        return
    print(f"--- Jobs" + (f" with status: {status}" if status else "") + " ---")
    for job in jobs:
        client_name = job.client.full_name or job.client.phone_number
        fixer_name = job.assigned_fixer.full_name if job.assigned_fixer else "N/A"
        print(f"ID: {job.id} | Status: {job.status} | Client: {client_name} | Fixer: {fixer_name} | Desc: {job.description[:30]}...")
    print("--------------------")

@app.cli.command("reassign-job")
@click.argument("job_id", type=int)
@click.argument("fixer_phone")
def reassign_job(job_id, fixer_phone):
    job = db.session.get(Job, job_id)
    if not job:
        print(f"Error: Job with ID {job_id} not found.")
        return
    if fixer_phone.startswith('0') and len(fixer_phone) == 10: formatted_phone = f"+27{fixer_phone[1:]}"
    elif fixer_phone.startswith('+') and len(fixer_phone) == 12: formatted_phone = fixer_phone
    else:
        print("Error: Invalid phone number format for fixer."); return
    whatsapp_phone = f"whatsapp:{formatted_phone}"
    new_fixer = Fixer.query.filter_by(phone_number=whatsapp_phone).first()
    if not new_fixer:
        print(f"Error: New fixer with phone number {whatsapp_phone} not found.")
        return
    if new_fixer.vetting_status != 'approved':
        print(f"Error: New fixer '{new_fixer.full_name}' is not approved and cannot be assigned jobs.")
        return
    old_fixer_name = job.assigned_fixer.full_name if job.assigned_fixer else "None"
    job.fixer_id = new_fixer.id
    job.status = 'assigned'
    db.session.commit()
    print(f"Success! Job #{job.id} has been reassigned from {old_fixer_name} to {new_fixer.full_name}.")
    send_whatsapp_message(to_number=new_fixer.phone_number, message_body=f"Job Reassigned to You:\n\nService: {job.description}\nClient Contact: {job.client_contact_number}\n\nPlease go to your Fixer Portal to accept this job.")


# --- Helper Functions ---
# (Helper functions like classify_service_request, get_or_create_user, etc., are unchanged)
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
        if classification in ['plumbing', 'electrical', 'general']:
            return classification
        return 'general'
    except Exception as e:
        print(f"ERROR: Gemini API call failed during classification: {e}. Defaulting to 'general'.")
        return 'general'

def get_or_create_user(phone_number):
    if not phone_number.startswith("whatsapp:"): phone_number = f"whatsapp:{phone_number}"
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user: user = User(phone_number=phone_number); db.session.add(user); db.session.commit()
    return user

def set_user_state(user, new_state, data=None):
    cached_data = json.loads(user.service_request_cache) if user.service_request_cache else {}
    if data:
        cached_data.update(data)
    user.conversation_state = new_state
    user.service_request_cache = json.dumps(cached_data)
    db.session.commit()
    print(f"State for {user.phone_number} set to {new_state} with data: {cached_data}")

def get_user_cache(user):
    if user.service_request_cache:
        return json.loads(user.service_request_cache)
    return {}

def clear_user_state(user):
    user.conversation_state = None
    user.service_request_cache = None
    db.session.commit()
    print(f"State for {user.phone_number} cleared.")

def find_fixer_for_job(job):
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
    best_fixer.last_assigned_at = datetime.now(timezone.utc)
    db.session.commit()
    print(f"Best match found: {best_fixer.full_name} with score {best_fixer_data['score']:.2f}")
    return best_fixer

def create_new_job_in_db(user, job_data):
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


# --- Web and WhatsApp Routes ---
# (All web routes like index, terms, privacy, etc., are unchanged)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy_policy():
    return render_template('privacy.html')

@app.route('/api/update_location', methods=['POST'])
@login_required
def update_location():
    if session.get('user_type') != 'fixer':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    lat, lng = data.get('latitude'), data.get('longitude')
    if not lat or not lng:
        return jsonify({'error': 'Missing location data'}), 400
    fixer = current_user
    fixer.current_latitude, fixer.current_longitude = lat, lng
    db.session.commit()
    print(f"Updated location for {fixer.full_name}: {lat}, {lng}")
    return jsonify({'status': 'success'}), 200

@app.route('/api/fixer_location/<int:job_id>')
@login_required
def get_fixer_location(job_id):
    job = Job.query.filter_by(id=job_id, client_id=current_user.id).first_or_404()
    if job and job.assigned_fixer and job.assigned_fixer.current_latitude is not None:
        return jsonify({
            'latitude': job.assigned_fixer.current_latitude,
            'longitude': job.assigned_fixer.current_longitude
        })
    return jsonify({'error': 'Fixer location not available'}), 404

@app.route('/track/<int:job_id>')
@login_required
def track_job(job_id):
    job = Job.query.filter_by(id=job_id, client_id=current_user.id).first_or_404()
    return render_template('track_job.html', job=job)

@app.route('/fixer/update_location/<int:job_id>')
@login_required
def location_updater(job_id):
    if session.get('user_type') != 'fixer':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    job = Job.query.filter_by(id=job_id, fixer_id=current_user.id).first_or_404()
    return render_template('update_location.html', job=job)

@app.route('/admin/update_vetting_status', methods=['POST'])
@login_required
def update_vetting_status():
    if not getattr(current_user, 'is_admin', False):
        return redirect(url_for('login'))
    fixer_id = request.form.get('fixer_id')
    new_status = request.form.get('new_status')
    fixer = db.session.get(Fixer, int(fixer_id))
    if fixer and new_status in ['approved', 'rejected']:
        fixer.vetting_status = new_status
        db.session.commit()
        flash(f"Fixer '{fixer.full_name}' has been {new_status}.", 'success')
    else:
        flash("Invalid request.", 'danger')
    return redirect(url_for('admin_dashboard'))

# --- Authentication Routes ---
# (Authentication routes are unchanged)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form.get('phone')
        if not phone_number or not re.match(r'^(0[6-8][0-9]{8})$', phone_number.replace(" ", "")):
            flash('Please enter a valid 10-digit South African cell number.', 'danger'); return redirect(url_for('login'))
        formatted_number_db = f"whatsapp:+27{phone_number[1:]}"
        user = get_or_create_user(formatted_number_db)
        token = serializer.dumps({'id': user.id, 'type': 'user'}, salt='login-salt')
        login_url = url_for('authenticate', token=token, _external=True)
        send_whatsapp_message(to_number=formatted_number_db, message_body=f"Hi! To log in to your FixMate-SA dashboard, please click this link:\n\n{login_url}")
        flash('A login link has been sent to your WhatsApp number.', 'success'); return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/fixer/login', methods=['GET', 'POST'])
def fixer_login():
    if request.method == 'POST':
        phone_number = request.form.get('phone')
        if not phone_number or not re.match(r'^(0[6-8][0-9]{8})$', phone_number.replace(" ", "")):
            flash('Please enter a valid 10-digit SA cell number.', 'danger'); return redirect(url_for('fixer_login'))
        formatted_number_db = f"whatsapp:+27{phone_number[1:]}"
        fixer = Fixer.query.filter_by(phone_number=formatted_number_db).first()
        if not fixer: flash('This phone number is not registered as a Fixer.', 'danger'); return redirect(url_for('fixer_login'))
        token = serializer.dumps({'id': fixer.id, 'type': 'fixer'}, salt='login-salt')
        login_url = url_for('authenticate', token=token, _external=True)
        send_whatsapp_message(to_number=fixer.phone_number, message_body=f"Hi {fixer.full_name}! To log in to your Fixer Portal, please click this link:\n\n{login_url}")
        flash('A login link has been sent to your WhatsApp number.', 'success'); return redirect(url_for('fixer_login'))
    return render_template('login.html', fixer_login=True)

@app.route('/authenticate/<token>')
def authenticate(token):
    try:
        data = serializer.loads(token, salt='login-salt', max_age=3600)
        user_id, user_type = data.get('id'), data.get('type')
        if user_type == 'fixer':
            user = db.session.get(Fixer, user_id); redirect_to = 'fixer_dashboard'
        else:
            user = db.session.get(User, user_id)
            redirect_to = 'admin_dashboard' if user and user.is_admin else 'dashboard'
        if user:
            session['user_type'] = user_type; login_user(user)
            flash('You have been logged in successfully!', 'success'); return redirect(url_for(redirect_to))
        else: flash('Login failed. User not found.', 'danger')
    except Exception: flash('Invalid or expired login link. Please try again.', 'danger')
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout(): logout_user(); flash('You have been logged out.', 'info'); return redirect(url_for('login'))

# --- Dashboard & Job Action Routes ---
# (Dashboard and Job Action routes are unchanged)
@app.route('/dashboard')
@login_required
def dashboard():
    jobs = Job.query.filter_by(client_id=current_user.id).order_by(Job.id.desc()).all()
    return render_template('dashboard.html', jobs=jobs)

@app.route('/fixer/dashboard')
@login_required
def fixer_dashboard():
    if session.get('user_type') != 'fixer': flash('Access denied.', 'danger'); return redirect(url_for('login'))
    latest_insight = DataInsight.query.order_by(DataInsight.id.desc()).first()
    return render_template('fixer_dashboard.html', latest_insight=latest_insight)

@app.route('/admin')
@login_required
def admin_dashboard():
    if not getattr(current_user, 'is_admin', False):
        flash('You do not have permission to access this page.', 'danger'); return redirect(url_for('dashboard'))
    all_users = User.query.order_by(User.id.desc()).all()
    all_fixers = Fixer.query.order_by(Fixer.id.desc()).all()
    all_jobs = Job.query.order_by(Job.id.desc()).all()
    all_insights = DataInsight.query.order_by(DataInsight.id.desc()).all()
    return render_template('admin_dashboard.html',
                           users=all_users,
                           fixers=all_fixers,
                           jobs=all_jobs,
                           insights=all_insights)

@app.route('/admin/assign_job', methods=['POST'])
@login_required
def admin_assign_job():
    if not getattr(current_user, 'is_admin', False): return redirect(url_for('login'))
    job_id, fixer_id = request.form.get('job_id'), request.form.get('fixer_id')
    if not all([job_id, fixer_id, fixer_id.isdigit()]):
        flash('Invalid selection.', 'danger'); return redirect(url_for('admin_dashboard'))
    job, fixer = db.session.get(Job, int(job_id)), db.session.get(Fixer, int(fixer_id))
    if job and fixer:
        if job.assigned_fixer:
            flash(f'Job #{job.id} is already assigned.', 'warning'); return redirect(url_for('admin_dashboard'))
        job.assigned_fixer, job.status = fixer, 'assigned'
        db.session.commit()
        send_whatsapp_message(to_number=fixer.phone_number, message_body=f"NEW JOB (Admin Assigned)\n\nService: {job.description}\nClient Contact: {job.client_contact_number}\n\nPlease go to your Fixer Portal to accept this job.")
        flash(f'Job #{job.id} has been manually assigned to {fixer.full_name}.', 'success')
    else: flash('Error assigning job. Job or Fixer not found.', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/job/accept/<int:job_id>')
@login_required
def accept_job(job_id):
    if session.get('user_type') != 'fixer':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    job = Job.query.filter_by(id=job_id, fixer_id=current_user.id).first_or_404()
    if job.status == 'assigned':
        job.status = 'accepted'
        db.session.commit()
        client_tracking_url = url_for('track_job', job_id=job.id, _external=True)
        fixer_update_url = url_for('location_updater', job_id=job.id, _external=True)
        client_message = (
            f"Great news! Your Fixer, {job.assigned_fixer.full_name}, has accepted your job (#{job.id}) and is on their way.\n\n"
            f"You can track their location in real-time here:\n{client_tracking_url}"
        )
        send_whatsapp_message(to_number=job.client.phone_number, message_body=client_message)
        fixer_message = (
            f"You have accepted Job #{job.id}. Please use the link below to periodically update your location for the client.\n\n"
            f"{fixer_update_url}"
        )
        send_whatsapp_message(to_number=job.assigned_fixer.phone_number, message_body=fixer_message)
        flash(f'You have accepted Job #{job.id}. A tracking link has been sent to the client.', 'success')
    else:
        flash(f'This job can no longer be accepted.', 'warning')
    return redirect(url_for('fixer_dashboard'))

@app.route('/job/complete/<int:job_id>')
@login_required
def complete_job(job_id):
    if session.get('user_type') != 'fixer': return redirect(url_for('login'))
    job = Job.query.filter_by(id=job_id, fixer_id=current_user.id).first_or_404()
    if job.status == 'accepted':
        job.status = 'complete'; db.session.commit()
        send_whatsapp_message(to_number=job.client.phone_number, message_body=f"Your FixMate job (#{job.id}: '{job.description}') has been marked as complete by {job.assigned_fixer.full_name}.\n\nHow would you rate the service? Please reply with a number from 1 (bad) to 5 (excellent).")
        set_user_state(job.client, 'awaiting_rating', data={'job_id': job.id})
        flash(f'Job #{job.id} marked as complete.', 'success')
    else: flash('This job cannot be marked as complete at this time.', 'warning')
    return redirect(url_for('fixer_dashboard'))

# --- Payment Routes ---
# (Payment routes are unchanged)
@app.route('/payment/success')
def payment_success():
    job_id = request.args.get('job_id')
    job = db.session.get(Job, int(job_id)) if job_id else None
    if job and job.payment_status != 'paid':
        job.payment_status = 'paid'
        matched_fixer = find_fixer_for_job(job) # Updated to pass job object
        if matched_fixer:
            job.assigned_fixer, job.status = matched_fixer, 'assigned'
            send_whatsapp_message(to_number=matched_fixer.phone_number, message_body=f"New FixMate Job Alert!\n\nService Needed: {job.description}\nClient Contact: {job.client_contact_number}\n\nPlease go to your Fixer Portal to accept this job:\n{url_for('fixer_login', _external=True)}")
        else:
            job.status = 'paid_unassigned'
        db.session.commit()
        return "<h1>Thank you! Your payment was successful.</h1><p>We are now finding a fixer for you.</p>"
    return "<h1>Payment Confirmed</h1><p>Your payment may have already been processed.</p>"

@app.route('/payment/cancel')
def payment_cancel():
    job_id = request.args.get('job_id')
    job = db.session.get(Job, int(job_id)) if job_id else None
    if job: job.status = 'cancelled'; db.session.commit()
    return "<h1>Payment Cancelled</h1><p>Your payment was not processed.</p>"

@app.route('/payment/notify', methods=['POST'])
def payment_notify():
    print("Received ITN from PayFast"); return Response(status=200)


# --- Main WhatsApp Webhook (REWRITTEN FOR 360DIALOG) ---
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Endpoint to receive incoming WhatsApp messages from 360dialog."""
    data = request.json
    print(f"Received 360dialog webhook: {json.dumps(data, indent=2)}")

    # Initialize variables to be extracted from the payload
    from_number = None
    incoming_msg = ""
    latitude = None
    longitude = None
    media_url = None
    media_type = None

    # --- Start Payload Parsing ---
    if 'contacts' in data and 'messages' in data:
        message = data['messages'][0]
        
        # Ensure it's an incoming message, not an outbound status update
        if message.get('from'):
            from_number = f"whatsapp:+{message.get('from')}"
            
            # Determine message type and extract content
            msg_type = message.get('type')
            
            if msg_type == 'text':
                incoming_msg = message['text'].get('body', '').strip()
            elif msg_type == 'location':
                latitude = message['location'].get('latitude')
                longitude = message['location'].get('longitude')
            elif msg_type == 'audio':
                # This part assumes you can get a direct download URL for media.
                # 360dialog might require a separate API call to get the media URL from the ID.
                # This is a placeholder for that logic.
                audio_id = message['audio'].get('id')
                # In a real scenario, you'd call a function here:
                # media_url = get_media_url_from_360dialog(audio_id)
                # For now, we'll simulate that we can't process it without a direct URL.
                print(f"Received audio message with ID: {audio_id}. Media URL retrieval not implemented.")
                # We will handle the transcription call below if a media_url is somehow retrieved.
            else:
                print(f"Received unhandled message type: {msg_type}")
    
    # If we couldn't identify the sender, we can't proceed.
    if not from_number:
        return Response(status=200)
    # --- End Payload Parsing ---

    # --- Start Media Processing ---
    if media_url and media_type:
        print(f"Processing audio message from {from_number}.")
        transcribed_text = transcribe_audio(media_url, media_type)
        if transcribed_text:
            incoming_msg = transcribed_text # Overwrite text with transcription
        else:
            send_whatsapp_message(from_number, "Sorry, I had trouble understanding that audio. Please try sending a text message instead.")
            return Response(status=200)
    # --- End Media Processing ---

    user = get_or_create_user(from_number)
    current_state = user.conversation_state
    response_message = ""

    # --- Start Conversation State Machine (Unchanged Logic) ---
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
            comment_text = incoming_msg
            job.rating_comment = comment_text
            sentiment = analyze_feedback_sentiment(comment_text)
            job.sentiment = sentiment
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
            if fixer_found:
                response_message = f"Perfect! We have logged your request (Job #{job_id}) and have notified a nearby fixer. They will contact you shortly."
            else:
                response_message = f"Thank you. We have logged your request (Job #{job_id}), but all our fixers for this skill are currently busy. We will notify you as soon as one becomes available."
            clear_user_state(user)
        else:
            response_message = "Job request cancelled. Please say 'hello' to start a new request."
            clear_user_state(user)
    
    else: # Default state / start of conversation
        response_message = "Welcome to FixMate-SA! To request a service, please describe what you need (e.g., 'Leaking pipe' or 'Garden cleaning') or send a voice note."
        set_user_state(user, 'awaiting_service_request')
    
    if response_message:
        send_whatsapp_message(from_number, response_message)
        
    return Response(status=200)
