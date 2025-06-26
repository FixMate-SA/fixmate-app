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
FIXED_CALLOUT_FEE = 350.00

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


# --- Admin Commands & Helper Functions (condensed for brevity) ---
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

def get_or_create_user(phone_number):
    if not phone_number.startswith("whatsapp:"): phone_number = f"whatsapp:{phone_number}"
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user: user = User(phone_number=phone_number); db.session.add(user); db.session.commit()
    return user

def set_user_state(user, new_state, data=None):
    user.conversation_state = new_state
    if data is not None:
        user.service_request_cache = data.get('service', user.service_request_cache)
        user.latitude_cache = data.get('latitude', user.latitude_cache)
        user.longitude_cache = data.get('longitude', user.longitude_cache)
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

from app.services import send_whatsapp_message


# --- Web and WhatsApp Routes ---
@app.route('/')
def index(): return "<h1>FixMate WhatsApp Bot is running.</h1>"

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Endpoint to receive incoming WhatsApp messages."""
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    latitude = request.values.get('Latitude')
    longitude = request.values.get('Longitude')

    user = get_or_create_user(from_number)
    current_state = user.conversation_state
    response_message = ""
    
    # --- Full Conversational Logic ---
    if current_state == 'awaiting_service_request':
        service_details = incoming_msg
        response_message = (
            "Got it. To help us find the nearest fixer, please share your location pin.\n\n"
            "Tap the paperclip icon 📎, then choose 'Location'."
        )
        set_user_state(user, 'awaiting_location', data={'service': service_details})

    elif current_state == 'awaiting_location' and latitude and longitude:
        response_message = (
            "Thank you for sharing your location.\n\n"
            "Lastly, please provide a contact number (e.g., 082 123 4567) that the fixer can call if needed."
        )
        set_user_state(user, 'awaiting_contact_number', data={'latitude': latitude, 'longitude': longitude})

    elif current_state == 'awaiting_contact_number':
        potential_number = incoming_msg
        if any(char.isdigit() for char in potential_number) and len(potential_number) >= 10:
            # Now that we have all info, we create the job and quote the price
            job = Job(
                description=user.service_request_cache,
                latitude=user.latitude_cache,
                longitude=user.longitude_cache,
                client_contact_number=potential_number,
                client_id=user.id,
                amount=FIXED_CALLOUT_FEE
            )
            db.session.add(job)
            db.session.commit()

            response_message = (
                f"Great! We have all the details.\n\n"
                f"There is a standard call-out fee of **R{FIXED_CALLOUT_FEE:.2f}** for this service.\n\n"
                "Reply *YES* to approve the quote and proceed to payment."
            )
            # We store the job_id in the cache field to remember which job we're paying for
            set_user_state(user, 'awaiting_quote_approval', data={'service': str(job.id)})
        else:
            response_message = "That doesn't seem to be a valid phone number. Please try again."

    elif current_state == 'awaiting_quote_approval':
        job_id = user.service_request_cache # service_request_cache now holds the job_id
        job = db.session.get(Job, int(job_id))
        
        if 'yes' in incoming_msg.lower() and job:
            payment_data = {
                'merchant_id': PAYFAST_MERCHANT_ID,
                'merchant_key': PAYFAST_MERCHANT_KEY,
                'return_url': url_for('payment_success', job_id=job.id, _external=True),
                'cancel_url': url_for('payment_cancel', job_id=job.id, _external=True),
                'notify_url': url_for('payment_notify', _external=True),
                'm_payment_id': str(job.id),
                'amount': f"{job.amount:.2f}",
                'item_name': f"FixMate Job #{job.id}: {job.description}"
            }
            payment_url = f"{PAYFAST_URL}?{urlencode(payment_data)}"

            response_message = (
                "Thank you for your approval.\n\n"
                "Please use the following secure link to complete the payment for your call-out fee:\n\n"
                f"{payment_url}"
            )
            clear_user_state(user)
        else:
            job.status = 'cancelled'
            db.session.commit()
            response_message = "Okay, the job request has been cancelled. Please say 'hello' if you need anything else."
            clear_user_state(user)

    # (Other states like registration, or the initial 'hello')
    else: 
        if 'hello' in incoming_msg.lower() or 'hi' in incoming_msg.lower():
            response_message = (
                "Welcome to FixMate! Your reliable help is a message away. \n\n"
                "To request a service, please describe what you need (e.g., 'Leaking pipe', 'Broken light switch')."
            )
            set_user_state(user, 'awaiting_service_request')
        else:
            # If the user sends something unexpected, guide them to start a request
            response_message = "Sorry, I didn't understand. To start a new request, please tell us what service you need."
            set_user_state(user, 'awaiting_service_request')

    if response_message: send_whatsapp_message(from_number, response_message)
    return Response(status=200)

# --- NEW: Payment Callback Routes Updated ---
@app.route('/payment/success')
def payment_success():
    """
    Page user sees after a successful payment.
    This is where we confirm the payment and dispatch the fixer.
    """
    job_id = request.args.get('job_id')
    job = db.session.get(Job, int(job_id)) if job_id else None

    if job and job.payment_status != 'paid':
        job.payment_status = 'paid'
        
        # Now that payment is confirmed, find and notify a fixer
        matched_fixer = find_fixer_for_job(job.description)
        if matched_fixer:
            job.assigned_fixer = matched_fixer
            job.status = 'assigned'
            notification_message = f"New FixMate Job Alert!\n\nService Needed: {job.description}\nClient Contact: {job.client_contact_number}\n\nPlease go to your Fixer Portal to accept this job:\n{url_for('fixer_login', _external=True)}"
            send_whatsapp_message(to_number=matched_fixer.phone_number, message_body=notification_message)
        else:
            job.status = 'paid_unassigned' # A new status for paid but unassigned jobs
        
        db.session.commit()
        return "<h1>Thank you! Your payment was successful.</h1><p>We are now finding a fixer for you.</p>"
    
    return "<h1>Payment Confirmed</h1><p>Your payment has already been processed. We are assigning a fixer.</p>"

@app.route('/payment/cancel')
def payment_cancel():
    job_id = request.args.get('job_id')
    job = db.session.get(Job, int(job_id)) if job_id else None
    if job:
        job.status = 'cancelled'
        db.session.commit()
    return "<h1>Payment Cancelled</h1><p>Your payment was not processed. Please start again by saying 'hello' on WhatsApp.</p>"

@app.route('/payment/notify', methods=['POST'])
def payment_notify():
    # In a real app, you would add logic here to verify the ITN from PayFast
    # and securely update the job status, as a backup to the /payment/success route.
    print("Received ITN from PayFast")
    return Response(status=200)

# All other web routes (login, dashboard, etc.) remain the same.
# ...

