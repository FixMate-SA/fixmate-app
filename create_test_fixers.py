#!/usr/bin/env python3
"""
Create additional test fixers with proper JSON services format
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

def create_test_fixers():
    """Create test fixers with proper JSON services format"""
    session = requests.Session()
    
    # Test fixers with different services and locations
    test_fixers = [
        {
            "name": "Alex Painter",
            "services": ["painting", "interior design", "wall preparation"],
            "location": "Cape Town",
            "phone_suffix": "555"
        },
        {
            "name": "Sarah Gardener",
            "services": ["gardening", "landscaping", "tree trimming"],
            "location": "Durban",
            "phone_suffix": "666"
        },
        {
            "name": "Tom Handyman",
            "services": ["general repairs", "maintenance", "installations"],
            "location": "Port Elizabeth",
            "phone_suffix": "777"
        }
    ]
    
    created_count = 0
    for fixer_info in test_fixers:
        timestamp = str(int(time.time()))[-6:]
        
        # Create user first
        user_data = {
            "phone": f"+2782{fixer_info['phone_suffix']}{timestamp}",
            "first_name": fixer_info["name"].split()[0],
            "last_name": fixer_info["name"].split()[1] if len(fixer_info["name"].split()) > 1 else "Fixer",
            "id_number": f"8001015009{timestamp[-3:]}",
            "town": fixer_info["location"],
            "email": f"{fixer_info['name'].lower().replace(' ', '.')}.{timestamp}@fixmate.com",
            "address": f"123 {fixer_info['name']} St, {fixer_info['location']}"
        }
        
        try:
            user_response = session.post(f"{API_BASE}/users", json=user_data)
            if user_response.status_code != 200:
                print(f"❌ Failed to create user for {fixer_info['name']}: {user_response.status_code}")
                continue
            
            fixer_user = user_response.json()
            
            # Create fixer with proper JSON services
            fixer_data = {
                "user_id": fixer_user['id'],
                "phone": user_data["phone"],
                "name": fixer_info["name"],
                "email": user_data["email"],
                "services": json.dumps(fixer_info["services"]),  # Proper JSON format
                "location": fixer_info["location"]
            }
            
            fixer_response = session.post(f"{API_BASE}/fixers", json=fixer_data)
            if fixer_response.status_code == 200:
                created_fixer = fixer_response.json()
                print(f"✅ Created fixer: {fixer_info['name']} with services {fixer_info['services']}")
                created_count += 1
            else:
                print(f"❌ Failed to create fixer {fixer_info['name']}: {fixer_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error creating fixer {fixer_info['name']}: {str(e)}")
    
    print(f"\n✅ Successfully created {created_count} test fixers with proper JSON services format")

if __name__ == "__main__":
    create_test_fixers()