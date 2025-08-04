#!/usr/bin/env python3
"""
Setup test users for comprehensive job workflow testing
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

def create_test_user(phone, first_name, last_name, id_number, password):
    """Create a test user via signup endpoint"""
    try:
        signup_data = {
            "phone": phone,
            "first_name": first_name,
            "last_name": last_name,
            "id_number": id_number,
            "town": "Cape Town",
            "email": f"{first_name.lower()}.{last_name.lower()}@fixmate.test",
            "password": password,
            "confirm_password": password
        }
        
        response = requests.post(f"{API_BASE}/auth/signup", json=signup_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Created user: {phone} ({first_name} {last_name}) - Role: {data.get('role_info', {}).get('role', 'unknown')}")
            return True
        else:
            print(f"❌ Failed to create user {phone}: HTTP {response.status_code} - {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error creating user {phone}: {str(e)}")
        return False

def create_fixer_record(user_id, phone, name):
    """Create a fixer record for a user"""
    try:
        fixer_data = {
            "user_id": user_id,
            "phone": phone,
            "name": name,
            "email": f"{name.lower().replace(' ', '.')}@fixmate.test",
            "services": '["plumbing", "electrical", "carpentry"]',
            "location": "Cape Town"
        }
        
        response = requests.post(f"{API_BASE}/fixers", json=fixer_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Created fixer record: {name} (ID: {data['id']})")
            return True
        else:
            print(f"❌ Failed to create fixer record for {name}: HTTP {response.status_code} - {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error creating fixer record for {name}: {str(e)}")
        return False

def test_login(phone, password):
    """Test login for a user"""
    try:
        login_data = {
            "phone": phone,
            "password": password
        }
        
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            role = data.get('role_info', {}).get('role', 'unknown')
            print(f"✅ Login successful: {phone} - Role: {role}")
            return data
        else:
            print(f"❌ Login failed for {phone}: HTTP {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Login error for {phone}: {str(e)}")
        return None

def main():
    print("🔧 Setting up test users for comprehensive job workflow testing")
    print("=" * 70)
    
    # Test API health first
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print(f"❌ API health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection error: {str(e)}")
        return False
    
    # Create test users
    test_users = [
        ("+27800000001", "Admin", "Test", "8001015001001", "admin2024test"),
        ("+27800000002", "Client", "Test", "8001015002002", "client2024test"),
        ("+27800000003", "Fixer", "Test", "8001015003003", "fixer2024test")
    ]
    
    created_users = []
    
    print("\n📋 Creating test users...")
    for phone, first_name, last_name, id_number, password in test_users:
        if create_test_user(phone, first_name, last_name, id_number, password):
            created_users.append((phone, first_name, last_name, password))
    
    print(f"\n📊 Created {len(created_users)}/{len(test_users)} test users")
    
    # Test logins
    print("\n🔐 Testing logins...")
    login_results = []
    for phone, first_name, last_name, password in created_users:
        login_data = test_login(phone, password)
        if login_data:
            login_results.append((phone, first_name, last_name, login_data))
    
    print(f"\n📊 Successful logins: {len(login_results)}/{len(created_users)}")
    
    # Create fixer record for the fixer user
    print("\n🔧 Creating fixer record...")
    fixer_user = None
    for phone, first_name, last_name, login_data in login_results:
        if phone == "+27800000003":  # Fixer user
            fixer_user = login_data
            break
    
    if fixer_user:
        user_id = fixer_user['user']['id']
        create_fixer_record(user_id, "+27800000003", "Fixer Test")
    
    print("\n" + "=" * 70)
    print("🎉 Test user setup complete!")
    print("✅ Ready for comprehensive job workflow testing")
    
    return len(login_results) >= 2  # At least 2 users should be able to login

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)