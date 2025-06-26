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


# --- Admin Commands & Helper Functions (condensed for brevity) ---
@app.cli.command("add-fixer")
@click.argument("name")@click.argument("phone")@click.argument("skills")
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

# --- NEW: Dynamic Quoting Logic ---
def get_quote_for_service(service_description):
    """Determines the price based on keywords in the service description."""
    description = service_description.lower()
    
    # Plumbing jobs - higher fee for complexity
    if any(keyword in description for keyword in ['plumb', 'pipe', 'leak', 'geyser', 'tap', 'toilet', 'drain']):
        return 450.00
    
    # Electrical jobs
    if any(keyword in description for keyword in ['light', 'electr', 'plug', 'wiring', 'switch', 'db board']):
        return 400.00

    # Default call-out fee for other/general jobs
    return 350.00

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
    
    # --- Full Conversational Logic with Dynamic Quoting ---
    if current_state == 'awaiting_service_request':
        service_details = incoming_msg
        
        # --- MODIFIED: Get dynamic quote ---
        quote_amount = get_quote_for_service(service_details)
        
        # We still save the service description to the user's cache
        set_user_state(user, 'awaiting_location', data={'service': service_details, 'quote': quote_amount})
        
        response_message = (
            f"Got it: '{service_details}'.\n\n"
            "To help us find the nearest fixer, please share your location pin.\n\n"
            "Tap the paperclip icon 📎, then choose 'Location'."
        )

    elif current_state == 'awaiting_location' and latitude and longitude:
        response_message = (
            "Thank you for sharing your location.\n\n"
            "Lastly, please provide a contact number (e.g., 082 123 4567) that the fixer can call if needed."
        )
        set_user_state(user, 'awaiting_contact_number', data={'latitude': latitude, 'longitude': longitude})

    elif current_state == 'awaiting_contact_number':
        potential_number = incoming_msg
        if any(char.isdigit() for char in potential_number) and len(potential_number) >= 10:
            
            # --- MODIFIED: Use the quote amount that was cached earlier ---
            quote_amount = float(user.latitude_cache) # Re-using latitude_cache to store the quote
            
            job = Job(
                description=user.service_request_cache,
                latitude=user.longitude_cache, # Re-using longitude_cache to store the lat
                longitude=latitude, # This seems wrong. Let's fix state management
                client_contact_number=potential_number,
                client_id=user.id,
                amount=quote_amount
            )
            # Let's fix the state management before proceeding.
            # I will refactor the state management to be more robust.
            # This is a good time to introduce a JSON field in the User model.
            # For now, let's proceed with a simpler fix.
            # We will refactor the `set_user_state` function
            
            # This logic needs to be rewritten based on a better state machine.
            # Let's revert to the simpler flow for this step to avoid confusion.
            # I will provide a simpler change that just modifies the quote logic.
            
            # --- REVERTING a bit to make it simpler and more correct ---
            # The logic to get quote should happen before we ask for location.
            # Let's correct the flow from awaiting_service_request.

            # I will rewrite the flow from the top to be clearer.
            pass # I will provide the full corrected file below this thought block.

    # I've rethought the logic. It's better to get the quote, then ask for location/contact, then present the quote.
    # No, that's confusing. The user wants to know the price before giving more info.
    # The original plan was better: Service -> Quote -> Approve -> Location/Contact -> Pay.
    # Let me refactor the provided code block to match this better flow.
    # I'll stick to my initial plan for this turn: just add dynamic quoting.

    # --- Full Conversational Logic (Corrected from previous thought block) ---
    if current_state == 'awaiting_service_request':
        service_details = incoming_msg
        
        # --- NEW: Get dynamic quote ---
        quote_amount = get_quote_for_service(service_details)
        
        # We create the job immediately to get an ID. This is okay.
        job = Job(description=service_details, client_id=user.id, amount=quote_amount)
        db.session.add(job)
        db.session.commit()

        response_message = (
            f"Got it: '{service_details}'.\n\n"
            f"The estimated call-out fee for this service is **R{quote_amount:.2f}**.\n\n"
            "Reply *YES* to approve this quote."
        )
        # We store the job_id in the cache to find it in the next step
        set_user_state(user, 'awaiting_quote_approval', data={'service': str(job.id)})

    elif current_state == 'awaiting_quote_approval':
        job_id = user.service_request_cache
        job = db.session.get(Job, int(job_id))
        
        if 'yes' in incoming_msg.lower() and job:
            response_message = (
                "Quote approved. Now, to dispatch a fixer, please share your location pin.\n\n"
                "Tap the paperclip icon 📎, then choose 'Location'."
            )
            set_user_state(user, 'awaiting_location', data={'service': str(job.id)})
        else:
            job.status = 'cancelled'
            db.session.commit()
            response_message = "Okay, the job request has been cancelled. Please say 'hello' if you need anything else."
            clear_user_state(user)

    elif current_state == 'awaiting_location' and latitude and longitude:
        job_id = user.service_request_cache
        job = db.session.get(Job, int(job_id))
        if job:
            job.latitude = latitude
            job.longitude = longitude
            db.session.commit()
            response_message = (
                "Thank you for sharing your location.\n\n"
                "Lastly, please provide a contact number (e.g., 082 123 4567) that the fixer can call if needed."
            )
            set_user_state(user, 'awaiting_contact_number', data={'service': str(job.id)})

    elif current_state == 'awaiting_contact_number':
        potential_number = incoming_msg
        job_id = user.service_request_cache
        job = db.session.get(Job, int(job_id))
        
        if job and any(char.isdigit() for char in potential_number) and len(potential_number) >= 10:
            job.client_contact_number = potential_number
            db.session.commit()

            # Now generate the payment link
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
                "Thank you! We have all the details.\n\n"
                "Please use the following secure link to complete your payment:\n\n"
                f"{payment_url}"
            )
            clear_user_state(user)
        else:
            response_message = "That doesn't seem to be a valid phone number. Please try again."

    else: 
        if 'hello' in incoming_msg.lower() or 'hi' in incoming_msg.lower():
            response_message = (
                "Welcome to FixMate! Your reliable help is a message away. \n\n"
                "To request a service, please describe what you need (e.g., 'Leaking pipe', 'Broken light switch')."
            )
            set_user_state(user, 'awaiting_service_request')
        else:
            set_user_state(user, 'awaiting_service_request')
            # Re-run the webhook logic to treat the message as a service request
            return whatsapp_webhook()

    if response_message: send_whatsapp_message(from_number, response_message)
    return Response(status=200)

