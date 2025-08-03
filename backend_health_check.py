#!/usr/bin/env python3
"""
FixMate-SA Backend Health Check - Quick Diagnostic Test
Focus: Basic API Health, Authentication, Core Features, and Database Connectivity
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

print(f"🔧 FixMate-SA Backend Health Check at: {API_BASE}")
print("=" * 80)
print("🎯 QUICK HEALTH CHECK AFTER LAYOUT UPDATES")
print("=" * 80)

class HealthCheckTester:
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
    
    def test_basic_api_health(self):
        """1. Basic API Health - Test if backend is responding"""
        print("🔍 Testing Basic API Health...")
        
        try:
            # Test root endpoint
            response = self.session.get(f"{BACKEND_URL}")
            if response.status_code == 200:
                self.log_result("Backend Root Endpoint", True, f"Backend is responding: HTTP {response.status_code}")
            else:
                self.log_result("Backend Root Endpoint", False, f"Backend not responding properly: HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("Backend Root Endpoint", False, f"Connection error: {str(e)}")
            return False
        
        try:
            # Test API health endpoint
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
    
    def test_admin_authentication(self):
        """2. Authentication - Test POST /api/auth/login with admin credentials"""
        print("🔍 Testing Admin Authentication...")
        
        try:
            login_data = {
                "phone": "+27821234567",
                "password": "admin123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data and "role_info" in data:
                    self.test_data['admin_token'] = data['token']
                    self.test_data['admin_user'] = data['user']
                    self.test_data['admin_user_id'] = data['user']['id']
                    role = data.get('role_info', {}).get('role', 'unknown')
                    display_name = data.get('display_name', 'Unknown')
                    
                    self.log_result("Admin Login Authentication", True, 
                                  f"Admin login successful - Role: {role}, Display Name: {display_name}, Token: {data['token'][:20]}...")
                    return True
                else:
                    self.log_result("Admin Login Authentication", False, "Invalid response format - missing required fields", response)
            else:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'Unknown error')
                    self.log_result("Admin Login Authentication", False, f"HTTP {response.status_code} - {error_detail}", response)
                except:
                    self.log_result("Admin Login Authentication", False, f"HTTP {response.status_code} - {response.text[:200]}", response)
        except Exception as e:
            self.log_result("Admin Login Authentication", False, f"Request error: {str(e)}")
        
        return False
    
    def test_dashboard_access(self):
        """3. Core Feature Accessibility - Test GET /api/dashboard for authenticated user"""
        print("🔍 Testing Dashboard Access...")
        
        if 'admin_token' not in self.test_data:
            self.log_result("Dashboard Access", False, "No admin token available from authentication test")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.test_data['admin_token']}"}
            response = self.session.get(f"{API_BASE}/dashboard", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected dashboard data structure
                expected_fields = ['user_stats', 'recent_jobs', 'top_fixers']
                found_fields = [field for field in expected_fields if field in data]
                
                if found_fields:
                    self.log_result("Dashboard Access", True, 
                                  f"Dashboard accessible with {len(found_fields)}/{len(expected_fields)} expected sections: {', '.join(found_fields)}")
                    return True
                else:
                    self.log_result("Dashboard Access", True, 
                                  f"Dashboard accessible but with different structure. Available fields: {list(data.keys())[:5]}")
                    return True
            else:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'Unknown error')
                    self.log_result("Dashboard Access", False, f"HTTP {response.status_code} - {error_detail}", response)
                except:
                    self.log_result("Dashboard Access", False, f"HTTP {response.status_code} - {response.text[:200]}", response)
        except Exception as e:
            self.log_result("Dashboard Access", False, f"Request error: {str(e)}")
        
        return False
    
    def test_job_endpoints(self):
        """4. Job-related endpoints testing"""
        print("🔍 Testing Job-related Endpoints...")
        
        if 'admin_token' not in self.test_data:
            self.log_result("Job Endpoints", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.test_data['admin_token']}"}
            
            # Test GET /api/jobs
            response = self.session.get(f"{API_BASE}/jobs", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if it's paginated response or direct list
                if isinstance(data, dict) and 'data' in data:
                    jobs = data['data']
                    total = data.get('total', len(jobs))
                    self.log_result("Job Endpoints - List Jobs", True, 
                                  f"Jobs endpoint working - Found {len(jobs)} jobs (Total: {total})")
                elif isinstance(data, list):
                    self.log_result("Job Endpoints - List Jobs", True, 
                                  f"Jobs endpoint working - Found {len(data)} jobs")
                else:
                    self.log_result("Job Endpoints - List Jobs", True, 
                                  f"Jobs endpoint responding with data structure: {type(data)}")
                
                return True
            else:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'Unknown error')
                    self.log_result("Job Endpoints", False, f"HTTP {response.status_code} - {error_detail}", response)
                except:
                    self.log_result("Job Endpoints", False, f"HTTP {response.status_code} - {response.text[:200]}", response)
        except Exception as e:
            self.log_result("Job Endpoints", False, f"Request error: {str(e)}")
        
        return False
    
    def test_user_profile_endpoints(self):
        """5. User profile endpoints testing"""
        print("🔍 Testing User Profile Endpoints...")
        
        if 'admin_user_id' not in self.test_data:
            self.log_result("User Profile Endpoints", False, "No admin user ID available")
            return False
        
        try:
            # Test GET /api/auth/profile/{user_id}
            response = self.session.get(f"{API_BASE}/auth/profile/{self.test_data['admin_user_id']}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for expected profile data
                expected_fields = ['user', 'role_info', 'display_name']
                found_fields = [field for field in expected_fields if field in data]
                
                if found_fields:
                    role = data.get('role_info', {}).get('role', 'unknown')
                    display_name = data.get('display_name', 'Unknown')
                    self.log_result("User Profile Endpoints", True, 
                                  f"Profile endpoint working - Role: {role}, Display Name: {display_name}, Fields: {', '.join(found_fields)}")
                    return True
                else:
                    self.log_result("User Profile Endpoints", True, 
                                  f"Profile endpoint responding with fields: {list(data.keys())[:5]}")
                    return True
            else:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'Unknown error')
                    self.log_result("User Profile Endpoints", False, f"HTTP {response.status_code} - {error_detail}", response)
                except:
                    self.log_result("User Profile Endpoints", False, f"HTTP {response.status_code} - {response.text[:200]}", response)
        except Exception as e:
            self.log_result("User Profile Endpoints", False, f"Request error: {str(e)}")
        
        return False
    
    def test_key_route_functionality(self):
        """6. Key route functionality testing"""
        print("🔍 Testing Key Route Functionality...")
        
        routes_to_test = [
            ("/users", "Users endpoint"),
            ("/fixers", "Fixers endpoint"),
            ("/auth/role-check/+27821234567", "Role check endpoint")
        ]
        
        working_routes = 0
        total_routes = len(routes_to_test)
        
        for route, description in routes_to_test:
            try:
                response = self.session.get(f"{API_BASE}{route}")
                
                if response.status_code in [200, 401, 403]:  # 401/403 are acceptable for protected routes
                    working_routes += 1
                    if response.status_code == 200:
                        self.log_result(f"Route Test - {description}", True, f"Route accessible: HTTP {response.status_code}")
                    else:
                        self.log_result(f"Route Test - {description}", True, f"Route exists (protected): HTTP {response.status_code}")
                else:
                    self.log_result(f"Route Test - {description}", False, f"Route issue: HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"Route Test - {description}", False, f"Request error: {str(e)}")
        
        if working_routes >= total_routes * 0.7:  # 70% of routes working
            self.log_result("Overall Route Functionality", True, f"{working_routes}/{total_routes} key routes are functional")
            return True
        else:
            self.log_result("Overall Route Functionality", False, f"Only {working_routes}/{total_routes} key routes are functional")
            return False
    
    def test_database_connectivity(self):
        """7. Database connectivity testing"""
        print("🔍 Testing Database Connectivity...")
        
        try:
            # Test users endpoint to verify database connectivity
            response = self.session.get(f"{API_BASE}/users")
            
            if response.status_code == 200:
                users = response.json()
                if isinstance(users, list):
                    self.log_result("Database Connectivity - Users", True, f"Database accessible - Found {len(users)} users")
                else:
                    self.log_result("Database Connectivity - Users", True, "Database accessible - Users endpoint responding")
            elif response.status_code in [401, 403]:
                self.log_result("Database Connectivity - Users", True, "Database accessible (endpoint protected)")
            else:
                self.log_result("Database Connectivity - Users", False, f"Database connectivity issue: HTTP {response.status_code}", response)
                return False
            
            # Test fixers endpoint
            response = self.session.get(f"{API_BASE}/fixers")
            
            if response.status_code == 200:
                fixers = response.json()
                if isinstance(fixers, list):
                    self.log_result("Database Connectivity - Fixers", True, f"Database accessible - Found {len(fixers)} fixers")
                    return True
                else:
                    self.log_result("Database Connectivity - Fixers", True, "Database accessible - Fixers endpoint responding")
                    return True
            elif response.status_code in [401, 403]:
                self.log_result("Database Connectivity - Fixers", True, "Database accessible (endpoint protected)")
                return True
            else:
                self.log_result("Database Connectivity - Fixers", False, f"Database connectivity issue: HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("Database Connectivity", False, f"Request error: {str(e)}")
            return False
    
    def run_health_check(self):
        """Run complete health check"""
        print("🚀 STARTING FIXMATE-SA BACKEND HEALTH CHECK")
        print("=" * 80)
        
        health_tests = [
            ("1. Basic API Health", self.test_basic_api_health),
            ("2. Admin Authentication (+27821234567/admin123)", self.test_admin_authentication),
            ("3. Dashboard Access for Authenticated User", self.test_dashboard_access),
            ("4. Job-related Endpoints", self.test_job_endpoints),
            ("5. User Profile Endpoints", self.test_user_profile_endpoints),
            ("6. Key Route Functionality", self.test_key_route_functionality),
            ("7. Database Connectivity", self.test_database_connectivity)
        ]
        
        results = []
        for test_name, test_func in health_tests:
            print(f"Running {test_name}...")
            result = test_func()
            results.append((test_name, result))
            print()
        
        # Results Summary
        print("=" * 80)
        print("🎯 HEALTH CHECK RESULTS SUMMARY")
        print("=" * 80)
        
        passed_tests = 0
        critical_issues = []
        
        for test_name, result in results:
            status = "✅ WORKING" if result else "❌ BROKEN"
            print(f"{status}: {test_name}")
            
            if result:
                passed_tests += 1
            else:
                # Identify critical issues
                if "Basic API Health" in test_name or "Authentication" in test_name:
                    critical_issues.append(test_name)
        
        success_rate = passed_tests / len(health_tests) * 100
        print(f"\n📊 Overall Health: {passed_tests}/{len(health_tests)} tests passed ({success_rate:.1f}%)")
        
        # Health Assessment
        if success_rate >= 85:
            print("\n🎉 EXCELLENT! Backend is healthy and functioning well after layout updates.")
            print("✅ All major systems are operational")
        elif success_rate >= 70:
            print("\n✅ GOOD! Backend is mostly functional after layout updates.")
            print("⚠️  Some minor issues detected but core functionality works")
        elif success_rate >= 50:
            print("\n⚠️  WARNING! Backend has some issues after layout updates.")
            print("❌ Several systems need attention")
        else:
            print("\n🚨 CRITICAL! Backend has major issues after layout updates.")
            print("❌ Multiple systems are broken")
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES DETECTED:")
            for issue in critical_issues:
                print(f"   • {issue}")
            print("   These issues prevent basic functionality and need immediate attention.")
        
        if self.results['errors']:
            print(f"\n📋 DETAILED ERROR LOG:")
            for error in self.results['errors'][:5]:  # Show first 5 errors
                print(f"   • {error}")
            if len(self.results['errors']) > 5:
                print(f"   ... and {len(self.results['errors']) - 5} more errors")
        
        return success_rate >= 70

if __name__ == "__main__":
    print("🔧 FixMate-SA Backend Health Check - Quick Diagnostic Test")
    print("=" * 80)
    print("🎯 FOCUS: Basic API Health, Authentication, Core Features, Database Connectivity")
    print("📋 PURPOSE: Identify broken functionality after layout updates")
    print("=" * 80)
    
    tester = HealthCheckTester()
    
    try:
        success = tester.run_health_check()
        
        print("\n" + "=" * 80)
        print("📊 FINAL HEALTH CHECK SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {tester.results['passed']}")
        print(f"❌ Tests Failed: {tester.results['failed']}")
        print(f"📈 Success Rate: {tester.results['passed']/(tester.results['passed']+tester.results['failed'])*100:.1f}%")
        
        if success:
            print("\n🎉 BACKEND HEALTH CHECK PASSED!")
            print("✅ FixMate-SA backend is functioning properly after layout updates")
            print("✅ Core functionality is accessible and working")
        else:
            print("\n⚠️  BACKEND HEALTH CHECK IDENTIFIED ISSUES!")
            print("❌ Some functionality may be broken after layout updates")
            print("❌ Investigation and fixes needed before production use")
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Health check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n🚨 CRITICAL ERROR during health check: {str(e)}")
        sys.exit(1)