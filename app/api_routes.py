# app/api_routes.py
from flask import Blueprint, request, jsonify
from .models import db, User, Fixer, Job
from .services import send_whatsapp_message # We can reuse our existing services
from flask_login import login_user, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer
import os

# Create a new Blueprint for the API
api = Blueprint('api', __name__)

# We will need a serializer for creating secure tokens for the app
serializer = None

# This function will be called from run.py to initialize the serializer
def init_api_serializer(secret_key):
    global serializer
    serializer = URLSafeTimedSerializer(secret_key)

# --- API AUTHENTICATION ROUTES ---

@api.route('/request_login_link', methods=['POST'])
def api_request_login_link():
    """
    API endpoint for the mobile app to request a login link.
    It receives a phone number and user type ('client' or 'fixer').
    """
    data = request.json
    phone_number = data.get('phone_number')
    user_type = data.get('user_type', 'client') # Default to client

    # Placeholder for logic to generate and send a link via WhatsApp
    print(f"API: Received login request for {user_type} with number {phone_number}")

    # In the next step, we will add the logic here to:
    # 1. Find the user/fixer in the database.
    # 2. Generate a secure token.
    # 3. Send them a WhatsApp message with a special deep link that opens the app.
    
    return jsonify({'status': 'success', 'message': 'If your number is registered, you will receive a login link via WhatsApp.'})


# --- API DATA ROUTES ---

@api.route('/jobs', methods=['GET'])
def api_get_jobs():
    """
    API endpoint for the mobile app to get a list of jobs.
    This will be a protected route.
    """
    # Placeholder for logic to get jobs for the logged-in user or fixer
    print("API: Received request to get jobs.")
    
    # Example of what the JSON response will look like
    mock_jobs = [
        {'id': 1, 'description': 'Leaking pipe under kitchen sink', 'status': 'complete'},
        {'id': 2, 'description': 'Install new ceiling fan', 'status': 'accepted'}
    ]
    
    return jsonify(mock_jobs)

