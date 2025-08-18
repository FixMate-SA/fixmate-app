#!/usr/bin/env python3
"""
Focused Heroku Compatibility Test - Direct API Testing
"""

import requests
import json
import uuid
import time

# Configuration
BACKEND_URL = "https://service-pros-2.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_fixer_application_compatibility():
    """Test fixer application with Heroku compatibility fixes"""
    print("🔧 TESTING FIXER APPLICATION COMPATIBILITY")
    print("=" * 60)
    
    # Create a test user
    test_phone = f"+2780000{str(uuid.uuid4())[:4]}"
    signup_data = {
        "phone": test_phone,
        "first_name": "Test",
        "last_name": "Fixer",
        "id_number": "9001010000000",
        "town": "Cape Town",
        "email": f"testfixer{uuid.uuid4().hex[:8]}@example.com",
        "password": "testpass123",
        "confirm_password": "testpass123"
    }
    
    print(f"📝 Creating test user with phone: {test_phone}")
    signup_response = requests.post(f"{API_BASE}/auth/signup", json=signup_data)
    
    if signup_response.status_code == 200:
        signup_result = signup_response.json()
        if signup_result.get("success"):
            user_id = signup_result["user"]["id"]
            print(f"✅ User created successfully: {user_id}")
            
            # Test fixer application with services as string
            fixer_data = {
                "user_id": user_id,
                "services_offered": "Plumbing, Electrical, Carpentry",  # String format for Heroku compatibility
                "experience_years": "5",
                "why_fixer": "I want to help people fix their problems"
            }
            
            print("🔧 Testing fixer application with services as string...")
            fixer_response = requests.post(f"{API_BASE}/fixer/apply", data=fixer_data)
            
            if fixer_response.status_code == 200:
                fixer_result = fixer_response.json()
                if fixer_result.get("success"):
                    fixer_id = fixer_result.get("fixer_id")
                    print(f"✅ Fixer application successful: {fixer_id}")
                    
                    # Verify the fixer was created correctly
                    fixers_response = requests.get(f"{API_BASE}/fixers")
                    if fixers_response.status_code == 200:
                        fixers_data = fixers_response.json()
                        if fixers_data.get("success"):
                            fixers = fixers_data.get("fixers", [])
                            created_fixer = None
                            for fixer in fixers:
                                if fixer.get("user_id") == user_id:
                                    created_fixer = fixer
                                    break
                            
                            if created_fixer:
                                services = created_fixer.get("services")
                                print(f"✅ Services field verification: {services}")
                                print(f"✅ Fixer name: {created_fixer.get('name')}")
                                print(f"✅ Fixer location: {created_fixer.get('location')}")
                                return True
                            else:
                                print("❌ Created fixer not found in fixers list")
                                return False
                        else:
                            print("❌ Failed to retrieve fixers list")
                            return False
                    else:
                        print(f"❌ Fixers endpoint error: {fixers_response.status_code}")
                        return False
                else:
                    print(f"❌ Fixer application failed: {fixer_result.get('message')}")
                    return False
            else:
                print(f"❌ Fixer application HTTP error: {fixer_response.status_code} - {fixer_response.text}")
                return False
        else:
            print(f"❌ User signup failed: {signup_result.get('message')}")
            return False
    else:
        print(f"❌ User signup HTTP error: {signup_response.status_code} - {signup_response.text}")
        return False

def test_password_reset_compatibility():
    """Test password reset system with PostgreSQL compatibility"""
    print("\n🔐 TESTING PASSWORD RESET COMPATIBILITY")
    print("=" * 60)
    
    # Create a test user for password reset
    test_phone = f"+2780000{str(uuid.uuid4())[:4]}"
    signup_data = {
        "phone": test_phone,
        "first_name": "Reset",
        "last_name": "Test",
        "id_number": "9002020000000",
        "town": "Johannesburg",
        "email": f"resettest{uuid.uuid4().hex[:8]}@example.com",
        "password": "originalpass123",
        "confirm_password": "originalpass123"
    }
    
    print(f"📝 Creating test user for password reset: {test_phone}")
    signup_response = requests.post(f"{API_BASE}/auth/signup", json=signup_data)
    
    if signup_response.status_code == 200:
        signup_result = signup_response.json()
        if signup_result.get("success"):
            user_id = signup_result["user"]["id"]
            print(f"✅ User created successfully: {user_id}")
            
            # Test password reset request
            print("🔐 Testing password reset request...")
            reset_data = {"phone": test_phone}
            reset_response = requests.post(f"{API_BASE}/auth/request-password-reset", data=reset_data)
            
            if reset_response.status_code == 200:
                reset_result = reset_response.json()
                if reset_result.get("success"):
                    reset_code = reset_result.get("dev_code")
                    print(f"✅ Password reset request successful, code: {reset_code}")
                    
                    # Test code verification
                    print("🔍 Testing reset code verification...")
                    verify_data = {
                        "phone": test_phone,
                        "reset_code": reset_code
                    }
                    verify_response = requests.post(f"{API_BASE}/auth/verify-reset-code", data=verify_data)
                    
                    if verify_response.status_code == 200:
                        verify_result = verify_response.json()
                        if verify_result.get("success"):
                            print("✅ Reset code verification successful")
                            
                            # Test password update with column compatibility
                            print("🔄 Testing password update with column compatibility...")
                            new_password = "newpassword123"
                            update_data = {
                                "phone": test_phone,
                                "reset_code": reset_code,
                                "new_password": new_password
                            }
                            update_response = requests.post(f"{API_BASE}/auth/reset-password", data=update_data)
                            
                            if update_response.status_code == 200:
                                update_result = update_response.json()
                                if update_result.get("success"):
                                    print("✅ Password update successful")
                                    
                                    # Test login with new password
                                    print("🔑 Testing login with new password...")
                                    login_data = {
                                        "phone": test_phone,
                                        "password": new_password
                                    }
                                    login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
                                    
                                    if login_response.status_code == 200:
                                        login_result = login_response.json()
                                        if login_result.get("success"):
                                            print(f"✅ Login with new password successful: {login_result.get('user', {}).get('id')}")
                                            return True
                                        else:
                                            print(f"❌ Login failed: {login_result.get('message')}")
                                            return False
                                    else:
                                        print(f"❌ Login HTTP error: {login_response.status_code}")
                                        return False
                                else:
                                    print(f"❌ Password update failed: {update_result.get('message')}")
                                    return False
                            else:
                                print(f"❌ Password update HTTP error: {update_response.status_code} - {update_response.text}")
                                return False
                        else:
                            print(f"❌ Code verification failed: {verify_result.get('message')}")
                            return False
                    else:
                        print(f"❌ Code verification HTTP error: {verify_response.status_code} - {verify_response.text}")
                        return False
                else:
                    print(f"❌ Password reset request failed: {reset_result.get('message')}")
                    return False
            else:
                print(f"❌ Password reset HTTP error: {reset_response.status_code} - {reset_response.text}")
                return False
        else:
            print(f"❌ User signup failed: {signup_result.get('message')}")
            return False
    else:
        print(f"❌ User signup HTTP error: {signup_response.status_code} - {signup_response.text}")
        return False

