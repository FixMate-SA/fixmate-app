# run.py
import os
import re
import hashlib
from urllib.parse import urlencode
from flask import Flask, request, Response, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
import click

# --- App Initialization & Config ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-very-secret-key-that-is-long-and-random')
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- PayFast Configuration ---
PAYFAST_MERCHANT_ID = os.environ.get('PAYFAST_MERCHANT_ID')
PAYFAST_MERCHANT_KEY = os.environ.get('PAYFAST_MERCHANT_KEY')
PAYFAST_URL = 'https://sandbox.payfast.co.za/eng/process'

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
    print(f"Successfully added fixer: {name} with number {whatsapp_phone}")

# --- State Management & Service Functions ---
def get_or_create_user(phone_number):
    if not phone_number.startswith("whatsapp:"): phone_number = f"whatsapp:{phone_number}"
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user: user = User(phone_number=phone_number); db.session.add(user); db.session.commit()
    return user
def set_user_state(user, new_state, data=None):
    user.conversation_state = new_state
    if data is not None:
        user.service_request_cache = str(data.get('job_id')) if data.get('job_id') else None
    db.session.commit()
def clear_user_state(user):
    user.conversation_state, user.service_request_cache = None, None
    db.session.commit()
def create_user_account_in_db(user, name): user.full_name = name; db.session.commit(); return True

# --- UPDATED: More Flexible Logic ---
def find_fixer_for_job(service_description):
    """Finds an available fixer based on specific or general skills."""
    desc = service_description.lower()
    skill_needed = None
    if any(k in desc for k in ['plumb', 'pipe', 'leak', 'geyser', 'tap']): skill_needed = 'plumbing'
    elif any(k in desc for k in ['light', 'electr', 'plug', 'wiring']): skill_needed = 'electrical'
    
    if skill_needed:
        fixer = Fixer.query.filter(Fixer.is_active==True, Fixer.skills.ilike(f'%{skill_needed}%')).first()
        if fixer:
            return fixer
            
    # Fallback to a general handyman if no specialist is found or needed
    return Fixer.query.filter(Fixer.is_active==True, Fixer.skills.ilike('%general%')).first()

def get_quote_for_service(service_description):
    """Determines the price based on keywords."""
    desc = service_description.lower()
    if any(k in desc for k in ['plumb', 'pipe', 'leak', 'geyser', 'tap', 'toilet']): return 450.00
    if any(k in desc for k in ['light', 'electr', 'plug', 'wiring', 'switch']): return 400.00
    return 350.00 # Default fee for all other general services

from app.services import send_whatsapp_message

def create_new_job_in_db(user, service, lat, lon, contact):
    """Creates a Job record and attempts to find a fixer."""
    new_job = Job(description=service, latitude=lat, longitude=lon, client_contact_number=contact, client_id=user.id)
    matched_fixer = find_fixer_for_job(service)
    if matched_fixer:
        new_job.assigned_fixer = matched_fixer
        new_job.status = 'assigned'
        notification_message = f"New FixMate Job Alert!\n\nService Needed: {service}\nClient Contact: {contact}\n\nPlease go to your Fixer Portal to accept this job:\n{url_for('fixer_login', _external=True)}"
        send_whatsapp_message(to_number=matched_fixer.phone_number, message_body=notification_message)
    db.session.add(new_job)
    db.session.commit()
    return new_job.id, matched_fixer is not None


# --- Web and WhatsApp Routes ---
@app.route('/')
def index(): return "<h1>FixMate WhatsApp Bot is running.</h1>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form.get('phone')
        if not phone_number or not re.match(r'^(0[6-8][0-9]{8})$', phone_number.replace(" ", "")):
            flash('Please enter a valid 10-digit SA cell number.', 'danger'); return redirect(url_for('login'))
        formatted_number_db = f"whatsapp:+27{phone_number[1:]}"
        user = get_or_create_user(formatted_number_db)
        token = serializer.dumps({'id': user.id, 'type': 'user'}, salt='login-salt')
        login_url = url_for('authenticate', token=token, _external=True)
        send_whatsapp_message(to_number=formatted_number_db, message_body=f"Hi! To securely log in to your FixMate dashboard, please click this link:\n\n{login_url}")
        flash('A login link has been sent to your WhatsApp number.', 'success'); return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/authenticate/<token>')
