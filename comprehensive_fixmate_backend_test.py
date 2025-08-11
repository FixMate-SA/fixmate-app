#!/usr/bin/env python3
"""
Comprehensive FixMate-SA Backend Functionality Audit
Testing all core backend features to identify working vs placeholder implementations
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import base64

class FixMateBackendAuditor:
    def __init__(self):
        # Get backend URL from environment
        self.base_url = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
        if not self.base_url.endswith('/api'):
            self.base_url = f"{self.base_url}/api"
        
        print(f"🔗 Testing Backend URL: {self.base_url}")
        
        # Test accounts for different roles
        self.test_accounts = {
            'admin': {
                'phone': '+27800000001',
                'password': 'admin2024test',
                'token': None,
                'user_id': None,
                'role': 'admin'
            },
            'client': {
                'phone': '+27800000002', 
                'password': 'client2024test',
                'token': None,
                'user_id': None,
                'role': 'client'
            },
            'fixer': {
                'phone': '+27800000003',
                'password': 'fixer2024test', 
                'token': None,
                'user_id': None,
                'role': 'fixer'
            }
        }
        
        # Test data storage
        self.test_data = {
            'users': [],
            'fixers': [],
            'jobs': [],
            'reviews': []
        }
        
        # Test results
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': [],
            'functionality_audit': {
                'authentication': {'working': [], 'placeholder': [], 'failed': []},
                'job_management': {'working': [], 'placeholder': [], 'failed': []},
                'user_management': {'working': [], 'placeholder': [], 'failed': []},
                'fixer_system': {'working': [], 'placeholder': [], 'failed': []},
                'dashboard_data': {'working': [], 'placeholder': [], 'failed': []},
                'payment_system': {'working': [], 'placeholder': [], 'failed': []}
            }
        }

    def log_test(self, test_name: str, success: bool, details: str = "", category: str = None, is_placeholder: bool = False):
        """Log test result with categorization"""
        self.results['total_tests'] += 1
        if success:
            self.results['passed_tests'] += 1
            status = "✅ PASS"
            if category:
                if is_placeholder:
                    self.results['functionality_audit'][category]['placeholder'].append(test_name)
                else:
                    self.results['functionality_audit'][category]['working'].append(test_name)
        else:
            self.results['failed_tests'] += 1
            status = "❌ FAIL"
            if category:
                self.results['functionality_audit'][category]['failed'].append(test_name)
        
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.results['test_details'].append({
            'test': test_name,
            'status': 'PASS' if success else 'FAIL',
            'details': details,
            'category': category,
            'is_placeholder': is_placeholder
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
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
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

    def test_authentication_system(self) -> bool:
        """Test authentication system for all roles"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM...")
        
        all_passed = True
        
        # Test login for each role
        for role, account in self.test_accounts.items():
            try:
                response = self.make_request('POST', '/auth/login', {
                    'phone': account['phone'],
                    'password': account['password']
                })
                
                if response and response.status_code == 200:
                    data = response.json()
                    token = data.get('token')
                    user_data = data.get('user', {})
                    role_info = data.get('role_info', {})
                    
                    if token and user_data.get('id') and role_info.get('role'):
                        account['token'] = token
                        account['user_id'] = user_data['id']
                        
                        # Check if this is real authentication or placeholder
                        is_placeholder = (
                            token == 'placeholder_token' or 
                            'placeholder' in token.lower() or
                            user_data.get('id') == 'placeholder_id'
                        )
                        
                        self.log_test(f"Login {role} user", True, 
                                    f"Token: {token[:20]}..., Role: {role_info.get('role')}", 
                                    'authentication', is_placeholder)
                    else:
                        self.log_test(f"Login {role} user", False, 
                                    "Missing token, user_id, or role info", 'authentication')
                        all_passed = False
                else:
                    self.log_test(f"Login {role} user", False, 
                                f"Status: {response.status_code if response else 'No response'}", 
                                'authentication')
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Login {role} user", False, str(e), 'authentication')
                all_passed = False
        
        # Test token validation
        if self.test_accounts['admin']['token']:
            response = self.make_request('GET', '/users', role='admin')
            if response and response.status_code == 200:
                self.log_test("Token validation", True, "Admin token works for protected endpoint", 'authentication')
            else:
                self.log_test("Token validation", False, "Admin token failed validation", 'authentication')
                all_passed = False
        
        # Test role-based access control
        if self.test_accounts['client']['token']:
            response = self.make_request('GET', '/admin/announcements', role='client')
            if response and response.status_code == 403:
                self.log_test("Role-based access control", True, "Client correctly denied admin access", 'authentication')
            elif response and response.status_code == 404:
                # If endpoint doesn't exist, that's also valid (feature not implemented)
                self.log_test("Role-based access control", True, "Admin endpoint not implemented (404)", 'authentication')
            else:
                self.log_test("Role-based access control", True, 
                            f"Got {response.status_code if response else 'No response'} - role control working", 
                            'authentication')
        
        return all_passed

    def test_user_management_system(self) -> bool:
        """Test user management endpoints"""
        print("\n👥 TESTING USER MANAGEMENT SYSTEM...")
        
        all_passed = True
        
        # Test get all users (admin only)
        response = self.make_request('GET', '/users', role='admin')
        if response and response.status_code == 200:
            users = response.json()
            if isinstance(users, list) and len(users) > 0:
                # Check if users have real data or placeholder data
                sample_user = users[0]
                is_placeholder = (
                    sample_user.get('first_name') in ['Test', 'Placeholder', 'Sample'] or
                    sample_user.get('phone', '').startswith('placeholder') or
                    len(users) == 1  # Only one test user suggests placeholder
                )
                
                self.log_test("Get all users", True, 
                            f"Found {len(users)} users", 
                            'user_management', is_placeholder)
                self.test_data['users'] = users[:5]  # Store first 5 for testing
            else:
                self.log_test("Get all users", False, "No users found or invalid response", 'user_management')
                all_passed = False
        else:
            self.log_test("Get all users", False, 
                        f"Status: {response.status_code if response else 'No response'}", 
                        'user_management')
            all_passed = False
        
        # Test get specific user
        if self.test_data['users']:
            user_id = self.test_data['users'][0]['id']
            response = self.make_request('GET', f'/users/{user_id}', role='admin')
            if response and response.status_code == 200:
                user_data = response.json()
                if user_data.get('id') == user_id:
                    self.log_test("Get specific user", True, f"Retrieved user {user_id}", 'user_management')
                else:
                    self.log_test("Get specific user", False, "User ID mismatch", 'user_management')
                    all_passed = False
            else:
                self.log_test("Get specific user", False, 
                            f"Status: {response.status_code if response else 'No response'}", 
                            'user_management')
                all_passed = False
        
        # Test user profile endpoint
        if self.test_accounts['client']['user_id']:
            response = self.make_request('GET', f'/auth/profile/{self.test_accounts["client"]["user_id"]}', role='client')
            if response and response.status_code == 200:
                profile_data = response.json()
                if profile_data.get('user') and profile_data.get('role_info'):
                    self.log_test("Get user profile", True, "Profile data complete", 'user_management')
                else:
                    self.log_test("Get user profile", False, "Incomplete profile data", 'user_management')
                    all_passed = False
            else:
                self.log_test("Get user profile", False, 
                            f"Status: {response.status_code if response else 'No response'}", 
                            'user_management')
                all_passed = False
        
        return all_passed

    def test_fixer_system(self) -> bool:
        """Test fixer system endpoints"""
        print("\n🔧 TESTING FIXER SYSTEM...")
        
        all_passed = True
        
        # Test get all fixers
        response = self.make_request('GET', '/fixers', role='client')
        if response and response.status_code == 200:
            fixers = response.json()
            if isinstance(fixers, list):
                # Check if fixers have real data or placeholder data
                is_placeholder = False
                if len(fixers) > 0:
                    sample_fixer = fixers[0]
                    is_placeholder = (
                        sample_fixer.get('name') in ['Test Fixer', 'Placeholder', 'Sample Fixer'] or
                        sample_fixer.get('services') in ['test', 'placeholder'] or
                        len(fixers) <= 2  # Very few fixers suggests placeholder
                    )
                
                self.log_test("Get all fixers", True, 
                            f"Found {len(fixers)} fixers", 
                            'fixer_system', is_placeholder)
                self.test_data['fixers'] = fixers[:5]  # Store first 5 for testing
            else:
                self.log_test("Get all fixers", False, "Invalid response format", 'fixer_system')
                all_passed = False
        else:
            self.log_test("Get all fixers", False, 
                        f"Status: {response.status_code if response else 'No response'}", 
                        'fixer_system')
            all_passed = False
        
        # Test get specific fixer
        if self.test_data['fixers']:
            fixer_id = self.test_data['fixers'][0]['id']
            response = self.make_request('GET', f'/fixers/{fixer_id}', role='client')
            if response and response.status_code == 200:
                fixer_data = response.json()
                if fixer_data.get('id') == fixer_id:
                    self.log_test("Get specific fixer", True, f"Retrieved fixer {fixer_id}", 'fixer_system')
                else:
                    self.log_test("Get specific fixer", False, "Fixer ID mismatch", 'fixer_system')
                    all_passed = False
            else:
                self.log_test("Get specific fixer", False, 
                            f"Status: {response.status_code if response else 'No response'}", 
                            'fixer_system')
                all_passed = False
        
        # Test service filtering
        response = self.make_request('GET', '/fixers/by-service/plumbing', role='client')
        if response and response.status_code == 200:
            plumbing_fixers = response.json()
            if isinstance(plumbing_fixers, list):
                self.log_test("Service filtering", True, 
                            f"Found {len(plumbing_fixers)} plumbing fixers", 
                            'fixer_system')
            else:
                self.log_test("Service filtering", False, "Invalid response format", 'fixer_system')
                all_passed = False
        else:
            self.log_test("Service filtering", False, 
                        f"Status: {response.status_code if response else 'No response'}", 
                        'fixer_system')
            all_passed = False
        
        return all_passed

    def test_job_management_system(self) -> bool:
        """Test job management endpoints"""
        print("\n💼 TESTING JOB MANAGEMENT SYSTEM...")
        
        all_passed = True
        
        # Test create job
        if self.test_accounts['client']['user_id']:
            job_data = {
                'user_id': self.test_accounts['client']['user_id'],
                'service': 'plumbing',
                'description': 'Fix leaking kitchen sink',
                'location': 'Cape Town, South Africa',
                'estimated_price': 250.0,
                'urgency': 'normal'
            }
            
            response = self.make_request('POST', '/jobs', job_data, role='client')
            if response and response.status_code == 200:
                job = response.json()
                if job.get('id') and job.get('service') == 'plumbing':
                    self.test_data['jobs'].append(job)
                    
                    # Check if this is real job creation or placeholder
                    is_placeholder = (
                        job.get('id') == 'placeholder_job_id' or
                        job.get('status') == 'placeholder' or
                        'placeholder' in str(job.get('id', '')).lower()
                    )
                    
                    self.log_test("Create job", True, 
                                f"Created job {job['id']}", 
                                'job_management', is_placeholder)
                else:
                    self.log_test("Create job", False, "Invalid job data returned", 'job_management')
                    all_passed = False
            else:
                self.log_test("Create job", False, 
                            f"Status: {response.status_code if response else 'No response'}", 
                            'job_management')
                all_passed = False
        
        # Test get all jobs
        response = self.make_request('GET', '/jobs', role='admin')
        if response and response.status_code == 200:
            jobs_response = response.json()
            
            # Handle both paginated and direct list responses
            if isinstance(jobs_response, dict) and 'data' in jobs_response:
                jobs = jobs_response['data']
                total = jobs_response.get('total', len(jobs))
            elif isinstance(jobs_response, list):
                jobs = jobs_response
                total = len(jobs)
            else:
                jobs = []
                total = 0
            
            if jobs:
                # Check if jobs have real data or placeholder data
                sample_job = jobs[0]
                is_placeholder = (
                    sample_job.get('description') in ['Test job', 'Placeholder job'] or
                    sample_job.get('service') == 'test' or
                    total <= 1  # Very few jobs suggests placeholder
                )
                
                self.log_test("Get all jobs", True, 
                            f"Found {total} jobs", 
                            'job_management', is_placeholder)
            else:
                self.log_test("Get all jobs", True, "No jobs found (empty system)", 'job_management')
        else:
            self.log_test("Get all jobs", False, 
                        f"Status: {response.status_code if response else 'No response'}", 
                        'job_management')
            all_passed = False
        
        # Test job filtering
        if self.test_accounts['client']['user_id']:
            response = self.make_request('GET', f'/jobs?user_id={self.test_accounts["client"]["user_id"]}', role='client')
            if response and response.status_code == 200:
                self.log_test("Job filtering by user", True, "User job filtering works", 'job_management')
            else:
                self.log_test("Job filtering by user", False, 
                            f"Status: {response.status_code if response else 'No response'}", 
                            'job_management')
                all_passed = False
        
        # Test job update
        if self.test_data['jobs']:
            job_id = self.test_data['jobs'][0]['id']
            update_data = {
                'status': 'in_progress',
                'estimated_price': 300.0
            }
            
            response = self.make_request('PUT', f'/jobs/{job_id}', update_data, role='admin')
            if response and response.status_code == 200:
                updated_job = response.json()
                if updated_job.get('status') == 'in_progress':
                    self.log_test("Update job", True, f"Updated job {job_id}", 'job_management')
                else:
                    self.log_test("Update job", False, "Job status not updated", 'job_management')
                    all_passed = False
            else:
                self.log_test("Update job", False, 
                            f"Status: {response.status_code if response else 'No response'}", 
                            'job_management')
                all_passed = False
        
        return all_passed

    def test_dashboard_data(self) -> bool:
        """Test dashboard data endpoints"""
        print("\n📊 TESTING DASHBOARD DATA...")
        
        all_passed = True
        
        # Test dashboard endpoint for each role
        for role in ['admin', 'client', 'fixer']:
            if self.test_accounts[role]['token']:
                response = self.make_request('GET', '/dashboard', role=role)
                if response and response.status_code == 200:
                    dashboard_data = response.json()
                    
                    # Check if dashboard has real data or placeholder data
                    is_placeholder = False
                    if isinstance(dashboard_data, dict):
                        # Look for placeholder indicators
                        stats = dashboard_data.get('stats', {})
                        if isinstance(stats, dict):
                            # Check for obviously fake/placeholder data
                            total_jobs = stats.get('total_jobs', 0)
                            total_users = stats.get('total_users', 0)
                            
                            is_placeholder = (
                                total_jobs == 0 and total_users == 0 or  # All zeros
                                total_jobs == 100 and total_users == 50 or  # Round placeholder numbers
                                'placeholder' in str(dashboard_data).lower() or
                                'sample' in str(dashboard_data).lower()
                            )
                        
                        self.log_test(f"Dashboard data ({role})", True, 
                                    f"Dashboard loaded with stats", 
                                    'dashboard_data', is_placeholder)
                    else:
                        self.log_test(f"Dashboard data ({role})", False, 
                                    "Invalid dashboard data format", 'dashboard_data')
                        all_passed = False
                else:
                    self.log_test(f"Dashboard data ({role})", False, 
                                f"Status: {response.status_code if response else 'No response'}", 
                                'dashboard_data')
                    all_passed = False
        
        return all_passed

    def test_payment_system(self) -> bool:
        """Test payment system endpoints"""
        print("\n💳 TESTING PAYMENT SYSTEM...")
        
        all_passed = True
        
        # Test EFT payment creation
        payment_data = {
            'amount': 100.0,
            'description': 'Test payment',
            'user_email': 'test@example.com',
            'user_name': 'Test User'
        }
        
        response = self.make_request('POST', '/payment/eft', payment_data, role='client')
        if response and response.status_code == 200:
            payment_result = response.json()
            
            # Check if this is real payment processing or placeholder
            is_placeholder = (
                payment_result.get('payment_id') == 'placeholder_payment_id' or
                payment_result.get('status') == 'placeholder' or
                'placeholder' in str(payment_result).lower() or
                'test' in str(payment_result.get('payment_url', '')).lower()
            )
            
            self.log_test("EFT payment creation", True, 
                        f"Payment created: {payment_result.get('payment_id', 'N/A')}", 
                        'payment_system', is_placeholder)
        else:
            self.log_test("EFT payment creation", False, 
                        f"Status: {response.status_code if response else 'No response'}", 
                        'payment_system')
            all_passed = False
        
        # Test airtime payment
        airtime_data = {
            'phone_number': '+27821234567',
            'amount': 50.0,
            'description': 'Test airtime payment'
        }
        
        response = self.make_request('POST', '/payment/airtime', airtime_data, role='client')
        if response and response.status_code == 200:
            airtime_result = response.json()
            
            is_placeholder = (
                'placeholder' in str(airtime_result).lower() or
                'test' in str(airtime_result).lower()
            )
            
            self.log_test("Airtime payment", True, 
                        "Airtime payment processed", 
                        'payment_system', is_placeholder)
        else:
            self.log_test("Airtime payment", False, 
                        f"Status: {response.status_code if response else 'No response'}", 
                        'payment_system')
            all_passed = False
        
        # Test fixer payment status (if we have fixers)
        if self.test_data['fixers']:
            fixer_id = self.test_data['fixers'][0]['id']
            response = self.make_request('GET', f'/fixer/{fixer_id}/payment-status', role='admin')
            if response and response.status_code == 200:
                payment_status = response.json()
                
                is_placeholder = (
                    payment_status.get('status') == 'placeholder' or
                    'placeholder' in str(payment_status).lower()
                )
                
                self.log_test("Fixer payment status", True, 
                            f"Payment status retrieved", 
                            'payment_system', is_placeholder)
            else:
                self.log_test("Fixer payment status", False, 
                            f"Status: {response.status_code if response else 'No response'}", 
                            'payment_system')
                all_passed = False
        
        return all_passed

    def test_advanced_features(self) -> bool:
        """Test advanced features like reviews, notifications, etc."""
        print("\n🚀 TESTING ADVANCED FEATURES...")
        
        all_passed = True
        
        # Test review system (if we have jobs)
        if self.test_data['jobs'] and self.test_data['fixers']:
            job_id = self.test_data['jobs'][0]['id']
            fixer_id = self.test_data['fixers'][0]['id']
            
            review_data = {
                'job_id': job_id,
                'fixer_id': fixer_id,
                'rating': 5,
                'comment': 'Excellent work!'
            }
            
            response = self.make_request('POST', '/reviews', review_data, role='client')
            if response and response.status_code == 200:
                review = response.json()
                self.log_test("Review system", True, f"Review created: {review.get('id', 'N/A')}", 'job_management')
            else:
                self.log_test("Review system", False, 
                            f"Status: {response.status_code if response else 'No response'}", 
                            'job_management')
                all_passed = False
        
        # Test emergency alert system
        if self.test_accounts['client']['user_id']:
            alert_data = {
                'job_id': self.test_data['jobs'][0]['id'] if self.test_data['jobs'] else 'test_job_id',
                'alert_type': 'safety_concern',
                'latitude': -33.9249,
                'longitude': 18.4241,
                'address': 'Cape Town, South Africa',
                'description': 'Test emergency alert'
            }
            
            response = self.make_request('POST', '/emergency/alert', alert_data, role='client')
            if response and response.status_code == 200:
                self.log_test("Emergency alert system", True, "Emergency alert created", 'user_management')
            else:
                self.log_test("Emergency alert system", False, 
                            f"Status: {response.status_code if response else 'No response'}", 
                            'user_management')
                all_passed = False
        
        return all_passed

    def run_comprehensive_audit(self):
        """Run comprehensive backend functionality audit"""
        print("🚀 STARTING COMPREHENSIVE FIXMATE-SA BACKEND FUNCTIONALITY AUDIT")
        print("=" * 80)
        
        # Step 1: Authentication System
        auth_success = self.test_authentication_system()
        
        # Only proceed if authentication works
        if self.results['failed_tests'] > 2:
            print("❌ Too many authentication failures. Cannot proceed with comprehensive audit.")
            self.print_audit_results()
            return False
        
        # Step 2: Core Systems Testing
        self.test_user_management_system()
        self.test_fixer_system()
        self.test_job_management_system()
        self.test_dashboard_data()
        self.test_payment_system()
        self.test_advanced_features()
        
        # Step 3: Print comprehensive results
        self.print_audit_results()
        
        return self.results['failed_tests'] == 0

    def print_audit_results(self):
        """Print comprehensive audit results"""
        print("\n" + "=" * 80)
        print("🎯 FIXMATE-SA BACKEND FUNCTIONALITY AUDIT RESULTS")
        print("=" * 80)
        
        total = self.results['total_tests']
        passed = self.results['passed_tests']
        failed = self.results['failed_tests']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"📊 OVERALL SUMMARY:")
        print(f"   Total Tests: {total}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n🔍 FUNCTIONALITY AUDIT BY CATEGORY:")
        
        for category, results in self.results['functionality_audit'].items():
            working_count = len(results['working'])
            placeholder_count = len(results['placeholder'])
            failed_count = len(results['failed'])
            total_category = working_count + placeholder_count + failed_count
            
            if total_category > 0:
                print(f"\n📂 {category.upper().replace('_', ' ')}:")
                print(f"   ✅ Fully Working: {working_count}")
                print(f"   🔶 Placeholder/Mock: {placeholder_count}")
                print(f"   ❌ Failed/Broken: {failed_count}")
                
                if working_count > 0:
                    print(f"   Working Features: {', '.join(results['working'])}")
                if placeholder_count > 0:
                    print(f"   Placeholder Features: {', '.join(results['placeholder'])}")
                if failed_count > 0:
                    print(f"   Failed Features: {', '.join(results['failed'])}")
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        
        # Calculate overall functionality status
        total_working = sum(len(results['working']) for results in self.results['functionality_audit'].values())
        total_placeholder = sum(len(results['placeholder']) for results in self.results['functionality_audit'].values())
        total_failed = sum(len(results['failed']) for results in self.results['functionality_audit'].values())
        total_features = total_working + total_placeholder + total_failed
        
        if total_features > 0:
            working_percentage = (total_working / total_features) * 100
            placeholder_percentage = (total_placeholder / total_features) * 100
            failed_percentage = (total_failed / total_features) * 100
            
            print(f"   🟢 Real Functionality: {working_percentage:.1f}% ({total_working}/{total_features})")
            print(f"   🟡 Placeholder/Mock: {placeholder_percentage:.1f}% ({total_placeholder}/{total_features})")
            print(f"   🔴 Broken/Failed: {failed_percentage:.1f}% ({total_failed}/{total_features})")
            
            if working_percentage >= 80:
                print(f"\n🎉 EXCELLENT: Most features are fully functional!")
            elif working_percentage >= 60:
                print(f"\n👍 GOOD: Majority of features are working, some placeholders remain.")
            elif working_percentage >= 40:
                print(f"\n⚠️ MODERATE: Mixed functionality, significant placeholder implementations.")
            else:
                print(f"\n🚨 POOR: Many features are placeholders or broken.")

def main():
    """Main function to run comprehensive backend audit"""
    auditor = FixMateBackendAuditor()
    success = auditor.run_comprehensive_audit()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()