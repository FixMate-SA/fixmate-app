#!/usr/bin/env python3
"""
Debug script to check FastAPI routes
"""

import requests
import json
import sys
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')

print(f"🔧 Debugging FastAPI routes at: {BACKEND_URL}")
print("=" * 80)

# Test direct API access
try:
    response = requests.get(f"{BACKEND_URL}/api/")
    print(f"API Health Check: {response.status_code} - {response.text}")
except Exception as e:
    print(f"API Health Check Error: {e}")

# Test WhatsApp endpoint directly
try:
    response = requests.get(f"{BACKEND_URL}/whatsapp")
    print(f"WhatsApp GET: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response content type: {response.headers.get('content-type', 'unknown')}")
    if response.headers.get('content-type', '').startswith('application/json'):
        print(f"Response JSON: {response.json()}")
    else:
        print(f"Response text (first 200 chars): {response.text[:200]}")
except Exception as e:
    print(f"WhatsApp GET Error: {e}")

print()

# Test WhatsApp POST endpoint
try:
    response = requests.post(f"{BACKEND_URL}/whatsapp", json={"test": "data"})
    print(f"WhatsApp POST: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response content type: {response.headers.get('content-type', 'unknown')}")
    if response.headers.get('content-type', '').startswith('application/json'):
        print(f"Response JSON: {response.json()}")
    else:
        print(f"Response text (first 200 chars): {response.text[:200]}")
except Exception as e:
    print(f"WhatsApp POST Error: {e}")

print()

# Test with Facebook verification parameters
try:
    params = {
        'hub.mode': 'subscribe',
        'hub.challenge': 'test_challenge_12345',
        'hub.verify_token': 'test_verify_token'
    }
    response = requests.get(f"{BACKEND_URL}/whatsapp", params=params)
    print(f"WhatsApp GET with params: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response content type: {response.headers.get('content-type', 'unknown')}")
    print(f"Response text: {response.text}")
except Exception as e:
    print(f"WhatsApp GET with params Error: {e}")