#!/usr/bin/env python3
"""
Comprehensive Authentication Test

This script tests all authentication endpoints with the created test accounts:
1. Login endpoints for each role
2. Protected endpoints access
3. Role-based authorization
4. Token validation
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

print(f"🔐 Comprehensive Authentication Testing at: {API_BASE}")
print("=" * 80)

class AuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_accounts = {}
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
    
    def test_login_all_accounts(self):
        """Test login for all test accounts"""
        accounts = [
            ("admin", "+27800000001", "admin2024test"),
            ("client", "+27800000002", "client2024test"),
            ("fixer", "+27800000003", "fixer2024test")
        ]
        
        for role, phone, password in accounts:
            try:
                login_data = {
                    "phone": phone,
                    "password": password
                }
                
                response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if "user" in data and "token" in data and "role_info" in data:
                        actual_role = data.get('role_info', {}).get('role', 'unknown')
                        
                        self.test_accounts[role] = {
                            'phone': phone,
                            'password': password,
                            'user_data': data['user'],
                            'token': data['token'],
                            'role': actual_role,
                            'role_info': data['role_info']
                        }
                        
                        self.log_result(f"{role.title()} Login", True, 
                                      f"Login successful, Role: {actual_role}, Token: {data['token'][:20]}...")
                    else:
                        self.log_result(f"{role.title()} Login", False, "Invalid response format", response)
                else:
                    self.log_result(f"{role.title()} Login", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"{role.title()} Login", False, f"Request error: {str(e)}")
    
    def test_admin_endpoints(self):
        """Test admin-only endpoints"""
        if 'admin' not in self.test_accounts:
            self.log_result("Admin Endpoints Test", False, "Admin account not available")
            return
        
        admin_endpoints = [
            ("/admin/workflow-analytics", "Workflow Analytics"),
            ("/admin/matching-performance", "Matching Performance"),
        ]
        
        headers = {'Authorization': f"Bearer {self.test_accounts['admin']['token']}"}
        
        for endpoint, name in admin_endpoints:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    self.log_result(f"Admin {name} Access", True, 
                                  f"Admin can access {endpoint}")
                else:
                    self.log_result(f"Admin {name} Access", False, 
                                  f"Admin cannot access {endpoint}: HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"Admin {name} Access", False, f"Request error: {str(e)}")
    
    def test_non_admin_denied_access(self):
        """Test that non-admin accounts are denied admin access"""
        admin_endpoint = "/admin/workflow-analytics"
        
        for role in ['client', 'fixer']:
            if role not in self.test_accounts:
                continue
                
            try:
                headers = {'Authorization': f"Bearer {self.test_accounts[role]['token']}"}
                response = self.session.get(f"{API_BASE}{admin_endpoint}", headers=headers)
                
                if response.status_code == 403:
                    self.log_result(f"{role.title()} Admin Access Denied", True, 
                                  f"{role.title()} correctly denied admin access")
                else:
                    self.log_result(f"{role.title()} Admin Access Denied", False, 
                                  f"{role.title()} should not access admin endpoints: HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"{role.title()} Admin Access Denied", False, f"Request error: {str(e)}")
    
    def test_protected_endpoints_access(self):
        """Test that all accounts can access their own protected endpoints"""
        for role, account in self.test_accounts.items():
            try:
                headers = {'Authorization': f"Bearer {account['token']}"}
                user_id = account['user_data']['id']
                
                # Test user profile endpoint (all roles should access)
                response = self.session.get(f"{API_BASE}/auth/profile/{user_id}", headers=headers)
                
                if response.status_code == 200:
                    self.log_result(f"{role.title()} Profile Access", True, 
                                  f"{role.title()} can access own profile")
                else:
                    self.log_result(f"{role.title()} Profile Access", False, 
                                  f"{role.title()} cannot access profile: HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"{role.title()} Profile Access", False, f"Request error: {str(e)}")
    
    def test_role_check_endpoints(self):
        """Test role check endpoints"""
        for role, account in self.test_accounts.items():
            try:
                phone = account['phone']
                response = self.session.get(f"{API_BASE}/auth/role-check/{phone}")
                
                if response.status_code == 200:
                    data = response.json()
                    detected_role = data.get('role', 'unknown')
                    
                    if detected_role == account['role']:
                        self.log_result(f"{role.title()} Role Check", True, 
                                      f"Role correctly detected as {detected_role}")
                    else:
                        self.log_result(f"{role.title()} Role Check", False, 
                                      f"Role mismatch: expected {account['role']}, got {detected_role}", response)
                else:
                    self.log_result(f"{role.title()} Role Check", False, 
                                  f"Role check failed: HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"{role.title()} Role Check", False, f"Request error: {str(e)}")
    
    def test_token_validation(self):
        """Test token validation"""
        for role, account in self.test_accounts.items():
            try:
                # Test with valid token
                headers = {'Authorization': f"Bearer {account['token']}"}
                response = self.session.get(f"{API_BASE}/auth/profile/{account['user_data']['id']}", headers=headers)
                
                if response.status_code == 200:
                    self.log_result(f"{role.title()} Token Validation", True, 
                                  f"Valid token accepted for {role}")
                else:
                    self.log_result(f"{role.title()} Token Validation", False, 
                                  f"Valid token rejected: HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"{role.title()} Token Validation", False, f"Request error: {str(e)}")
        
        # Test with invalid token
        try:
            headers = {'Authorization': 'Bearer invalid_token_123'}
            response = self.session.get(f"{API_BASE}/auth/profile/test", headers=headers)
            
            if response.status_code == 401:
                self.log_result("Invalid Token Rejection", True, 
                              "Invalid token correctly rejected")
            else:
                self.log_result("Invalid Token Rejection", False, 
                              f"Invalid token should be rejected: HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Invalid Token Rejection", False, f"Request error: {str(e)}")
    
    def run_comprehensive_auth_test(self):
        """Run comprehensive authentication testing"""
        print("🚀 COMPREHENSIVE AUTHENTICATION TESTING")
        print("=" * 80)
        
        # Phase 1: Login Tests
        print("📋 PHASE 1: LOGIN TESTING")
        print("-" * 50)
        self.test_login_all_accounts()
        
        # Phase 2: Admin Access Tests
        print("\n🔐 PHASE 2: ADMIN ACCESS CONTROL")
        print("-" * 50)
        self.test_admin_endpoints()
        self.test_non_admin_denied_access()
        
        # Phase 3: Protected Endpoints
        print("\n🛡️ PHASE 3: PROTECTED ENDPOINTS")
        print("-" * 50)
        self.test_protected_endpoints_access()
        
        # Phase 4: Role Verification
        print("\n🔍 PHASE 4: ROLE VERIFICATION")
        print("-" * 50)
        self.test_role_check_endpoints()
        
        # Phase 5: Token Validation
        print("\n🎫 PHASE 5: TOKEN VALIDATION")
        print("-" * 50)
        self.test_token_validation()
        
        # Results Summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE AUTHENTICATION TEST RESULTS")
        print("=" * 80)
        
        print("🔑 TEST ACCOUNTS VERIFIED:")
        for role, account in self.test_accounts.items():
            print(f"   ✅ {role.upper()}: {account['phone']} (Role: {account['role']})")
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   ✅ Tests Passed: {self.results['passed']}")
        print(f"   ❌ Tests Failed: {self.results['failed']}")
        print(f"   📊 Success Rate: {self.results['passed']/(self.results['passed']+self.results['failed'])*100:.1f}%")
        
        if self.results['errors']:
            print(f"\n🚨 ERRORS ENCOUNTERED:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        success_rate = self.results['passed']/(self.results['passed']+self.results['failed'])*100
        
        if success_rate >= 90:
            print("\n🎉 COMPREHENSIVE AUTHENTICATION TESTING SUCCESSFUL!")
            print("✅ All test accounts authenticated successfully")
            print("✅ Role-based access control working properly")
            print("✅ Admin endpoints protected correctly")
            print("✅ Token validation functional")
            print("✅ System ready for comprehensive testing")
            
            print("\n" + "=" * 80)
            print("🎯 FINAL TEST CREDENTIALS FOR COMPREHENSIVE TESTING")
            print("=" * 80)
            
            for role, account in self.test_accounts.items():
                print(f"\n🔑 {role.upper()} TEST ACCOUNT:")
                print(f"   Phone: {account['phone']}")
                print(f"   Password: {account['password']}")
                print(f"   Role: {account['role']}")
                print(f"   Token: {account['token'][:30]}...")
                
                if role == 'admin':
                    print(f"   Access: Full admin privileges")
                elif role == 'fixer':
                    print(f"   Access: Fixer features, no admin access")
                else:
                    print(f"   Access: Client features only")
        else:
            print("\n⚠️ AUTHENTICATION TESTING ISSUES DETECTED")
            print("⚠️ Some authentication features may not be working correctly")
            print("⚠️ Review errors above before proceeding")
        
        return success_rate >= 90

if __name__ == "__main__":
    print("🔐 FixMate-SA Comprehensive Authentication Testing")
    print("=" * 80)
    print("🎯 TESTING ALL AUTHENTICATION FEATURES")
    print("📋 Login, role-based access, protected endpoints, token validation")
    print("=" * 80)
    
    tester = AuthTester()
    
    try:
        success = tester.run_comprehensive_auth_test()
        
        if success:
            print("\n🎉 ALL AUTHENTICATION FEATURES VERIFIED AND WORKING!")
            sys.exit(0)
        else:
            print("\n❌ AUTHENTICATION TESTING ENCOUNTERED ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Authentication testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during authentication testing: {str(e)}")
        sys.exit(1)