def authenticate(token):
    try:
        data = serializer.loads(token, salt='login-salt', max_age=3600)
        user_id, user_type = data.get('id'), data.get('type')
        user = db.session.get(Fixer, user_id) if user_type == 'fixer' else db.session.get(User, user_id)
        if user:
            session['user_type'] = user_type; login_user(user)
            flash('You have been logged in successfully!', 'success')
            return redirect(url_for('fixer_dashboard' if user_type == 'fixer' else 'dashboard'))
    except Exception: flash('Invalid or expired login link.', 'danger')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard(): return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout(): logout_user(); flash('You have been logged out.', 'info'); return redirect(url_for('login'))

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

@app.route('/fixer/dashboard')
@login_required
def fixer_dashboard():
    if session.get('user_type') != 'fixer': flash('Access denied.', 'danger'); return redirect(url_for('login'))
    return render_template('fixer_dashboard.html')

@app.route('/fixer/logout')
@login_required
def fixer_logout(): logout_user(); flash('You have been logged out.', 'info'); return redirect(url_for('fixer_login'))

@app.route('/job/accept/<int:job_id>')
@login_required
def accept_job(job_id):
    if session.get('user_type') != 'fixer': flash('Access denied.', 'danger'); return redirect(url_for('login'))
    job = Job.query.filter_by(id=job_id, fixer_id=current_user.id).first_or_404()
    if job.status == 'assigned':
        job.status = 'accepted'; db.session.commit()
        send_whatsapp_message(to_number=job.client.phone_number, message_body=f"Great news! Your Fixer, {job.assigned_fixer.full_name}, has accepted your job (#{job.id}) and is on their way.")
        flash(f'You have accepted Job #{job.id}. Please contact the client.', 'success')
    else: flash(f'This job can no longer be accepted.', 'warning')
    return redirect(url_for('fixer_dashboard'))

@app.route('/job/decline/<int:job_id>')
@login_required
def decline_job(job_id):
    flash(f'Job #{job_id} has been noted as declined. In a full app, this would be re-assigned.', 'info')
    return redirect(url_for('fixer_dashboard'))

