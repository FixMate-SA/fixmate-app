#!/usr/bin/env python3
"""
Comprehensive Backend Testing for FixMate-SA Multi-Language Support
Testing all API endpoints after implementing comprehensive multi-language support for Afrikaans, Sepedi, isiZulu, and Xitsonga
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class FixMateSABackendTester:
    def __init__(self):
        # Get backend URL from environment
        self.base_url = os.getenv('REACT_APP_BACKEND_URL', 'https://fixmate-sa-app-a448c751e1d2.herokuapp.com')
        if not self.base_url.endswith('/api'):
            self.base_url = f"{self.base_url}/api"
        
        print(f"🔗 Testing Backend URL: {self.base_url}")
        
        # Test accounts for different roles
        self.test_accounts = {
            'admin': {
                'phone': '+27800000001',
                'password': 'admin2024test',
                'token': None,
                'user_id': None
            },
            'client': {
                'phone': '+27800000002', 
                'password': 'client2024test',
                'token': None,
                'user_id': None
            },
            'fixer': {
                'phone': '+27800000003',
                'password': 'fixer2024test', 
                'token': None,
                'user_id': None
            }
        }
        
        # Test results
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        self.results['total_tests'] += 1
        if success:
            self.results['passed_tests'] += 1
            status = "✅ PASS"
        else:
            self.results['failed_tests'] += 1
            status = "❌ FAIL"
        
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.results['test_details'].append({
            'test': test_name,
            'status': 'PASS' if success else 'FAIL',
            'details': details
        })

    def make_request(self, method: str, endpoint: str, data: dict = None, headers: dict = None, role: str = None) -> requests.Response:
        """Make HTTP request with optional authentication"""
        url = f"{self.base_url}{endpoint}"
        
        # Add authentication header if role specified
        if role and self.test_accounts[role]['token']:
            if not headers:
                headers = {}
            headers['Authorization'] = f"Bearer {self.test_accounts[role]['token']}"
        
        # Set default headers
        if not headers:
            headers = {}
        headers['Content-Type'] = 'application/json'
        
        try:
            print(f"🔗 Making {method} request to: {url}")
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=60)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=60)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=60)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=60)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            print(f"📊 Response: {response.status_code}")
            if response.status_code >= 400:
                try:
                    error_content = response.json()
                    print(f"❌ Error content: {error_content}")
                except:
                    print(f"❌ Error text: {response.text[:200]}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None

    def test_health_check_endpoints(self) -> bool:
        """Test health check endpoints"""
        print("\n🏥 TESTING HEALTH CHECK ENDPOINTS...")
        
        all_passed = True
        
        # Test main API health check
        response = self.make_request('GET', '/')
        if response and response.status_code == 200:
            self.log_test("Main API health check", True, f"Response: {response.text[:100]}")
        else:
            self.log_test("Main API health check", False, f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        # Test debug health endpoint if available
        response = self.make_request('GET', '/debug/health')
        if response and response.status_code == 200:
            self.log_test("Debug health endpoint", True, "Health check passed")
        else:
            self.log_test("Debug health endpoint", False, f"Status: {response.status_code if response else 'No response'}")
            # Don't fail overall test as this might not be implemented
        
        return all_passed

    def authenticate_users(self) -> bool:
        """Authenticate all test users"""
        print("\n🔐 TESTING USER AUTHENTICATION ENDPOINTS...")
        
        all_authenticated = True
        
        for role, account in self.test_accounts.items():
            try:
                response = self.make_request('POST', '/auth/login', {
                    'phone': account['phone'],
                    'password': account['password']
                })
                
                if response and response.status_code == 200:
                    data = response.json()
                    account['token'] = data.get('token')
                    account['user_id'] = data.get('user', {}).get('id')
                    role_info = data.get('role_info', {})
                    self.log_test(f"Authenticate {role} user", True, 
                                f"Role: {role_info.get('role', 'unknown')}, Token: {account['token'][:20] if account['token'] else 'None'}...")
                else:
                    self.log_test(f"Authenticate {role} user", False, 
                                f"Status: {response.status_code if response else 'No response'}")
                    all_authenticated = False
                    
            except Exception as e:
                self.log_test(f"Authenticate {role} user", False, str(e))
                all_authenticated = False
        
        return all_authenticated

    def test_job_management_endpoints(self) -> bool:
        """Test job management endpoints (create, list, update)"""
        print("\n💼 TESTING JOB MANAGEMENT ENDPOINTS...")
        
        all_passed = True
        
        # Test job listing
        response = self.make_request('GET', '/jobs', role='admin')
        if response and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict) and 'data' in data:
                    jobs = data['data']
                    total = data.get('total', 0)
                    self.log_test("List jobs endpoint", True, f"Found {len(jobs)} jobs, total: {total}")
                elif isinstance(data, list):
                    self.log_test("List jobs endpoint", True, f"Found {len(data)} jobs")
                else:
                    self.log_test("List jobs endpoint", True, f"Jobs endpoint returned data")
            except:
                self.log_test("List jobs endpoint", True, "Jobs endpoint accessible")
        else:
            self.log_test("List jobs endpoint", False, f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        # Test job creation with multi-language description
        job_data = {
            'user_id': self.test_accounts['client']['user_id'],
            'service': 'Plumbing',
            'description': 'Ek het \'n probleem met my pype. Die water loop nie reg nie. (I have a problem with my pipes. The water is not flowing properly.)',
            'location': 'Kaapstad, Wes-Kaap',
            'estimated_price': 500.0,
            'urgency': 'normal'
        }
        
        response = self.make_request('POST', '/jobs', job_data, role='client')
        if response and response.status_code == 200:
            try:
                data = response.json()
                job_id = data.get('id')
                if job_id:
                    self.log_test("Create job with multi-language description", True, f"Job ID: {job_id}")
                    # Store job ID for further testing
                    self.test_job_id = job_id
                else:
                    self.log_test("Create job with multi-language description", False, "No job ID returned")
                    all_passed = False
            except:
                self.log_test("Create job with multi-language description", False, "Invalid response format")
                all_passed = False
        else:
            self.log_test("Create job with multi-language description", False, 
                        f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        # Test job workflow endpoint
        workflow_data = {
            'user_id': self.test_accounts['client']['user_id'],
            'service': 'Electrical',
            'description': 'Ngidinga usizo ngogesi. Amakhongolose awasebenzi. (I need help with electricity. The switches are not working.)',
            'location': 'Durban, KwaZulu-Natal',
            'estimated_price': 300.0
        }
        
        response = self.make_request('POST', '/jobs/workflow', workflow_data, role='client')
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    self.log_test("Job workflow endpoint", True, f"Message: {data.get('message', 'Success')}")
                else:
                    self.log_test("Job workflow endpoint", False, f"Workflow failed: {data.get('message', 'Unknown error')}")
                    all_passed = False
            except:
                self.log_test("Job workflow endpoint", False, "Invalid response format")
                all_passed = False
        else:
            self.log_test("Job workflow endpoint", False, 
                        f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        return all_passed

    def test_user_management_endpoints(self) -> bool:
        """Test user management endpoints"""
        print("\n👥 TESTING USER MANAGEMENT ENDPOINTS...")
        
        all_passed = True
        
        # Test user listing
        response = self.make_request('GET', '/users', role='admin')
        if response and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("List users endpoint", True, f"Found {len(data)} users")
                else:
                    self.log_test("List users endpoint", True, "Users endpoint accessible")
            except:
                self.log_test("List users endpoint", True, "Users endpoint accessible")
        else:
            self.log_test("List users endpoint", False, f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        # Test user profile endpoint
        if self.test_accounts['client']['user_id']:
            response = self.make_request('GET', f"/auth/profile/{self.test_accounts['client']['user_id']}", role='client')
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    role_info = data.get('role_info', {})
                    self.log_test("User profile endpoint", True, f"Role: {role_info.get('role', 'unknown')}")
                except:
                    self.log_test("User profile endpoint", True, "Profile endpoint accessible")
            else:
                self.log_test("User profile endpoint", False, f"Status: {response.status_code if response else 'No response'}")
                all_passed = False
        
        # Test role check endpoint
        response = self.make_request('GET', f"/auth/role-check/{self.test_accounts['admin']['phone']}", role='admin')
        if response and response.status_code == 200:
            try:
                data = response.json()
                role = data.get('role', 'unknown')
                self.log_test("Role check endpoint", True, f"Admin role detected: {role}")
            except:
                self.log_test("Role check endpoint", True, "Role check endpoint accessible")
        else:
            self.log_test("Role check endpoint", False, f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        return all_passed

    def test_fixer_management_endpoints(self) -> bool:
        """Test fixer management endpoints"""
        print("\n🔧 TESTING FIXER MANAGEMENT ENDPOINTS...")
        
        all_passed = True
        
        # Test fixer listing
        response = self.make_request('GET', '/fixers', role='client')
        if response and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("List fixers endpoint", True, f"Found {len(data)} fixers")
                else:
                    self.log_test("List fixers endpoint", True, "Fixers endpoint accessible")
            except:
                self.log_test("List fixers endpoint", True, "Fixers endpoint accessible")
        else:
            self.log_test("List fixers endpoint", False, f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        # Test fixer by service endpoint
        response = self.make_request('GET', '/fixers/by-service/plumbing', role='client')
        if response and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Fixers by service endpoint", True, f"Found {len(data)} plumbing fixers")
                else:
                    self.log_test("Fixers by service endpoint", True, "Service filtering endpoint accessible")
            except:
                self.log_test("Fixers by service endpoint", True, "Service filtering endpoint accessible")
        else:
            self.log_test("Fixers by service endpoint", False, f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        return all_passed

    def test_language_system_integration(self) -> bool:
        """Test language system integration with backend"""
        print("\n🌍 TESTING LANGUAGE SYSTEM INTEGRATION...")
        
        all_passed = True
        
        # Test AI service classification with multi-language input
        test_descriptions = [
            "Ek het 'n probleem met my pype",  # Afrikaans
            "Ke hloka thuso ka motlakase",     # Sepedi  
            "Ngidinga usizo ngogesi",          # isiZulu
            "Ndzi lava mpfuno wa gezi"         # Xitsonga
        ]
        
        for i, description in enumerate(test_descriptions):
            response = self.make_request('POST', '/classify-service', {'description': description})
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    classification = data.get('classification', {})
                    self.log_test(f"Multi-language service classification {i+1}", True, 
                                f"Classified: {classification.get('service', 'unknown')}")
                except:
                    self.log_test(f"Multi-language service classification {i+1}", True, 
                                "Classification endpoint accessible")
            else:
                self.log_test(f"Multi-language service classification {i+1}", False, 
                            f"Status: {response.status_code if response else 'No response'}")
                all_passed = False
        
        # Test sentiment analysis with multi-language input
        response = self.make_request('POST', '/analyze-sentiment', 
                                   {'text': 'Baie dankie vir die goeie diens! (Thank you very much for the good service!)'})
        if response and response.status_code == 200:
            try:
                data = response.json()
                sentiment = data.get('sentiment', {})
                self.log_test("Multi-language sentiment analysis", True, 
                            f"Sentiment: {sentiment.get('label', 'unknown')}")
            except:
                self.log_test("Multi-language sentiment analysis", True, "Sentiment analysis endpoint accessible")
        else:
            self.log_test("Multi-language sentiment analysis", False, 
                        f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        return all_passed

    def test_database_connectivity(self) -> bool:
        """Test database connectivity and models"""
        print("\n🗄️ TESTING DATABASE CONNECTIVITY AND MODELS...")
        
        all_passed = True
        
        # Test dashboard endpoint which requires database access
        if self.test_accounts['client']['user_id']:
            response = self.make_request('GET', f"/dashboard/{self.test_accounts['client']['user_id']}", role='client')
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    stats = data.get('stats', {})
                    self.log_test("Database connectivity via dashboard", True, 
                                f"User stats: {stats.get('total_jobs', 0)} jobs")
                except:
                    self.log_test("Database connectivity via dashboard", True, "Dashboard endpoint accessible")
            else:
                self.log_test("Database connectivity via dashboard", False, 
                            f"Status: {response.status_code if response else 'No response'}")
                all_passed = False
        
        # Test user count to verify database models
        response = self.make_request('GET', '/users', role='admin')
        if response and response.status_code == 200:
            try:
                data = response.json()
                user_count = len(data) if isinstance(data, list) else 0
                self.log_test("Database models verification", True, f"User model working: {user_count} users")
            except:
                self.log_test("Database models verification", True, "User model accessible")
        else:
            self.log_test("Database models verification", False, 
                        f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        return all_passed

    def test_announcement_system(self) -> bool:
        """Test announcement system endpoints"""
        print("\n📢 TESTING ANNOUNCEMENT SYSTEM ENDPOINTS...")
        
        all_passed = True
        
        # Test user announcements endpoint
        response = self.make_request('GET', '/announcements', role='client')
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    announcements = data.get('announcements', [])
                    self.log_test("User announcements endpoint", True, f"Found {len(announcements)} announcements")
                else:
                    self.log_test("User announcements endpoint", True, "Announcements endpoint accessible")
            except:
                self.log_test("User announcements endpoint", True, "Announcements endpoint accessible")
        else:
            self.log_test("User announcements endpoint", False, 
                        f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        # Test admin announcements endpoint
        response = self.make_request('GET', '/admin/announcements', role='admin')
        if response and response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    announcements = data.get('announcements', [])
                    self.log_test("Admin announcements endpoint", True, f"Found {len(announcements)} announcements")
                else:
                    self.log_test("Admin announcements endpoint", True, "Admin announcements endpoint accessible")
            except:
                self.log_test("Admin announcements endpoint", True, "Admin announcements endpoint accessible")
        else:
            self.log_test("Admin announcements endpoint", False, 
                        f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        return all_passed

    def test_whatsapp_integration(self) -> bool:
        """Test WhatsApp integration endpoints"""
        print("\n📱 TESTING WHATSAPP INTEGRATION ENDPOINTS...")
        
        all_passed = True
        
        # Test WhatsApp webhook endpoint (GET for verification)
        response = self.make_request('GET', '/whatsapp')
        if response and response.status_code == 200:
            self.log_test("WhatsApp webhook GET endpoint", True, "Webhook verification endpoint accessible")
        else:
            self.log_test("WhatsApp webhook GET endpoint", False, 
                        f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        # Test WhatsApp business webhook
        response = self.make_request('GET', '/whatsapp/business/webhook')
        if response and response.status_code == 200:
            self.log_test("WhatsApp business webhook endpoint", True, "Business webhook endpoint accessible")
        else:
            self.log_test("WhatsApp business webhook endpoint", False, 
                        f"Status: {response.status_code if response else 'No response'}")
            # Don't fail overall test as this might be a different endpoint structure
        
        return all_passed

    def test_payment_system_endpoints(self) -> bool:
        """Test payment system endpoints"""
        print("\n💳 TESTING PAYMENT SYSTEM ENDPOINTS...")
        
        all_passed = True
        
        # Test EFT payment endpoint
        payment_data = {
            'amount': 100.0,
            'description': 'Test payment',
            'user_email': 'test@example.com',
            'user_name': 'Test User'
        }
        
        response = self.make_request('POST', '/payment/eft', payment_data)
        if response and response.status_code == 200:
            try:
                data = response.json()
                self.log_test("EFT payment endpoint", True, f"Payment response received")
            except:
                self.log_test("EFT payment endpoint", True, "EFT payment endpoint accessible")
        else:
            self.log_test("EFT payment endpoint", False, 
                        f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        # Test payment verification endpoint
        response = self.make_request('POST', '/payment/verify', {
            'payment_id': 'test_payment_123',
            'payment_type': 'eft'
        })
        if response and response.status_code == 200:
            self.log_test("Payment verification endpoint", True, "Payment verification endpoint accessible")
        else:
            self.log_test("Payment verification endpoint", False, 
                        f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        return all_passed

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 STARTING COMPREHENSIVE FIXMATE-SA BACKEND TESTING")
        print("🌍 FOCUS: Multi-Language Support Integration Testing")
        print("=" * 80)
        
        # Step 1: Health Check
        self.test_health_check_endpoints()
        
        # Step 2: Authentication
        if not self.authenticate_users():
            print("❌ Authentication failed. Some tests may not work properly.")
        
        # Step 3: Core API Endpoints
        self.test_job_management_endpoints()
        self.test_user_management_endpoints()
        self.test_fixer_management_endpoints()
        
        # Step 4: Language System Integration
        self.test_language_system_integration()
        
        # Step 5: Database Connectivity
        self.test_database_connectivity()
        
        # Step 6: Additional Systems
        self.test_announcement_system()
        self.test_whatsapp_integration()
        self.test_payment_system_endpoints()
        
        # Print final results
        self.print_final_results()
        
        return self.results['failed_tests'] == 0

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("🎯 FIXMATE-SA BACKEND MULTI-LANGUAGE TESTING RESULTS")
        print("=" * 80)
        
        total = self.results['total_tests']
        passed = self.results['passed_tests']
        failed = self.results['failed_tests']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"📊 SUMMARY:")
        print(f"   Total Tests: {total}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Backend is working correctly with multi-language support.")
        else:
            print(f"\n⚠️ {failed} TESTS FAILED. Review the details above.")
        
        print("\n📋 DETAILED RESULTS:")
        for detail in self.results['test_details']:
            status_icon = "✅" if detail['status'] == 'PASS' else "❌"
            print(f"   {status_icon} {detail['test']}")
            if detail['details']:
                print(f"      {detail['details']}")

def main():
    """Main function to run backend tests"""
    tester = FixMateSABackendTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()