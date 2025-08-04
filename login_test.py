#!/usr/bin/env python3
"""
URGENT LOGIN DIAGNOSTIC - Test Login Endpoint

This script tests the login functionality to identify the exact issue:
1. Test POST /api/auth/login with phone/password combination
2. Use existing test accounts: +27800000001/admin2024test, +27800000002/client2024test, +27800000003/fixer2024test
3. Verify the endpoint is responding correctly
4. Check authentication flow
5. Verify authentication schema
6. Test what fields the login endpoint expects
7. Check if there are any schema validation errors
8. Check user authentication and token generation
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

print(f"🔧 URGENT LOGIN DIAGNOSTIC - Testing Login Endpoint at: {API_BASE}")
print("=" * 80)

class LoginTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def log_result(self, test_name, success, message="", response=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if response and not success:
            print(f"   Response Status: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            print(f"   Response Body: {response.text[:500]}")
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")
        print()
    
    def test_health_check(self):
        """Test API health check"""
        try:
            response = self.session.get(f"{API_BASE}/")
            if response.status_code == 200:
                data = response.json()
                self.log_result("API Health Check", True, f"API is running: {data.get('message', 'OK')}")
                return True
            else:
                self.log_result("API Health Check", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("API Health Check", False, f"Connection error: {str(e)}")
        return False
    
    def test_login_endpoint_schema(self):
        """Test login endpoint schema validation"""
        print("🔍 Testing Login Endpoint Schema...")
        
        # Test 1: Empty request
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={})
            print(f"   Empty request: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   Empty request error: {str(e)}")
        
        # Test 2: Missing password
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={"phone": "+27800000001"})
            print(f"   Missing password: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   Missing password error: {str(e)}")
        
        # Test 3: Missing phone
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={"password": "admin2024test"})
            print(f"   Missing phone: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   Missing phone error: {str(e)}")
        
        # Test 4: Wrong field names
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={"username": "+27800000001", "password_hash": "admin2024test"})
            print(f"   Wrong field names: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   Wrong field names error: {str(e)}")
        
        print()
        return True
    
    def test_user_existence(self):
        """Test if users exist in database"""
        print("🔍 Testing User Existence in Database...")
        
        test_phones = ["+27800000001", "+27800000002", "+27800000003"]
        
        for phone in test_phones:
            try:
                # Try to get user info via role check endpoint
                response = self.session.get(f"{API_BASE}/auth/role-check/{phone}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   User {phone}: EXISTS - Role: {data.get('role', 'unknown')}")
                else:
                    print(f"   User {phone}: HTTP {response.status_code} - {response.text[:100]}")
            except Exception as e:
                print(f"   User {phone}: Error - {str(e)}")
        
        print()
        return True
    
    def test_login_with_test_accounts(self):
        """Test login with all test accounts"""
        print("🔍 Testing Login with Test Accounts...")
        
        test_accounts = [
            {
                "name": "Admin Account",
                "phone": "+27800000001",
                "password": "admin2024test",
                "expected_role": "admin"
            },
            {
                "name": "Client Account", 
                "phone": "+27800000002",
                "password": "client2024test",
                "expected_role": "client"
            },
            {
                "name": "Fixer Account",
                "phone": "+27800000003", 
                "password": "fixer2024test",
                "expected_role": "fixer"
            }
        ]
        
        successful_logins = 0
        
        for account in test_accounts:
            print(f"   Testing {account['name']} ({account['phone']})...")
            
            try:
                login_data = {
                    "phone": account["phone"],
                    "password": account["password"]
                }
                
                response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                
                print(f"      Status: HTTP {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"      Response keys: {list(data.keys())}")
                        
                        # Check for required fields
                        if "user" in data and "token" in data:
                            user_info = data["user"]
                            role_info = data.get("role_info", {})
                            actual_role = role_info.get("role", "unknown")
                            
                            print(f"      ✅ LOGIN SUCCESS!")
                            print(f"      User ID: {user_info.get('id', 'N/A')}")
                            print(f"      Phone: {user_info.get('phone', 'N/A')}")
                            print(f"      Role: {actual_role}")
                            print(f"      Token: {data['token'][:20]}...")
                            print(f"      Display Name: {data.get('display_name', 'N/A')}")
                            
                            successful_logins += 1
                            
                            # Store token for further testing
                            if account["expected_role"] == "admin":
                                self.admin_token = data["token"]
                                self.admin_user_id = user_info.get("id")
                        else:
                            print(f"      ❌ INVALID RESPONSE FORMAT - Missing user or token")
                            print(f"      Response: {response.text[:300]}")
                    except json.JSONDecodeError:
                        print(f"      ❌ INVALID JSON RESPONSE")
                        print(f"      Response: {response.text[:300]}")
                else:
                    print(f"      ❌ LOGIN FAILED")
                    print(f"      Response: {response.text[:300]}")
                    
            except Exception as e:
                print(f"      ❌ REQUEST ERROR: {str(e)}")
            
            print()
        
        # Summary
        if successful_logins == len(test_accounts):
            self.log_result("Login with Test Accounts", True, f"All {successful_logins}/{len(test_accounts)} test accounts logged in successfully")
        elif successful_logins > 0:
            self.log_result("Login with Test Accounts", False, f"Only {successful_logins}/{len(test_accounts)} test accounts logged in successfully")
        else:
            self.log_result("Login with Test Accounts", False, "No test accounts could log in")
        
        return successful_logins > 0
    
    def test_token_validation(self):
        """Test token validation with authenticated requests"""
        if not hasattr(self, 'admin_token'):
            print("   No admin token available for validation testing")
            return False
        
        print("🔍 Testing Token Validation...")
        
        try:
            # Test authenticated request with token
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{API_BASE}/users", headers=headers)
            
            print(f"   Authenticated request status: HTTP {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ TOKEN VALIDATION SUCCESS - Retrieved {len(data)} users")
                self.log_result("Token Validation", True, "Authentication token works correctly")
                return True
            else:
                print(f"   ❌ TOKEN VALIDATION FAILED - {response.text[:200]}")
                self.log_result("Token Validation", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ TOKEN VALIDATION ERROR: {str(e)}")
            self.log_result("Token Validation", False, f"Request error: {str(e)}")
            return False
    
    def test_password_variations(self):
        """Test different password variations to identify issues"""
        print("🔍 Testing Password Variations...")
        
        # Test with admin account using different password formats
        phone = "+27800000001"
        password_variations = [
            "admin2024test",      # Correct password
            "Admin2024test",      # Different case
            "admin2024test ",     # With trailing space
            " admin2024test",     # With leading space
            "admin123",           # Old password format
            "password",           # Generic password
        ]
        
        for password in password_variations:
            try:
                login_data = {
                    "phone": phone,
                    "password": password
                }
                
                response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                print(f"   Password '{password}': HTTP {response.status_code}")
                
                if response.status_code == 200:
                    print(f"      ✅ SUCCESS with password: '{password}'")
                    break
                else:
                    print(f"      Response: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   Password '{password}': Error - {str(e)}")
        
        print()
        return True
    
    def test_phone_number_formats(self):
        """Test different phone number formats"""
        print("🔍 Testing Phone Number Formats...")
        
        password = "admin2024test"
        phone_variations = [
            "+27800000001",           # Standard format
            "27800000001",            # Without +
            "0800000001",             # Local format
            "whatsapp:+27800000001",  # WhatsApp format
            "+27 80 000 0001",        # With spaces
            "+27-80-000-0001",        # With dashes
        ]
        
        for phone in phone_variations:
            try:
                login_data = {
                    "phone": phone,
                    "password": password
                }
                
                response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                print(f"   Phone '{phone}': HTTP {response.status_code}")
                
                if response.status_code == 200:
                    print(f"      ✅ SUCCESS with phone: '{phone}'")
                else:
                    print(f"      Response: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   Phone '{phone}': Error - {str(e)}")
        
        print()
        return True
    
    def run_comprehensive_login_test(self):
        """Run comprehensive login diagnostic"""
        print("🚀 COMPREHENSIVE LOGIN DIAGNOSTIC")
        print("=" * 80)
        
        # Test 1: Health Check
        if not self.test_health_check():
            print("❌ API is not responding. Cannot proceed with login testing.")
            return False
        
        # Test 2: Schema Validation
        self.test_login_endpoint_schema()
        
        # Test 3: User Existence
        self.test_user_existence()
        
        # Test 4: Phone Number Formats
        self.test_phone_number_formats()
        
        # Test 5: Password Variations
        self.test_password_variations()
        
        # Test 6: Main Login Test
        login_success = self.test_login_with_test_accounts()
        
        # Test 7: Token Validation (if login succeeded)
        if login_success:
            self.test_token_validation()
        
        return login_success

if __name__ == "__main__":
    print("🔧 URGENT LOGIN DIAGNOSTIC - FixMate-SA Login Endpoint Testing")
    print("=" * 80)
    print("🎯 TESTING: POST /api/auth/login endpoint functionality")
    print("📋 ACCOUNTS: +27800000001/admin2024test, +27800000002/client2024test, +27800000003/fixer2024test")
    print("🔍 VALIDATION: Authentication schema, user existence, token generation")
    print("=" * 80)
    
    tester = LoginTester()
    
    try:
        success = tester.run_comprehensive_login_test()
        
        print("\n" + "=" * 80)
        print("📊 URGENT LOGIN DIAGNOSTIC RESULTS")
        print("=" * 80)
        print(f"✅ Tests Passed: {tester.results['passed']}")
        print(f"❌ Tests Failed: {tester.results['failed']}")
        
        if tester.results['errors']:
            print(f"\n🚨 CRITICAL ERRORS FOUND:")
            for error in tester.results['errors']:
                print(f"   • {error}")
        
        if success:
            print("\n🎉 LOGIN FUNCTIONALITY IS WORKING!")
            print("✅ Authentication endpoint is operational")
            print("✅ Test accounts can log in successfully")
            print("✅ Token generation is functional")
        else:
            print("\n❌ LOGIN FUNCTIONALITY HAS ISSUES!")
            print("🚨 URGENT: Login endpoint needs immediate attention")
            print("🔧 Check the specific errors above for exact fix needed")
        
        print("\n" + "=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ CRITICAL ERROR: {str(e)}")
        sys.exit(1)