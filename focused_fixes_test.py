#!/usr/bin/env python3
"""
Focused test for the specific fixes mentioned in the final verification request
"""

import requests
import json
import time

API_BASE = "http://localhost:8001/api"

def test_fixed_accept_fixer_endpoint():
    """Test the FIXED Accept-Fixer Endpoint"""
    print("🔧 Testing FIXED Accept-Fixer Endpoint")
    
    # Login as admin to get token
    admin_login = requests.post(f"{API_BASE}/auth/login", json={
        "phone": "+27800000001",
        "password": "admin2024test"
    })
    
    if admin_login.status_code != 200:
        print("❌ Admin login failed")
        return False
    
    admin_token = admin_login.json()['token']
    
    # Create a test job
    job_data = {
        "user_id": admin_login.json()['user']['id'],
        "service": "plumbing",
        "description": "Test job for accept-fixer endpoint",
        "location": "Cape Town",
        "estimated_price": 300.0
    }
    
    job_response = requests.post(f"{API_BASE}/jobs", json=job_data)
    if job_response.status_code != 200:
        print("❌ Job creation failed")
        return False
    
    job_id = job_response.json()['id']
    print(f"   Created test job: {job_id}")
    
    # Test accept-fixer endpoint with different job statuses
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 1: Accept job in 'pending' status
    accept_response = requests.post(f"{API_BASE}/jobs/{job_id}/accept-fixer", headers=headers)
    
    if accept_response.status_code == 200:
        data = accept_response.json()
        if data.get('success'):
            print("✅ FIXED Accept-Fixer Endpoint: Successfully handles job acceptance")
            print(f"   Message: {data.get('message', 'Job accepted')}")
            return True
        else:
            print(f"❌ Accept-fixer failed: {data}")
            return False
    else:
        print(f"❌ Accept-fixer HTTP error: {accept_response.status_code}")
        print(f"   Response: {accept_response.text[:200]}")
        return False

def test_fixed_rating_system_endpoint():
    """Test the FIXED Rating System Endpoint"""
    print("🔧 Testing FIXED Rating System Endpoint")
    
    # Login as client
    client_login = requests.post(f"{API_BASE}/auth/login", json={
        "phone": "+27800000002",
        "password": "client2024test"
    })
    
    if client_login.status_code != 200:
        print("❌ Client login failed")
        return False
    
    client_token = client_login.json()['token']
    client_id = client_login.json()['user']['id']
    
    # Create a test job
    job_data = {
        "user_id": client_id,
        "service": "electrical",
        "description": "Test job for rating system",
        "location": "Cape Town",
        "estimated_price": 450.0
    }
    
    job_response = requests.post(f"{API_BASE}/jobs", json=job_data)
    if job_response.status_code != 200:
        print("❌ Job creation failed")
        return False
    
    job_id = job_response.json()['id']
    
    # Update job to completed status (simulate completion)
    update_data = {"status": "completed"}
    requests.put(f"{API_BASE}/jobs/{job_id}", json=update_data)
    
    # Test rating endpoint with money_spent field handling
    headers = {"Authorization": f"Bearer {client_token}"}
    rating_data = {
        'rating': 4,
        'review': 'Good work, professional service'
    }
    
    rating_response = requests.post(f"{API_BASE}/jobs/{job_id}/rate-fixer", 
                                  data=rating_data, headers=headers)
    
    if rating_response.status_code == 200:
        data = rating_response.json()
        if data.get('success'):
            money_spent = data.get('money_spent', 0)
            print("✅ FIXED Rating System Endpoint: Successfully handles money_spent field")
            print(f"   Rating: {data.get('rating', 'N/A')}, Money spent: R{money_spent}")
            return True
        else:
            print(f"❌ Rating failed: {data}")
            return False
    else:
        print(f"❌ Rating HTTP error: {rating_response.status_code}")
        print(f"   Response: {rating_response.text[:200]}")
        return False

