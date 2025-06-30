# run.py
import os
import re
import hashlib
import requests
from urllib.parse import urlencode
from flask import Flask, request, Response, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
import click
import google.generativeai as genai

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
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
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


# --- Speech-to-Text Function ---
def transcribe_audio(media_url, media_type):
    """Downloads audio and transcribes it using the Gemini API directly."""
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY not set."); return None
        
    try:
        auth = (os.environ.get('TWILIO_ACCOUNT_SID'), os.environ.get('TWILIO_AUTH_TOKEN'))
        r = requests.get(media_url, auth=auth)
        
        if r.status_code == 200:
            print(f"Audio downloaded. Uploading to Gemini with MIME type: {media_type}")
            
            # --- THIS IS THE CORRECTED LINE ---
            # We explicitly name the parameter `file_data` to pass the raw bytes
            gemini_file = genai.upload_file(file_data=r.content, mime_type=media_type)
            
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            prompt = "Please transcribe the following audio. The speaker may be using English, Sepedi, Xitsonga, or Venda."
            response = model.generate_content([prompt, gemini_file])
            
            genai.delete_file(gemini_file.name)
            
            if response.text:
                print(f"Transcription successful: '{response.text}'")
                return response.text
            return None
        else:
            print(f"Error downloading audio: {r.status_code}"); return None
    except Exception as e:
        print(f"An error occurred during transcription: {e}"); return None


# --- Admin Commands ---
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


# --- Helper & Service Functions ---
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


# --- Main Web Routes ---
@app.route('/')
def index(): return "<h1>FixMate-SA Bot is running.</h1>"

# --- Authentication Routes ---
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
@app.route('/dashboard')
@login_required
def dashboard(): return render_template('dashboard.html')
@app.route('/fixer/dashboard')
@login_required
def fixer_dashboard():
    if session.get('user_type') != 'fixer': flash('Access denied.', 'danger'); return redirect(url_for('login'))
    return render_template('fixer_dashboard.html')
@app.route('/admin')
@login_required
def admin_dashboard():
    if not getattr(current_user, 'is_admin', False):
        flash('You do not have permission to access this page.', 'danger'); return redirect(url_for('dashboard'))
    all_users = User.query.order_by(User.id.desc()).all()
    all_fixers = Fixer.query.order_by(Fixer.id.desc()).all()
    all_jobs = Job.query.order_by(Job.id.desc()).all()
    return render_template('admin_dashboard.html', users=all_users, fixers=all_fixers, jobs=all_jobs)
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
    if session.get('user_type') != 'fixer': return redirect(url_for('login'))
    job = Job.query.filter_by(id=job_id, fixer_id=current_user.id).first_or_404()
    if job.status == 'assigned':
        job.status = 'accepted'; db.session.commit()
        send_whatsapp_message(to_number=job.client.phone_number, message_body=f"Great news! Your Fixer, {job.assigned_fixer.full_name}, has accepted your job (#{job.id}) and is on their way.")
        flash(f'You have accepted Job #{job.id}.', 'success')
    else: flash('This job can no longer be accepted.', 'warning')
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
@app.route('/payment/success')
def payment_success():
    job_id = request.args.get('job_id')
    job = db.session.get(Job, int(job_id)) if job_id else None
    if job and job.payment_status != 'paid':
        job.payment_status = 'paid'
        matched_fixer = find_fixer_for_job(job.description)
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


# --- Main WhatsApp Webhook ---
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Endpoint to receive incoming WhatsApp messages."""
    from_number = request.values.get('From', '')
    media_url = request.values.get('MediaUrl0')
    media_type = request.values.get('MediaContentType0', '')
    incoming_msg = request.values.get('Body', '').strip()
    
    if media_url and 'audio' in media_type:
        print(f"Received audio message from {from_number}.")
        transcribed_text = transcribe_audio(media_url, media_type)
        if transcribed_text:
            incoming_msg = transcribed_text
        else:
            send_whatsapp_message(from_number, "Sorry, I had trouble understanding that audio. Please try sending a text message instead.")
            return Response(status=200)

    latitude = request.values.get('Latitude'); longitude = request.values.get('Longitude')
    user = get_or_create_user(from_number)
    current_state = user.conversation_state
    response_message = ""
    
    if current_state == 'awaiting_rating':
        job_id_to_rate = user.service_request_cache
        job = db.session.get(Job, int(job_id_to_rate)) if job_id_to_rate else None
        if job and incoming_msg.isdigit() and 1 <= int(incoming_msg) <= 5:
            job.rating = int(incoming_msg); db.session.commit()
            response_message = "Thank you for your valuable feedback!"
        else: response_message = "Thank you for your feedback!"
        clear_user_state(user)
    elif current_state == 'awaiting_service_request':
        quote = get_quote_for_service(incoming_msg)
        job = Job(description=incoming_msg, client_id=user.id, amount=quote)
        db.session.add(job); db.session.commit()
        response_message = f"Got it: '{incoming_msg}'.\n\nThe estimated call-out fee is **R{quote:.2f}**.\n\nReply *YES* to approve."
        set_user_state(user, 'awaiting_quote_approval', data={'job_id': job.id})
    elif current_state == 'awaiting_quote_approval':
        job_id = user.service_request_cache
        job = db.session.get(Job, int(job_id)) if job_id else None
        if 'yes' in incoming_msg.lower() and job:
            response_message = "Quote approved. Please share your location pin.\n\nTap 📎, then 'Location'."
            set_user_state(user, 'awaiting_location', data={'job_id': job.id})
        else:
            if job: job.status = 'cancelled'; db.session.commit()
            response_message = "Job request cancelled. Say 'hello' to start again."; clear_user_state(user)
    elif current_state == 'awaiting_location' and latitude and longitude:
        job_id = user.service_request_cache
        job = db.session.get(Job, int(job_id)) if job_id else None
        if job:
            job.latitude, job.longitude = latitude, longitude; db.session.commit()
            response_message = "Thank you. What is the best contact number for the fixer to use?"
            set_user_state(user, 'awaiting_contact_number', data={'job_id': job.id})
    elif current_state == 'awaiting_contact_number':
        potential_number, job_id = incoming_msg, user.service_request_cache
        job = db.session.get(Job, int(job_id)) if job_id else None
        if job and any(char.isdigit() for char in potential_number) and len(potential_number) >= 10:
            job.client_contact_number = potential_number; db.session.commit()
            payment_data = {
                'merchant_id': PAYFAST_MERCHANT_ID, 'merchant_key': PAYFAST_MERCHANT_KEY,
                'return_url': url_for('payment_success', job_id=job.id, _external=True),
                'cancel_url': url_for('payment_cancel', job_id=job.id, _external=True),
                'notify_url': url_for('payment_notify', _external=True),
                'm_payment_id': str(job.id), 'amount': f"{job.amount:.2f}",
                'item_name': f"FixMate-SA Job #{job.id}: {job.description}"
            }
            payment_url = f"{PAYFAST_URL}?{urlencode(payment_data)}"
            response_message = f"Thank you! We have all the details.\n\nPlease use the following secure link to complete your payment:\n\n{payment_url}"
            clear_user_state(user)
        else: response_message = "That doesn't look like a valid phone number. Please try again."
    else: # Default state
        response_message = "Welcome to FixMate-SA! To request a service, please describe what you need (e.g., 'Leaking pipe') or send a voice note."
        set_user_state(user, 'awaiting_service_request')
    
    if response_message:
        send_whatsapp_message(from_number, response_message)
    return Response(status=200)

