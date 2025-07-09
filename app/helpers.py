# app/helpers.py
import re
import os
from functools import wraps
from flask import flash, redirect, url_for, session
from flask_login import current_user
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def format_sa_phone_number(phone_str):
    """Formats a 10-digit SA number to the whatsapp:+27... format."""
    if not phone_str:
        return None
    phone_str = phone_str.replace(" ", "")
    if re.match(r'^(0[6-8][0-9]{8})$', phone_str):
        return f"whatsapp:+27{phone_str[1:]}"
    if phone_str.startswith('+') and len(phone_str) == 12:
        return f"whatsapp:{phone_str}"
    return None

def get_gemini_model(model_name='models/gemini-1.5-flash'):
    """Initializes and returns a Gemini model, checking for the API key."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured.")
    return genai.GenerativeModel(model_name)

# --- Decorators for Authorization ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, 'is_admin', False):
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def fixer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'fixer':
            flash('Access denied.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function