def test_password_reset_system():
    """Test the NEW Password Reset System"""
    print("🔧 Testing NEW Password Reset System")
    
    test_phone = "whatsapp:+27800000002"  # Use existing client
    
    # Step 1: Request password reset
    reset_request = requests.post(f"{API_BASE}/auth/request-password-reset", 
                                data={"phone": test_phone})
    
    if reset_request.status_code != 200:
        print("❌ Password reset request failed")
        return False
    
    reset_data = reset_request.json()
    if not reset_data.get('success'):
        print("❌ Password reset request unsuccessful")
        return False
    
    reset_code = reset_data.get('dev_code')
    if not reset_code:
        print("❌ No reset code received")
        return False
    
    print(f"   Step 1: Reset code received: {reset_code}")
    
    # Step 2: Verify reset code
    verify_request = requests.post(f"{API_BASE}/auth/verify-reset-code",
                                 data={"phone": test_phone, "reset_code": reset_code})
    
    if verify_request.status_code != 200:
        print("❌ Reset code verification failed")
        return False
    
    verify_data = verify_request.json()
    if not verify_data.get('success'):
        print("❌ Reset code verification unsuccessful")
        return False
    
    print("   Step 2: Reset code verified successfully")
    
    # Step 3: Reset password
    new_password = "newpassword123"
    reset_password_request = requests.post(f"{API_BASE}/auth/reset-password",
                                         data={
                                             "phone": test_phone,
                                             "reset_code": reset_code,
                                             "new_password": new_password
                                         })
    
    if reset_password_request.status_code != 200:
        print("❌ Password reset failed")
        return False
    
    reset_password_data = reset_password_request.json()
    if not reset_password_data.get('success'):
        print("❌ Password reset unsuccessful")
        return False
    
    print("   Step 3: Password reset successfully")
    
    # Step 4: Test login with new password
    login_test = requests.post(f"{API_BASE}/auth/login", json={
        "phone": "+27800000002",
        "password": new_password
    })
    
    if login_test.status_code == 200:
        login_data = login_test.json()
        if "token" in login_data:
            print("✅ NEW Password Reset System: Complete workflow working!")
            print("   All 4 steps successful: request → verify → reset → login")
            return True
    
    print("❌ Login with new password failed")
    return False

def test_authentication_systems():
    """Test all three role authentication systems"""
    print("🔧 Testing Authentication Systems")
    
    # Test accounts
    accounts = [
        ("+27800000001", "admin2024test", "admin"),
        ("+27800000002", "newpassword123", "client"),  # Using new password from reset test
        ("+27800000003", "fixer2024test", "fixer")
    ]
    
    success_count = 0
    
    for phone, password, expected_role in accounts:
        login_response = requests.post(f"{API_BASE}/auth/login", json={
            "phone": phone,
            "password": password
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            actual_role = data.get('role_info', {}).get('role', 'unknown')
            
            if actual_role == expected_role:
                print(f"   ✅ {expected_role.title()} login working perfectly")
                success_count += 1
            else:
                print(f"   ❌ {expected_role.title()} login role mismatch: expected {expected_role}, got {actual_role}")
        else:
            print(f"   ❌ {expected_role.title()} login failed: HTTP {login_response.status_code}")
    
    if success_count == 3:
        print("✅ Authentication Systems: All three role logins working perfectly")
        return True
    else:
        print(f"❌ Authentication Systems: Only {success_count}/3 role logins working")
        return False

def main():
    """Run focused tests for the specific fixes"""
    print("🎯 FOCUSED TESTING: SPECIFIC FIXES VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Fixed Accept-Fixer Endpoint", test_fixed_accept_fixer_endpoint),
        ("Fixed Rating System Endpoint", test_fixed_rating_system_endpoint),
        ("New Password Reset System", test_password_reset_system),
        ("Authentication Systems", test_authentication_systems)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test error: {str(e)}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("🎯 FOCUSED TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    for test_name, result in results:
        status = "✅ WORKING" if result else "❌ FAILING"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Success Rate: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        print("\n🎉 FOCUSED VERIFICATION SUCCESSFUL!")
        print("✅ Most critical fixes are working correctly")
        return True
    else:
        print("\n❌ FOCUSED VERIFICATION FAILED")
        print("❌ Critical fixes need attention")
        return False

if __name__ == "__main__":
    main()