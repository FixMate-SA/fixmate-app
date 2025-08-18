#!/usr/bin/env python3
"""
FixMate-SA Profile Management Security Testing
Testing SECURITY FIXES for enhanced profile management system authentication middleware
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
import io

# Configuration - Get from frontend .env
BACKEND_URL = "https://51889874-0b20-4a58-a006-376948278cd6.preview.emergentagent.com/api"

# Test user credentials (from review request)
CLIENT_CREDENTIALS = {
    "phone": "+27800000002",
    "password": "client2024test"
}

ADMIN_CREDENTIALS = {
    "phone": "+27800000001", 
    "password": "admin2024test"
}

class ProfileSecurityTester:
    def __init__(self):
        self.session = requests.Session()
        # Disable SSL verification for testing
        self.session.verify = False
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.test_results = []
        self.client_token = None
        self.client_user_id = None
        self.admin_token = None
        self.admin_user_id = None
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()
        
    def authenticate_client(self):
        """Authenticate client user and get token"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=CLIENT_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    self.client_token = data["token"]
                    self.client_user_id = data.get("user", {}).get("id")
                    
                    self.log_test(
                        "Client Authentication",
                        True,
                        f"Successfully authenticated client user",
                        {
                            "user_id": self.client_user_id,
                            "token_format": f"token_{self.client_user_id}" if self.client_user_id else "unknown",
                            "phone": data.get("user", {}).get("phone")
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Client Authentication",
                        False,
                        f"Authentication failed: {data.get('message', 'Unknown error')}"
                    )
                    return False
            else:
                self.log_test(
                    "Client Authentication",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Client Authentication",
                False,
                f"Authentication error: {str(e)}"
            )
            return False
    
    def authenticate_admin(self):
        """Authenticate admin user and get token"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    self.admin_token = data["token"]
                    self.admin_user_id = data.get("user", {}).get("id")
                    
                    self.log_test(
                        "Admin Authentication",
                        True,
                        f"Successfully authenticated admin user",
                        {
                            "user_id": self.admin_user_id,
                            "token_format": f"token_{self.admin_user_id}" if self.admin_user_id else "unknown",
                            "phone": data.get("user", {}).get("phone")
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Admin Authentication",
                        False,
                        f"Authentication failed: {data.get('message', 'Unknown error')}"
                    )
                    return False
            else:
                self.log_test(
                    "Admin Authentication",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Admin Authentication",
                False,
                f"Authentication error: {str(e)}"
            )
            return False
    
    def test_get_profile_authentication(self):
        """Test GET /api/profile/{user_id} requires authentication"""
        try:
            if not self.client_user_id:
                self.log_test(
                    "GET Profile Authentication Test",
                    False,
                    "Client not authenticated"
                )
                return False
            
            # Test 1: Access without authentication (should fail)
            response = self.session.get(f"{BACKEND_URL}/profile/{self.client_user_id}")
            
            no_auth_blocked = response.status_code in [401, 403, 422]
            
            # Test 2: Access with valid Bearer token (should succeed)
            headers = {"Authorization": f"Bearer {self.client_token}"}
            response = self.session.get(f"{BACKEND_URL}/profile/{self.client_user_id}", headers=headers)
            
            valid_auth_works = response.status_code == 200 and response.json().get("success")
            
            # Test 3: Access with invalid token (should fail)
            headers = {"Authorization": "Bearer invalid_token_12345"}
            response = self.session.get(f"{BACKEND_URL}/profile/{self.client_user_id}", headers=headers)
            
            invalid_token_blocked = response.status_code in [401, 403]
            
            # Test 4: Access with malformed token (should fail)
            headers = {"Authorization": "Bearer "}
            response = self.session.get(f"{BACKEND_URL}/profile/{self.client_user_id}", headers=headers)
            
            malformed_token_blocked = response.status_code in [401, 403]
            
            all_tests_pass = no_auth_blocked and valid_auth_works and invalid_token_blocked and malformed_token_blocked
            
            self.log_test(
                "GET Profile Authentication Test",
                all_tests_pass,
                f"Authentication tests: No auth {'✅ blocked' if no_auth_blocked else '❌ allowed'}, Valid token {'✅ works' if valid_auth_works else '❌ fails'}, Invalid token {'✅ blocked' if invalid_token_blocked else '❌ allowed'}, Malformed token {'✅ blocked' if malformed_token_blocked else '❌ allowed'}",
                {
                    "no_auth_blocked": no_auth_blocked,
                    "valid_auth_works": valid_auth_works,
                    "invalid_token_blocked": invalid_token_blocked,
                    "malformed_token_blocked": malformed_token_blocked
                }
            )
            return all_tests_pass
                
        except Exception as e:
            self.log_test(
                "GET Profile Authentication Test",
                False,
                f"Test error: {str(e)}"
            )
            return False
    
    def test_put_profile_authentication(self):
        """Test PUT /api/profile/{user_id} requires proper Bearer token"""
        try:
            if not self.client_user_id:
                self.log_test(
                    "PUT Profile Authentication Test",
                    False,
                    "Client not authenticated"
                )
                return False
            
            update_data = {"first_name": "SecurityTest"}
            
            # Test 1: Update without authentication (should fail)
            response = self.session.put(f"{BACKEND_URL}/profile/{self.client_user_id}", json=update_data)
            
            no_auth_blocked = response.status_code in [401, 403, 422]
            
            # Test 2: Update with valid Bearer token (should succeed)
            headers = {"Authorization": f"Bearer {self.client_token}"}
            response = self.session.put(f"{BACKEND_URL}/profile/{self.client_user_id}", json=update_data, headers=headers)
            
            valid_auth_works = response.status_code == 200 and response.json().get("success")
            
            # Test 3: Update with invalid token (should fail)
            headers = {"Authorization": "Bearer invalid_token_12345"}
            response = self.session.put(f"{BACKEND_URL}/profile/{self.client_user_id}", json=update_data, headers=headers)
            
            invalid_token_blocked = response.status_code in [401, 403]
            
            # Test 4: Update with missing Bearer prefix (should fail)
            headers = {"Authorization": self.client_token}
            response = self.session.put(f"{BACKEND_URL}/profile/{self.client_user_id}", json=update_data, headers=headers)
            
            missing_bearer_blocked = response.status_code in [401, 403]
            
            all_tests_pass = no_auth_blocked and valid_auth_works and invalid_token_blocked and missing_bearer_blocked
            
            self.log_test(
                "PUT Profile Authentication Test",
                all_tests_pass,
                f"Authentication tests: No auth {'✅ blocked' if no_auth_blocked else '❌ allowed'}, Valid token {'✅ works' if valid_auth_works else '❌ fails'}, Invalid token {'✅ blocked' if invalid_token_blocked else '❌ allowed'}, Missing Bearer {'✅ blocked' if missing_bearer_blocked else '❌ allowed'}",
                {
                    "no_auth_blocked": no_auth_blocked,
                    "valid_auth_works": valid_auth_works,
                    "invalid_token_blocked": invalid_token_blocked,
                    "missing_bearer_blocked": missing_bearer_blocked
                }
            )
            return all_tests_pass
                
        except Exception as e:
            self.log_test(
                "PUT Profile Authentication Test",
                False,
                f"Test error: {str(e)}"
            )
            return False
    
    def test_upload_image_authentication(self):
        """Test POST /api/profile/{user_id}/upload-image requires authentication"""
        try:
            if not self.client_user_id:
                self.log_test(
                    "Upload Image Authentication Test",
                    False,
                    "Client not authenticated"
                )
                return False
            
            # Create test image data
            test_image_data = b'\x89PNG\r\n\x1a\n\rIHDR\x01\x01\x08\x02\x90wS\xde\tpHYs\x0b\x13\x0b\x13\x01\x9a\x9c\x18\nIDATx\x9cc\xf8\x01\x01IEND\xaeB`\x82'
            files = {'image': ('test.png', io.BytesIO(test_image_data), 'image/png')}
            
            # Test 1: Upload without authentication (should fail)
            response = self.session.post(f"{BACKEND_URL}/profile/{self.client_user_id}/upload-image", files=files)
            
            no_auth_blocked = response.status_code in [401, 403, 422]
            
            # Test 2: Upload with valid Bearer token (should succeed)
            files = {'image': ('test.png', io.BytesIO(test_image_data), 'image/png')}
            headers = {"Authorization": f"Bearer {self.client_token}"}
            response = self.session.post(f"{BACKEND_URL}/profile/{self.client_user_id}/upload-image", files=files, headers=headers)
            
            valid_auth_works = response.status_code == 200 and response.json().get("success")
            
            # Test 3: Upload with invalid token (should fail)
            files = {'image': ('test.png', io.BytesIO(test_image_data), 'image/png')}
            headers = {"Authorization": "Bearer invalid_token_12345"}
            response = self.session.post(f"{BACKEND_URL}/profile/{self.client_user_id}/upload-image", files=files, headers=headers)
            
            invalid_token_blocked = response.status_code in [401, 403]
            
            all_tests_pass = no_auth_blocked and valid_auth_works and invalid_token_blocked
            
            self.log_test(
                "Upload Image Authentication Test",
                all_tests_pass,
                f"Authentication tests: No auth {'✅ blocked' if no_auth_blocked else '❌ allowed'}, Valid token {'✅ works' if valid_auth_works else '❌ fails'}, Invalid token {'✅ blocked' if invalid_token_blocked else '❌ allowed'}",
                {
                    "no_auth_blocked": no_auth_blocked,
                    "valid_auth_works": valid_auth_works,
                    "invalid_token_blocked": invalid_token_blocked
                }
            )
            return all_tests_pass
                
        except Exception as e:
            self.log_test(
                "Upload Image Authentication Test",
                False,
                f"Test error: {str(e)}"
            )
            return False
    
    def test_cross_user_access_prevention(self):
        """Test that users cannot access other users' profiles"""
        try:
            if not self.client_user_id or not self.admin_user_id:
                self.log_test(
                    "Cross-User Access Prevention Test",
                    False,
                    "Both client and admin users must be authenticated"
                )
                return False
            
            # Test 1: Client trying to access admin profile (should fail)
            headers = {"Authorization": f"Bearer {self.client_token}"}
            response = self.session.get(f"{BACKEND_URL}/profile/{self.admin_user_id}", headers=headers)
            
            client_blocked_from_admin = response.status_code in [401, 403]
            
            # Test 2: Admin trying to access client profile (should fail)
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/profile/{self.client_user_id}", headers=headers)
            
            admin_blocked_from_client = response.status_code in [401, 403]
            
            # Test 3: Client can access own profile (should succeed)
            headers = {"Authorization": f"Bearer {self.client_token}"}
            response = self.session.get(f"{BACKEND_URL}/profile/{self.client_user_id}", headers=headers)
            
            client_can_access_own = response.status_code == 200 and response.json().get("success")
            
            # Test 4: Admin can access own profile (should succeed)
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/profile/{self.admin_user_id}", headers=headers)
            
            admin_can_access_own = response.status_code == 200 and response.json().get("success")
            
            all_tests_pass = client_blocked_from_admin and admin_blocked_from_client and client_can_access_own and admin_can_access_own
            
            self.log_test(
                "Cross-User Access Prevention Test",
                all_tests_pass,
                f"Access control: Client→Admin {'✅ blocked' if client_blocked_from_admin else '❌ allowed'}, Admin→Client {'✅ blocked' if admin_blocked_from_client else '❌ allowed'}, Client→Own {'✅ works' if client_can_access_own else '❌ fails'}, Admin→Own {'✅ works' if admin_can_access_own else '❌ fails'}",
                {
                    "client_blocked_from_admin": client_blocked_from_admin,
                    "admin_blocked_from_client": admin_blocked_from_client,
                    "client_can_access_own": client_can_access_own,
                    "admin_can_access_own": admin_can_access_own
                }
            )
            return all_tests_pass
                
        except Exception as e:
            self.log_test(
                "Cross-User Access Prevention Test",
                False,
                f"Test error: {str(e)}"
            )
            return False
    
    def test_token_validation(self):
        """Test that tokens are properly validated"""
        try:
            if not self.client_user_id:
                self.log_test(
                    "Token Validation Test",
                    False,
                    "Client not authenticated"
                )
                return False
            
            # Test 1: Valid token format (token_{user_id})
            headers = {"Authorization": f"Bearer {self.client_token}"}
            response = self.session.get(f"{BACKEND_URL}/profile/{self.client_user_id}", headers=headers)
            
            valid_token_works = response.status_code == 200
            
            # Test 2: Invalid token format (not starting with token_)
            headers = {"Authorization": "Bearer invalid_format_12345"}
            response = self.session.get(f"{BACKEND_URL}/profile/{self.client_user_id}", headers=headers)
            
            invalid_format_blocked = response.status_code in [401, 403]
            
            # Test 3: Token for non-existent user
            headers = {"Authorization": "Bearer token_nonexistent_user_id"}
            response = self.session.get(f"{BACKEND_URL}/profile/{self.client_user_id}", headers=headers)
            
            nonexistent_user_blocked = response.status_code in [401, 403]
            
            # Test 4: Empty token
            headers = {"Authorization": "Bearer "}
            response = self.session.get(f"{BACKEND_URL}/profile/{self.client_user_id}", headers=headers)
            
            empty_token_blocked = response.status_code in [401, 403]
            
            all_tests_pass = valid_token_works and invalid_format_blocked and nonexistent_user_blocked and empty_token_blocked
            
            self.log_test(
                "Token Validation Test",
                all_tests_pass,
                f"Token validation: Valid token {'✅ works' if valid_token_works else '❌ fails'}, Invalid format {'✅ blocked' if invalid_format_blocked else '❌ allowed'}, Nonexistent user {'✅ blocked' if nonexistent_user_blocked else '❌ allowed'}, Empty token {'✅ blocked' if empty_token_blocked else '❌ allowed'}",
                {
                    "valid_token_works": valid_token_works,
                    "invalid_format_blocked": invalid_format_blocked,
                    "nonexistent_user_blocked": nonexistent_user_blocked,
                    "empty_token_blocked": empty_token_blocked
                }
            )
            return all_tests_pass
                
        except Exception as e:
            self.log_test(
                "Token Validation Test",
                False,
                f"Test error: {str(e)}"
            )
            return False
    
    def test_profile_update_security(self):
        """Test profile update security with authentication"""
        try:
            if not self.client_user_id:
                self.log_test(
                    "Profile Update Security Test",
                    False,
                    "Client not authenticated"
                )
                return False
            
            update_data = {
                "first_name": "SecurityTestUpdate",
                "last_name": "ClientUser",
                "email": "security.test@fixmate-sa.com"
            }
            
            # Test 1: Update with valid authentication (should succeed)
            headers = {"Authorization": f"Bearer {self.client_token}"}
            response = self.session.put(f"{BACKEND_URL}/profile/{self.client_user_id}", json=update_data, headers=headers)
            
            valid_update_works = response.status_code == 200 and response.json().get("success")
            
            # Test 2: Update without authentication (should fail)
            response = self.session.put(f"{BACKEND_URL}/profile/{self.client_user_id}", json=update_data)
            
            no_auth_update_blocked = response.status_code in [401, 403, 422]
            
            # Test 3: Update with wrong user's token (should fail if admin user exists)
            if self.admin_token and self.admin_user_id:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = self.session.put(f"{BACKEND_URL}/profile/{self.client_user_id}", json=update_data, headers=headers)
                
                wrong_user_blocked = response.status_code in [401, 403]
            else:
                wrong_user_blocked = True  # Skip this test if admin not available
            
            all_tests_pass = valid_update_works and no_auth_update_blocked and wrong_user_blocked
            
            self.log_test(
                "Profile Update Security Test",
                all_tests_pass,
                f"Update security: Valid auth {'✅ works' if valid_update_works else '❌ fails'}, No auth {'✅ blocked' if no_auth_update_blocked else '❌ allowed'}, Wrong user {'✅ blocked' if wrong_user_blocked else '❌ allowed'}",
                {
                    "valid_update_works": valid_update_works,
                    "no_auth_update_blocked": no_auth_update_blocked,
                    "wrong_user_blocked": wrong_user_blocked
                }
            )
            return all_tests_pass
                
        except Exception as e:
            self.log_test(
                "Profile Update Security Test",
                False,
                f"Test error: {str(e)}"
            )
            return False
    
    def run_security_tests(self):
        """Run all security tests for profile management"""
        print("🔒 PROFILE MANAGEMENT SECURITY TESTING")
        print("Testing SECURITY FIXES for enhanced profile management system")
        print("=" * 70)
        print()
        
        # Step 1: Authentication
        print("🔑 STEP 1: User Authentication")
        print("-" * 30)
        client_auth = self.authenticate_client()
        admin_auth = self.authenticate_admin()
        print()
        
        if not client_auth:
            print("❌ Cannot proceed without client authentication")
            return
        
        # Step 2: GET Profile Authentication Tests
        print("🔍 STEP 2: GET Profile Authentication Security")
        print("-" * 45)
        self.test_get_profile_authentication()
        print()
        
        # Step 3: PUT Profile Authentication Tests
        print("✏️ STEP 3: PUT Profile Authentication Security")
        print("-" * 45)
        self.test_put_profile_authentication()
        print()
        
        # Step 4: Image Upload Authentication Tests
        print("📷 STEP 4: Image Upload Authentication Security")
        print("-" * 45)
        self.test_upload_image_authentication()
        print()
        
        # Step 5: Cross-User Access Prevention
        print("🛡️ STEP 5: Cross-User Access Prevention")
        print("-" * 40)
        if admin_auth:
            self.test_cross_user_access_prevention()
        else:
            print("⚠️ Skipping cross-user test - admin authentication failed")
        print()
        
        # Step 6: Token Validation
        print("🎫 STEP 6: Token Validation Security")
        print("-" * 35)
        self.test_token_validation()
        print()
        
        # Step 7: Profile Update Security
        print("🔐 STEP 7: Profile Update Security")
        print("-" * 35)
        self.test_profile_update_security()
        print()
        
        # Generate summary
        self.generate_security_summary()
    
    def generate_security_summary(self):
        """Generate security test summary"""
        print("📊 SECURITY TEST SUMMARY")
        print("=" * 30)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Security Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Security Score: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ SECURITY ISSUES DETECTED:")
            print("-" * 30)
            for test in self.test_results:
                if not test["success"]:
                    print(f"• {test['test']}: {test['message']}")
            print()
        
        print("🔒 SECURITY REQUIREMENTS VERIFICATION:")
        print("-" * 40)
        
        # Check specific security requirements from review request
        auth_tests = [t for t in self.test_results if "Authentication Test" in t["test"]]
        cross_user_tests = [t for t in self.test_results if "Cross-User Access" in t["test"]]
        token_tests = [t for t in self.test_results if "Token Validation" in t["test"]]
        
        print(f"• GET /api/profile/{{user_id}} requires authentication: {'✅ SECURED' if any(t['success'] for t in auth_tests if 'GET' in t['test']) else '❌ VULNERABLE'}")
        print(f"• PUT /api/profile/{{user_id}} requires Bearer token: {'✅ SECURED' if any(t['success'] for t in auth_tests if 'PUT' in t['test']) else '❌ VULNERABLE'}")
        print(f"• POST /api/profile/{{user_id}}/upload-image requires auth: {'✅ SECURED' if any(t['success'] for t in auth_tests if 'Upload' in t['test']) else '❌ VULNERABLE'}")
        print(f"• Cross-user access prevention: {'✅ WORKING' if any(t['success'] for t in cross_user_tests) else '❌ FAILING'}")
        print(f"• Bearer token format validation: {'✅ WORKING' if any(t['success'] for t in token_tests) else '❌ FAILING'}")
        print(f"• User ownership verification: {'✅ WORKING' if any(t['success'] for t in cross_user_tests) else '❌ FAILING'}")
        
        print()
        print("🎯 SECURITY CONCLUSION:")
        print("-" * 25)
        
        if passed_tests >= total_tests * 0.9:  # 90% success rate for security
            print("✅ SECURITY FIXES SUCCESSFULLY IMPLEMENTED!")
            print("   Authentication middleware is properly working")
            print("   All profile endpoints require proper Bearer token authentication")
            print("   Cross-user access is properly prevented")
            print("   Token validation is working correctly")
        elif passed_tests >= total_tests * 0.7:  # 70% success rate
            print("⚠️ SECURITY FIXES PARTIALLY IMPLEMENTED")
            print("   Most security measures are working but some issues remain")
            print("   Review failed tests and address remaining vulnerabilities")
        else:
            print("❌ CRITICAL SECURITY VULNERABILITIES DETECTED!")
            print("   Authentication middleware is not properly implemented")
            print("   Immediate action required before production deployment")
        
        print()
        print(f"Security test completed at: {datetime.now().isoformat()}")
        print("=" * 70)

def main():
    """Main test execution"""
    tester = ProfileSecurityTester()
    tester.run_security_tests()

if __name__ == "__main__":
    main()