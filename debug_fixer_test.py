#!/usr/bin/env python3
"""
Debug test for fixer endpoints to understand the failures
"""

import requests
import json
import os

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://fixmate-deploy-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
FIXER_CREDENTIALS = {
    "phone": "+27800000003", 
    "password": "fixer2024test"
}

def test_fixer_debug():
    print("🔍 DEBUGGING FIXER ENDPOINTS")
    print("=" * 50)
    
    # 1. Authenticate fixer
    print("1. Testing fixer authentication...")
    auth_response = requests.post(f"{API_BASE}/auth/login", json=FIXER_CREDENTIALS)
    print(f"Auth Response: {auth_response.status_code}")
    
    if auth_response.status_code == 200:
        auth_data = auth_response.json()
        print(f"Auth Success: {auth_data.get('success')}")
        print(f"User Role: {auth_data.get('user', {}).get('role')}")
        print(f"Is Fixer: {auth_data.get('user', {}).get('is_fixer')}")
        
        token = auth_data.get('token')
        user_id = auth_data.get('user', {}).get('id')
        print(f"Token: {token}")
        print(f"User ID: {user_id}")
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # 2. Check if user has fixer record
        print("\n2. Checking fixer record...")
        fixer_check_response = requests.get(f"{API_BASE}/fixers", headers=headers)
        print(f"Fixers List Response: {fixer_check_response.status_code}")
        
        if fixer_check_response.status_code == 200:
            fixers_data = fixer_check_response.json()
            print(f"Total fixers: {len(fixers_data.get('fixers', []))}")
            
            # Look for our test fixer
            test_fixer = None
            for fixer in fixers_data.get('fixers', []):
                if fixer.get('user_id') == user_id:
                    test_fixer = fixer
                    break
            
            if test_fixer:
                print(f"✅ Found fixer record: {test_fixer.get('name')}")
                print(f"   Fixer ID: {test_fixer.get('id')}")
                print(f"   Services: {test_fixer.get('services')}")
                print(f"   Is Active: {test_fixer.get('is_active')}")
                print(f"   Is Approved: {test_fixer.get('is_approved')}")
            else:
                print("❌ No fixer record found for this user")
        
        # 3. Test available jobs endpoint
        print("\n3. Testing available jobs endpoint...")
        jobs_response = requests.get(f"{API_BASE}/fixer/available-jobs", headers=headers)
        print(f"Available Jobs Response: {jobs_response.status_code}")
        
        if jobs_response.status_code == 200:
            jobs_data = jobs_response.json()
            print(f"Success: {jobs_data.get('success')}")
            print(f"Message: {jobs_data.get('message')}")
            print(f"Available Jobs Count: {len(jobs_data.get('available_jobs', []))}")
        else:
            print(f"Error Response: {jobs_response.text}")
        
        # 4. Test notifications endpoint
        print("\n4. Testing notifications endpoint...")
        notif_response = requests.get(f"{API_BASE}/fixer/notifications", headers=headers)
        print(f"Notifications Response: {notif_response.status_code}")
        
        if notif_response.status_code == 200:
            notif_data = notif_response.json()
            print(f"Success: {notif_data.get('success')}")
            print(f"Message: {notif_data.get('message')}")
            print(f"Notifications Count: {len(notif_data.get('notifications', []))}")
            print(f"Unread Count: {notif_data.get('unread_count')}")
        else:
            print(f"Error Response: {notif_response.text}")
    
    else:
        print(f"❌ Authentication failed: {auth_response.text}")

if __name__ == "__main__":
    test_fixer_debug()