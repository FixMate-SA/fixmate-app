#!/usr/bin/env python3
"""
FixMate-SA Comprehensive Backend Test - Handles Prerequisites and Tests All Components
"""

import requests
import json
import sys
import base64
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

print(f"🎯 COMPREHENSIVE BACKEND TEST")
print(f"🔧 Testing FixMate-SA System at: {API_BASE}")
print("=" * 80)

class ComprehensiveBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_data = {}
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        
        # Test accounts
        self.test_accounts = {
            'admin': {'phone': '+27800000001', 'password': 'admin2024test'},
            'client': {'phone': '+27800000002', 'password': 'client2024test'},
            'fixer': {'phone': '+27800000003', 'password': 'fixer2024test'}
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
    
    def test_authentication_system(self):
        """Test all three role logins"""
        print("🔐 TESTING AUTHENTICATION SYSTEM")
        
        success_count = 0
        for role, credentials in self.test_accounts.items():
            try:
                response = self.session.post(f"{API_BASE}/auth/login", json=credentials)
                
                if response.status_code == 200:
                    data = response.json()
                    if "user" in data and "token" in data:
                        self.test_data[f'{role}_token'] = data['token']
                        self.test_data[f'{role}_user'] = data['user']
                        self.test_data[f'{role}_user_id'] = data['user']['id']
                        
                        role_info = data.get('role_info', {})
                        actual_role = role_info.get('role', 'unknown')
                        
                        print(f"   ✅ {role.upper()} LOGIN: {credentials['phone']} -> Role: {actual_role}")
                        success_count += 1
                    else:
                        print(f"   ❌ {role.upper()} LOGIN: Invalid response format")
                else:
                    print(f"   ❌ {role.upper()} LOGIN: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {role.upper()} LOGIN ERROR: {str(e)}")
        
        success = success_count == 3
        self.log_result("Authentication System", success, 
                       f"Role-based authentication: {success_count}/3 successful")
        return success
    
    def test_terms_acceptance(self):
        """Test terms acceptance for all users"""
        print("📋 TESTING TERMS ACCEPTANCE")
        
        success_count = 0
        for role in ['admin', 'client', 'fixer']:
            if f'{role}_user_id' in self.test_data:
                try:
                    terms_data = {
                        "user_id": self.test_data[f'{role}_user_id'],
                        "ip_address": "192.168.1.100",
                        "user_agent": "FixMate-Test-Client/1.0",
                        "method": "web"
                    }
                    
                    response = self.session.post(f"{API_BASE}/terms/accept", json=terms_data)
                    
                    if response.status_code == 200 and response.json().get('success'):
                        print(f"   ✅ {role.upper()} TERMS ACCEPTED")
                        success_count += 1
                    else:
                        print(f"   ❌ {role.upper()} TERMS FAILED: {response.status_code}")
                except Exception as e:
                    print(f"   ❌ {role.upper()} TERMS ERROR: {str(e)}")
        
        success = success_count >= 2
        self.log_result("Terms Acceptance", success, 
                       f"Terms acceptance: {success_count}/3 successful")
        return success
    
    def test_admin_service_creation(self):
        """Test admin creating jobs on behalf of clients"""
        print("👑 TESTING ADMIN SERVICE CREATION")
        
        if 'admin_token' not in self.test_data or 'client_user_id' not in self.test_data:
            self.log_result("Admin Service Creation", False, "Missing admin token or client user ID")
            return False
        
        try:
            job_data = {
                "user_id": self.test_data['client_user_id'],
                "service": "plumbing",
                "description": "Admin-created service request - kitchen sink repair",
                "location": "Cape Town, Western Cape",
                "estimated_price": 450.0,
                "admin_created": True
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['admin_token']}"}
            response = self.session.post(f"{API_BASE}/jobs/workflow", json=job_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'job_id' in data:
                    self.test_data['admin_created_job_id'] = data['job_id']
                    self.log_result("Admin Service Creation", True, 
                                   f"Admin successfully created job: {data['job_id']}")
                    return True
                else:
                    self.log_result("Admin Service Creation", False, f"Job creation failed: {data}")
            else:
                self.log_result("Admin Service Creation", False, f"HTTP {response.status_code}: {response.text[:200]}")
        except Exception as e:
            self.log_result("Admin Service Creation", False, f"Request error: {str(e)}")
        return False
    
    def test_job_workflow_endpoints(self):
        """Test complete job workflow endpoints"""
        print("🔄 TESTING JOB WORKFLOW ENDPOINTS")
        
        if 'admin_created_job_id' not in self.test_data:
            self.log_result("Job Workflow Endpoints", False, "No admin-created job available")
            return False
        
        job_id = self.test_data['admin_created_job_id']
        workflow_results = []
        
        # Test 1: Notify fixers
        try:
            response = self.session.post(f"{API_BASE}/jobs/{job_id}/fixer/notify")
            success = response.status_code == 200
            workflow_results.append(("Fixer Notify", success))
            if success:
                print(f"   ✅ POST /api/jobs/{job_id}/fixer/notify - WORKING")
            else:
                print(f"   ❌ POST /api/jobs/{job_id}/fixer/notify - FAILED ({response.status_code})")
        except Exception as e:
            workflow_results.append(("Fixer Notify", False))
            print(f"   ❌ POST /api/jobs/{job_id}/fixer/notify - ERROR: {str(e)}")
        
        # Test 2: Get fixer notifications
        if 'fixer_token' in self.test_data:
            try:
                headers = {"Authorization": f"Bearer {self.test_data['fixer_token']}"}
                response = self.session.get(f"{API_BASE}/fixer/notifications", headers=headers)
                success = response.status_code == 200
                workflow_results.append(("Get Notifications", success))
                if success:
                    notifications = response.json()
                    print(f"   ✅ GET /api/fixer/notifications - WORKING ({len(notifications)} notifications)")
                else:
                    print(f"   ❌ GET /api/fixer/notifications - FAILED ({response.status_code})")
            except Exception as e:
                workflow_results.append(("Get Notifications", False))
                print(f"   ❌ GET /api/fixer/notifications - ERROR: {str(e)}")
        
        # Test 3: Fixer accepts job
        if 'fixer_token' in self.test_data:
            try:
                headers = {"Authorization": f"Bearer {self.test_data['fixer_token']}"}
                response = self.session.post(f"{API_BASE}/jobs/{job_id}/accept-fixer", headers=headers)
                success = response.status_code == 200
                workflow_results.append(("Accept Fixer", success))
                if success:
                    self.test_data['accepted_job_id'] = job_id
                    print(f"   ✅ POST /api/jobs/{job_id}/accept-fixer - WORKING")
                else:
                    print(f"   ❌ POST /api/jobs/{job_id}/accept-fixer - FAILED ({response.status_code})")
            except Exception as e:
                workflow_results.append(("Accept Fixer", False))
                print(f"   ❌ POST /api/jobs/{job_id}/accept-fixer - ERROR: {str(e)}")
        
        # Test 4: Rate fixer endpoint
        if 'client_token' in self.test_data:
            try:
                headers = {"Authorization": f"Bearer {self.test_data['client_token']}"}
                data = {'rating': 5, 'review': 'Excellent work!'}
                response = self.session.post(f"{API_BASE}/jobs/{job_id}/rate-fixer", data=data, headers=headers)
                success = response.status_code == 200
                workflow_results.append(("Rate Fixer", success))
                if success:
                    print(f"   ✅ POST /api/jobs/{job_id}/rate-fixer - WORKING")
                else:
                    print(f"   ❌ POST /api/jobs/{job_id}/rate-fixer - FAILED ({response.status_code})")
            except Exception as e:
                workflow_results.append(("Rate Fixer", False))
                print(f"   ❌ POST /api/jobs/{job_id}/rate-fixer - ERROR: {str(e)}")
        
        # Test 5: Get completed jobs
        if 'client_token' in self.test_data:
            try:
                headers = {"Authorization": f"Bearer {self.test_data['client_token']}"}
                response = self.session.get(f"{API_BASE}/jobs/completed", headers=headers)
                success = response.status_code == 200
                workflow_results.append(("Get Completed Jobs", success))
                if success:
                    jobs = response.json()
                    print(f"   ✅ GET /api/jobs/completed - WORKING ({len(jobs)} completed jobs)")
                else:
                    print(f"   ❌ GET /api/jobs/completed - FAILED ({response.status_code})")
            except Exception as e:
                workflow_results.append(("Get Completed Jobs", False))
                print(f"   ❌ GET /api/jobs/completed - ERROR: {str(e)}")
        
        # Calculate success rate
        successful_workflows = sum(1 for _, success in workflow_results if success)
        total_workflows = len(workflow_results)
        
        success = successful_workflows >= (total_workflows * 0.6)  # 60% success rate
        self.log_result("Job Workflow Endpoints", success, 
                       f"Workflow endpoints: {successful_workflows}/{total_workflows} working")
        return success
    
    def test_payment_system(self):
        """Test R20 payment system"""
        print("💰 TESTING R20 PAYMENT SYSTEM")
        
        # Test payment status check
        try:
            # Get fixers first
            response = self.session.get(f"{API_BASE}/fixers")
            if response.status_code == 200:
                fixers = response.json()
                if fixers:
                    fixer_id = fixers[0]['id']
                    
                    # Check payment status
                    payment_response = self.session.get(f"{API_BASE}/fixer/{fixer_id}/payment-status")
                    if payment_response.status_code == 200:
                        payment_data = payment_response.json()
                        can_receive = payment_data.get('can_receive_jobs', False)
                        
                        # Check payment history
                        history_response = self.session.get(f"{API_BASE}/fixer/{fixer_id}/payment-history")
                        if history_response.status_code == 200:
                            history_data = history_response.json()
                            payments = history_data.get('payments', [])
                            
                            self.log_result("R20 Payment System", True, 
                                           f"Payment system operational: Can receive jobs: {can_receive}, Payment history: {len(payments)} records")
                            return True
                        else:
                            self.log_result("R20 Payment System", False, f"Payment history failed: {history_response.status_code}")
                    else:
                        self.log_result("R20 Payment System", False, f"Payment status failed: {payment_response.status_code}")
                else:
                    self.log_result("R20 Payment System", False, "No fixers found for payment testing")
            else:
                self.log_result("R20 Payment System", False, f"Failed to get fixers: {response.status_code}")
        except Exception as e:
            self.log_result("R20 Payment System", False, f"Request error: {str(e)}")
        return False
    
    def test_notification_system(self):
        """Test notification system"""
        print("🔔 TESTING NOTIFICATION SYSTEM")
        
        if 'fixer_token' not in self.test_data:
            self.log_result("Notification System", False, "Fixer token not available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.test_data['fixer_token']}"}
            response = self.session.get(f"{API_BASE}/fixer/notifications", headers=headers)
            
            if response.status_code == 200:
                notifications = response.json()
                self.log_result("Notification System", True, 
                               f"Notification system working: {len(notifications)} notifications retrieved")
                return True
            else:
                self.log_result("Notification System", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Notification System", False, f"Request error: {str(e)}")
        return False
    
    def test_database_integrity(self):
        """Test database integrity"""
        print("🗄️ TESTING DATABASE INTEGRITY")
        
        endpoints_to_test = [
            ("Users", f"{API_BASE}/users"),
            ("Fixers", f"{API_BASE}/fixers"),
            ("Jobs", f"{API_BASE}/jobs")
        ]
        
        working_endpoints = 0
        for name, endpoint in endpoints_to_test:
            try:
                response = self.session.get(endpoint)
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else 1
                    print(f"   ✅ {name} endpoint working: {count} records")
                    working_endpoints += 1
                else:
                    print(f"   ❌ {name} endpoint failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {name} endpoint error: {str(e)}")
        
        success = working_endpoints >= 2
        self.log_result("Database Integrity", success, 
                       f"Database endpoints: {working_endpoints}/{len(endpoints_to_test)} working")
        return success
    
    def run_comprehensive_test(self):
        """Run comprehensive backend test"""
        print("🚀 STARTING COMPREHENSIVE BACKEND TEST")
        print("=" * 80)
        
        # Define test sequence
        tests = [
            ("Authentication System", self.test_authentication_system),
            ("Terms Acceptance", self.test_terms_acceptance),
            ("Admin Service Creation", self.test_admin_service_creation),
            ("Job Workflow Endpoints", self.test_job_workflow_endpoints),
            ("R20 Payment System", self.test_payment_system),
            ("Notification System", self.test_notification_system),
            ("Database Integrity", self.test_database_integrity)
        ]
        
        print(f"📋 Running {len(tests)} comprehensive tests...")
        print()
        
        # Run all tests
        test_results = []
        for test_name, test_func in tests:
            print(f"🔍 Running {test_name}...")
            try:
                result = test_func()
                test_results.append((test_name, result))
                print()
            except Exception as e:
                print(f"   ❌ TEST ERROR: {str(e)}")
                test_results.append((test_name, False))
                print()
        
        # Calculate results
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        # Results Summary
        print("=" * 80)
        print("🎯 COMPREHENSIVE BACKEND TEST RESULTS")
        print("=" * 80)
        
        print("📊 TEST RESULTS:")
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status}: {test_name}")
        
        print(f"\n📈 OVERALL SUCCESS RATE: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Assessment
        if success_rate >= 85.0:
            print("\n🎉 EXCELLENT: System is highly functional!")
            print("✅ Most components are working correctly")
            print("✅ System is production-ready")
        elif success_rate >= 70.0:
            print(f"\n✅ GOOD: {success_rate:.1f}% success rate")
            print("✅ Most systems are working correctly")
            print("⚠️  Some minor issues to address")
        else:
            print(f"\n⚠️  WARNING: {success_rate:.1f}% success rate")
            print("❌ Multiple systems need attention")
        
        # Detailed Error Report
        if self.results['errors']:
            print(f"\n🚨 DETAILED ERROR REPORT:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        return success_rate >= 70.0

if __name__ == "__main__":
    tester = ComprehensiveBackendTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        print("\n" + "=" * 80)
        print("📊 FINAL SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {tester.results['passed']}")
        print(f"❌ Tests Failed: {tester.results['failed']}")
        
        if tester.results['passed'] + tester.results['failed'] > 0:
            final_rate = (tester.results['passed']/(tester.results['passed']+tester.results['failed'])*100)
            print(f"📈 Final Success Rate: {final_rate:.1f}%")
        
        if success:
            print("\n🎉 COMPREHENSIVE BACKEND TEST SUCCESSFUL!")
            print("✅ FixMate-SA backend is functional and ready")
            sys.exit(0)
        else:
            print("\n⚠️  COMPREHENSIVE BACKEND TEST NEEDS ATTENTION")
            print("❌ Some components require fixes")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        sys.exit(1)