def test_existing_user_compatibility():
    """Test with the existing user from review request"""
    print("\n👤 TESTING EXISTING USER COMPATIBILITY")
    print("=" * 60)
    
    existing_user_phone = "+27800000003"
    existing_user_id = "c417ef19-cdb6-44ee-80aa-8128e0ff8e75"
    
    # Check if user exists
    print(f"🔍 Checking existing user: {existing_user_phone}")
    role_response = requests.get(f"{API_BASE}/auth/role-check/{existing_user_phone}")
    
    if role_response.status_code == 200:
        role_result = role_response.json()
        if role_result.get("success") and role_result.get("user_exists"):
            print(f"✅ Existing user found: {role_result.get('display_name')} ({role_result.get('role')})")
            
            # Check if user already has fixer application
            fixers_response = requests.get(f"{API_BASE}/fixers")
            if fixers_response.status_code == 200:
                fixers_data = fixers_response.json()
                if fixers_data.get("success"):
                    existing_fixer = None
                    for fixer in fixers_data.get("fixers", []):
                        if fixer.get("user_id") == existing_user_id:
                            existing_fixer = fixer
                            break
                    
                    if existing_fixer:
                        print(f"✅ Existing user already has fixer profile: {existing_fixer.get('id')}")
                        print(f"✅ Services: {existing_fixer.get('services')}")
                        return True
                    else:
                        print("ℹ️ Existing user doesn't have fixer profile yet")
                        return True
                else:
                    print("❌ Failed to retrieve fixers")
                    return False
            else:
                print(f"❌ Fixers endpoint error: {fixers_response.status_code}")
                return False
        else:
            print("❌ Existing user not found")
            return False
    else:
        print(f"❌ Role check error: {role_response.status_code}")
        return False

def main():
    """Run all compatibility tests"""
    print("🚀 FIXMATE-SA HEROKU COMPATIBILITY TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 80)
    
    results = []
    
    # Test 1: Fixer Application Compatibility
    try:
        result1 = test_fixer_application_compatibility()
        results.append(("Fixer Application Compatibility", result1))
    except Exception as e:
        print(f"❌ Fixer application test error: {e}")
        results.append(("Fixer Application Compatibility", False))
    
    # Test 2: Password Reset Compatibility
    try:
        result2 = test_password_reset_compatibility()
        results.append(("Password Reset Compatibility", result2))
    except Exception as e:
        print(f"❌ Password reset test error: {e}")
        results.append(("Password Reset Compatibility", False))
    
    # Test 3: Existing User Compatibility
    try:
        result3 = test_existing_user_compatibility()
        results.append(("Existing User Compatibility", result3))
    except Exception as e:
        print(f"❌ Existing user test error: {e}")
        results.append(("Existing User Compatibility", False))
    
    # Print final results
    print("\n" + "=" * 80)
    print("🎯 HEROKU COMPATIBILITY TEST RESULTS")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\n🎉 HEROKU COMPATIBILITY TESTING SUCCESSFUL!")
        print("✅ Fixer signup and password reset endpoints are ready for Heroku deployment")
    elif success_rate >= 60:
        print("\n⚠️ HEROKU COMPATIBILITY TESTING COMPLETED WITH WARNINGS")
        print("🔧 Some issues detected but core functionality works")
    else:
        print("\n❌ HEROKU COMPATIBILITY TESTING FAILED")
        print("🚨 Critical issues need to be resolved")
    
    return results

if __name__ == "__main__":
    main()