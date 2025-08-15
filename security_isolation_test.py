#!/usr/bin/env python3
"""
FixMate-SA Security Isolation Testing
Testing critical security fixes for user data isolation in jobs and dashboard endpoints
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class SecurityIsolationTester:
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://fixmate-deploy-2.preview.emergentagent.com')
        self.api_base = f"{self.backend_url}/api"
        
        # Test users for isolation testing
        self.test_users = {
            "user1": {
                "phone": "+27800000002",
                "password": "client2024test",
                "token": None,
                "user_id": None
            },
            "user2": {
                "phone": "+27800000003", 
                "password": "fixer2024test",
                "token": None,
                "user_id": None
            },
            "admin": {
                "phone": "+27800000001",
                "password": "admin2024test", 
                "token": None,
                "user_id": None
            }
        }
        
        # Test results tracking
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        print(f"🔒 Security Isolation Testing Initialized")
        print(f"🔗 Backend URL: {self.backend_url}")
        print(f"🔗 API Base: {self.api_base}")
        print("=" * 80)

    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result with details"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.test_results.append(result)
        print(f"{status} {test_name}")
        if details:
            print(f"    📝 {details}")
        if not success and response_data:
            print(f"    📊 Response: {response_data}")
        print()

    def authenticate_user(self, user_key: str) -> bool:
        """Authenticate a test user and store token"""
        try:
            user = self.test_users[user_key]
            
            response = requests.post(
                f"{self.api_base}/auth/login",
                json={
                    "phone": user["phone"],
                    "password": user["password"]
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    user["token"] = data["token"]
                    user["user_id"] = data["user"]["id"]
                    self.log_test_result(
                        f"Authentication - {user_key}",
                        True,
                        f"Successfully authenticated {user['phone']} with token {user['token'][:20]}..."
                    )
                    return True
                else:
                    self.log_test_result(
                        f"Authentication - {user_key}",
                        False,
                        f"Login failed: {data.get('message', 'Unknown error')}",
                        data
                    )
                    return False
            else:
                self.log_test_result(
                    f"Authentication - {user_key}",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                f"Authentication - {user_key}",
                False,
                f"Exception: {str(e)}"
            )
            return False

    def test_jobs_endpoint_without_token(self):
        """Test GET /api/jobs without authentication token - should return 401"""
        try:
            response = requests.get(
                f"{self.api_base}/jobs",
                timeout=10
            )
            
            if response.status_code == 401:
                self.log_test_result(
                    "Jobs Endpoint - No Token",
                    True,
                    "Correctly returned 401 Unauthorized for missing token"
                )
            elif response.status_code == 422:
                # Check if it's a proper error response
                try:
                    data = response.json()
                    if "Missing or invalid authorization token" in str(data):
                        self.log_test_result(
                            "Jobs Endpoint - No Token",
                            True,
                            "Correctly returned 422 with authorization error message"
                        )
                    else:
                        self.log_test_result(
                            "Jobs Endpoint - No Token",
                            False,
                            f"Got 422 but wrong error message: {data}",
                            data
                        )
                except:
                    self.log_test_result(
                        "Jobs Endpoint - No Token",
                        False,
                        f"Expected 401, got {response.status_code}",
                        response.text
                    )
            else:
                self.log_test_result(
                    "Jobs Endpoint - No Token",
                    False,
                    f"Expected 401, got {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Jobs Endpoint - No Token",
                False,
                f"Exception: {str(e)}"
            )

    def test_jobs_endpoint_invalid_token(self):
        """Test GET /api/jobs with invalid token - should return 401"""
        try:
            response = requests.get(
                f"{self.api_base}/jobs",
                headers={"Authorization": "Bearer invalid_token_12345"},
                timeout=10
            )
            
            if response.status_code == 401:
                self.log_test_result(
                    "Jobs Endpoint - Invalid Token",
                    True,
                    "Correctly returned 401 Unauthorized for invalid token"
                )
            else:
                self.log_test_result(
                    "Jobs Endpoint - Invalid Token",
                    False,
                    f"Expected 401, got {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Jobs Endpoint - Invalid Token",
                False,
                f"Exception: {str(e)}"
            )

    def test_jobs_endpoint_malformed_tokens(self):
        """Test GET /api/jobs with various malformed tokens"""
        malformed_tokens = [
            "Bearer ",
            "Bearer token_",
            "Bearer malformed_token",
            "InvalidFormat token_123",
            "Bearer token_nonexistent_user"
        ]
        
        for token in malformed_tokens:
            try:
                response = requests.get(
                    f"{self.api_base}/jobs",
                    headers={"Authorization": token},
                    timeout=10
                )
                
                if response.status_code == 401:
                    self.log_test_result(
                        f"Jobs Endpoint - Malformed Token ({token[:20]}...)",
                        True,
                        "Correctly returned 401 Unauthorized for malformed token"
                    )
                else:
                    self.log_test_result(
                        f"Jobs Endpoint - Malformed Token ({token[:20]}...)",
                        False,
                        f"Expected 401, got {response.status_code}",
                        response.text
                    )
                    
            except Exception as e:
                self.log_test_result(
                    f"Jobs Endpoint - Malformed Token ({token[:20]}...)",
                    False,
                    f"Exception: {str(e)}"
                )

    def test_jobs_endpoint_user_isolation(self):
        """Test that users can only see their own jobs"""
        user1 = self.test_users["user1"]
        user2 = self.test_users["user2"]
        
        if not user1["token"] or not user2["token"]:
            self.log_test_result(
                "Jobs Endpoint - User Isolation",
                False,
                "Cannot test isolation - users not authenticated"
            )
            return
        
        # Test User1 jobs access
        try:
            response1 = requests.get(
                f"{self.api_base}/jobs",
                headers={"Authorization": f"Bearer {user1['token']}"},
                timeout=10
            )
            
            if response1.status_code == 200:
                data1 = response1.json()
                jobs1 = data1.get("jobs", [])
                
                # Verify all jobs belong to user1
                user1_jobs_valid = all(job.get("client_id") == user1["user_id"] for job in jobs1)
                
                if user1_jobs_valid:
                    self.log_test_result(
                        "Jobs Endpoint - User1 Isolation",
                        True,
                        f"User1 correctly sees only their own jobs ({len(jobs1)} jobs)"
                    )
                else:
                    self.log_test_result(
                        "Jobs Endpoint - User1 Isolation",
                        False,
                        f"User1 sees jobs from other users",
                        jobs1
                    )
            else:
                self.log_test_result(
                    "Jobs Endpoint - User1 Isolation",
                    False,
                    f"User1 request failed with {response1.status_code}",
                    response1.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Jobs Endpoint - User1 Isolation",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test User2 jobs access
        try:
            response2 = requests.get(
                f"{self.api_base}/jobs",
                headers={"Authorization": f"Bearer {user2['token']}"},
                timeout=10
            )
            
            if response2.status_code == 200:
                data2 = response2.json()
                jobs2 = data2.get("jobs", [])
                
                # Verify all jobs belong to user2
                user2_jobs_valid = all(job.get("client_id") == user2["user_id"] for job in jobs2)
                
                if user2_jobs_valid:
                    self.log_test_result(
                        "Jobs Endpoint - User2 Isolation",
                        True,
                        f"User2 correctly sees only their own jobs ({len(jobs2)} jobs)"
                    )
                else:
                    self.log_test_result(
                        "Jobs Endpoint - User2 Isolation",
                        False,
                        f"User2 sees jobs from other users",
                        jobs2
                    )
            else:
                self.log_test_result(
                    "Jobs Endpoint - User2 Isolation",
                    False,
                    f"User2 request failed with {response2.status_code}",
                    response2.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Jobs Endpoint - User2 Isolation",
                False,
                f"Exception: {str(e)}"
            )

    def test_dashboard_endpoint_without_token(self):
        """Test GET /api/dashboard/{user_id} without authentication token - should return 401"""
        user1 = self.test_users["user1"]
        
        try:
            response = requests.get(
                f"{self.api_base}/dashboard/{user1['user_id']}",
                timeout=10
            )
            
            if response.status_code == 401:
                self.log_test_result(
                    "Dashboard Endpoint - No Token",
                    True,
                    "Correctly returned 401 Unauthorized for missing token"
                )
            else:
                self.log_test_result(
                    "Dashboard Endpoint - No Token",
                    False,
                    f"Expected 401, got {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Dashboard Endpoint - No Token",
                False,
                f"Exception: {str(e)}"
            )

    def test_dashboard_endpoint_invalid_token(self):
        """Test GET /api/dashboard/{user_id} with invalid token - should return 401"""
        user1 = self.test_users["user1"]
        
        try:
            response = requests.get(
                f"{self.api_base}/dashboard/{user1['user_id']}",
                headers={"Authorization": "Bearer invalid_token_12345"},
                timeout=10
            )
            
            if response.status_code == 401:
                self.log_test_result(
                    "Dashboard Endpoint - Invalid Token",
                    True,
                    "Correctly returned 401 Unauthorized for invalid token"
                )
            else:
                self.log_test_result(
                    "Dashboard Endpoint - Invalid Token",
                    False,
                    f"Expected 401, got {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Dashboard Endpoint - Invalid Token",
                False,
                f"Exception: {str(e)}"
            )

    def test_dashboard_endpoint_ownership_verification(self):
        """Test dashboard ownership verification - users should only access their own dashboard"""
        user1 = self.test_users["user1"]
        user2 = self.test_users["user2"]
        
        if not user1["token"] or not user2["token"]:
            self.log_test_result(
                "Dashboard Endpoint - Ownership Verification",
                False,
                "Cannot test ownership - users not authenticated"
            )
            return
        
        # Test User1 accessing their own dashboard (should work)
        try:
            response1 = requests.get(
                f"{self.api_base}/dashboard/{user1['user_id']}",
                headers={"Authorization": f"Bearer {user1['token']}"},
                timeout=10
            )
            
            if response1.status_code == 200:
                self.log_test_result(
                    "Dashboard Endpoint - User1 Own Access",
                    True,
                    "User1 successfully accessed their own dashboard"
                )
            else:
                self.log_test_result(
                    "Dashboard Endpoint - User1 Own Access",
                    False,
                    f"User1 failed to access own dashboard: {response1.status_code}",
                    response1.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Dashboard Endpoint - User1 Own Access",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test User1 accessing User2's dashboard (should fail with 403)
        try:
            response2 = requests.get(
                f"{self.api_base}/dashboard/{user2['user_id']}",
                headers={"Authorization": f"Bearer {user1['token']}"},
                timeout=10
            )
            
            if response2.status_code == 403:
                self.log_test_result(
                    "Dashboard Endpoint - Cross-User Access Blocked",
                    True,
                    "User1 correctly denied access to User2's dashboard (403 Forbidden)"
                )
            else:
                self.log_test_result(
                    "Dashboard Endpoint - Cross-User Access Blocked",
                    False,
                    f"Expected 403, got {response2.status_code} - User1 can access User2's dashboard!",
                    response2.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Dashboard Endpoint - Cross-User Access Blocked",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test User2 accessing their own dashboard (should work)
        try:
            response3 = requests.get(
                f"{self.api_base}/dashboard/{user2['user_id']}",
                headers={"Authorization": f"Bearer {user2['token']}"},
                timeout=10
            )
            
            if response3.status_code == 200:
                self.log_test_result(
                    "Dashboard Endpoint - User2 Own Access",
                    True,
                    "User2 successfully accessed their own dashboard"
                )
            else:
                self.log_test_result(
                    "Dashboard Endpoint - User2 Own Access",
                    False,
                    f"User2 failed to access own dashboard: {response3.status_code}",
                    response3.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Dashboard Endpoint - User2 Own Access",
                False,
                f"Exception: {str(e)}"
            )

    def test_admin_access_verification(self):
        """Test that admin access still works for aggregated data"""
        admin = self.test_users["admin"]
        
        if not admin["token"]:
            self.log_test_result(
                "Admin Access Verification",
                False,
                "Cannot test admin access - admin not authenticated"
            )
            return
        
        # Test admin accessing their own dashboard
        try:
            response = requests.get(
                f"{self.api_base}/dashboard/{admin['user_id']}",
                headers={"Authorization": f"Bearer {admin['token']}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("role") == "admin":
                    self.log_test_result(
                        "Admin Access Verification",
                        True,
                        "Admin successfully accessed dashboard with admin role"
                    )
                else:
                    self.log_test_result(
                        "Admin Access Verification",
                        False,
                        f"Admin dashboard access working but role incorrect: {data.get('role')}",
                        data
                    )
            else:
                self.log_test_result(
                    "Admin Access Verification",
                    False,
                    f"Admin dashboard access failed: {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Admin Access Verification",
                False,
                f"Exception: {str(e)}"
            )

    def run_comprehensive_security_tests(self):
        """Run all security isolation tests"""
        print("🔒 STARTING COMPREHENSIVE SECURITY ISOLATION TESTING")
        print("=" * 80)
        
        # Step 1: Authenticate all test users
        print("📋 STEP 1: AUTHENTICATING TEST USERS")
        print("-" * 40)
        
        for user_key in self.test_users.keys():
            self.authenticate_user(user_key)
        
        print("\n📋 STEP 2: TESTING JOBS ENDPOINT SECURITY")
        print("-" * 40)
        
        # Test jobs endpoint without authentication
        self.test_jobs_endpoint_without_token()
        
        # Test jobs endpoint with invalid token
        self.test_jobs_endpoint_invalid_token()
        
        # Test jobs endpoint with malformed tokens
        self.test_jobs_endpoint_malformed_tokens()
        
        # Test user isolation for jobs
        self.test_jobs_endpoint_user_isolation()
        
        print("\n📋 STEP 3: TESTING DASHBOARD ENDPOINT SECURITY")
        print("-" * 40)
        
        # Test dashboard endpoint without authentication
        self.test_dashboard_endpoint_without_token()
        
        # Test dashboard endpoint with invalid token
        self.test_dashboard_endpoint_invalid_token()
        
        # Test dashboard ownership verification
        self.test_dashboard_endpoint_ownership_verification()
        
        print("\n📋 STEP 4: TESTING ADMIN ACCESS")
        print("-" * 40)
        
        # Test admin access verification
        self.test_admin_access_verification()
        
        # Print final results
        self.print_final_results()

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("🔒 SECURITY ISOLATION TESTING RESULTS")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize results
        critical_failures = []
        security_passes = []
        
        for result in self.test_results:
            if not result["success"]:
                if any(keyword in result["test"].lower() for keyword in ["isolation", "cross-user", "ownership", "token"]):
                    critical_failures.append(result)
            else:
                if any(keyword in result["test"].lower() for keyword in ["isolation", "cross-user", "ownership", "unauthorized"]):
                    security_passes.append(result)
        
        if critical_failures:
            print("🚨 CRITICAL SECURITY FAILURES:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
            print()
        
        if security_passes:
            print("✅ SECURITY CONTROLS WORKING:")
            for success in security_passes:
                print(f"   ✅ {success['test']}: {success['details']}")
            print()
        
        # Overall security assessment
        if success_rate >= 90:
            print("🎉 SECURITY STATUS: EXCELLENT - All critical security controls working")
        elif success_rate >= 75:
            print("⚠️  SECURITY STATUS: GOOD - Minor issues detected")
        elif success_rate >= 50:
            print("🚨 SECURITY STATUS: CONCERNING - Multiple security issues detected")
        else:
            print("💀 SECURITY STATUS: CRITICAL - Major security vulnerabilities detected")
        
        print("=" * 80)

def main():
    """Main testing function"""
    tester = SecurityIsolationTester()
    tester.run_comprehensive_security_tests()

if __name__ == "__main__":
    main()