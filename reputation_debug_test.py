#!/usr/bin/env python3
"""
Debug test for fixer reputation system
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔧 Debugging Fixer Reputation System at: {API_BASE}")
print("=" * 80)

def test_fixer_login_and_get_token():
    """Test fixer login to get authentication token"""
    try:
        # Try different fixer accounts
        fixer_accounts = [
            {'phone': '+27800000003', 'password': 'fixer2024test'},
            {'phone': '+27800000003', 'password': 'password123'},
            {'phone': '+27800000003', 'password': 'fixer123'},
        ]
        
        for account in fixer_accounts:
            print(f"Trying fixer login with {account['phone']} / {account['password']}")
            
            response = requests.post(f"{API_BASE}/auth/login", json=account)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Login successful! Role: {data.get('role_info', {}).get('role', 'unknown')}")
                return data.get('token'), data.get('user', {}).get('id')
            else:
                try:
                    error_data = response.json()
                    print(f"Login failed: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"Login failed: {response.text[:200]}")
        
        return None, None
    except Exception as e:
        print(f"Error during fixer login: {str(e)}")
        return None, None

def get_fixers():
    """Get all fixers"""
    try:
        response = requests.get(f"{API_BASE}/fixers")
        if response.status_code == 200:
            fixers = response.json()
            print(f"Found {len(fixers)} fixers:")
            for i, fixer in enumerate(fixers[:3]):  # Show first 3
                print(f"  {i+1}. ID: {fixer['id']}, Name: {fixer.get('name', 'Unknown')}, Active: {fixer.get('is_active', False)}")
            return fixers
        else:
            print(f"Failed to get fixers: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"Error getting fixers: {str(e)}")
        return []

def test_reputation_initialization(fixer_id, token):
    """Test reputation initialization for a fixer"""
    try:
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        
        print(f"Testing reputation initialization for fixer {fixer_id}")
        response = requests.post(f"{API_BASE}/fixer/{fixer_id}/reputation/initialize", headers=headers)
        
        print(f"Initialization response status: {response.status_code}")
        print(f"Initialization response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Initialization result: {data}")
            return data.get('success', False)
        else:
            return False
    except Exception as e:
        print(f"Error initializing reputation: {str(e)}")
        return False

def test_reputation_retrieval(fixer_id):
    """Test reputation retrieval for a fixer"""
    try:
        print(f"Testing reputation retrieval for fixer {fixer_id}")
        response = requests.get(f"{API_BASE}/fixer/{fixer_id}/reputation")
        
        print(f"Retrieval response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Reputation data: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"Retrieval failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error retrieving reputation: {str(e)}")
        return None

def main():
    print("🔍 DEBUGGING FIXER REPUTATION SYSTEM")
    print("-" * 50)
    
    # Get fixer token for authentication
    token, user_id = test_fixer_login_and_get_token()
    
    # Get all fixers
    fixers = get_fixers()
    
    if not fixers:
        print("No fixers found for testing")
        return
    
    # Test with first fixer
    test_fixer = fixers[0]
    fixer_id = test_fixer['id']
    
    print(f"\nTesting with fixer: {test_fixer.get('name', 'Unknown')} (ID: {fixer_id})")
    
    # Test reputation retrieval first
    reputation_data = test_reputation_retrieval(fixer_id)
    
    # If no reputation data, try to initialize
    if not reputation_data or reputation_data.get('reputation') is None:
        print("\nNo reputation data found, attempting to initialize...")
        
        if test_reputation_initialization(fixer_id, token):
            print("Initialization successful, testing retrieval again...")
            reputation_data = test_reputation_retrieval(fixer_id)
        else:
            print("Initialization failed")
    
    # Test with admin token if fixer token failed
    if not token:
        print("\nTrying with admin credentials...")
        admin_response = requests.post(f"{API_BASE}/auth/login", json={
            'phone': '+27800000001',
            'password': 'admin2024test'
        })
        
        if admin_response.status_code == 200:
            admin_data = admin_response.json()
            admin_token = admin_data.get('token')
            print("Admin login successful, retrying initialization...")
            
            if test_reputation_initialization(fixer_id, admin_token):
                print("Admin initialization successful, testing retrieval again...")
                reputation_data = test_reputation_retrieval(fixer_id)

if __name__ == "__main__":
    main()