# (The rest of the file remains the same)
# ...
# I will now construct the final, clean `run.py` file with this new, improved flow.
# This is a much better user experience.
# 1. User describes service.
# 2. App calculates quote and asks for approval.
# 3. User approves.
# 4. App asks for location.
# 5. App asks for contact number.
# 6. App provides payment link.
# This seems correct and logical.Of course. Let's move forward and make the FixMate service smarter.

On your project board, you can now move the previous task into the "Done" column. Let's create our new task:
* **`[ENHANCEMENT] Implement Dynamic Quoting`**
* Now, drag that card into your **`In Progress`** column.

### The Plan: A Smarter Conversation

We are going to change the conversation flow to be more logical from a customer's perspective. The new flow will be:

1.  **User:** "My geyser is leaking."
2.  **FixMate:** Calculates a price for a plumbing job and replies, "The call-out fee for a plumbing issue is R450.00. Reply YES to approve."
3.  **User:** "Yes"
4.  **FixMate:** "Great. Please share your location pin."
5.  **User:** (Shares location)
6.  **FixMate:** "Thank you. What is the best contact number for the fixer to use?"
7.  **User:** "082..."
8.  **FixMate:** "Perfect. Please use this secure link to pay..."

This flow feels more natural and ensures the customer agrees to the price before providing their sensitive information.

### The Code Change

The only file that needs to be updated is `run.py`. We will add a new pricing function and adjust the conversation states to follow our new, improved flow.

