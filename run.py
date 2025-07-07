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
    if session.get('user_type') == 'fixer':
        return db.session.get(Fixer, int(user_id))
    return db.session.get(User, int(user_id))

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# --- Helper Functions ---
def get_or_create_user(phone_number):
    if not phone_number.startswith("whatsapp:"):
        phone_number = f"whatsapp:{phone_number}"
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user:
        user = User(phone_number=phone_number)
        db.session.add(user)
        db.session.commit()
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

def transcribe_audio(media_url, media_type):
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY not set.")
        return None
    try:
        headers = {'D360-API-KEY': os.environ.get('DIALOG_360_API_KEY')}
        r = requests.get(media_url, headers=headers)
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
            print(f"Error downloading audio from 360dialog: {r.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return None

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
        clean_response = response.text.strip().replace("