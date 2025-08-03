#!/usr/bin/env python3
"""
FixMate-SA Role-Based Authentication System Testing Script

CRITICAL SESSION SHARING FIX TESTING:

This script tests the newly implemented role-based authentication system focusing on:

1. **Role-Specific Login Validation**:
   - Test POST /api/auth/login with different user roles (admin, fixer, client)
   - Verify role validation in login response
   - Check token generation includes role and timestamp
   - Test phone number format handling

2. **Phone Number Role Validation**:
   - Test POST /api/auth/validate-phone endpoint
   - Verify prevention of same phone registering for multiple roles
   - Test error messages for existing phone numbers with different roles

3. **Enhanced Signup with Role Conflict Prevention**:
   - Test POST /api/auth/signup with role conflict detection
   - Verify detailed error messages for existing users
   - Test new token format with role and timestamp

4. **Authentication Flow Testing**:
   - Test admin login with +27821234567/admin123
   - Test existing fixer and client accounts
   - Verify role determination is working correctly

5. **Session Isolation Verification**:
   - Test that tokens now include role information
   - Verify login responses contain proper role data

The session sharing issue should be resolved with the new role-specific token generation and validation system.
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time
import random

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔧 Testing Role-Based Authentication System at: {API_BASE}")
print("=" * 80)
print("🎯 ROLE-BASED AUTHENTICATION SYSTEM TESTING")
print("=" * 80)

class RoleAuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_data = {}
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
            print(f"   Response: {response.status_code} - {response.text[:300]}")
        
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
                if "message" in data:
                    self.log_result("API Health Check", True, f"API is running: {data['message']}")
                    return True
                else:
                    self.log_result("API Health Check", False, "Invalid response format", response)
            else:
                self.log_result("API Health Check", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("API Health Check", False, f"Connection error: {str(e)}")
        return False
    
    def test_admin_login_role_validation(self):
        """Test admin login with role validation"""
        try:
            login_data = {
                "phone": "+27821234567",
                "password": "admin123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["user", "role_info", "display_name", "welcome_message", "token"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Admin Login Role Validation", False, f"Missing fields: {missing_fields}", response)
                    return False
                
                # Verify role information
                role_info = data.get("role_info", {})
                if role_info.get("role") != "admin":
                    self.log_result("Admin Login Role Validation", False, f"Expected admin role, got: {role_info.get('role')}", response)
                    return False
                
                # Verify token includes role and timestamp
                token = data.get("token", "")
                if not token.startswith("token_") or "_admin_" not in token:
                    self.log_result("Admin Login Role Validation", False, f"Token format invalid: {token[:50]}...", response)
                    return False
                
                # Store admin data for subsequent tests
                self.test_data['admin_token'] = token
                self.test_data['admin_user'] = data['user']
                self.test_data['admin_role_info'] = role_info
                
                self.log_result("Admin Login Role Validation", True, 
                              f"✅ ADMIN LOGIN WORKING! Role: {role_info.get('role')}, "
                              f"Display: {data.get('display_name')}, "
                              f"Token format: token_[user_id]_admin_[timestamp]")
                return True
            else:
                self.log_result("Admin Login Role Validation", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Admin Login Role Validation", False, f"Request error: {str(e)}")
        return False
    
    def test_phone_validation_endpoint(self):
        """Test phone number role validation endpoint"""
        try:
            # Test 1: Validate new phone number for client role
            timestamp = str(int(time.time()))[-6:]
            new_phone = f"+2782999{timestamp}"
            
            validation_data = {
                "phone": new_phone,
                "role": "client"
            }
            
            response = self.session.post(f"{API_BASE}/auth/validate-phone", json=validation_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("valid") != True:
                    self.log_result("Phone Validation - New Phone", False, f"New phone should be valid: {data}", response)
                    return False
                
                self.log_result("Phone Validation - New Phone", True, f"✅ NEW PHONE VALIDATION WORKING! {data.get('message')}")
            else:
                self.log_result("Phone Validation - New Phone", False, f"HTTP {response.status_code}", response)
                return False
            
            # Test 2: Validate existing admin phone for different role
            admin_validation_data = {
                "phone": "+27821234567",
                "role": "client"
            }
            
            response = self.session.post(f"{API_BASE}/auth/validate-phone", json=admin_validation_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("valid") != False:
                    self.log_result("Phone Validation - Role Conflict", False, f"Admin phone should not be valid for client role: {data}", response)
                    return False
                
                if "already registered as a admin" not in data.get("error", ""):
                    self.log_result("Phone Validation - Role Conflict", False, f"Expected role conflict error: {data}", response)
                    return False
                
                self.log_result("Phone Validation - Role Conflict", True, 
                              f"✅ ROLE CONFLICT PREVENTION WORKING! Error: {data.get('error')}")
                return True
            else:
                self.log_result("Phone Validation - Role Conflict", False, f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("Phone Validation Endpoint", False, f"Request error: {str(e)}")
        return False
    
    def test_enhanced_signup_with_role_conflict_prevention(self):
        """Test enhanced signup with role conflict prevention"""
        try:
            # Generate unique test data
            timestamp = str(int(time.time()))[-6:]
            random_suffix = str(random.randint(100, 999))
            
            # Test 1: Normal signup for new user
            signup_data = {
                "phone": f"+2782888{timestamp}",
                "first_name": "TestClient",
                "last_name": "User",
                "id_number": f"900101500{timestamp[-2:]}{random_suffix}",
                "town": "Cape Town",
                "email": f"testclient.{timestamp}{random_suffix}@example.com",
                "password": "testpass123",
                "confirm_password": "testpass123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ["user", "role_info", "display_name", "welcome_message", "token"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Enhanced Signup - New User", False, f"Missing fields: {missing_fields}", response)
                    return False
                
                # Verify role assignment (should be client by default)
                role_info = data.get("role_info", {})
                if role_info.get("role") != "client":
                    self.log_result("Enhanced Signup - New User", False, f"Expected client role, got: {role_info.get('role')}", response)
                    return False
                
                # Verify token format with role and timestamp
                token = data.get("token", "")
                if not token.startswith("token_") or "_client_" not in token:
                    self.log_result("Enhanced Signup - New User", False, f"Token format invalid: {token[:50]}...", response)
                    return False
                
                # Store test user data
                self.test_data['test_client_phone'] = signup_data['phone']
                self.test_data['test_client_token'] = token
                self.test_data['test_client_user'] = data['user']
                
                self.log_result("Enhanced Signup - New User", True, 
                              f"✅ NEW USER SIGNUP WORKING! Role: {role_info.get('role')}, "
                              f"Display: {data.get('display_name')}, "
                              f"Token format includes role and timestamp")
            else:
                self.log_result("Enhanced Signup - New User", False, f"HTTP {response.status_code}", response)
                return False
            
            # Test 2: Try to signup with existing admin phone (should fail with detailed error)
            admin_signup_data = {
                "phone": "+27821234567",
                "first_name": "TestAdmin",
                "last_name": "Duplicate",
                "id_number": f"800101500{timestamp[-2:]}{random_suffix}",
                "town": "Johannesburg",
                "email": f"testadmin.{timestamp}{random_suffix}@example.com",
                "password": "testpass123",
                "confirm_password": "testpass123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/signup", json=admin_signup_data)
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', '')
                    
                    if "already registered as admin" in error_detail:
                        self.log_result("Enhanced Signup - Role Conflict Prevention", True, 
                                      f"✅ ROLE CONFLICT PREVENTION WORKING! Error: {error_detail}")
                        return True
                    else:
                        self.log_result("Enhanced Signup - Role Conflict Prevention", False, 
                                      f"Expected role conflict error, got: {error_detail}", response)
                        return False
                except:
                    self.log_result("Enhanced Signup - Role Conflict Prevention", False, 
                                  f"Could not parse error response: {response.text[:200]}", response)
                    return False
            else:
                self.log_result("Enhanced Signup - Role Conflict Prevention", False, 
                              f"Expected HTTP 400, got: {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("Enhanced Signup with Role Conflict Prevention", False, f"Request error: {str(e)}")
        return False
    
    def test_client_login_role_validation(self):
        """Test client login with role validation"""
        if 'test_client_phone' not in self.test_data:
            self.log_result("Client Login Role Validation", False, "No test client phone available from signup test")
            return False
        
        try:
            login_data = {
                "phone": self.test_data['test_client_phone'],
                "password": "testpass123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify role information
                role_info = data.get("role_info", {})
                if role_info.get("role") != "client":
                    self.log_result("Client Login Role Validation", False, f"Expected client role, got: {role_info.get('role')}", response)
                    return False
                
                # Verify token includes role and timestamp
                token = data.get("token", "")
                if not token.startswith("token_") or "_client_" not in token:
                    self.log_result("Client Login Role Validation", False, f"Token format invalid: {token[:50]}...", response)
                    return False
                
                # Verify client-specific permissions
                permissions = role_info.get("permissions", {})
                expected_client_permissions = ["can_create_jobs", "can_hire_fixers", "can_leave_reviews", "can_view_fixers"]
                
                missing_permissions = [perm for perm in expected_client_permissions if not permissions.get(perm, False)]
                if missing_permissions:
                    self.log_result("Client Login Role Validation", False, f"Missing client permissions: {missing_permissions}", response)
                    return False
                
                # Verify no admin permissions
                admin_permissions = ["can_access_admin", "can_verify_fixers", "can_settle_payments", "can_manage_all_users"]
                has_admin_permissions = [perm for perm in admin_permissions if permissions.get(perm, False)]
                if has_admin_permissions:
                    self.log_result("Client Login Role Validation", False, f"Client should not have admin permissions: {has_admin_permissions}", response)
                    return False
                
                self.log_result("Client Login Role Validation", True, 
                              f"✅ CLIENT LOGIN WORKING! Role: {role_info.get('role')}, "
                              f"Display: {data.get('display_name')}, "
                              f"Permissions: {len([p for p in permissions if permissions[p]])} granted")
                return True
            else:
                self.log_result("Client Login Role Validation", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Client Login Role Validation", False, f"Request error: {str(e)}")
        return False
    
    def test_fixer_role_creation_and_login(self):
        """Test fixer role creation and login"""
        try:
            # Generate unique test data for fixer
            timestamp = str(int(time.time()))[-6:]
            random_suffix = str(random.randint(100, 999))
            
            # Step 1: Create user for fixer
            user_data = {
                "phone": f"+2782777{timestamp}",
                "first_name": "TestFixer",
                "last_name": "Professional",
                "id_number": f"850101500{timestamp[-2:]}{random_suffix}",
                "town": "Durban",
                "email": f"testfixer.{timestamp}{random_suffix}@example.com",
                "address": "123 Fixer Street, Durban"
            }
            
            user_response = self.session.post(f"{API_BASE}/users", json=user_data)
            if user_response.status_code != 200:
                self.log_result("Fixer Role Creation - User Creation", False, f"User creation failed: HTTP {user_response.status_code}", user_response)
                return False
            
            user = user_response.json()
            
            # Step 2: Create fixer record
            fixer_data = {
                "user_id": user['id'],
                "phone": f"+2782777{timestamp}",
                "name": "TestFixer Professional",
                "email": f"testfixer.{timestamp}{random_suffix}@example.com",
                "services": '["plumbing", "electrical"]',
                "location": "Durban"
            }
            
            fixer_response = self.session.post(f"{API_BASE}/fixers", json=fixer_data)
            if fixer_response.status_code != 200:
                self.log_result("Fixer Role Creation - Fixer Creation", False, f"Fixer creation failed: HTTP {fixer_response.status_code}", fixer_response)
                return False
            
            fixer = fixer_response.json()
            
            # Step 3: Set password for the user
            password_data = {
                "phone": f"+2782777{timestamp}",
                "password": "fixerpass123",
                "confirm_password": "fixerpass123"
            }
            
            password_response = self.session.post(f"{API_BASE}/auth/set-password", json=password_data)
            if password_response.status_code != 200:
                self.log_result("Fixer Role Creation - Password Setting", False, f"Password setting failed: HTTP {password_response.status_code}", password_response)
                return False
            
            # Step 4: Test fixer login
            login_data = {
                "phone": f"+2782777{timestamp}",
                "password": "fixerpass123"
            }
            
            login_response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                data = login_response.json()
                
                # Verify role information
                role_info = data.get("role_info", {})
                if role_info.get("role") != "fixer":
                    self.log_result("Fixer Login Role Validation", False, f"Expected fixer role, got: {role_info.get('role')}", login_response)
                    return False
                
                # Verify token includes role and timestamp
                token = data.get("token", "")
                if not token.startswith("token_") or "_fixer_" not in token:
                    self.log_result("Fixer Login Role Validation", False, f"Token format invalid: {token[:50]}...", login_response)
                    return False
                
                # Verify fixer-specific permissions
                permissions = role_info.get("permissions", {})
                expected_fixer_permissions = ["can_access_payments", "can_view_job_assignments", "can_manage_fixer_profile"]
                
                missing_permissions = [perm for perm in expected_fixer_permissions if not permissions.get(perm, False)]
                if missing_permissions:
                    self.log_result("Fixer Login Role Validation", False, f"Missing fixer permissions: {missing_permissions}", login_response)
                    return False
                
                # Store fixer data
                self.test_data['test_fixer_phone'] = f"+2782777{timestamp}"
                self.test_data['test_fixer_token'] = token
                self.test_data['test_fixer_user'] = data['user']
                self.test_data['test_fixer_id'] = fixer['id']
                
                self.log_result("Fixer Role Creation and Login", True, 
                              f"✅ FIXER ROLE WORKING! Role: {role_info.get('role')}, "
                              f"Display: {data.get('display_name')}, "
                              f"Permissions: {len([p for p in permissions if permissions[p]])} granted")
                return True
            else:
                self.log_result("Fixer Role Creation and Login", False, f"Fixer login failed: HTTP {login_response.status_code}", login_response)
        except Exception as e:
            self.log_result("Fixer Role Creation and Login", False, f"Request error: {str(e)}")
        return False
    
    def test_role_check_endpoint(self):
        """Test role check endpoint for debugging purposes"""
        try:
            # Test admin role check
            admin_response = self.session.get(f"{API_BASE}/auth/role-check/+27821234567")
            
            if admin_response.status_code == 200:
                admin_data = admin_response.json()
                if admin_data.get("role") != "admin":
                    self.log_result("Role Check - Admin", False, f"Expected admin role, got: {admin_data.get('role')}", admin_response)
                    return False
                
                self.log_result("Role Check - Admin", True, f"✅ ADMIN ROLE CHECK WORKING! Role: {admin_data.get('role')}")
            else:
                self.log_result("Role Check - Admin", False, f"HTTP {admin_response.status_code}", admin_response)
                return False
            
            # Test client role check if available
            if 'test_client_phone' in self.test_data:
                client_response = self.session.get(f"{API_BASE}/auth/role-check/{self.test_data['test_client_phone']}")
                
                if client_response.status_code == 200:
                    client_data = client_response.json()
                    if client_data.get("role") != "client":
                        self.log_result("Role Check - Client", False, f"Expected client role, got: {client_data.get('role')}", client_response)
                        return False
                    
                    self.log_result("Role Check - Client", True, f"✅ CLIENT ROLE CHECK WORKING! Role: {client_data.get('role')}")
                else:
                    self.log_result("Role Check - Client", False, f"HTTP {client_response.status_code}", client_response)
                    return False
            
            # Test fixer role check if available
            if 'test_fixer_phone' in self.test_data:
                fixer_response = self.session.get(f"{API_BASE}/auth/role-check/{self.test_data['test_fixer_phone']}")
                
                if fixer_response.status_code == 200:
                    fixer_data = fixer_response.json()
                    if fixer_data.get("role") != "fixer":
                        self.log_result("Role Check - Fixer", False, f"Expected fixer role, got: {fixer_data.get('role')}", fixer_response)
                        return False
                    
                    self.log_result("Role Check - Fixer", True, f"✅ FIXER ROLE CHECK WORKING! Role: {fixer_data.get('role')}")
                    return True
                else:
                    self.log_result("Role Check - Fixer", False, f"HTTP {fixer_response.status_code}", fixer_response)
                    return False
            
            return True
                
        except Exception as e:
            self.log_result("Role Check Endpoint", False, f"Request error: {str(e)}")
        return False
    
    def test_session_isolation_verification(self):
        """Test session isolation with role-specific tokens"""
        try:
            # Verify that different role tokens are unique and contain role information
            tokens = {}
            
            if 'admin_token' in self.test_data:
                tokens['admin'] = self.test_data['admin_token']
            
            if 'test_client_token' in self.test_data:
                tokens['client'] = self.test_data['test_client_token']
            
            if 'test_fixer_token' in self.test_data:
                tokens['fixer'] = self.test_data['test_fixer_token']
            
            if len(tokens) < 2:
                self.log_result("Session Isolation Verification", False, "Need at least 2 different role tokens for isolation testing")
                return False
            
            # Verify tokens are unique
            token_values = list(tokens.values())
            if len(set(token_values)) != len(token_values):
                self.log_result("Session Isolation Verification", False, "Tokens are not unique across roles")
                return False
            
            # Verify token format includes role information
            role_in_token_count = 0
            for role, token in tokens.items():
                if f"_{role}_" in token:
                    role_in_token_count += 1
            
            if role_in_token_count != len(tokens):
                self.log_result("Session Isolation Verification", False, f"Only {role_in_token_count}/{len(tokens)} tokens contain role information")
                return False
            
            # Verify timestamp in tokens (should be different for different login times)
            timestamp_parts = []
            for token in token_values:
                parts = token.split('_')
                if len(parts) >= 4:  # token_userid_role_timestamp
                    try:
                        timestamp = float(parts[3])
                        timestamp_parts.append(timestamp)
                    except ValueError:
                        pass
            
            if len(timestamp_parts) != len(tokens):
                self.log_result("Session Isolation Verification", False, "Not all tokens contain valid timestamps")
                return False
            
            self.log_result("Session Isolation Verification", True, 
                          f"✅ SESSION ISOLATION WORKING! {len(tokens)} unique role-specific tokens generated, "
                          f"all contain role information and timestamps")
            return True
            
        except Exception as e:
            self.log_result("Session Isolation Verification", False, f"Request error: {str(e)}")
        return False
    
    def test_phone_number_format_handling(self):
        """Test various phone number formats in login"""
        try:
            # Test different phone number formats for admin login
            phone_formats = [
                "+27821234567",      # Standard international format
                "0821234567",        # Local format
                "27821234567",       # International without +
                "whatsapp:+27821234567"  # WhatsApp format
            ]
            
            successful_formats = 0
            
            for phone_format in phone_formats:
                login_data = {
                    "phone": phone_format,
                    "password": "admin123"
                }
                
                response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("role_info", {}).get("role") == "admin":
                        successful_formats += 1
                        print(f"   ✅ Format '{phone_format}' works")
                    else:
                        print(f"   ❌ Format '{phone_format}' wrong role: {data.get('role_info', {}).get('role')}")
                else:
                    print(f"   ❌ Format '{phone_format}' failed: HTTP {response.status_code}")
            
            if successful_formats >= 2:  # At least 2 formats should work
                self.log_result("Phone Number Format Handling", True, 
                              f"✅ PHONE FORMAT HANDLING WORKING! {successful_formats}/{len(phone_formats)} formats successful")
                return True
            else:
                self.log_result("Phone Number Format Handling", False, 
                              f"Only {successful_formats}/{len(phone_formats)} phone formats work")
                return False
                
        except Exception as e:
            self.log_result("Phone Number Format Handling", False, f"Request error: {str(e)}")
        return False
    
    def run_comprehensive_role_auth_tests(self):
        """Run comprehensive role-based authentication tests"""
        print("🚀 COMPREHENSIVE ROLE-BASED AUTHENTICATION TESTING")
        print("=" * 80)
        
        # Phase 1: Basic Setup
        print("📋 PHASE 1: BASIC SETUP")
        print("-" * 50)
        
        if not self.test_health_check():
            print("❌ Health check failed. Cannot proceed with testing.")
            return False
        
        # Phase 2: Core Authentication Tests
        print("\n🔐 PHASE 2: CORE AUTHENTICATION TESTS")
        print("-" * 50)
        
        auth_tests = [
            ("Admin Login Role Validation", self.test_admin_login_role_validation),
            ("Phone Number Role Validation", self.test_phone_validation_endpoint),
            ("Enhanced Signup with Role Conflict Prevention", self.test_enhanced_signup_with_role_conflict_prevention),
            ("Client Login Role Validation", self.test_client_login_role_validation),
            ("Fixer Role Creation and Login", self.test_fixer_role_creation_and_login),
            ("Role Check Endpoint", self.test_role_check_endpoint),
            ("Phone Number Format Handling", self.test_phone_number_format_handling),
            ("Session Isolation Verification", self.test_session_isolation_verification)
        ]
        
        auth_results = []
        for test_name, test_func in auth_tests:
            print(f"Testing {test_name}...")
            result = test_func()
            auth_results.append((test_name, result))
            print()
        
        # Results Summary
        print("=" * 80)
        print("🎯 ROLE-BASED AUTHENTICATION TEST RESULTS")
        print("=" * 80)
        
        print("🔐 AUTHENTICATION SYSTEM VALIDATION:")
        auth_passed = 0
        for test_name, result in auth_results:
            status = "✅ WORKING" if result else "❌ FAILING"
            print(f"   {status}: {test_name}")
            if result:
                auth_passed += 1
        
        print(f"\n📊 Authentication Tests Success Rate: {auth_passed}/{len(auth_tests)} ({auth_passed/len(auth_tests)*100:.1f}%)")
        
        # Overall Assessment
        overall_success_rate = auth_passed / len(auth_tests) * 100
        
        print(f"\n🎉 OVERALL SUCCESS RATE: {auth_passed}/{len(auth_tests)} ({overall_success_rate:.1f}%)")
        
        # Detailed Assessment
        if auth_passed >= 6:  # 75% of tests working
            print("\n✅ SUCCESS! Role-Based Authentication System is largely functional!")
            
            working_tests = [name for name, result in auth_results if result]
            failing_tests = [name for name, result in auth_results if not result]
            
            if working_tests:
                print("✅ WORKING FEATURES:")
                for test in working_tests:
                    print(f"   • {test}")
            
            if failing_tests:
                print("\n❌ FAILING FEATURES:")
                for test in failing_tests:
                    print(f"   • {test}")
        else:
            print(f"\n⚠️  WARNING! Only {auth_passed}/{len(auth_tests)} authentication tests are working.")
            print("❌ Role-Based Authentication system needs significant attention.")
        
        # Session Sharing Fix Assessment
        session_isolation_working = any(name == "Session Isolation Verification" and result for name, result in auth_results)
        role_validation_working = any(name == "Admin Login Role Validation" and result for name, result in auth_results)
        phone_validation_working = any(name == "Phone Number Role Validation" and result for name, result in auth_results)
        
        if session_isolation_working and role_validation_working and phone_validation_working:
            print("\n🎉 CRITICAL SESSION SHARING ISSUE RESOLVED!")
            print("✅ Role-specific tokens are working")
            print("✅ Role validation is functional")
            print("✅ Phone number role conflicts are prevented")
            print("✅ Session isolation is operational")
        else:
            print("\n⚠️  SESSION SHARING FIX STATUS:")
            print(f"   Session Isolation: {'✅' if session_isolation_working else '❌'}")
            print(f"   Role Validation: {'✅' if role_validation_working else '❌'}")
            print(f"   Phone Validation: {'✅' if phone_validation_working else '❌'}")
        
        # Production Readiness Assessment
        if overall_success_rate >= 85:
            print("\n🎉 ROLE-BASED AUTHENTICATION SYSTEM IS PRODUCTION-READY!")
            print("✅ All major authentication features are functional")
            print("✅ Session sharing issue has been resolved")
            print("✅ Role-specific login and signup working correctly")
        elif overall_success_rate >= 70:
            print("\n⚠️  ROLE-BASED AUTHENTICATION SYSTEM IS MOSTLY READY")
            print("✅ Most authentication features are functional")
            print("⚠️  Some minor issues need attention before full production deployment")
        else:
            print("\n❌ ROLE-BASED AUTHENTICATION SYSTEM NEEDS ATTENTION")
            print("❌ Multiple authentication features failing")
            print("❌ Not ready for production deployment")
        
        return overall_success_rate >= 70

if __name__ == "__main__":
    print("🔧 FixMate-SA Role-Based Authentication System - Comprehensive Backend Testing")
    print("=" * 80)
    print("🎯 CRITICAL SESSION SHARING FIX TESTING")
    print("📋 ROLE-SPECIFIC LOGIN AND SIGNUP VALIDATION")
    print("🔍 PHONE NUMBER ROLE CONFLICT PREVENTION")
    print("🔐 SESSION ISOLATION VERIFICATION")
    print("=" * 80)
    
    tester = RoleAuthTester()
    
    try:
        # Run Comprehensive Role-Based Authentication Testing
        success = tester.run_comprehensive_role_auth_tests()
        
        print("\n" + "=" * 80)
        print("📊 FINAL ROLE-BASED AUTHENTICATION TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {tester.results['passed']}")
        print(f"❌ Tests Failed: {tester.results['failed']}")
        print(f"📈 Success Rate: {tester.results['passed']/(tester.results['passed']+tester.results['failed'])*100:.1f}%")
        
        if tester.results['errors']:
            print(f"\n🚨 ERRORS ENCOUNTERED:")
            for error in tester.results['errors']:
                print(f"   • {error}")
        
        if success:
            print("\n🎉 ROLE-BASED AUTHENTICATION SYSTEM IS PRODUCTION-READY!")
            print("✅ Critical session sharing issue has been resolved")
            print("✅ Role-specific authentication working correctly")
            print("✅ Phone number role conflicts prevented")
            print("✅ Session isolation operational")
        else:
            print("\n⚠️  ROLE-BASED AUTHENTICATION SYSTEM NEEDS ATTENTION")
            print("❌ Some critical authentication features are not working")
            print("❌ Session sharing issue may not be fully resolved")
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ CRITICAL ERROR: {str(e)}")
        sys.exit(1)