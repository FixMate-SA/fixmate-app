#!/usr/bin/env python3
"""
FixMate-SA Authentication Flow Testing Script
Focused testing for role-based authentication as requested in the review
"""

import requests
import json
import sys
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

print(f"Testing authentication at: {API_BASE}")

class AuthenticationTester:
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
            print(f"   Response: {response.status_code} - {response.text[:200]}")
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")
        print()
    
    def test_admin_authentication(self):
        """Test admin authentication with +27821234567"""
        try:
            # Admin phone from role_service.py
            admin_phone = "+27821234567"
            
            # First check role determination
            response = self.session.get(f"{API_BASE}/auth/role-check/{admin_phone}")
            if response.status_code == 200:
                role_data = response.json()
                if role_data.get("role") != "admin":
                    self.log_result("Admin Role Check", False, f"Admin phone not identified as admin. Role: {role_data.get('role')}")
                    return False
                else:
                    self.log_result("Admin Role Check", True, f"Admin phone correctly identified as admin role")
            else:
                self.log_result("Admin Role Check", False, f"Role check failed. HTTP {response.status_code}", response)
                return False
            
            # Check if admin user exists and get the correct phone format
            response = self.session.get(f"{API_BASE}/users")
            if response.status_code != 200:
                self.log_result("Admin User Lookup", False, "Failed to get users list", response)
                return False
            
            users = response.json()
            admin_users = [u for u in users if '821234567' in u.get('phone', '') and u.get('role') == 'admin']
            
            if not admin_users:
                self.log_result("Admin User Lookup", False, "No admin user found in database")
                return False
            
            admin_user = admin_users[0]  # Use the first admin user found
            admin_phone_db = admin_user['phone']  # This will be the correct format from DB
            
            self.log_result("Admin User Lookup", True, f"Found admin user with phone: {admin_phone_db}")
            
            # Set password for admin user
            password_data = {
                "phone": admin_phone_db,
                "password": "admin123",
                "confirm_password": "admin123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/set-password", json=password_data)
            if response.status_code != 200:
                self.log_result("Admin Set Password", False, f"Failed to set admin password. HTTP {response.status_code}", response)
                return False
            
            self.log_result("Admin Set Password", True, "Admin password set successfully")
            
            # Test admin login
            login_data = {
                "phone": admin_phone_db,
                "password": "admin123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                
                # Verify admin role and messages
                role = data.get("role_info", {}).get("role")
                display_name = data.get("display_name", "")
                welcome_message = data.get("welcome_message", "")
                
                if (role == "admin" and 
                    "Admin" in display_name and
                    "Welcome Admin" in welcome_message):
                    
                    self.test_data['admin_user'] = data
                    self.log_result("Admin Login", True, 
                                  f"Admin login successful. Role: {role}, Display: '{display_name}', Welcome: '{welcome_message}'")
                    
                    # Test admin permissions
                    permissions = data.get("role_info", {}).get("permissions", {})
                    admin_permissions = ["can_access_admin", "can_verify_fixers", "can_settle_payments", "can_manage_all_users"]
                    missing_permissions = [perm for perm in admin_permissions if not permissions.get(perm, False)]
                    
                    if not missing_permissions:
                        self.log_result("Admin Permissions", True, f"All admin permissions correctly assigned")
                        return True
                    else:
                        self.log_result("Admin Permissions", False, f"Missing admin permissions: {missing_permissions}")
                        return False
                else:
                    self.log_result("Admin Login", False, 
                                  f"Admin role/messages incorrect. Role: {role}, Display: '{display_name}', Welcome: '{welcome_message}'")
                    return False
            else:
                self.log_result("Admin Login", False, f"Admin login failed. HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_fixer_authentication(self):
        """Test fixer authentication"""
        try:
            import time
            timestamp = str(int(time.time()))[-6:]
            fixer_phone = f"+2782987{timestamp}"
            
            # First signup as a regular user (this will create user with proper phone formatting)
            signup_data = {
                "phone": fixer_phone,
                "first_name": "Mike",
                "last_name": "Fixer",
                "id_number": f"8001015009{timestamp[-3:]}",
                "town": "Johannesburg",
                "email": f"mike.fixer.{timestamp}@fixmate.com",
                "password": "fixer123",
                "confirm_password": "fixer123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            if response.status_code != 200:
                self.log_result("Fixer User Signup", False, "Failed to signup fixer user", response)
                return False
            
            fixer_user_data = response.json()
            fixer_user = fixer_user_data['user']
            self.log_result("Fixer User Signup", True, f"Signed up user: {fixer_user['full_name']}")
            
            # Create fixer record using the properly formatted phone from signup
            fixer_phone_formatted = fixer_user['phone']  # This will have the correct format
            
            fixer_data = {
                "user_id": fixer_user['id'],
                "phone": fixer_phone_formatted,
                "name": "Mike Fixer",
                "email": f"mike.fixer.{timestamp}@fixmate.com",
                "services": '["plumbing", "electrical"]',
                "location": "Johannesburg"
            }
            
            response = self.session.post(f"{API_BASE}/fixers", json=fixer_data)
            if response.status_code != 200:
                self.log_result("Fixer Record Creation", False, "Failed to create fixer record", response)
                return False
            
            fixer_record = response.json()
            self.test_data['fixer_record'] = fixer_record
            self.log_result("Fixer Record Creation", True, f"Created fixer: {fixer_record['name']}")
            
            # Check role determination (use original phone format for role check)
            response = self.session.get(f"{API_BASE}/auth/role-check/{fixer_phone}")
            if response.status_code == 200:
                role_data = response.json()
                if role_data.get("role") == "fixer":
                    self.log_result("Fixer Role Check", True, f"Fixer phone correctly identified as fixer role")
                else:
                    self.log_result("Fixer Role Check", False, f"Fixer phone not identified as fixer. Role: {role_data.get('role')}")
                    return False
            else:
                self.log_result("Fixer Role Check", False, f"Fixer role check failed. HTTP {response.status_code}", response)
                return False
            
            # Test fixer login
            login_data = {
                "phone": fixer_phone,
                "password": "fixer123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                
                # Verify fixer role and messages
                role = data.get("role_info", {}).get("role")
                display_name = data.get("display_name", "")
                welcome_message = data.get("welcome_message", "")
                
                if (role == "fixer" and 
                    "Fixer" in display_name and
                    "Welcome Fixer" in welcome_message):
                    
                    self.test_data['fixer_user'] = data
                    self.log_result("Fixer Login", True, 
                                  f"Fixer login successful. Role: {role}, Display: '{display_name}', Welcome: '{welcome_message}'")
                    
                    # Test fixer permissions
                    permissions = data.get("role_info", {}).get("permissions", {})
                    fixer_permissions = ["can_access_payments", "can_view_job_assignments", "can_manage_fixer_profile"]
                    missing_permissions = [perm for perm in fixer_permissions if not permissions.get(perm, False)]
                    
                    # Check that fixer doesn't have admin permissions
                    admin_permissions = ["can_access_admin", "can_verify_fixers", "can_manage_all_users"]
                    has_admin_permissions = [perm for perm in admin_permissions if permissions.get(perm, False)]
                    
                    if not missing_permissions and not has_admin_permissions:
                        self.log_result("Fixer Permissions", True, f"Fixer permissions correctly assigned")
                        return True
                    else:
                        error_msg = ""
                        if missing_permissions:
                            error_msg += f"Missing fixer permissions: {missing_permissions}. "
                        if has_admin_permissions:
                            error_msg += f"Incorrectly has admin permissions: {has_admin_permissions}"
                        self.log_result("Fixer Permissions", False, error_msg)
                        return False
                else:
                    self.log_result("Fixer Login", False, 
                                  f"Fixer role/messages incorrect. Role: {role}, Display: '{display_name}', Welcome: '{welcome_message}'")
                    return False
            else:
                self.log_result("Fixer Login", False, f"Fixer login failed. HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("Fixer Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_client_authentication(self):
        """Test client authentication with new phone number"""
        try:
            import time
            timestamp = str(int(time.time()))[-6:]
            client_phone = f"+2781234{timestamp}"
            
            # Check role determination for new phone
            response = self.session.get(f"{API_BASE}/auth/role-check/{client_phone}")
            if response.status_code == 200:
                role_data = response.json()
                if role_data.get("role") == "client":
                    self.log_result("Client Role Check", True, f"New phone correctly identified as client role")
                else:
                    self.log_result("Client Role Check", False, f"New phone not identified as client. Role: {role_data.get('role')}")
                    return False
            else:
                self.log_result("Client Role Check", False, f"Client role check failed. HTTP {response.status_code}", response)
                return False
            
            # Test client signup
            signup_data = {
                "phone": client_phone,
                "first_name": "John",
                "last_name": "Client",
                "id_number": f"8001015009{timestamp[-3:]}",
                "town": "Durban",
                "email": f"john.client.{timestamp}@example.com",
                "password": "client123",
                "confirm_password": "client123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            if response.status_code == 200:
                data = response.json()
                
                # Verify client role and messages (no role prefix for clients)
                role = data.get("role_info", {}).get("role")
                display_name = data.get("display_name", "").strip()
                welcome_message = data.get("welcome_message", "")
                
                if (role == "client" and 
                    display_name == "John" and  # No role prefix for clients
                    welcome_message == "Welcome John"):
                    
                    self.test_data['client_user'] = data
                    self.log_result("Client Signup", True, 
                                  f"Client signup successful. Role: {role}, Display: '{display_name}', Welcome: '{welcome_message}'")
                else:
                    self.log_result("Client Signup", False, 
                                  f"Client role/messages incorrect. Role: {role}, Display: '{display_name}', Welcome: '{welcome_message}'")
                    return False
            else:
                self.log_result("Client Signup", False, f"Client signup failed. HTTP {response.status_code}", response)
                return False
            
            # Test client login
            login_data = {
                "phone": client_phone,
                "password": "client123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                
                role = data.get("role_info", {}).get("role")
                display_name = data.get("display_name", "").strip()
                welcome_message = data.get("welcome_message", "")
                
                if (role == "client" and 
                    display_name == "John" and
                    welcome_message == "Welcome John"):
                    
                    self.log_result("Client Login", True, 
                                  f"Client login successful. Role: {role}, Display: '{display_name}', Welcome: '{welcome_message}'")
                    
                    # Test client permissions
                    permissions = data.get("role_info", {}).get("permissions", {})
                    client_permissions = ["can_create_jobs", "can_hire_fixers", "can_leave_reviews", "can_view_fixers"]
                    missing_permissions = [perm for perm in client_permissions if not permissions.get(perm, False)]
                    
                    # Check that client doesn't have restricted permissions
                    restricted_permissions = ["can_access_admin", "can_verify_fixers", "can_access_payments", "can_view_job_assignments"]
                    has_restricted_permissions = [perm for perm in restricted_permissions if permissions.get(perm, False)]
                    
                    if not missing_permissions and not has_restricted_permissions:
                        self.log_result("Client Permissions", True, f"Client permissions correctly assigned")
                        return True
                    else:
                        error_msg = ""
                        if missing_permissions:
                            error_msg += f"Missing client permissions: {missing_permissions}. "
                        if has_restricted_permissions:
                            error_msg += f"Incorrectly has restricted permissions: {has_restricted_permissions}"
                        self.log_result("Client Permissions", False, error_msg)
                        return False
                else:
                    self.log_result("Client Login", False, 
                                  f"Client role/messages incorrect. Role: {role}, Display: '{display_name}', Welcome: '{welcome_message}'")
                    return False
            else:
                self.log_result("Client Login", False, f"Client login failed. HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("Client Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_dashboard_access(self):
        """Test dashboard access for different roles"""
        try:
            success_count = 0
            total_tests = 0
            
            # Test admin dashboard
            if 'admin_user' in self.test_data:
                total_tests += 1
                admin_user_id = self.test_data['admin_user']['user']['id']
                response = self.session.get(f"{API_BASE}/dashboard/{admin_user_id}")
                if response.status_code == 200:
                    data = response.json()
                    if all(key in data for key in ['user', 'recent_jobs', 'top_fixers', 'stats']):
                        self.log_result("Dashboard Access - Admin", True, "Admin dashboard access successful")
                        success_count += 1
                    else:
                        self.log_result("Dashboard Access - Admin", False, "Admin dashboard missing sections")
                else:
                    self.log_result("Dashboard Access - Admin", False, f"Admin dashboard failed. HTTP {response.status_code}", response)
            
            # Test fixer dashboard
            if 'fixer_user' in self.test_data:
                total_tests += 1
                fixer_user_id = self.test_data['fixer_user']['user']['id']
                response = self.session.get(f"{API_BASE}/dashboard/{fixer_user_id}")
                if response.status_code == 200:
                    data = response.json()
                    if all(key in data for key in ['user', 'recent_jobs', 'top_fixers', 'stats']):
                        self.log_result("Dashboard Access - Fixer", True, "Fixer dashboard access successful")
                        success_count += 1
                    else:
                        self.log_result("Dashboard Access - Fixer", False, "Fixer dashboard missing sections")
                else:
                    self.log_result("Dashboard Access - Fixer", False, f"Fixer dashboard failed. HTTP {response.status_code}", response)
            
            # Test client dashboard
            if 'client_user' in self.test_data:
                total_tests += 1
                client_user_id = self.test_data['client_user']['user']['id']
                response = self.session.get(f"{API_BASE}/dashboard/{client_user_id}")
                if response.status_code == 200:
                    data = response.json()
                    if all(key in data for key in ['user', 'recent_jobs', 'top_fixers', 'stats']):
                        self.log_result("Dashboard Access - Client", True, "Client dashboard access successful")
                        success_count += 1
                    else:
                        self.log_result("Dashboard Access - Client", False, "Client dashboard missing sections")
                else:
                    self.log_result("Dashboard Access - Client", False, f"Client dashboard failed. HTTP {response.status_code}", response)
            
            return success_count == total_tests and total_tests > 0
            
        except Exception as e:
            self.log_result("Dashboard Access", False, f"Exception: {str(e)}")
            return False
    
    def test_database_connectivity(self):
        """Test PostgreSQL database connectivity"""
        try:
            # Test health check
            response = self.session.get(f"{API_BASE}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_result("Database Connectivity - Health Check", True, f"API health check passed: {data['message']}")
                else:
                    self.log_result("Database Connectivity - Health Check", False, "Invalid health check response")
                    return False
            else:
                self.log_result("Database Connectivity - Health Check", False, f"Health check failed. HTTP {response.status_code}", response)
                return False
            
            # Test user retrieval (database read)
            response = self.session.get(f"{API_BASE}/users")
            if response.status_code == 200:
                users = response.json()
                if isinstance(users, list):
                    self.log_result("Database Connectivity - User Retrieval", True, f"Successfully retrieved {len(users)} users from database")
                else:
                    self.log_result("Database Connectivity - User Retrieval", False, "Invalid users response format")
                    return False
            else:
                self.log_result("Database Connectivity - User Retrieval", False, f"User retrieval failed. HTTP {response.status_code}", response)
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Database Connectivity", False, f"Exception: {str(e)}")
            return False
    
    def run_authentication_tests(self):
        """Run all authentication tests"""
        print("=" * 80)
        print("FIXMATE-SA HEROKU DEPLOYMENT AUTHENTICATION FLOW TESTING")
        print("=" * 80)
        print()
        
        print("🔗 DATABASE CONNECTIVITY TEST")
        print("-" * 50)
        self.test_database_connectivity()
        print()
        
        print("🔐 CRITICAL AUTHENTICATION FLOW TESTS")
        print("-" * 50)
        self.test_admin_authentication()
        self.test_fixer_authentication()
        self.test_client_authentication()
        print()
        
        print("📊 DASHBOARD ACCESS TESTS")
        print("-" * 50)
        self.test_dashboard_access()
        print()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Total: {self.results['passed'] + self.results['failed']}")
        print()
        
        if self.results['failed'] > 0:
            print("🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
            print()
            print("⚠️  Some tests failed. Please check the errors above.")
        else:
            print("🎉 ALL TESTS PASSED! Authentication flow working correctly for all user roles.")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = AuthenticationTester()
    success = tester.run_authentication_tests()
    sys.exit(0 if success else 1)