➡️ Please **replace the entire contents of your `run.py` file** with this new version.


```python
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
PAYFAST_URL = '[https://sandbox.payfast.co.za/eng/process](https://sandbox.payfast.co.za/eng/process)'

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
        # We now only ever store the Job ID in the cache
        user.service_request_cache = str(data.get('job_id')) if data.get('job_id') else None
    db.session.commit()
def clear_user_state(user):
    user.conversation_state, user.service_request_cache = None, None
    db.session.commit()
def create_user_account_in_db(user, name): user.full_name = name; db.session.commit(); return True
def find_fixer_for_job(service_description):
    skill_needed = None
    if any(k in service_description.lower() for k in ['plumb', 'pipe', 'leak', 'geyser', 'tap']): skill_needed = 'plumbing'
    elif any(k in service_description.lower() for k in ['light', 'electr', 'plug', 'wiring']): skill_needed = 'electrical'
    if not skill_needed: return None
    return Fixer.query.filter(Fixer.is_active==True, Fixer.skills.ilike(f'%{skill_needed}%')).first()

# --- NEW: Dynamic Quoting Logic ---
def get_quote_for_service(service_description):
    """Determines the price based on keywords in the service description."""
    desc = service_description.lower()
    if any(k in desc for k in ['plumb', 'pipe', 'leak', 'geyser', 'tap', 'toilet']): return 450.00
    if any(k in desc for k in ['light', 'electr', 'plug', 'wiring', 'switch']): return 400.00
    return 350.00 # Default fee

from app.services import send_whatsapp_message


# --- Web and WhatsApp Routes ---
@app.route('/')
def index(): return "<h1>FixMate WhatsApp Bot is running.</h1>"

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')
    latitude = request.values.get('Latitude')
    longitude = request.values.get('Longitude')
    user = get_or_create_user(from_number)
    current_state = user.conversation_state
    response_message = ""
    
    if current_state == 'awaiting_service_request':
        quote = get_quote_for_service(incoming_msg)
        job = Job(description=incoming_msg, client_id=user.id, amount=quote)
        db.session.add(job)
        db.session.commit()
        response_message = (
            f"Got it: '{incoming_msg}'.\n\n"
            f"The estimated call-out fee for this service is **R{quote:.2f}**.\n\n"
            "Reply *YES* to approve this quote."
        )
        set_user_state(user, 'awaiting_quote_approval', data={'job_id': job.id})

    elif current_state == 'awaiting_quote_approval':
        job_id = user.service_request_cache
        job = db.session.get(Job, int(job_id))
        if 'yes' in incoming_msg.lower() and job:
            response_message = "Quote approved. To dispatch a fixer, please share your location pin.\n\nTap the paperclip icon 📎, then choose 'Location'."
            set_user_state(user, 'awaiting_location', data={'job_id': job.id})
        else:
            if job: job.status = 'cancelled'; db.session.commit()
            response_message = "Okay, the job request has been cancelled. Please say 'hello' if you need anything else."
            clear_user_state(user)

    elif current_state == 'awaiting_location' and latitude and longitude:
        job_id = user.service_request_cache
        job = db.session.get(Job, int(job_id))
        if job:
            job.latitude, job.longitude = latitude, longitude
            db.session.commit()
            response_message = "Thank you. Lastly, what is the best contact number for the fixer to use (e.g., 082 123 4567)?"
            set_user_state(user, 'awaiting_contact_number', data={'job_id': job.id})

    elif current_state == 'awaiting_contact_number':
        potential_number, job_id = incoming_msg, user.service_request_cache
        job = db.session.get(Job, int(job_id))
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
        response_message = "Welcome to FixMate! To request a service, please describe what you need (e.g., 'Leaking pipe')."
        set_user_state(user, 'awaiting_service_request')
    
    if response_message: send_whatsapp_message(from_number, response_message)
    return Response(status=200)

# All other web routes (login, dashboard, payments, etc.) remain the same.
# ...

