# app/config.py
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env'))

class Config:
    # --- UPDATED: Removed old Twilio credentials ---
    
    # --- NEW: Add 360dialog API Key ---
    DIALOG_360_API_KEY = os.environ.get('DIALOG_360_API_KEY')

    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')
