# run.py
import os
import re
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


# --- Service & State Functions (Unchanged, condensed for brevity) ---
def get_or_create_user(phone_number):
    if not phone_number.startswith("whatsapp:"): phone_number = f"whatsapp:{phone_number}"
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user: user = User(phone_number=phone_number); db.session.add(user); db.session.commit()
    return user
def set_user_state(user, new_state, data=None):
    user.conversation_state = new_state
    if data: user.service_request_cache, user.latitude_cache, user.longitude_cache = data.get('service'), data.get('latitude'), data.get('longitude')
    db.session.commit()
def clear_user_state(user):
    user.conversation_state, user.service_request_cache, user.latitude_cache, user.longitude_cache = None, None, None, None
    db.session.commit()
def create_user_account_in_db(user, name): user.full_name = name; db.session.commit(); return True
def find_fixer_for_job(service_description):
    skill_needed = None
    if 'plumb' in service_description.lower() or 'pipe' in service_description.lower() or 'leak' in service_description.lower(): skill_needed = 'plumbing'
    elif 'light' in service_description.lower() or 'electr' in service_description.lower(): skill_needed = 'electrical'
    if not skill_needed: return None
    return Fixer.query.filter(Fixer.is_active==True, Fixer.skills.ilike(f'%{skill_needed}%')).first()
def create_new_job_in_db(user, service, lat, lon, contact):
    new_job = Job(description=service, latitude=lat, longitude=lon, client_contact_number=contact, client_id=user.id)
    matched_fixer = find_fixer_for_job(service)
    if matched_fixer:
        new_job.assigned_fixer = matched_fixer; new_job.status = 'assigned'
        notification_message = f"New FixMate Job Alert!\n\nService Needed: {service}\nClient Contact: {contact}\n\nPlease go to your Fixer Portal to accept this job:\n{url_for('fixer_login', _external=True)}"
        send_whatsapp_message(to_number=matched_fixer.phone_number, message_body=notification_message)
    db.session.add(new_job); db.session.commit()
    return new_job.id, matched_fixer is not None
from app.services import send_whatsapp_message


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

# --- NEW: Job Completion Route ---
@app.route('/job/complete/<int:job_id>')
@login_required
def complete_job(job_id):
    if session.get('user_type') != 'fixer':
        flash('Access denied.', 'danger'); return redirect(url_for('login'))
    
    job = Job.query.filter_by(id=job_id, fixer_id=current_user.id).first_or_404()
    
    if job.status == 'accepted':
        job.status = 'complete'
        db.session.commit()

        # Ask the client for a rating
        rating_request_message = (
            f"Your FixMate job (#{job.id}: '{job.description}') has been marked as complete by {job.assigned_fixer.full_name}.\n\n"
            "How would you rate the service? Please reply with a number from 1 (bad) to 5 (excellent)."
        )
        send_whatsapp_message(to_number=job.client.phone_number, message_body=rating_request_message)

        # Set the client's state to await their rating
        set_user_state(job.client, 'awaiting_rating', data={'job_id': job.id})

        flash(f'Job #{job.id} marked as complete. The client has been asked for a rating.', 'success')
    else:
        flash(f'This job cannot be marked as complete at this time.', 'warning')

    return redirect(url_for('fixer_dashboard'))

# --- WhatsApp Webhook ---
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg, from_number = request.values.get('Body', '').strip(), request.values.get('From', '')
    user = get_or_create_user(from_number)
    current_state = user.conversation_state
    response_message = ""
    
    # --- NEW: Handle incoming rating response ---
    if current_state == 'awaiting_rating':
        job_id_to_rate = user.service_request_cache # We re-use this cache field
        job = db.session.get(Job, int(job_id_to_rate)) if job_id_to_rate else None

        if job and incoming_msg.isdigit() and 1 <= int(incoming_msg) <= 5:
            job.rating = int(incoming_msg)
            db.session.commit()
            response_message = "Thank you for your valuable feedback! We appreciate you using FixMate."
            clear_user_state(user)
        else:
            # If the input is not a valid rating, just thank them and clear the state.
            response_message = "Thank you for your feedback!"
            clear_user_state(user)

    # (The rest of the WhatsApp conversational logic remains the same)
    elif current_state == 'awaiting_location' and request.values.get('Latitude') and request.values.get('Longitude'):
        response_message = "Thank you for sharing your location.\n\nLastly, please provide a contact number (e.g., 082 123 4567) that the fixer can call to confirm the address if needed."
        set_user_state(user, 'awaiting_contact_number', data={'service': user.service_request_cache, 'latitude': request.values.get('Latitude'), 'longitude': request.values.get('Longitude')})
    elif current_state == 'awaiting_contact_number':
        potential_number = incoming_msg
        if any(char.isdigit() for char in potential_number) and len(potential_number) >= 10:
            job_id, fixer_found = create_new_job_in_db(user, user.service_request_cache, user.latitude_cache, user.longitude_cache, potential_number)
            if fixer_found: response_message = f"Perfect! Your request has been logged (Job #{job_id}) and we have assigned a fixer.\n\nThey will contact you on {potential_number} shortly."
            else: response_message = f"Thank you. Your request has been logged (Job #{job_id}).\n\nAll our qualified fixers are currently busy. We will notify you as soon as one becomes available."
            clear_user_state(user)
        else: response_message = "That doesn't seem to be a valid phone number. Please enter a valid South African contact number."
    elif current_state == 'awaiting_location': response_message = "Please use the WhatsApp location sharing feature (the paperclip icon 📎) to send your pin location."
    elif current_state is None:
        if 'hello' in incoming_msg.lower() or 'hi' in incoming_msg.lower(): response_message = "Welcome to FixMate! Your reliable help is a message away. \n\nWhat would you like to do? \n1. Request a Service 🛠️\n2. Register an Account 📝"; set_user_state(user, 'awaiting_initial_choice')
        else: response_message = "Sorry, I didn't understand. Please say 'Hello' to get started."
    elif current_state == 'awaiting_initial_choice':
        if '1' in incoming_msg or 'request' in incoming_msg.lower(): response_message = "Great! What service do you need? (e.g., 'Leaking pipe', 'Broken light switch')"; set_user_state(user, 'awaiting_service_request')
        elif '2' in incoming_msg or 'register' in incoming_msg.lower(): response_message = "Let's get you registered. What is your full name?"; set_user_state(user, 'awaiting_name_for_registration')
        else: response_message = "Invalid choice. Please reply with '1' to request a service or '2' to register."
    elif current_state == 'awaiting_name_for_registration':
        user_name = incoming_msg; create_user_account_in_db(user, user_name); response_message = f"Thanks, {user_name}! You are now registered with FixMate."; clear_user_state(user)
    elif current_state == 'awaiting_service_request':
        service_details = incoming_msg; response_message = f"Got it: '{service_details}'.\n\nNow, please share your location pin using the WhatsApp location feature so we can dispatch a fixer.\n\nTap the paperclip icon 📎, then choose 'Location'."; set_user_state(user, 'awaiting_location', data={'service': service_details})
    
    if response_message: send_whatsapp_message(from_number, response_message)
    return Response(status=200)

