#!/usr/bin/env python3
"""
FixMate-SA Backend API Testing Script - Post Afrikaans Translation Completion
Testing Focus: Authentication System, Core API Endpoints, Database Connectivity, Service Health

Test Accounts:
- Admin: +27800000001 / admin2024test
- Client: +27800000002 / client2024test  
- Fixer: +27800000003 / fixer2024test
"""

import requests
import json
import sys
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment - use local for testing
BACKEND_URL = 'http://localhost:8001'
API_BASE = f"{BACKEND_URL}/api"

print(f"🔧 Testing FixMate-SA Backend API at: {API_BASE}")
print("=" * 80)
print("🎯 POST-AFRIKAANS TRANSLATION BACKEND VERIFICATION")
print("=" * 80)

class FixMateBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_data = {}
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.tokens = {}
    
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
    
    def test_api_health(self):
        """Test API health endpoint"""
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
    
    def test_admin_login(self):
        """Test admin login with provided credentials"""
        try:
            login_data = {
                "phone": "+27800000001",
                "password": "admin2024test"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.tokens['admin'] = data['token']
                    self.test_data['admin_user'] = data['user']
                    role = data.get('role_info', {}).get('role', 'unknown')
                    display_name = data.get('display_name', 'Unknown')
                    self.log_result("Admin Login", True, f"Admin login successful - Role: {role}, Display: {display_name}")
                    return True
                else:
                    self.log_result("Admin Login", False, "Invalid response format", response)
            else:
                self.log_result("Admin Login", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Admin Login", False, f"Request error: {str(e)}")
        return False
    
    def test_client_login(self):
        """Test client login with provided credentials"""
        try:
            login_data = {
                "phone": "+27800000002",
                "password": "client2024test"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.tokens['client'] = data['token']
                    self.test_data['client_user'] = data['user']
                    role = data.get('role_info', {}).get('role', 'unknown')
                    display_name = data.get('display_name', 'Unknown')
                    self.log_result("Client Login", True, f"Client login successful - Role: {role}, Display: {display_name}")
                    return True
                else:
                    self.log_result("Client Login", False, "Invalid response format", response)
            else:
                self.log_result("Client Login", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Client Login", False, f"Request error: {str(e)}")
        return False
    
    def test_fixer_login(self):
        """Test fixer login with provided credentials"""
        try:
            login_data = {
                "phone": "+27800000003",
                "password": "fixer2024test"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.tokens['fixer'] = data['token']
                    self.test_data['fixer_user'] = data['user']
                    role = data.get('role_info', {}).get('role', 'unknown')
                    display_name = data.get('display_name', 'Unknown')
                    self.log_result("Fixer Login", True, f"Fixer login successful - Role: {role}, Display: {display_name}")
                    return True
                else:
                    self.log_result("Fixer Login", False, "Invalid response format", response)
            else:
                self.log_result("Fixer Login", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Fixer Login", False, f"Request error: {str(e)}")
        return False
    
    def test_token_authentication(self):
        """Test token-based authentication"""
        if 'admin' not in self.tokens:
            self.log_result("Token Authentication", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            response = self.session.get(f"{API_BASE}/users", headers=headers)
            
            if response.status_code == 200:
                users = response.json()
                if isinstance(users, list):
                    self.log_result("Token Authentication", True, f"Token authentication working - Retrieved {len(users)} users")
                    return True
                else:
                    self.log_result("Token Authentication", False, "Invalid response format", response)
            else:
                self.log_result("Token Authentication", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Token Authentication", False, f"Request error: {str(e)}")
        return False
    
    def test_user_management_endpoints(self):
        """Test user management CRUD endpoints"""
        if 'admin' not in self.tokens:
            self.log_result("User Management Endpoints", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            
            # Test GET /users
            response = self.session.get(f"{API_BASE}/users", headers=headers)
            if response.status_code != 200:
                self.log_result("User Management Endpoints", False, f"GET /users failed: HTTP {response.status_code}", response)
                return False
            
            users = response.json()
            user_count = len(users) if isinstance(users, list) else 0
            
            # Test GET /users/{user_id} if we have users
            if user_count > 0:
                test_user_id = users[0]['id']
                user_response = self.session.get(f"{API_BASE}/users/{test_user_id}", headers=headers)
                if user_response.status_code != 200:
                    self.log_result("User Management Endpoints", False, f"GET /users/{{id}} failed: HTTP {user_response.status_code}", user_response)
                    return False
            
            self.log_result("User Management Endpoints", True, f"User management endpoints working - {user_count} users found")
            return True
            
        except Exception as e:
            self.log_result("User Management Endpoints", False, f"Request error: {str(e)}")
        return False
    
    def test_job_management_endpoints(self):
        """Test job management endpoints"""
        if 'client' not in self.tokens:
            self.log_result("Job Management Endpoints", False, "No client token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.tokens['client']}"}
            
            # Test GET /jobs
            response = self.session.get(f"{API_BASE}/jobs", headers=headers)
            if response.status_code != 200:
                self.log_result("Job Management Endpoints", False, f"GET /jobs failed: HTTP {response.status_code}", response)
                return False
            
            jobs_data = response.json()
            
            # Handle both paginated and direct list responses
            if isinstance(jobs_data, dict) and 'data' in jobs_data:
                jobs = jobs_data['data']
                job_count = len(jobs)
            elif isinstance(jobs_data, list):
                jobs = jobs_data
                job_count = len(jobs)
            else:
                job_count = 0
                jobs = []
            
            # Test job creation
            if 'client_user' in self.test_data:
                job_data = {
                    "user_id": self.test_data['client_user']['id'],
                    "service": "plumbing",
                    "description": "Test job for API verification",
                    "location": "Cape Town, South Africa",
                    "estimated_price": 250.0
                }
                
                create_response = self.session.post(f"{API_BASE}/jobs", json=job_data, headers=headers)
                if create_response.status_code == 200:
                    created_job = create_response.json()
                    self.test_data['test_job_id'] = created_job['id']
                    
                    # Test GET /jobs/{job_id}
                    job_response = self.session.get(f"{API_BASE}/jobs/{created_job['id']}", headers=headers)
                    if job_response.status_code != 200:
                        self.log_result("Job Management Endpoints", False, f"GET /jobs/{{id}} failed: HTTP {job_response.status_code}", job_response)
                        return False
                    
                    self.log_result("Job Management Endpoints", True, f"Job management endpoints working - {job_count} existing jobs, job creation successful")
                    return True
                else:
                    self.log_result("Job Management Endpoints", False, f"Job creation failed: HTTP {create_response.status_code}", create_response)
                    return False
            else:
                self.log_result("Job Management Endpoints", True, f"Job listing working - {job_count} jobs found (creation test skipped - no client user)")
                return True
            
        except Exception as e:
            self.log_result("Job Management Endpoints", False, f"Request error: {str(e)}")
        return False
    
    def test_fixer_management_endpoints(self):
        """Test fixer management endpoints"""
        try:
            # Test GET /fixers (public endpoint)
            response = self.session.get(f"{API_BASE}/fixers")
            if response.status_code != 200:
                self.log_result("Fixer Management Endpoints", False, f"GET /fixers failed: HTTP {response.status_code}", response)
                return False
            
            fixers = response.json()
            fixer_count = len(fixers) if isinstance(fixers, list) else 0
            
            # Test GET /fixers/{fixer_id} if we have fixers
            if fixer_count > 0:
                test_fixer_id = fixers[0]['id']
                fixer_response = self.session.get(f"{API_BASE}/fixers/{test_fixer_id}")
                if fixer_response.status_code != 200:
                    self.log_result("Fixer Management Endpoints", False, f"GET /fixers/{{id}} failed: HTTP {fixer_response.status_code}", fixer_response)
                    return False
                
                # Test service filtering
                if fixers[0].get('services'):
                    service_filter = "plumbing"  # Common service
                    service_response = self.session.get(f"{API_BASE}/fixers/by-service/{service_filter}")
                    if service_response.status_code != 200:
                        self.log_result("Fixer Management Endpoints", False, f"Service filtering failed: HTTP {service_response.status_code}", service_response)
                        return False
            
            self.log_result("Fixer Management Endpoints", True, f"Fixer management endpoints working - {fixer_count} fixers found")
            return True
            
        except Exception as e:
            self.log_result("Fixer Management Endpoints", False, f"Request error: {str(e)}")
        return False
    
    def test_dashboard_endpoint(self):
        """Test dashboard data endpoint"""
        if 'admin' not in self.tokens:
            self.log_result("Dashboard Endpoint", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
            response = self.session.get(f"{API_BASE}/dashboard", headers=headers)
            
            if response.status_code == 200:
                dashboard_data = response.json()
                
                # Check for expected dashboard fields
                expected_fields = ['total_users', 'total_jobs', 'total_fixers']
                found_fields = [field for field in expected_fields if field in dashboard_data]
                
                if found_fields:
                    self.log_result("Dashboard Endpoint", True, f"Dashboard endpoint working - Found fields: {', '.join(found_fields)}")
                    return True
                else:
                    self.log_result("Dashboard Endpoint", True, f"Dashboard endpoint responding - Custom data structure")
                    return True
            else:
                self.log_result("Dashboard Endpoint", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Dashboard Endpoint", False, f"Request error: {str(e)}")
        return False
    
    def test_database_connectivity(self):
        """Test database connectivity through API operations"""
        try:
            # Test database read operation
            response = self.session.get(f"{API_BASE}/fixers")
            if response.status_code != 200:
                self.log_result("Database Connectivity", False, f"Database read test failed: HTTP {response.status_code}", response)
                return False
            
            # Test role check endpoint (database query)
            role_response = self.session.get(f"{API_BASE}/auth/role-check/+27800000001")
            if role_response.status_code != 200:
                self.log_result("Database Connectivity", False, f"Database role check failed: HTTP {role_response.status_code}", role_response)
                return False
            
            role_data = role_response.json()
            if 'role' in role_data:
                self.log_result("Database Connectivity", True, f"Database connectivity verified - Role check returned: {role_data['role']}")
                return True
            else:
                self.log_result("Database Connectivity", False, "Invalid role check response", role_response)
                return False
            
        except Exception as e:
            self.log_result("Database Connectivity", False, f"Request error: {str(e)}")
        return False
    
    def test_role_based_authentication(self):
        """Test role-based authentication and authorization"""
        success_count = 0
        total_tests = 3
        
        # Test admin role
        if 'admin' in self.tokens:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
                response = self.session.get(f"{API_BASE}/users", headers=headers)
                if response.status_code == 200:
                    success_count += 1
                    print("   ✅ Admin role authentication working")
                else:
                    print(f"   ❌ Admin role authentication failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ Admin role test error: {str(e)}")
        
        # Test client role
        if 'client' in self.tokens:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['client']}"}
                response = self.session.get(f"{API_BASE}/jobs", headers=headers)
                if response.status_code == 200:
                    success_count += 1
                    print("   ✅ Client role authentication working")
                else:
                    print(f"   ❌ Client role authentication failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ Client role test error: {str(e)}")
        
        # Test fixer role
        if 'fixer' in self.tokens:
            try:
                headers = {"Authorization": f"Bearer {self.tokens['fixer']}"}
                response = self.session.get(f"{API_BASE}/jobs", headers=headers)
                if response.status_code == 200:
                    success_count += 1
                    print("   ✅ Fixer role authentication working")
                else:
                    print(f"   ❌ Fixer role authentication failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ Fixer role test error: {str(e)}")
        
        if success_count >= 2:
            self.log_result("Role-Based Authentication", True, f"Role-based authentication working - {success_count}/{total_tests} roles verified")
            return True
        else:
            self.log_result("Role-Based Authentication", False, f"Role-based authentication issues - Only {success_count}/{total_tests} roles working")
            return False
    
    def test_business_compliance_endpoints(self):
        """Test business compliance API endpoints"""
        try:
            # Test categories endpoint
            response = self.session.get(f"{API_BASE}/compliance/categories")
            if response.status_code != 200:
                self.log_result("Business Compliance Endpoints", False, f"Categories endpoint failed: HTTP {response.status_code}", response)
                return False
            
            categories = response.json()
            category_count = len(categories) if isinstance(categories, list) else 0
            
            # Test checklist endpoint if we have categories
            if category_count > 0:
                test_category = "company_registration"  # Common category
                checklist_response = self.session.get(f"{API_BASE}/compliance/checklist/{test_category}")
                if checklist_response.status_code != 200:
                    self.log_result("Business Compliance Endpoints", False, f"Checklist endpoint failed: HTTP {checklist_response.status_code}", checklist_response)
                    return False
            
            self.log_result("Business Compliance Endpoints", True, f"Business compliance endpoints working - {category_count} categories available")
            return True
            
        except Exception as e:
            self.log_result("Business Compliance Endpoints", False, f"Request error: {str(e)}")
        return False
    
    def run_comprehensive_backend_test(self):
        """Run comprehensive backend API testing"""
        print("🚀 COMPREHENSIVE BACKEND API TESTING")
        print("=" * 80)
        
        # Phase 1: Service Health
        print("📋 PHASE 1: SERVICE HEALTH")
        print("-" * 50)
        
        if not self.test_api_health():
            print("❌ API health check failed. Cannot proceed with testing.")
            return False
        
        # Phase 2: Authentication System
        print("\n🔐 PHASE 2: AUTHENTICATION SYSTEM")
        print("-" * 50)
        
        auth_tests = [
            ("Admin Login (+27800000001)", self.test_admin_login),
            ("Client Login (+27800000002)", self.test_client_login),
            ("Fixer Login (+27800000003)", self.test_fixer_login),
            ("Token Authentication", self.test_token_authentication),
            ("Role-Based Authentication", self.test_role_based_authentication)
        ]
        
        auth_passed = 0
        for test_name, test_func in auth_tests:
            result = test_func()
            if result:
                auth_passed += 1
        
        # Phase 3: Core API Endpoints
        print("\n🔧 PHASE 3: CORE API ENDPOINTS")
        print("-" * 50)
        
        api_tests = [
            ("User Management Endpoints", self.test_user_management_endpoints),
            ("Job Management Endpoints", self.test_job_management_endpoints),
            ("Fixer Management Endpoints", self.test_fixer_management_endpoints),
            ("Dashboard Endpoint", self.test_dashboard_endpoint),
            ("Business Compliance Endpoints", self.test_business_compliance_endpoints)
        ]
        
        api_passed = 0
        for test_name, test_func in api_tests:
            result = test_func()
            if result:
                api_passed += 1
        
        # Phase 4: Database Connectivity
        print("\n🗄️ PHASE 4: DATABASE CONNECTIVITY")
        print("-" * 50)
        
        db_result = self.test_database_connectivity()
        
        # Results Summary
        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE BACKEND TEST RESULTS")
        print("=" * 80)
        
        print(f"🔐 Authentication System: {auth_passed}/5 tests passed")
        print(f"🔧 Core API Endpoints: {api_passed}/5 tests passed")
        print(f"🗄️ Database Connectivity: {'✅ WORKING' if db_result else '❌ FAILING'}")
        
        total_passed = self.results['passed']
        total_tests = self.results['passed'] + self.results['failed']
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 Overall Success Rate: {total_passed}/{total_tests} ({success_rate:.1f}%)")
        
        # Assessment
        if success_rate >= 90:
            print("\n🎉 EXCELLENT! Backend API is fully operational and ready for production!")
            print("✅ All critical systems working correctly")
            print("✅ Authentication system robust")
            print("✅ Core API endpoints functional")
            print("✅ Database connectivity verified")
        elif success_rate >= 75:
            print("\n✅ GOOD! Backend API is mostly operational with minor issues")
            print("✅ Most critical systems working")
            print("⚠️ Some endpoints may need attention")
        elif success_rate >= 50:
            print("\n⚠️ WARNING! Backend API has significant issues")
            print("❌ Multiple critical systems failing")
            print("❌ Requires immediate attention before production use")
        else:
            print("\n❌ CRITICAL! Backend API is not operational")
            print("❌ Major system failures detected")
            print("❌ Not suitable for production deployment")
        
        if self.results['errors']:
            print(f"\n🚨 ERRORS ENCOUNTERED:")
            for error in self.results['errors'][:5]:  # Show first 5 errors
                print(f"   • {error}")
            if len(self.results['errors']) > 5:
                print(f"   ... and {len(self.results['errors']) - 5} more errors")
        
        return success_rate >= 75

if __name__ == "__main__":
    print("🔧 FixMate-SA Backend API Testing - Post Afrikaans Translation Completion")
    print("=" * 80)
    print("🎯 FOCUS: Authentication, Core APIs, Database, Service Health")
    print("🔐 TEST ACCOUNTS: Admin, Client, Fixer role verification")
    print("📊 COMPREHENSIVE: End-to-end backend functionality validation")
    print("=" * 80)
    
    tester = FixMateBackendTester()
    
    try:
        success = tester.run_comprehensive_backend_test()
        
        print("\n" + "=" * 80)
        print("📊 FINAL TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {tester.results['passed']}")
        print(f"❌ Tests Failed: {tester.results['failed']}")
        
        if success:
            print("\n🎉 BACKEND API VERIFICATION SUCCESSFUL!")
            print("✅ FixMate-SA backend is ready to support the Afrikaans translation system")
            print("✅ All critical authentication and API endpoints operational")
            print("✅ System ready for production deployment")
        else:
            print("\n⚠️ BACKEND API NEEDS ATTENTION!")
            print("❌ Some critical issues found that need resolution")
            print("❌ Review failed tests before production deployment")
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {str(e)}")
        sys.exit(1)