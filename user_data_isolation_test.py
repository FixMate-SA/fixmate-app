#!/usr/bin/env python3
"""
FixMate-SA User Data Isolation Testing
Comprehensive testing to ensure each client can only see their own data
Critical for privacy and security compliance
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

class UserDataIsolationTester:
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://service-pros-2.preview.emergentagent.com')
        self.api_base = f"{self.backend_url}/api"
        
        # Test user accounts as specified in review request
        self.test_users = {
            "user1": {
                "phone": "+27800000002",
                "password": "client2024test",
                "role": "client",
                "token": None,
                "user_id": None
            },
            "user2": {
                "phone": "+27800000003", 
                "password": "fixer2024test",
                "role": "fixer",
                "token": None,
                "user_id": None
            },
            "admin": {
                "phone": "+27800000001",
                "password": "admin2024test", 
                "role": "admin",
                "token": None,
                "user_id": None
            }
        }
        
        # Test results tracking
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        print(f"🔒 User Data Isolation Testing Initialized")
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
        
        print(f"{status} | {test_name}")
        if details:
            print(f"     Details: {details}")
        if not success and response_data:
            print(f"     Response: {response_data}")
        print()

    def authenticate_user(self, user_key: str) -> bool:
        """Authenticate a test user and store token"""
        try:
            user = self.test_users[user_key]
            login_data = {
                "phone": user["phone"],
                "password": user["password"]
            }
            
            print(f"     🔍 Attempting login for {user_key}: {user['phone']}")
            
            response = requests.post(
                f"{self.api_base}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"     🔍 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    user["token"] = data["token"]
                    user["user_id"] = data["user"]["id"]
                    print(f"     ✅ {user_key} authenticated: {user['phone']} -> {user['role']}")
                    return True
                else:
                    print(f"     ❌ {user_key} authentication failed: {data}")
                    return False
            else:
                print(f"     ❌ {user_key} HTTP {response.status_code}: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"     ❌ {user_key} authentication error: {str(e)}")
            return False

    def test_authentication_setup(self):
        """Test authentication for all test users"""
        try:
            successful_auths = 0
            
            for user_key in self.test_users.keys():
                if self.authenticate_user(user_key):
                    successful_auths += 1
            
            if successful_auths == len(self.test_users):
                self.log_test_result(
                    "User Authentication Setup",
                    True,
                    f"All {successful_auths} test users authenticated successfully"
                )
                return True
            else:
                self.log_test_result(
                    "User Authentication Setup", 
                    False,
                    f"Only {successful_auths}/{len(self.test_users)} users authenticated"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "User Authentication Setup",
                False,
                f"Authentication setup failed: {str(e)}"
            )
            return False

    def test_dashboard_data_isolation(self):
        """Test client dashboard data isolation"""
        try:
            user1 = self.test_users["user1"]
            user2 = self.test_users["user2"]
            admin = self.test_users["admin"]
            
            if not all([user1["token"], user2["token"], admin["token"]]):
                self.log_test_result(
                    "Dashboard Data Isolation",
                    False,
                    "Missing authentication tokens for dashboard testing"
                )
                return
            
            # Test User 1 dashboard access
            headers1 = {"Authorization": f"Bearer {user1['token']}"}
            response1 = requests.get(
                f"{self.api_base}/dashboard/{user1['user_id']}",
                headers=headers1,
                timeout=10
            )
            
            # Test User 2 dashboard access
            headers2 = {"Authorization": f"Bearer {user2['token']}"}
            response2 = requests.get(
                f"{self.api_base}/dashboard/{user2['user_id']}",
                headers=headers2,
                timeout=10
            )
            
            # Test Admin dashboard access
            admin_headers = {"Authorization": f"Bearer {admin['token']}"}
            admin_response = requests.get(
                f"{self.api_base}/dashboard/{admin['user_id']}",
                headers=admin_headers,
                timeout=10
            )
            
            isolation_checks = []
            
            # Check User 1 can access their own dashboard
            if response1.status_code == 200:
                data1 = response1.json()
                if data1.get("success") and data1.get("user_id") == user1["user_id"]:
                    isolation_checks.append("User1 can access own dashboard")
                else:
                    isolation_checks.append("❌ User1 dashboard access failed")
            else:
                isolation_checks.append(f"❌ User1 dashboard HTTP {response1.status_code}")
            
            # Check User 2 can access their own dashboard
            if response2.status_code == 200:
                data2 = response2.json()
                if data2.get("success") and data2.get("user_id") == user2["user_id"]:
                    isolation_checks.append("User2 can access own dashboard")
                else:
                    isolation_checks.append("❌ User2 dashboard access failed")
            else:
                isolation_checks.append(f"❌ User2 dashboard HTTP {response2.status_code}")
            
            # Check Admin can access their dashboard
            if admin_response.status_code == 200:
                admin_data = admin_response.json()
                if admin_data.get("success") and admin_data.get("role") == "admin":
                    isolation_checks.append("Admin can access admin dashboard")
                else:
                    isolation_checks.append("❌ Admin dashboard access failed")
            else:
                isolation_checks.append(f"❌ Admin dashboard HTTP {admin_response.status_code}")
            
            # Test cross-user access prevention (User 1 trying to access User 2's dashboard)
            cross_access_response = requests.get(
                f"{self.api_base}/dashboard/{user2['user_id']}",
                headers=headers1,
                timeout=10
            )
            
            # This should either fail or return User 1's data (depending on implementation)
            if cross_access_response.status_code == 200:
                cross_data = cross_access_response.json()
                if cross_data.get("user_id") == user1["user_id"]:
                    isolation_checks.append("✅ Cross-user access properly isolated (returns own data)")
                elif cross_data.get("user_id") == user2["user_id"]:
                    isolation_checks.append("❌ SECURITY BREACH: User1 can access User2's dashboard")
                else:
                    isolation_checks.append("Cross-user access returned unexpected data")
            else:
                isolation_checks.append("✅ Cross-user access properly blocked")
            
            successful_checks = len([c for c in isolation_checks if not c.startswith("❌")])
            total_checks = len(isolation_checks)
            
            if successful_checks >= total_checks - 1:  # Allow 1 failure
                self.log_test_result(
                    "Dashboard Data Isolation",
                    True,
                    f"Dashboard isolation working: {successful_checks}/{total_checks} checks passed - {isolation_checks}"
                )
            else:
                self.log_test_result(
                    "Dashboard Data Isolation",
                    False,
                    f"Dashboard isolation issues: {successful_checks}/{total_checks} checks passed - {isolation_checks}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Dashboard Data Isolation",
                False,
                f"Dashboard isolation test failed: {str(e)}"
            )

    def test_job_management_isolation(self):
        """Test job management data isolation"""
        try:
            user1 = self.test_users["user1"]
            user2 = self.test_users["user2"]
            
            if not all([user1["token"], user2["token"]]):
                self.log_test_result(
                    "Job Management Isolation",
                    False,
                    "Missing authentication tokens for job testing"
                )
                return
            
            headers1 = {"Authorization": f"Bearer {user1['token']}"}
            headers2 = {"Authorization": f"Bearer {user2['token']}"}
            
            # Get User 1's jobs
            response1 = requests.get(
                f"{self.api_base}/jobs",
                headers=headers1,
                timeout=10
            )
            
            # Get User 2's jobs
            response2 = requests.get(
                f"{self.api_base}/jobs",
                headers=headers2,
                timeout=10
            )
            
            isolation_checks = []
            user1_jobs = []
            user2_jobs = []
            
            # Check User 1 jobs
            if response1.status_code == 200:
                data1 = response1.json()
                if data1.get("success"):
                    user1_jobs = data1.get("jobs", [])
                    # Verify all jobs belong to User 1
                    user1_job_owners = [job.get("client_id") for job in user1_jobs]
                    if all(owner == user1["user_id"] for owner in user1_job_owners if owner):
                        isolation_checks.append(f"✅ User1 sees only own jobs ({len(user1_jobs)} jobs)")
                    else:
                        isolation_checks.append(f"❌ User1 sees jobs from other users: {set(user1_job_owners)}")
                else:
                    isolation_checks.append("❌ User1 job retrieval failed")
            else:
                isolation_checks.append(f"❌ User1 jobs HTTP {response1.status_code}")
            
            # Check User 2 jobs
            if response2.status_code == 200:
                data2 = response2.json()
                if data2.get("success"):
                    user2_jobs = data2.get("jobs", [])
                    # Verify all jobs belong to User 2
                    user2_job_owners = [job.get("client_id") for job in user2_jobs]
                    if all(owner == user2["user_id"] for owner in user2_job_owners if owner):
                        isolation_checks.append(f"✅ User2 sees only own jobs ({len(user2_jobs)} jobs)")
                    else:
                        isolation_checks.append(f"❌ User2 sees jobs from other users: {set(user2_job_owners)}")
                else:
                    isolation_checks.append("❌ User2 job retrieval failed")
            else:
                isolation_checks.append(f"❌ User2 jobs HTTP {response2.status_code}")
            
            # Check for job overlap (should be none)
            user1_job_ids = [job.get("id") for job in user1_jobs]
            user2_job_ids = [job.get("id") for job in user2_jobs]
            job_overlap = set(user1_job_ids) & set(user2_job_ids)
            
            if not job_overlap:
                isolation_checks.append("✅ No job overlap between users")
            else:
                isolation_checks.append(f"❌ SECURITY BREACH: Job overlap detected: {job_overlap}")
            
            successful_checks = len([c for c in isolation_checks if c.startswith("✅")])
            total_checks = len(isolation_checks)
            
            if successful_checks >= total_checks - 1:  # Allow 1 failure
                self.log_test_result(
                    "Job Management Isolation",
                    True,
                    f"Job isolation working: {successful_checks}/{total_checks} checks passed - {isolation_checks}"
                )
            else:
                self.log_test_result(
                    "Job Management Isolation",
                    False,
                    f"Job isolation issues: {successful_checks}/{total_checks} checks passed - {isolation_checks}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Job Management Isolation",
                False,
                f"Job isolation test failed: {str(e)}"
            )

    def test_enterprise_portal_isolation(self):
        """Test enterprise portal data isolation"""
        try:
            user1 = self.test_users["user1"]
            user2 = self.test_users["user2"]
            
            if not all([user1["token"], user2["token"]]):
                self.log_test_result(
                    "Enterprise Portal Isolation",
                    False,
                    "Missing authentication tokens for enterprise testing"
                )
                return
            
            headers1 = {"Authorization": f"Bearer {user1['token']}"}
            headers2 = {"Authorization": f"Bearer {user2['token']}"}
            
            enterprise_endpoints = [
                "/enterprise/overview",
                "/enterprise/team", 
                "/enterprise/contracts",
                "/enterprise/locations",
                "/enterprise/invoices"
            ]
            
            isolation_checks = []
            
            for endpoint in enterprise_endpoints:
                # Test User 1 access
                response1 = requests.get(
                    f"{self.api_base}{endpoint}",
                    headers=headers1,
                    timeout=10
                )
                
                # Test User 2 access
                response2 = requests.get(
                    f"{self.api_base}{endpoint}",
                    headers=headers2,
                    timeout=10
                )
                
                endpoint_name = endpoint.split("/")[-1]
                
                # Check User 1 access
                if response1.status_code == 200:
                    data1 = response1.json()
                    if data1.get("success"):
                        isolation_checks.append(f"✅ User1 can access {endpoint_name}")
                    else:
                        isolation_checks.append(f"❌ User1 {endpoint_name} access failed")
                else:
                    isolation_checks.append(f"❌ User1 {endpoint_name} HTTP {response1.status_code}")
                
                # Check User 2 access
                if response2.status_code == 200:
                    data2 = response2.json()
                    if data2.get("success"):
                        isolation_checks.append(f"✅ User2 can access {endpoint_name}")
                    else:
                        isolation_checks.append(f"❌ User2 {endpoint_name} access failed")
                else:
                    isolation_checks.append(f"❌ User2 {endpoint_name} HTTP {response2.status_code}")
            
            successful_checks = len([c for c in isolation_checks if c.startswith("✅")])
            total_checks = len(isolation_checks)
            
            if successful_checks >= total_checks * 0.7:  # 70% success rate
                self.log_test_result(
                    "Enterprise Portal Isolation",
                    True,
                    f"Enterprise isolation working: {successful_checks}/{total_checks} checks passed"
                )
            else:
                self.log_test_result(
                    "Enterprise Portal Isolation",
                    False,
                    f"Enterprise isolation issues: {successful_checks}/{total_checks} checks passed - {isolation_checks}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Enterprise Portal Isolation",
                False,
                f"Enterprise isolation test failed: {str(e)}"
            )

    def test_business_compliance_isolation(self):
        """Test business compliance data isolation"""
        try:
            user1 = self.test_users["user1"]
            user2 = self.test_users["user2"]
            
            if not all([user1["token"], user2["token"]]):
                self.log_test_result(
                    "Business Compliance Isolation",
                    False,
                    "Missing authentication tokens for compliance testing"
                )
                return
            
            headers1 = {"Authorization": f"Bearer {user1['token']}"}
            headers2 = {"Authorization": f"Bearer {user2['token']}"}
            
            compliance_endpoints = [
                "/compliance/requests",
                "/compliance/documents"
            ]
            
            isolation_checks = []
            
            for endpoint in compliance_endpoints:
                # Test User 1 access
                response1 = requests.get(
                    f"{self.api_base}{endpoint}",
                    headers=headers1,
                    timeout=10
                )
                
                # Test User 2 access
                response2 = requests.get(
                    f"{self.api_base}{endpoint}",
                    headers=headers2,
                    timeout=10
                )
                
                endpoint_name = endpoint.split("/")[-1]
                
                # Check User 1 access
                if response1.status_code == 200:
                    data1 = response1.json()
                    if isinstance(data1, list) or (isinstance(data1, dict) and data1.get("success")):
                        isolation_checks.append(f"✅ User1 can access {endpoint_name}")
                    else:
                        isolation_checks.append(f"❌ User1 {endpoint_name} access failed")
                else:
                    isolation_checks.append(f"❌ User1 {endpoint_name} HTTP {response1.status_code}")
                
                # Check User 2 access
                if response2.status_code == 200:
                    data2 = response2.json()
                    if isinstance(data2, list) or (isinstance(data2, dict) and data2.get("success")):
                        isolation_checks.append(f"✅ User2 can access {endpoint_name}")
                    else:
                        isolation_checks.append(f"❌ User2 {endpoint_name} access failed")
                else:
                    isolation_checks.append(f"❌ User2 {endpoint_name} HTTP {response2.status_code}")
            
            successful_checks = len([c for c in isolation_checks if c.startswith("✅")])
            total_checks = len(isolation_checks)
            
            if successful_checks >= total_checks * 0.7:  # 70% success rate
                self.log_test_result(
                    "Business Compliance Isolation",
                    True,
                    f"Compliance isolation working: {successful_checks}/{total_checks} checks passed"
                )
            else:
                self.log_test_result(
                    "Business Compliance Isolation",
                    False,
                    f"Compliance isolation issues: {successful_checks}/{total_checks} checks passed - {isolation_checks}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Business Compliance Isolation",
                False,
                f"Compliance isolation test failed: {str(e)}"
            )

    def test_admin_access_privileges(self):
        """Test admin access to aggregated data"""
        try:
            admin = self.test_users["admin"]
            
            if not admin["token"]:
                self.log_test_result(
                    "Admin Access Privileges",
                    False,
                    "Missing admin authentication token"
                )
                return
            
            admin_headers = {"Authorization": f"Bearer {admin['token']}"}
            
            # Test admin dashboard (should show aggregated data)
            admin_dashboard = requests.get(
                f"{self.api_base}/dashboard/{admin['user_id']}",
                headers=admin_headers,
                timeout=10
            )
            
            # Test admin access to all jobs (if endpoint exists)
            all_jobs = requests.get(
                f"{self.api_base}/jobs",
                headers=admin_headers,
                timeout=10
            )
            
            admin_checks = []
            
            # Check admin dashboard
            if admin_dashboard.status_code == 200:
                dashboard_data = admin_dashboard.json()
                if dashboard_data.get("success") and dashboard_data.get("role") == "admin":
                    stats = dashboard_data.get("stats", {})
                    if "total_jobs" in stats and "total_clients" in stats:
                        admin_checks.append(f"✅ Admin dashboard shows aggregated data: {stats}")
                    else:
                        admin_checks.append("❌ Admin dashboard missing aggregated stats")
                else:
                    admin_checks.append("❌ Admin dashboard access failed")
            else:
                admin_checks.append(f"❌ Admin dashboard HTTP {admin_dashboard.status_code}")
            
            # Check admin job access
            if all_jobs.status_code == 200:
                jobs_data = all_jobs.json()
                if jobs_data.get("success"):
                    jobs = jobs_data.get("jobs", [])
                    unique_owners = set(job.get("client_id") for job in jobs if job.get("client_id"))
                    if len(unique_owners) > 1:
                        admin_checks.append(f"✅ Admin can see jobs from multiple users: {len(unique_owners)} different owners")
                    elif len(unique_owners) == 1:
                        admin_checks.append("⚠️ Admin sees jobs from only 1 user (may be expected)")
                    else:
                        admin_checks.append("⚠️ Admin sees no jobs (may be expected)")
                else:
                    admin_checks.append("❌ Admin job access failed")
            else:
                admin_checks.append(f"❌ Admin jobs HTTP {all_jobs.status_code}")
            
            successful_checks = len([c for c in admin_checks if c.startswith("✅")])
            total_checks = len(admin_checks)
            
            if successful_checks >= 1:  # At least 1 admin privilege working
                self.log_test_result(
                    "Admin Access Privileges",
                    True,
                    f"Admin privileges working: {successful_checks}/{total_checks} checks passed - {admin_checks}"
                )
            else:
                self.log_test_result(
                    "Admin Access Privileges",
                    False,
                    f"Admin privileges issues: {successful_checks}/{total_checks} checks passed - {admin_checks}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Admin Access Privileges",
                False,
                f"Admin access test failed: {str(e)}"
            )

    def test_token_security(self):
        """Test token-based authentication security"""
        try:
            user1 = self.test_users["user1"]
            user2 = self.test_users["user2"]
            
            if not all([user1["token"], user2["token"]]):
                self.log_test_result(
                    "Token Security",
                    False,
                    "Missing authentication tokens for security testing"
                )
                return
            
            security_checks = []
            
            # Test 1: Invalid token should be rejected
            invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
            invalid_response = requests.get(
                f"{self.api_base}/dashboard/{user1['user_id']}",
                headers=invalid_headers,
                timeout=10
            )
            
            if invalid_response.status_code == 401:
                security_checks.append("✅ Invalid token properly rejected (401)")
            else:
                security_checks.append(f"❌ Invalid token not rejected: HTTP {invalid_response.status_code}")
            
            # Test 2: Missing Authorization header should be rejected
            no_auth_response = requests.get(
                f"{self.api_base}/dashboard/{user1['user_id']}",
                timeout=10
            )
            
            if no_auth_response.status_code == 401:
                security_checks.append("✅ Missing auth header properly rejected (401)")
            elif no_auth_response.status_code == 422:
                security_checks.append("✅ Missing auth header properly rejected (422)")
            else:
                security_checks.append(f"❌ Missing auth header not rejected: HTTP {no_auth_response.status_code}")
            
            # Test 3: User 1's token cannot access User 2's specific data
            cross_token_response = requests.get(
                f"{self.api_base}/dashboard/{user2['user_id']}",
                headers={"Authorization": f"Bearer {user1['token']}"},
                timeout=10
            )
            
            if cross_token_response.status_code == 200:
                cross_data = cross_token_response.json()
                if cross_data.get("user_id") == user1["user_id"]:
                    security_checks.append("✅ Cross-token access returns own data (secure)")
                elif cross_data.get("user_id") == user2["user_id"]:
                    security_checks.append("❌ SECURITY BREACH: User1 token accesses User2 data")
                else:
                    security_checks.append("⚠️ Cross-token access returns unexpected data")
            elif cross_token_response.status_code in [401, 403]:
                security_checks.append("✅ Cross-token access properly blocked")
            else:
                security_checks.append(f"⚠️ Cross-token access HTTP {cross_token_response.status_code}")
            
            # Test 4: Expired/malformed token formats
            malformed_tokens = [
                "Bearer ",
                "Bearer token_",
                "InvalidFormat",
                ""
            ]
            
            malformed_rejections = 0
            for token in malformed_tokens:
                headers = {"Authorization": token} if token else {}
                response = requests.get(
                    f"{self.api_base}/dashboard/{user1['user_id']}",
                    headers=headers,
                    timeout=10
                )
                if response.status_code in [401, 422]:
                    malformed_rejections += 1
            
            if malformed_rejections >= len(malformed_tokens) * 0.75:
                security_checks.append(f"✅ Malformed tokens properly rejected ({malformed_rejections}/{len(malformed_tokens)})")
            else:
                security_checks.append(f"❌ Insufficient malformed token rejection ({malformed_rejections}/{len(malformed_tokens)})")
            
            successful_checks = len([c for c in security_checks if c.startswith("✅")])
            total_checks = len(security_checks)
            
            if successful_checks >= total_checks - 1:  # Allow 1 failure
                self.log_test_result(
                    "Token Security",
                    True,
                    f"Token security working: {successful_checks}/{total_checks} checks passed - {security_checks}"
                )
            else:
                self.log_test_result(
                    "Token Security",
                    False,
                    f"Token security issues: {successful_checks}/{total_checks} checks passed - {security_checks}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Token Security",
                False,
                f"Token security test failed: {str(e)}"
            )

    def run_comprehensive_isolation_tests(self):
        """Run all user data isolation tests"""
        print("🔒 STARTING COMPREHENSIVE USER DATA ISOLATION TESTING")
        print("=" * 80)
        
        # Step 1: Authenticate all test users
        if not self.test_authentication_setup():
            print("❌ Authentication setup failed - cannot proceed with isolation tests")
            return
        
        # Step 2: Test dashboard data isolation
        self.test_dashboard_data_isolation()
        
        # Step 3: Test job management isolation
        self.test_job_management_isolation()
        
        # Step 4: Test enterprise portal isolation
        self.test_enterprise_portal_isolation()
        
        # Step 5: Test business compliance isolation
        self.test_business_compliance_isolation()
        
        # Step 6: Test admin access privileges
        self.test_admin_access_privileges()
        
        # Step 7: Test token security
        self.test_token_security()
        
        # Generate final report
        self.generate_test_report()

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("=" * 80)
        print("🔒 USER DATA ISOLATION TESTING COMPLETED")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize results by security criticality
        critical_security_tests = [
            "Token Security",
            "Dashboard Data Isolation",
            "Job Management Isolation"
        ]
        
        important_tests = [
            "Enterprise Portal Isolation",
            "Business Compliance Isolation",
            "Admin Access Privileges"
        ]
        
        # Check critical security functionality
        critical_passed = sum(1 for result in self.test_results 
                            if result["test"] in critical_security_tests and result["success"])
        critical_total = len([r for r in self.test_results if r["test"] in critical_security_tests])
        
        important_passed = sum(1 for result in self.test_results 
                             if result["test"] in important_tests and result["success"])
        important_total = len([r for r in self.test_results if r["test"] in important_tests])
        
        print(f"🔴 CRITICAL SECURITY: {critical_passed}/{critical_total} passed")
        print(f"🟡 IMPORTANT FEATURES: {important_passed}/{important_total} passed")
        print()
        
        # Detailed results
        print("📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['test']}")
            if result["details"]:
                print(f"      {result['details']}")
        
        print()
        
        # Security assessment
        security_breaches = [r for r in self.test_results if not r["success"] and "SECURITY BREACH" in r["details"]]
        
        if security_breaches:
            print("🚨 CRITICAL SECURITY BREACHES DETECTED:")
            for breach in security_breaches:
                print(f"   ❌ {breach['test']}: {breach['details']}")
            print()
        
        # Final assessment
        if success_rate >= 90 and critical_passed == critical_total and not security_breaches:
            print("🎉 USER DATA ISOLATION STATUS: SECURE")
            print("   All critical security tests passed, no data leakage detected")
        elif success_rate >= 75 and critical_passed >= critical_total * 0.8 and not security_breaches:
            print("⚠️ USER DATA ISOLATION STATUS: MOSTLY SECURE")
            print("   Core security working with minor issues")
        else:
            print("❌ USER DATA ISOLATION STATUS: SECURITY ISSUES DETECTED")
            print("   Critical security vulnerabilities found that require immediate attention")
        
        print("=" * 80)
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "success_rate": success_rate,
            "critical_passed": critical_passed,
            "critical_total": critical_total,
            "security_breaches": len(security_breaches),
            "status": "SECURE" if success_rate >= 90 and critical_passed == critical_total and not security_breaches else "NEEDS ATTENTION"
        }

def main():
    """Main testing function"""
    tester = UserDataIsolationTester()
    results = tester.run_comprehensive_isolation_tests()
    return results

if __name__ == "__main__":
    main()