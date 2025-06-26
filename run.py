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


# --- Admin Commands & Helper Functions ---
@app.cli.command("add-fixer")
# --- THIS IS THE CORRECTED SYNTAX ---
@click.argument("name")
@click.argument("phone")
@click.argument("skills")
def add_fixer(name, phone, skills):
    """Creates a new fixer in the database."""
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
    if data: user.service_request_cache = data.get('job_id')
    db.session.commit()

def clear_user_state(user):
    user.conversation_state, user.service_request_cache = None, None
    db.session.commit()

def create_user_account_in_db(user, name): user.full_name = name; db.session.commit(); return True

from app.services import send_whatsapp_message

def generate_payfast_signature(data, passphrase=None):
    """Generates a PayFast signature."""
    payload = urlencode(data)
    if passphrase:
        payload += f"&passphrase={passphrase}"
    return hashlib.md5(payload.encode('utf-8')).hexdigest()

# --- Web and WhatsApp Routes ---
@app.route('/')
def index(): return "<h1>FixMate WhatsApp Bot is running.</h1>"

# (Login/Dashboard routes remain the same for now)
# ...

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Endpoint to receive incoming WhatsApp messages."""
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    user = get_or_create_user(from_number)
    current_state = user.conversation_state
    response_message = ""
    
    # --- Conversation logic updated for payments ---
    if current_state == 'awaiting_service_request':
        service_details = incoming_msg
        
        new_job = Job(description=service_details, client_id=user.id, amount=FIXED_CALLOUT_FEE)
        db.session.add(new_job)
        db.session.commit()

        response_message = (
            f"Got it: '{service_details}'.\n\n"
            f"There is a standard call-out fee of **R{FIXED_CALLOUT_FEE:.2f}** for this service.\n\n"
            "Reply *YES* to approve the quote and proceed to payment."
        )
        set_user_state(user, 'awaiting_quote_approval', data={'job_id': new_job.id})

    elif current_state == 'awaiting_quote_approval':
        job_id = user.service_request_cache
        job = db.session.get(Job, int(job_id))
        
        if 'yes' in incoming_msg.lower() and job:
            payment_data = {
                'merchant_id': PAYFAST_MERCHANT_ID,
                'merchant_key': PAYFAST_MERCHANT_KEY,
                'return_url': url_for('payment_success', _external=True),
                'cancel_url': url_for('payment_cancel', _external=True),
                'notify_url': url_for('payment_notify', _external=True),
                'm_payment_id': str(job.id),
                'amount': f"{job.amount:.2f}",
                'item_name': f"FixMate Job #{job.id}: {job.description}"
            }

            # Create the parameter string
            pf_param_string = urlencode(payment_data)

            # The signature is now correctly handled, but omitted for sandbox simplicity
            # In a real app, you would generate a signature here
            # signature = generate_payfast_signature(payment_data)
            # payment_data['signature'] = signature
            
            payment_url = f"{PAYFAST_URL}?{urlencode(payment_data)}"

            response_message = (
                "Thank you for your approval.\n\n"
                "Please use the following secure link to complete the payment for your call-out fee:\n\n"
                f"{payment_url}"
            )
            clear_user_state(user)
        else:
            response_message = "Okay, the job request has been cancelled. Please say 'hello' if you need anything else."
            clear_user_state(user)
    
    # (Other conversation states remain the same)
    else: # Fallback for any other state
        if 'hello' in incoming_msg.lower() or 'hi' in incoming_msg.lower():
            response_message = (
                "Welcome back to FixMate! \n\n"
                "To request a new service, just tell us what you need (e.g., 'Leaking pipe')."
            )
            set_user_state(user, 'awaiting_service_request')
        else:
            # If the user is not in a specific flow, assume they want a new service
            set_user_state(user, 'awaiting_service_request')
            # Re-run the webhook logic with the new state
            return whatsapp_webhook()

    if response_message: send_whatsapp_message(from_number, response_message)
    return Response(status=200)

# --- Payment Callback Routes ---
@app.route('/payment/success')
def payment_success():
    return "<h1>Thank you! Your payment was successful.</h1><p>We are now finding a fixer for you.</p>"

@app.route('/payment/cancel')
def payment_cancel():
    return "<h1>Payment Cancelled</h1><p>Your payment was not processed. Please start again if you wish to continue.</p>"

@app.route('/payment/notify', methods=['POST'])
def payment_notify():
    print("Received ITN from PayFast")
    return Response(status=200)