@app.route('/job/complete/<int:job_id>')
@login_required
def complete_job(job_id):
    if session.get('user_type') != 'fixer': flash('Access denied.', 'danger'); return redirect(url_for('login'))
    job = Job.query.filter_by(id=job_id, fixer_id=current_user.id).first_or_404()
    if job.status == 'accepted':
        job.status = 'complete'; db.session.commit()
        rating_request_message = f"Your FixMate job (#{job.id}: '{job.description}') has been marked as complete by {job.assigned_fixer.full_name}.\n\nHow would you rate the service? Please reply with a number from 1 (bad) to 5 (excellent)."
        send_whatsapp_message(to_number=job.client.phone_number, message_body=rating_request_message)
        set_user_state(job.client, 'awaiting_rating', data={'job_id': job.id})
        flash(f'Job #{job.id} marked as complete. The client has been asked for a rating.', 'success')
    else: flash(f'This job cannot be marked as complete at this time.', 'warning')
    return redirect(url_for('fixer_dashboard'))

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg, from_number = request.values.get('Body', '').strip(), request.values.get('From', '')
    latitude, longitude = request.values.get('Latitude'), request.values.get('Longitude')
    user = get_or_create_user(from_number)
    current_state = user.conversation_state
    response_message = ""
    
    if current_state == 'awaiting_rating':
        job_id_to_rate = user.service_request_cache
        job = db.session.get(Job, int(job_id_to_rate)) if job_id_to_rate else None
        if job and incoming_msg.isdigit() and 1 <= int(incoming_msg) <= 5:
            job.rating = int(incoming_msg); db.session.commit()
            response_message = "Thank you for your valuable feedback! We appreciate you using FixMate."
            clear_user_state(user)
        else:
            response_message = "Thank you for your feedback!"; clear_user_state(user)

    elif current_state == 'awaiting_service_request':
        quote = get_quote_for_service(incoming_msg)
        job = Job(description=incoming_msg, client_id=user.id, amount=quote)
        db.session.add(job); db.session.commit()
        response_message = f"Got it: '{incoming_msg}'.\n\nThe estimated call-out fee for this service is **R{quote:.2f}**.\n\nReply *YES* to approve this quote."
        set_user_state(user, 'awaiting_quote_approval', data={'job_id': job.id})

    elif current_state == 'awaiting_quote_approval':
        job_id = user.service_request_cache
        job = db.session.get(Job, int(job_id)) if job_id else None
        if 'yes' in incoming_msg.lower() and job:
            response_message = "Quote approved. To dispatch a fixer, please share your location pin.\n\nTap the paperclip icon 📎, then choose 'Location'."
            set_user_state(user, 'awaiting_location', data={'job_id': job.id})
        else:
            if job: job.status = 'cancelled'; db.session.commit()
            response_message = "Okay, the job request has been cancelled. Please say 'hello' if you need anything else."; clear_user_state(user)

    elif current_state == 'awaiting_location' and latitude and longitude:
        job_id = user.service_request_cache
        job = db.session.get(Job, int(job_id)) if job_id else None
        if job:
            job.latitude, job.longitude = latitude, longitude
            db.session.commit()
            response_message = "Thank you. Lastly, what is the best contact number for the fixer to use (e.g., 082 123 4567)?"
            set_user_state(user, 'awaiting_contact_number', data={'job_id': job.id})

    elif current_state == 'awaiting_contact_number':
        potential_number, job_id = incoming_msg, user.service_request_cache
        job = db.session.get(Job, int(job_id)) if job_id else None
        if job and any(char.isdigit() for char in potential_number) and len(potential_number) >= 10:
            job.client_contact_number = potential_number
            db.session.commit()
            payment_data = {
                'merchant_id': PAYFAST_MERCHANT_ID, 'merchant_key': PAYFAST_MERCHANT_KEY,
                'return_url': url_for('payment_success', job_id=job.id, _external=True),
                'cancel_url': url_for('payment_cancel', job_id=job.id, _external=True),
                'notify_url': url_for('payment_notify', _external=True),
                'm_payment_id': str(job.id), 'amount': f"{job.amount:.2f}",
                'item_name': f"FixMate Job #{job.id}: {job.description}"
            }
            payment_url = f"{PAYFAST_URL}?{urlencode(payment_data)}"
            response_message = f"Thank you! We have all the details.\n\nPlease use the following secure link to complete your payment:\n\n{payment_url}"
            clear_user_state(user)
        else:
            response_message = "That doesn't look like a valid phone number. Please try again."

    else: # Default state / start of conversation
        response_message = "Welcome to FixMate! To request a service, please describe what you need (e.g., 'Leaking pipe' or 'Garden cleaning')."
        set_user_state(user, 'awaiting_service_request')
    
    if response_message: send_whatsapp_message(from_number, response_message)
    return Response(status=200)

@app.route('/payment/success')
def payment_success():
    job_id = request.args.get('job_id')
    job = db.session.get(Job, int(job_id)) if job_id else None
    if job and job.payment_status != 'paid':
        job.payment_status = 'paid'
        matched_fixer = find_fixer_for_job(job.description)
        if matched_fixer:
            job.assigned_fixer = matched_fixer
            job.status = 'assigned'
            notification_message = f"New FixMate Job Alert!\n\nService Needed: {job.description}\nClient Contact: {job.client_contact_number}\n\nPlease go to your Fixer Portal to accept this job:\n{url_for('fixer_login', _external=True)}"
            send_whatsapp_message(to_number=matched_fixer.phone_number, message_body=notification_message)
        else:
            job.status = 'paid_unassigned'
        db.session.commit()
        return "<h1>Thank you! Your payment was successful.</h1><p>We are now finding a fixer for you.</p>"
    return "<h1>Payment Confirmed</h1><p>Your payment has already been processed. We are assigning a fixer.</p>"

@app.route('/payment/cancel')
def payment_cancel():
    job_id = request.args.get('job_id')
    job = db.session.get(Job, int(job_id)) if job_id else None
    if job: job.status = 'cancelled'; db.session.commit()
    return "<h1>Payment Cancelled</h1><p>Your payment was not processed. Please start again by saying 'hello' on WhatsApp.</p>"

@app.route('/payment/notify', methods=['POST'])
def payment_notify():
    print("Received ITN from PayFast")
    return Response(status=200)
