#!/usr/bin/env python3
"""
Role Service Backend Testing for FixMate-SA
Testing role determination logic for new client signups, admin detection, fixer detection, and role priority
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

# Test counters
total_tests = 0
passed_tests = 0
failed_tests = 0

def log_test(test_name, success, message=""):
    """Log test results"""
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    
    if success:
        passed_tests += 1
        status = "✅ PASS"
    else:
        failed_tests += 1
        status = "❌ FAIL"
    
    print(f"{status}: {test_name}")
    if message:
        print(f"    {message}")

def make_request(method, endpoint, data=None, headers=None, timeout=30):
    """Make HTTP request with error handling"""
    try:
        url = f"{API_BASE}{endpoint}"
        print(f"Making {method} request to: {url}")  # Debug logging
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=timeout, verify=False)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=timeout, verify=False)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers, timeout=timeout, verify=False)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=timeout, verify=False)
        
        print(f"Response status: {response.status_code}")  # Debug logging
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        return None

def test_new_client_signup_role_assignment():
    """Test that new client signups are correctly assigned 'client' role"""
    print("\n🔍 Testing New Client Signup Role Assignment...")
    
    # Generate unique phone number for new client
    timestamp = int(time.time())
    new_client_phone = f"+2780000{timestamp % 10000:04d}"
    
    signup_data = {
        "phone": new_client_phone,
        "first_name": "TestClient",
        "last_name": "RoleTest",
        "id_number": "9001010001088",
        "town": "Cape Town",
        "email": f"testclient{timestamp}@example.com",
        "password": "testpass123",
        "confirm_password": "testpass123"
    }
    
    # Test signup
    response = make_request('POST', '/auth/signup', signup_data)
    
    if response and response.status_code == 200:
        data = response.json()
        if data.get('success'):
            user_data = data.get('user', {})
            role = user_data.get('role')
            
            if role == 'client':
                log_test("New Client Signup - Role Assignment", True, f"New client correctly assigned 'client' role")
                
                # Test login to verify role persistence
                login_data = {
                    "phone": new_client_phone,
                    "password": "testpass123"
                }
                
                login_response = make_request('POST', '/auth/login', login_data)
                if login_response and login_response.status_code == 200:
                    login_result = login_response.json()
                    if login_result.get('success'):
                        login_user = login_result.get('user', {})
                        login_role = login_user.get('role')
                        
                        if login_role == 'client':
                            log_test("New Client Login - Role Persistence", True, f"Role correctly persisted as 'client' after login")
                        else:
                            log_test("New Client Login - Role Persistence", False, f"Role changed to '{login_role}' after login, expected 'client'")
                    else:
                        log_test("New Client Login - Role Persistence", False, f"Login failed: {login_result.get('message')}")
                else:
                    log_test("New Client Login - Role Persistence", False, f"Login request failed")
                    
            else:
                log_test("New Client Signup - Role Assignment", False, f"New client assigned '{role}' role instead of 'client'")
        else:
            log_test("New Client Signup - Role Assignment", False, f"Signup failed: {data.get('message')}")
    else:
        log_test("New Client Signup - Role Assignment", False, f"Signup request failed")

def test_admin_role_detection():
    """Test that only legitimate admin phone numbers are correctly identified as admin"""
    print("\n🔍 Testing Admin Role Detection...")
    
    # Test legitimate admin phone number
    admin_phone = "+27800000001"
    
    # Check role via role-check endpoint
    encoded_phone = quote(admin_phone, safe='')
    response = make_request('GET', f'/auth/role-check/{encoded_phone}')
    
    if response and response.status_code == 200:
        data = response.json()
        if data.get('success'):
            role = data.get('role')
            
            if role == 'admin':
                log_test("Admin Phone Detection - Legitimate Admin", True, f"Phone {admin_phone} correctly identified as admin")
            else:
                log_test("Admin Phone Detection - Legitimate Admin", False, f"Phone {admin_phone} identified as '{role}' instead of 'admin'")
        else:
            log_test("Admin Phone Detection - Legitimate Admin", False, f"Role check failed: {data.get('error')}")
    else:
        log_test("Admin Phone Detection - Legitimate Admin", False, f"Role check request failed")
    
    # Test whatsapp prefix admin phone number
    whatsapp_admin_phone = "whatsapp:+27800000001"
    
    response = make_request('GET', f'/auth/role-check/{whatsapp_admin_phone}')
    
    if response and response.status_code == 200:
        data = response.json()
        if data.get('success'):
            role = data.get('role')
            
            if role == 'admin':
                log_test("Admin Phone Detection - WhatsApp Admin", True, f"Phone {whatsapp_admin_phone} correctly identified as admin")
            else:
                log_test("Admin Phone Detection - WhatsApp Admin", False, f"Phone {whatsapp_admin_phone} identified as '{role}' instead of 'admin'")
        else:
            log_test("Admin Phone Detection - WhatsApp Admin", False, f"Role check failed: {data.get('error')}")
    else:
        log_test("Admin Phone Detection - WhatsApp Admin", False, f"Role check request failed")
    
    # Test non-admin phone number should not be admin
    non_admin_phone = "+27800000999"
    
    response = make_request('GET', f'/auth/role-check/{non_admin_phone}')
    
    if response and response.status_code == 200:
        data = response.json()
        if data.get('success'):
            role = data.get('role')
            
            if role != 'admin':
                log_test("Admin Phone Detection - Non-Admin Phone", True, f"Phone {non_admin_phone} correctly identified as '{role}' (not admin)")
            else:
                log_test("Admin Phone Detection - Non-Admin Phone", False, f"Phone {non_admin_phone} incorrectly identified as admin")
        else:
            log_test("Admin Phone Detection - Non-Admin Phone", False, f"Role check failed: {data.get('error')}")
    else:
        log_test("Admin Phone Detection - Non-Admin Phone", False, f"Role check request failed")

def test_fixer_role_detection():
    """Test that users with role='fixer' in database are correctly identified as fixers"""
    print("\n🔍 Testing Fixer Role Detection...")
    
    # Test known fixer phone number
    fixer_phone = "+27800000003"
    
    # Check role via role-check endpoint
    response = make_request('GET', f'/auth/role-check/{fixer_phone}')
    
    if response and response.status_code == 200:
        data = response.json()
        if data.get('success'):
            role = data.get('role')
            database_role = data.get('database_role')
            
            if role == 'fixer':
                log_test("Fixer Role Detection - Database Fixer", True, f"Phone {fixer_phone} correctly identified as fixer (DB role: {database_role})")
            else:
                log_test("Fixer Role Detection - Database Fixer", False, f"Phone {fixer_phone} identified as '{role}' instead of 'fixer' (DB role: {database_role})")
        else:
            log_test("Fixer Role Detection - Database Fixer", False, f"Role check failed: {data.get('error')}")
    else:
        log_test("Fixer Role Detection - Database Fixer", False, f"Role check request failed")
    
    # Test fixer login to verify role consistency
    fixer_credentials = {
        "phone": fixer_phone,
        "password": "fixer2024test"
    }
    
    login_response = make_request('POST', '/auth/login', fixer_credentials)
    
    if login_response and login_response.status_code == 200:
        login_data = login_response.json()
        if login_data.get('success'):
            user_data = login_data.get('user', {})
            login_role = user_data.get('role')
            is_fixer = user_data.get('is_fixer')
            fixer_data = user_data.get('fixer_data')
            
            if login_role == 'fixer' and is_fixer:
                log_test("Fixer Login - Role Consistency", True, f"Fixer login correctly returns role='fixer' and is_fixer=True")
                
                if fixer_data:
                    log_test("Fixer Login - Fixer Data", True, f"Fixer data provided in login response")
                else:
                    log_test("Fixer Login - Fixer Data", False, f"Fixer data missing in login response")
            else:
                log_test("Fixer Login - Role Consistency", False, f"Fixer login returns role='{login_role}', is_fixer={is_fixer}")
        else:
            log_test("Fixer Login - Role Consistency", False, f"Fixer login failed: {login_data.get('message')}")
    else:
        log_test("Fixer Login - Role Consistency", False, f"Fixer login request failed")

def test_role_priority_logic():
    """Test role determination priority: admin from database > admin from phone list > fixer > client"""
    print("\n🔍 Testing Role Priority Logic...")
    
    # Test 1: Admin from database should take priority
    admin_phone = "+27800000001"
    
    response = make_request('GET', f'/auth/role-check/{admin_phone}')
    
    if response and response.status_code == 200:
        data = response.json()
        if data.get('success'):
            role = data.get('role')
            database_role = data.get('database_role')
            
            # If user exists in database with admin role, it should take priority
            if database_role == 'admin' and role == 'admin':
                log_test("Role Priority - Database Admin Priority", True, f"Database admin role takes priority")
            elif database_role != 'admin' and role == 'admin':
                log_test("Role Priority - Phone List Admin Priority", True, f"Phone list admin role used when no database admin role")
            else:
                log_test("Role Priority - Admin Priority Logic", False, f"Unexpected role priority result: role={role}, db_role={database_role}")
        else:
            log_test("Role Priority - Admin Priority Logic", False, f"Role check failed: {data.get('error')}")
    else:
        log_test("Role Priority - Admin Priority Logic", False, f"Role check request failed")
    
    # Test 2: Fixer role should take priority over client for existing fixer users
    fixer_phone = "+27800000003"
    
    response = make_request('GET', f'/auth/role-check/{fixer_phone}')
    
    if response and response.status_code == 200:
        data = response.json()
        if data.get('success'):
            role = data.get('role')
            database_role = data.get('database_role')
            
            if role == 'fixer':
                log_test("Role Priority - Fixer Over Client", True, f"Fixer role correctly takes priority over client")
            else:
                log_test("Role Priority - Fixer Over Client", False, f"Expected fixer role, got '{role}' (DB role: {database_role})")
        else:
            log_test("Role Priority - Fixer Over Client", False, f"Role check failed: {data.get('error')}")
    else:
        log_test("Role Priority - Fixer Over Client", False, f"Role check request failed")
    
    # Test 3: Client should be default for non-admin, non-fixer users
    client_phone = "+27800000002"
    
    response = make_request('GET', f'/auth/role-check/{client_phone}')
    
    if response and response.status_code == 200:
        data = response.json()
        if data.get('success'):
            role = data.get('role')
            
            if role == 'client':
                log_test("Role Priority - Client Default", True, f"Client role correctly used as default")
            else:
                log_test("Role Priority - Client Default", False, f"Expected client role as default, got '{role}'")
        else:
            log_test("Role Priority - Client Default", False, f"Role check failed: {data.get('error')}")
    else:
        log_test("Role Priority - Client Default", False, f"Role check request failed")

def test_database_role_consistency():
    """Test that roles are correctly saved in the database during signup and login"""
    print("\n🔍 Testing Database Role Consistency...")
    
    # Test existing users have consistent roles
    test_users = [
        {
            "phone": "+27800000001",
            "expected_role": "admin",
            "credentials": {"phone": "+27800000001", "password": "admin2024test"}
        },
        {
            "phone": "+27800000002", 
            "expected_role": "client",
            "credentials": {"phone": "+27800000002", "password": "client2024test"}
        },
        {
            "phone": "+27800000003",
            "expected_role": "fixer", 
            "credentials": {"phone": "+27800000003", "password": "fixer2024test"}
        }
    ]
    
    for user in test_users:
        # Test role check
        response = make_request('GET', f'/auth/role-check/{user["phone"]}')
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get('success'):
                role = data.get('role')
                
                if role == user["expected_role"]:
                    log_test(f"Database Consistency - {user['expected_role'].title()} Role Check", True, f"Phone {user['phone']} correctly identified as {user['expected_role']}")
                else:
                    log_test(f"Database Consistency - {user['expected_role'].title()} Role Check", False, f"Phone {user['phone']} identified as '{role}' instead of '{user['expected_role']}'")
            else:
                log_test(f"Database Consistency - {user['expected_role'].title()} Role Check", False, f"Role check failed: {data.get('error')}")
        else:
            log_test(f"Database Consistency - {user['expected_role'].title()} Role Check", False, f"Role check request failed")
        
        # Test login consistency
        login_response = make_request('POST', '/auth/login', user["credentials"])
        
        if login_response and login_response.status_code == 200:
            login_data = login_response.json()
            if login_data.get('success'):
                user_data = login_data.get('user', {})
                login_role = user_data.get('role')
                
                if login_role == user["expected_role"]:
                    log_test(f"Database Consistency - {user['expected_role'].title()} Login Role", True, f"Login correctly returns role='{user['expected_role']}'")
                else:
                    log_test(f"Database Consistency - {user['expected_role'].title()} Login Role", False, f"Login returns role='{login_role}' instead of '{user['expected_role']}'")
            else:
                log_test(f"Database Consistency - {user['expected_role'].title()} Login Role", False, f"Login failed: {login_data.get('message')}")
        else:
            log_test(f"Database Consistency - {user['expected_role'].title()} Login Role", False, f"Login request failed")

def test_role_misassignment_scenarios():
    """Test specific scenarios that could cause role misassignment"""
    print("\n🔍 Testing Role Misassignment Scenarios...")
    
    # Test 1: New phone number not in admin list should be client
    new_phone = f"+2780000{int(time.time()) % 10000:04d}"
    
    response = make_request('GET', f'/auth/role-check/{new_phone}')
    
    if response and response.status_code == 200:
        data = response.json()
        if data.get('success'):
            role = data.get('role')
            user_exists = data.get('user_exists')
            
            if not user_exists and role == 'client':
                log_test("Role Misassignment - New Phone Default", True, f"New phone number correctly defaults to 'client' role")
            elif user_exists:
                log_test("Role Misassignment - New Phone Default", False, f"Phone number {new_phone} unexpectedly exists in database")
            else:
                log_test("Role Misassignment - New Phone Default", False, f"New phone number assigned '{role}' instead of 'client'")
        else:
            log_test("Role Misassignment - New Phone Default", False, f"Role check failed: {data.get('error')}")
    else:
        log_test("Role Misassignment - New Phone Default", False, f"Role check request failed")
    
    # Test 2: Phone number variations should be handled consistently
    test_phone_variations = [
        "+27800000002",
        "27800000002", 
        "0800000002"
    ]
    
    for phone_var in test_phone_variations:
        response = make_request('GET', f'/auth/role-check/{phone_var}')
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get('success'):
                role = data.get('role')
                # All variations should resolve to the same role (client for this test user)
                if role == 'client':
                    log_test(f"Role Consistency - Phone Format {phone_var}", True, f"Phone format variation correctly resolved to client")
                else:
                    log_test(f"Role Consistency - Phone Format {phone_var}", False, f"Phone format variation resolved to '{role}' instead of 'client'")
            else:
                log_test(f"Role Consistency - Phone Format {phone_var}", False, f"Role check failed: {data.get('error')}")
        else:
            log_test(f"Role Consistency - Phone Format {phone_var}", False, f"Role check request failed")

def run_all_tests():
    """Run all role service tests"""
    print("🚀 Starting Role Service Backend Testing...")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print("=" * 80)
    
    # Run all test functions
    test_new_client_signup_role_assignment()
    test_admin_role_detection()
    test_fixer_role_detection()
    test_role_priority_logic()
    test_database_role_consistency()
    test_role_misassignment_scenarios()
    
    # Print summary
    print("\n" + "=" * 80)
    print("🎯 ROLE SERVICE TESTING SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 ALL ROLE SERVICE TESTS PASSED!")
        print("✅ Role determination logic is working correctly")
        print("✅ New client signups are correctly assigned 'client' role")
        print("✅ Admin role detection is working properly")
        print("✅ Fixer role detection is functional")
        print("✅ Role priority logic is implemented correctly")
        print("✅ Database role consistency is maintained")
    else:
        print(f"\n⚠️ {failed_tests} TESTS FAILED")
        print("❌ Role service functionality needs attention")
        
        if failed_tests > total_tests * 0.5:
            print("🚨 CRITICAL: More than 50% of tests failed - role service may have serious issues")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)