#!/usr/bin/env python3
"""
Quick test to verify basic CRUD operations work with unique data
"""

import requests
import json
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

def test_basic_crud():
    session = requests.Session()
    
    # Generate unique data
    unique_id = str(uuid.uuid4())[:8]
    
    print("Testing basic CRUD operations...")
    
    # Test user creation with unique data
    user_data = {
        "phone": f"+2782{unique_id}",
        "name": f"Test User {unique_id}",
        "email": f"test{unique_id}@example.com",
        "address": f"123 Test St, Cape Town {unique_id}"
    }
    
    try:
        response = session.post(f"{API_BASE}/users", json=user_data)
        if response.status_code == 200:
            user = response.json()
            print(f"✅ User created: {user['id']}")
            
            # Test dashboard with AI insights
            dashboard_response = session.get(f"{API_BASE}/dashboard/{user['id']}")
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                if 'business_insight' in dashboard_data:
                    print(f"✅ Dashboard with AI insights: {dashboard_data['business_insight'][:50]}...")
                else:
                    print("❌ Dashboard missing business_insight")
            else:
                print(f"❌ Dashboard failed: {dashboard_response.status_code}")
                
        else:
            print(f"❌ User creation failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_basic_crud()