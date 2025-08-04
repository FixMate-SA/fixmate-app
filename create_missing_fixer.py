#!/usr/bin/env python3
"""
Create Missing Fixer Record
"""

import requests
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

def create_fixer_record():
    print("🔧 Creating Missing Fixer Record")
    print("=" * 50)
    
    session = requests.Session()
    
    # Get the fixer user ID first
    try:
        # Login as fixer to get user data
        login_data = {
            "phone": "+27800000003",
            "password": "fixer2024test"
        }
        
        response = session.post(f"{API_BASE}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            user_id = data['user']['id']
            print(f"✅ Found fixer user ID: {user_id}")
            
            # Create fixer record
            fixer_data = {
                "user_id": user_id,
                "phone": "whatsapp:+27800000003",
                "name": "Test Fixer User",
                "email": "fixer.test@fixmate.com",
                "services": '["Plumbing", "Electrical", "Handyman"]',
                "location": "Cape Town, South Africa"
            }
            
            fixer_response = session.post(f"{API_BASE}/fixers", json=fixer_data)
            
            if fixer_response.status_code == 200:
                fixer_record = fixer_response.json()
                print(f"✅ Created fixer record: {fixer_record['id']}")
                print(f"   Services: {fixer_record.get('services', 'Unknown')}")
                print(f"   Location: {fixer_record.get('location', 'Unknown')}")
                return True
            else:
                print(f"❌ Failed to create fixer record: HTTP {fixer_response.status_code}")
                print(f"   Response: {fixer_response.text[:200]}")
        else:
            print(f"❌ Failed to login as fixer: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error creating fixer record: {str(e)}")
    
    return False

if __name__ == "__main__":
    success = create_fixer_record()
    if success:
        print("\n🎉 Fixer record created successfully!")
    else:
        print("\n❌ Failed to create fixer record")
    sys.exit(0 if success else 1)