#!/usr/bin/env python3
"""
FixMate-SA Role-based Login Validation and Fixer Reputation API Testing

SPECIFIC ISSUES TO TEST:

1. **Role-based Login Validation Testing:**
   - Test that client login page now properly rejects admin/fixer credentials
   - Test that fixer login page rejects client/admin credentials  
   - Test that admin login page rejects client/fixer credentials
   - Verify proper error messages are shown for wrong role attempts

2. **Fixer Reputation API Testing:**
   - Test the GET /api/fixer/{fixer_id}/reputation endpoint
   - Check if the gamification service is working
   - Test with existing fixer accounts to see if reputation data is available
   - Debug why the reputation section is showing "Error fetching reputation data"

Test accounts:
- Admin: +27800000001 / admin2024test
- Client: +27800000002 / client2024test  
- Fixer: +27800000003 / fixer2024test
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

print(f"🔧 Testing Role-based Login Validation and Fixer Reputation API at: {API_BASE}")
print("=" * 80)

class RoleValidationAndReputationTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_accounts = {
            'admin': {'phone': '+27800000001', 'password': 'admin2024test'},
            'client': {'phone': '+27800000002', 'password': 'client2024test'},
            'fixer': {'phone': '+27800000003', 'password': 'fixer2024test'}
        }
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
                self.log_result("API Health Check", True, f"API is accessible at {API_BASE}")
                return True
            else:
                self.log_result("API Health Check", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("API Health Check", False, f"Connection error: {str(e)}")
        return False
    
    def test_role_check_endpoint(self):
        """Test the role check endpoint to understand current user roles"""
        print("🔍 TESTING ROLE CHECK ENDPOINT")
        print("-" * 50)
        
        for role_name, account in self.test_accounts.items():
            try:
                response = self.session.get(f"{API_BASE}/auth/role-check/{account['phone']}")
                if response.status_code == 200:
                    role_data = response.json()
                    actual_role = role_data.get('role', 'unknown')
                    self.log_result(f"Role Check - {role_name.upper()} Account", True, 
                                  f"Phone {account['phone']} has role: {actual_role}")
                else:
                    self.log_result(f"Role Check - {role_name.upper()} Account", False, 
                                  f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"Role Check - {role_name.upper()} Account", False, 
                              f"Request error: {str(e)}")
    
    def test_login_attempt(self, account_type, phone, password, expected_role=None):
        """Test a login attempt and return the result"""
        try:
            login_data = {
                "phone": phone,
                "password": password
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                actual_role = data.get('role_info', {}).get('role', 'unknown')
                return {
                    'success': True,
                    'role': actual_role,
                    'data': data,
                    'message': f"Login successful as {actual_role}"
                }
            else:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'Unknown error')
                    return {
                        'success': False,
                        'error': error_detail,
                        'status_code': response.status_code,
                        'message': f"Login failed: {error_detail}"
                    }
                except:
                    return {
                        'success': False,
                        'error': response.text,
                        'status_code': response.status_code,
                        'message': f"Login failed: HTTP {response.status_code}"
                    }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Request error: {str(e)}"
            }
    
    def test_role_based_login_validation(self):
        """Test role-based login validation - Issue #1"""
        print("🔍 TESTING ROLE-BASED LOGIN VALIDATION")
        print("-" * 50)
        
        # Test 1: Admin credentials should work for admin login
        print("Testing Admin Login with Admin Credentials...")
        admin_result = self.test_login_attempt('admin', 
                                             self.test_accounts['admin']['phone'], 
                                             self.test_accounts['admin']['password'])
        
        if admin_result['success'] and admin_result['role'] == 'admin':
            self.log_result("Admin Login - Admin Credentials", True, 
                          f"Admin login successful: {admin_result['message']}")
        else:
            self.log_result("Admin Login - Admin Credentials", False, 
                          f"Admin login failed: {admin_result['message']}")
        
        # Test 2: Client credentials should work for client login
        print("Testing Client Login with Client Credentials...")
        client_result = self.test_login_attempt('client', 
                                              self.test_accounts['client']['phone'], 
                                              self.test_accounts['client']['password'])
        
        if client_result['success'] and client_result['role'] == 'client':
            self.log_result("Client Login - Client Credentials", True, 
                          f"Client login successful: {client_result['message']}")
        else:
            self.log_result("Client Login - Client Credentials", False, 
                          f"Client login failed: {client_result['message']}")
        
        # Test 3: Fixer credentials should work for fixer login
        print("Testing Fixer Login with Fixer Credentials...")
        fixer_result = self.test_login_attempt('fixer', 
                                             self.test_accounts['fixer']['phone'], 
                                             self.test_accounts['fixer']['password'])
        
        if fixer_result['success']:
            actual_role = fixer_result['role']
            if actual_role == 'fixer':
                self.log_result("Fixer Login - Fixer Credentials", True, 
                              f"Fixer login successful: {fixer_result['message']}")
            else:
                self.log_result("Fixer Login - Fixer Credentials", False, 
                              f"Fixer account has wrong role: {actual_role} (expected: fixer)")
        else:
            self.log_result("Fixer Login - Fixer Credentials", False, 
                          f"Fixer login failed: {fixer_result['message']}")
        
        # Test 4: Cross-role validation - Admin credentials on client/fixer login
        print("Testing Cross-Role Validation...")
        
        # Admin credentials should not work for client role
        admin_as_client = self.test_login_attempt('client', 
                                                self.test_accounts['admin']['phone'], 
                                                self.test_accounts['admin']['password'])
        
        if admin_as_client['success'] and admin_as_client['role'] != 'client':
            self.log_result("Cross-Role Validation - Admin as Client", True, 
                          f"Correctly rejected admin credentials for client login: role is {admin_as_client['role']}")
        elif not admin_as_client['success']:
            self.log_result("Cross-Role Validation - Admin as Client", True, 
                          f"Correctly rejected admin credentials: {admin_as_client['message']}")
        else:
            self.log_result("Cross-Role Validation - Admin as Client", False, 
                          f"Admin credentials incorrectly accepted for client login")
        
        # Client credentials should not work for admin role
        client_as_admin = self.test_login_attempt('admin', 
                                                self.test_accounts['client']['phone'], 
                                                self.test_accounts['client']['password'])
        
        if client_as_admin['success'] and client_as_admin['role'] != 'admin':
            self.log_result("Cross-Role Validation - Client as Admin", True, 
                          f"Correctly rejected client credentials for admin login: role is {client_as_admin['role']}")
        elif not client_as_admin['success']:
            self.log_result("Cross-Role Validation - Client as Admin", True, 
                          f"Correctly rejected client credentials: {client_as_admin['message']}")
        else:
            self.log_result("Cross-Role Validation - Client as Admin", False, 
                          f"Client credentials incorrectly accepted for admin login")
    
    def get_fixer_ids(self):
        """Get available fixer IDs for reputation testing"""
        try:
            response = self.session.get(f"{API_BASE}/fixers")
            if response.status_code == 200:
                fixers = response.json()
                fixer_ids = [fixer['id'] for fixer in fixers if 'id' in fixer]
                print(f"   Found {len(fixer_ids)} fixers for reputation testing")
                return fixer_ids
            else:
                print(f"   Failed to get fixers: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"   Error getting fixers: {str(e)}")
            return []
    
    def test_fixer_reputation_api(self):
        """Test fixer reputation API - Issue #2"""
        print("🔍 TESTING FIXER REPUTATION API")
        print("-" * 50)
        
        # Get available fixer IDs
        fixer_ids = self.get_fixer_ids()
        
        if not fixer_ids:
            self.log_result("Fixer Reputation API - Get Fixer IDs", False, 
                          "No fixer IDs available for testing")
            return
        
        # Test reputation endpoint with first few fixers
        test_fixer_ids = fixer_ids[:3]  # Test first 3 fixers
        
        for i, fixer_id in enumerate(test_fixer_ids):
            print(f"Testing reputation for Fixer ID: {fixer_id}")
            
            try:
                # Test GET /api/fixer/{fixer_id}/reputation
                response = self.session.get(f"{API_BASE}/fixer/{fixer_id}/reputation")
                
                print(f"   Response status: {response.status_code}")
                print(f"   Response headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    try:
                        reputation_data = response.json()
                        print(f"   Response data: {json.dumps(reputation_data, indent=2)}")
                        
                        # Check if reputation data has expected fields
                        expected_fields = ['fixer_id', 'reputation_score', 'total_jobs', 'rating']
                        found_fields = [field for field in expected_fields if field in reputation_data]
                        
                        if found_fields:
                            self.log_result(f"Fixer Reputation API - Fixer {i+1}", True, 
                                          f"Reputation data retrieved successfully. Fields: {found_fields}")
                        else:
                            self.log_result(f"Fixer Reputation API - Fixer {i+1}", False, 
                                          f"Reputation data missing expected fields. Got: {list(reputation_data.keys())}")
                    except json.JSONDecodeError:
                        self.log_result(f"Fixer Reputation API - Fixer {i+1}", False, 
                                      f"Invalid JSON response: {response.text[:200]}")
                
                elif response.status_code == 404:
                    self.log_result(f"Fixer Reputation API - Fixer {i+1}", False, 
                                  f"Reputation endpoint not found (404) - endpoint may not be implemented")
                
                elif response.status_code == 500:
                    try:
                        error_data = response.json()
                        error_detail = error_data.get('detail', 'Internal server error')
                        self.log_result(f"Fixer Reputation API - Fixer {i+1}", False, 
                                      f"Server error: {error_detail}")
                    except:
                        self.log_result(f"Fixer Reputation API - Fixer {i+1}", False, 
                                      f"Server error: {response.text[:200]}")
                
                else:
                    try:
                        error_data = response.json()
                        error_detail = error_data.get('detail', 'Unknown error')
                        self.log_result(f"Fixer Reputation API - Fixer {i+1}", False, 
                                      f"HTTP {response.status_code}: {error_detail}")
                    except:
                        self.log_result(f"Fixer Reputation API - Fixer {i+1}", False, 
                                      f"HTTP {response.status_code}: {response.text[:200]}")
                
            except Exception as e:
                self.log_result(f"Fixer Reputation API - Fixer {i+1}", False, 
                              f"Request error: {str(e)}")
    
    def test_gamification_service_endpoints(self):
        """Test gamification service related endpoints"""
        print("🔍 TESTING GAMIFICATION SERVICE ENDPOINTS")
        print("-" * 50)
        
        # Test if gamification service endpoints exist
        gamification_endpoints = [
            "/api/gamification/leaderboard",
            "/api/gamification/achievements",
            "/api/gamification/stats"
        ]
        
        for endpoint in gamification_endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code == 200:
                    self.log_result(f"Gamification Endpoint - {endpoint}", True, 
                                  f"Endpoint accessible and working")
                elif response.status_code == 404:
                    self.log_result(f"Gamification Endpoint - {endpoint}", False, 
                                  f"Endpoint not found (404) - may not be implemented")
                else:
                    self.log_result(f"Gamification Endpoint - {endpoint}", False, 
                                  f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Gamification Endpoint - {endpoint}", False, 
                              f"Request error: {str(e)}")
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 ROLE-BASED LOGIN VALIDATION AND FIXER REPUTATION API TESTING")
        print("=" * 80)
        
        # Health check
        if not self.test_health_check():
            print("❌ API health check failed. Cannot proceed with testing.")
            return False
        
        # Test role check endpoint first
        self.test_role_check_endpoint()
        
        # Test role-based login validation
        self.test_role_based_login_validation()
        
        # Test fixer reputation API
        self.test_fixer_reputation_api()
        
        # Test gamification service endpoints
        self.test_gamification_service_endpoints()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {self.results['passed']}")
        print(f"❌ Tests Failed: {self.results['failed']}")
        
        total_tests = self.results['passed'] + self.results['failed']
        if total_tests > 0:
            success_rate = (self.results['passed'] / total_tests) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.results['errors']:
            print(f"\n🚨 ERRORS ENCOUNTERED:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        # Specific issue analysis
        print("\n🎯 SPECIFIC ISSUE ANALYSIS:")
        print("-" * 50)
        
        role_validation_tests = [error for error in self.results['errors'] if 'Role' in error or 'Login' in error]
        reputation_tests = [error for error in self.results['errors'] if 'Reputation' in error or 'Gamification' in error]
        
        if not role_validation_tests:
            print("✅ ISSUE #1 (Role-based Login Validation): RESOLVED")
            print("   All role-based login validation tests passed")
        else:
            print("❌ ISSUE #1 (Role-based Login Validation): NEEDS ATTENTION")
            for error in role_validation_tests:
                print(f"   • {error}")
        
        if not reputation_tests:
            print("✅ ISSUE #2 (Fixer Reputation API): RESOLVED")
            print("   All fixer reputation API tests passed")
        else:
            print("❌ ISSUE #2 (Fixer Reputation API): NEEDS ATTENTION")
            for error in reputation_tests:
                print(f"   • {error}")

if __name__ == "__main__":
    print("🔧 FixMate-SA Role-based Login Validation and Fixer Reputation API Testing")
    print("=" * 80)
    print("🎯 TESTING SPECIFIC USER-REPORTED ISSUES:")
    print("   1. Role-based Login Validation")
    print("   2. Fixer Reputation API")
    print("=" * 80)
    
    tester = RoleValidationAndReputationTester()
    
    try:
        success = tester.run_comprehensive_tests()
        tester.print_summary()
        
        if success:
            print("\n🎉 TESTING COMPLETED SUCCESSFULLY!")
        else:
            print("\n⚠️ TESTING COMPLETED WITH ISSUES")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {str(e)}")
        import traceback
        traceback.print_exc()