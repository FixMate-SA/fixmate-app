#!/usr/bin/env python3
"""
Focused Role Service Testing - Testing the specific scenarios mentioned in the review request
"""

import requests
import json
import time
from datetime import datetime
import os
import urllib3
from urllib.parse import quote

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://service-pros-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_role_scenarios():
    """Test the specific role scenarios from the review request"""
    print("🔍 FOCUSED ROLE SERVICE TESTING")
    print("=" * 60)
    
    # Test 1: New phone number not in admin list (should be client)
    print("\n1. Testing new phone number (should be client):")
    new_phone = f"+2780000{int(time.time()) % 10000:04d}"
    encoded_phone = quote(new_phone, safe='')
    
    response = requests.get(f"{API_BASE}/auth/role-check/{encoded_phone}", verify=False)
    if response.status_code == 200:
        data = response.json()
        print(f"   Phone: {new_phone}")
        print(f"   Role: {data.get('role')}")
        print(f"   User Exists: {data.get('user_exists')}")
        print(f"   ✅ PASS" if data.get('role') == 'client' and not data.get('user_exists') else f"   ❌ FAIL")
    else:
        print(f"   ❌ Request failed: {response.status_code}")
    
    # Test 2: Existing admin phone number +27800000001 (should be admin)
    print("\n2. Testing admin phone +27800000001 (should be admin):")
    admin_phone = "+27800000001"
    encoded_phone = quote(admin_phone, safe='')
    
    response = requests.get(f"{API_BASE}/auth/role-check/{encoded_phone}", verify=False)
    if response.status_code == 200:
        data = response.json()
        print(f"   Phone: {admin_phone}")
        print(f"   Role: {data.get('role')}")
        print(f"   Database Role: {data.get('database_role')}")
        print(f"   User Exists: {data.get('user_exists')}")
        print(f"   ✅ PASS" if data.get('role') == 'admin' else f"   ❌ FAIL")
    else:
        print(f"   ❌ Request failed: {response.status_code}")
    
    # Test 3: WhatsApp admin phone number (should be admin)
    print("\n3. Testing WhatsApp admin phone whatsapp:+27800000001 (should be admin):")
    whatsapp_admin = "whatsapp:+27800000001"
    encoded_phone = quote(whatsapp_admin, safe='')
    
    response = requests.get(f"{API_BASE}/auth/role-check/{encoded_phone}", verify=False)
    if response.status_code == 200:
        data = response.json()
        print(f"   Phone: {whatsapp_admin}")
        print(f"   Role: {data.get('role')}")
        print(f"   Database Role: {data.get('database_role')}")
        print(f"   User Exists: {data.get('user_exists')}")
        print(f"   ✅ PASS" if data.get('role') == 'admin' else f"   ❌ FAIL")
    else:
        print(f"   ❌ Request failed: {response.status_code}")
    
    # Test 4: Existing fixer user in database (should be fixer)
    print("\n4. Testing fixer phone +27800000003 (should be fixer):")
    fixer_phone = "+27800000003"
    encoded_phone = quote(fixer_phone, safe='')
    
    response = requests.get(f"{API_BASE}/auth/role-check/{encoded_phone}", verify=False)
    if response.status_code == 200:
        data = response.json()
        print(f"   Phone: {fixer_phone}")
        print(f"   Role: {data.get('role')}")
        print(f"   Database Role: {data.get('database_role')}")
        print(f"   User Exists: {data.get('user_exists')}")
        print(f"   ✅ PASS" if data.get('role') == 'fixer' else f"   ❌ FAIL")
    else:
        print(f"   ❌ Request failed: {response.status_code}")
    
    # Test 5: Existing client user in database (should remain client)
    print("\n5. Testing client phone +27800000002 (should be client):")
    client_phone = "+27800000002"
    encoded_phone = quote(client_phone, safe='')
    
    response = requests.get(f"{API_BASE}/auth/role-check/{encoded_phone}", verify=False)
    if response.status_code == 200:
        data = response.json()
        print(f"   Phone: {client_phone}")
        print(f"   Role: {data.get('role')}")
        print(f"   Database Role: {data.get('database_role')}")
        print(f"   User Exists: {data.get('user_exists')}")
        print(f"   ✅ PASS" if data.get('role') == 'client' else f"   ❌ FAIL")
    else:
        print(f"   ❌ Request failed: {response.status_code}")
    
    # Test 6: Test login consistency for each role
    print("\n6. Testing login consistency:")
    
    test_users = [
        {"phone": "+27800000001", "password": "admin2024test", "expected_role": "admin"},
        {"phone": "+27800000002", "password": "client2024test", "expected_role": "client"},
        {"phone": "+27800000003", "password": "fixer2024test", "expected_role": "fixer"}
    ]
    
    for user in test_users:
        print(f"\n   Testing {user['expected_role']} login:")
        login_data = {"phone": user["phone"], "password": user["password"]}
        
        response = requests.post(f"{API_BASE}/auth/login", json=login_data, verify=False)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                user_data = data.get('user', {})
                role = user_data.get('role')
                is_fixer = user_data.get('is_fixer', False)
                
                print(f"     Phone: {user['phone']}")
                print(f"     Role: {role}")
                print(f"     Is Fixer: {is_fixer}")
                print(f"     Expected: {user['expected_role']}")
                
                if role == user['expected_role']:
                    if user['expected_role'] == 'fixer' and is_fixer:
                        print(f"     ✅ PASS (role and is_fixer correct)")
                    elif user['expected_role'] != 'fixer':
                        print(f"     ✅ PASS")
                    else:
                        print(f"     ⚠️ PARTIAL (role correct but is_fixer={is_fixer})")
                else:
                    print(f"     ❌ FAIL (expected {user['expected_role']}, got {role})")
            else:
                print(f"     ❌ Login failed: {data.get('message')}")
        else:
            print(f"     ❌ Request failed: {response.status_code}")
    
    # Test 7: Test new client signup role assignment
    print("\n7. Testing new client signup role assignment:")
    timestamp = int(time.time())
    signup_data = {
        "phone": f"+2780000{timestamp % 10000:04d}",
        "first_name": "TestClient",
        "last_name": "RoleTest",
        "id_number": "9001010001088",
        "town": "Cape Town",
        "email": f"testclient{timestamp}@example.com",
        "password": "testpass123",
        "confirm_password": "testpass123"
    }
    
    response = requests.post(f"{API_BASE}/auth/signup", json=signup_data, verify=False)
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            user_data = data.get('user', {})
            role = user_data.get('role')
            
            print(f"   New Phone: {signup_data['phone']}")
            print(f"   Assigned Role: {role}")
            print(f"   ✅ PASS" if role == 'client' else f"   ❌ FAIL (expected client, got {role})")
            
            # Test login after signup
            login_data = {"phone": signup_data["phone"], "password": "testpass123"}
            login_response = requests.post(f"{API_BASE}/auth/login", json=login_data, verify=False)
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                if login_result.get('success'):
                    login_user = login_result.get('user', {})
                    login_role = login_user.get('role')
                    print(f"   Login Role: {login_role}")
                    print(f"   ✅ PASS (role persisted)" if login_role == 'client' else f"   ❌ FAIL (role changed to {login_role})")
                else:
                    print(f"   ❌ Login after signup failed: {login_result.get('message')}")
            else:
                print(f"   ❌ Login request failed: {login_response.status_code}")
        else:
            print(f"   ❌ Signup failed: {data.get('message')}")
    else:
        print(f"   ❌ Signup request failed: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎯 FOCUSED ROLE SERVICE TESTING COMPLETE")

if __name__ == "__main__":
    test_role_scenarios()