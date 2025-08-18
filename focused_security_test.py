#!/usr/bin/env python3
"""
FixMate-SA Security Isolation Testing - Focused Test
Testing critical security fixes for user data isolation in jobs and dashboard endpoints
"""

import requests
import json
import os
from datetime import datetime

class FocusedSecurityTester:
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://service-pros-2.preview.emergentagent.com')
        self.api_base = f"{self.backend_url}/api"
        
        # Test results tracking
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        print(f"🔒 Focused Security Testing Initialized")
        print(f"🔗 Backend URL: {self.backend_url}")
        print("=" * 80)

    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result with details"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"{status} {test_name}")
        if details:
            print(f"    📝 {details}")
        print()

    def test_authentication_working(self):
        """Test that authentication is working for valid users"""
        try:
            # Test User1 authentication
            response = requests.post(
                f"{self.api_base}/auth/login",
                json={"phone": "+27800000002", "password": "client2024test"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    self.user1_token = data["token"]
                    self.user1_id = data["user"]["id"]
                    self.log_test_result(
                        "Authentication - User1 Login",
                        True,
                        f"Successfully authenticated User1 ({data['user']['phone']})"
                    )
                else:
                    self.log_test_result(
                        "Authentication - User1 Login",
                        False,
                        f"Login response missing token or success flag"
                    )
                    return False
            else:
                self.log_test_result(
                    "Authentication - User1 Login",
                    False,
                    f"Login failed with status {response.status_code}"
                )
                return False
            
            # Test User2 authentication
            response = requests.post(
                f"{self.api_base}/auth/login",
                json={"phone": "+27800000003", "password": "fixer2024test"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    self.user2_token = data["token"]
                    self.user2_id = data["user"]["id"]
                    self.log_test_result(
                        "Authentication - User2 Login",
                        True,
                        f"Successfully authenticated User2 ({data['user']['phone']})"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Authentication - User2 Login",
                        False,
                        f"Login response missing token or success flag"
                    )
                    return False
            else:
                self.log_test_result(
                    "Authentication - User2 Login",
                    False,
                    f"Login failed with status {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Authentication Setup",
                False,
                f"Exception during authentication: {str(e)}"
            )
            return False

    def test_jobs_security(self):
        """Test jobs endpoint security"""
        
        # Test 1: No token should be rejected
        try:
            response = requests.get(f"{self.api_base}/jobs", timeout=10)
            
            # Check if request was properly rejected (any error status + authorization error message)
            if response.status_code >= 400:
                try:
                    data = response.json()
                    error_text = str(data).lower()
                    if ("authorization" in error_text or "token" in error_text) and "401" in str(data):
                        self.log_test_result(
                            "Jobs Security - No Token Rejection",
                            True,
                            f"Correctly rejected request without token (HTTP {response.status_code}, message contains 401)"
                        )
                    else:
                        self.log_test_result(
                            "Jobs Security - No Token Rejection",
                            False,
                            f"Got error {response.status_code} but wrong error message: {data}"
                        )
                except:
                    self.log_test_result(
                        "Jobs Security - No Token Rejection",
                        False,
                        f"Got {response.status_code} but couldn't parse error message"
                    )
            else:
                self.log_test_result(
                    "Jobs Security - No Token Rejection",
                    False,
                    f"Expected error status, got {response.status_code}: {response.text[:100]}"
                )
        except Exception as e:
            self.log_test_result(
                "Jobs Security - No Token Rejection",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test 2: Invalid token should be rejected
        try:
            response = requests.get(
                f"{self.api_base}/jobs",
                headers={"Authorization": "Bearer invalid_token_12345"},
                timeout=10
            )
            
            # Check if request was properly rejected (any error status + authorization error message)
            if response.status_code >= 400:
                try:
                    data = response.json()
                    error_text = str(data).lower()
                    if ("authorization" in error_text or "token" in error_text) and "401" in str(data):
                        self.log_test_result(
                            "Jobs Security - Invalid Token Rejection",
                            True,
                            f"Correctly rejected invalid token (HTTP {response.status_code}, message contains 401)"
                        )
                    else:
                        self.log_test_result(
                            "Jobs Security - Invalid Token Rejection",
                            False,
                            f"Got error {response.status_code} but wrong error message: {data}"
                        )
                except:
                    self.log_test_result(
                        "Jobs Security - Invalid Token Rejection",
                        False,
                        f"Got {response.status_code} but couldn't parse error message"
                    )
            else:
                self.log_test_result(
                    "Jobs Security - Invalid Token Rejection",
                    False,
                    f"Expected error status, got {response.status_code}: {response.text[:100]}"
                )
        except Exception as e:
            self.log_test_result(
                "Jobs Security - Invalid Token Rejection",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test 3: Valid token should work and return only user's jobs
        try:
            response = requests.get(
                f"{self.api_base}/jobs",
                headers={"Authorization": f"Bearer {self.user1_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get("jobs", [])
                
                # Check if all jobs belong to the authenticated user
                user_jobs_only = all(job.get("client_id") == self.user1_id for job in jobs)
                
                if user_jobs_only:
                    self.log_test_result(
                        "Jobs Security - User Isolation",
                        True,
                        f"User1 correctly sees only their own jobs ({len(jobs)} jobs)"
                    )
                else:
                    cross_user_jobs = [job for job in jobs if job.get("client_id") != self.user1_id]
                    self.log_test_result(
                        "Jobs Security - User Isolation",
                        False,
                        f"User1 sees {len(cross_user_jobs)} jobs from other users!"
                    )
            else:
                self.log_test_result(
                    "Jobs Security - User Isolation",
                    False,
                    f"Valid token request failed: {response.status_code}"
                )
        except Exception as e:
            self.log_test_result(
                "Jobs Security - User Isolation",
                False,
                f"Exception: {str(e)}"
            )

    def test_dashboard_security(self):
        """Test dashboard endpoint security"""
        
        # Test 1: No token should be rejected
        try:
            response = requests.get(f"{self.api_base}/dashboard/{self.user1_id}", timeout=10)
            
            if response.status_code in [401, 422]:
                try:
                    data = response.json()
                    if "authorization" in str(data).lower() or "token" in str(data).lower():
                        self.log_test_result(
                            "Dashboard Security - No Token Rejection",
                            True,
                            f"Correctly rejected request without token (HTTP {response.status_code})"
                        )
                    else:
                        self.log_test_result(
                            "Dashboard Security - No Token Rejection",
                            False,
                            f"Got {response.status_code} but wrong error message: {data}"
                        )
                except:
                    self.log_test_result(
                        "Dashboard Security - No Token Rejection",
                        True,
                        f"Correctly rejected request without token (HTTP {response.status_code})"
                    )
            else:
                self.log_test_result(
                    "Dashboard Security - No Token Rejection",
                    False,
                    f"Expected 401/422, got {response.status_code}: {response.text[:100]}"
                )
        except Exception as e:
            self.log_test_result(
                "Dashboard Security - No Token Rejection",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test 2: Invalid token should be rejected
        try:
            response = requests.get(
                f"{self.api_base}/dashboard/{self.user1_id}",
                headers={"Authorization": "Bearer invalid_token_12345"},
                timeout=10
            )
            
            if response.status_code in [401, 422]:
                self.log_test_result(
                    "Dashboard Security - Invalid Token Rejection",
                    True,
                    f"Correctly rejected invalid token (HTTP {response.status_code})"
                )
            else:
                self.log_test_result(
                    "Dashboard Security - Invalid Token Rejection",
                    False,
                    f"Expected 401/422, got {response.status_code}: {response.text[:100]}"
                )
        except Exception as e:
            self.log_test_result(
                "Dashboard Security - Invalid Token Rejection",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test 3: User should access their own dashboard
        try:
            response = requests.get(
                f"{self.api_base}/dashboard/{self.user1_id}",
                headers={"Authorization": f"Bearer {self.user1_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("user_id") == self.user1_id:
                    self.log_test_result(
                        "Dashboard Security - Own Access",
                        True,
                        f"User1 successfully accessed their own dashboard"
                    )
                else:
                    self.log_test_result(
                        "Dashboard Security - Own Access",
                        False,
                        f"Dashboard returned wrong user_id: {data.get('user_id')}"
                    )
            else:
                self.log_test_result(
                    "Dashboard Security - Own Access",
                    False,
                    f"Own dashboard access failed: {response.status_code}"
                )
        except Exception as e:
            self.log_test_result(
                "Dashboard Security - Own Access",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test 4: User should NOT access another user's dashboard
        try:
            response = requests.get(
                f"{self.api_base}/dashboard/{self.user2_id}",
                headers={"Authorization": f"Bearer {self.user1_token}"},
                timeout=10
            )
            
            if response.status_code == 403:
                self.log_test_result(
                    "Dashboard Security - Cross-User Access Blocked",
                    True,
                    "User1 correctly denied access to User2's dashboard (403 Forbidden)"
                )
            elif response.status_code in [401, 422]:
                try:
                    data = response.json()
                    if "access denied" in str(data).lower() or "own dashboard" in str(data).lower():
                        self.log_test_result(
                            "Dashboard Security - Cross-User Access Blocked",
                            True,
                            f"User1 correctly denied access to User2's dashboard (HTTP {response.status_code})"
                        )
                    else:
                        self.log_test_result(
                            "Dashboard Security - Cross-User Access Blocked",
                            False,
                            f"Got {response.status_code} but wrong error message: {data}"
                        )
                except:
                    self.log_test_result(
                        "Dashboard Security - Cross-User Access Blocked",
                        True,
                        f"User1 correctly denied access to User2's dashboard (HTTP {response.status_code})"
                    )
            else:
                self.log_test_result(
                    "Dashboard Security - Cross-User Access Blocked",
                    False,
                    f"Expected 403, got {response.status_code} - User1 can access User2's dashboard!"
                )
        except Exception as e:
            self.log_test_result(
                "Dashboard Security - Cross-User Access Blocked",
                False,
                f"Exception: {str(e)}"
            )

    def run_security_tests(self):
        """Run all security tests"""
        print("🔒 STARTING FOCUSED SECURITY TESTING")
        print("=" * 80)
        
        # Step 1: Setup authentication
        print("📋 STEP 1: SETTING UP AUTHENTICATION")
        print("-" * 40)
        
        if not self.test_authentication_working():
            print("❌ Authentication setup failed - cannot proceed with security tests")
            return
        
        # Step 2: Test jobs endpoint security
        print("\n📋 STEP 2: TESTING JOBS ENDPOINT SECURITY")
        print("-" * 40)
        self.test_jobs_security()
        
        # Step 3: Test dashboard endpoint security
        print("\n📋 STEP 3: TESTING DASHBOARD ENDPOINT SECURITY")
        print("-" * 40)
        self.test_dashboard_security()
        
        # Print results
        self.print_results()

    def print_results(self):
        """Print test results"""
        print("\n" + "=" * 80)
        print("🔒 SECURITY TESTING RESULTS")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        # Show critical security results
        critical_tests = [
            "Jobs Security - No Token Rejection",
            "Jobs Security - Invalid Token Rejection", 
            "Jobs Security - User Isolation",
            "Dashboard Security - No Token Rejection",
            "Dashboard Security - Invalid Token Rejection",
            "Dashboard Security - Cross-User Access Blocked"
        ]
        
        print("🔒 CRITICAL SECURITY TESTS:")
        for result in self.test_results:
            if result["test"] in critical_tests:
                status = "✅" if result["success"] else "❌"
                print(f"   {status} {result['test']}")
        print()
        
        # Security assessment
        critical_passed = sum(1 for r in self.test_results if r["test"] in critical_tests and r["success"])
        critical_total = len([r for r in self.test_results if r["test"] in critical_tests])
        
        if critical_passed == critical_total:
            print("🎉 SECURITY STATUS: EXCELLENT - All critical security fixes working correctly!")
        elif critical_passed >= critical_total * 0.8:
            print("⚠️  SECURITY STATUS: GOOD - Most security fixes working, minor issues detected")
        else:
            print("🚨 SECURITY STATUS: CRITICAL - Major security vulnerabilities still present")
        
        print("=" * 80)

def main():
    """Main testing function"""
    tester = FocusedSecurityTester()
    tester.run_security_tests()

if __name__ == "__main__":
    main()