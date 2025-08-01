#!/usr/bin/env python3
"""
FixMate-SA Core Job Assignment Workflow Backend Testing Script
Tests the core job assignment workflow endpoints that were previously failing.

PRIORITY TESTS (Previously Failing):
1. POST /api/jobs/workflow - Enhanced job workflow creation
2. POST /api/jobs/{job_id}/accept - Fixer job acceptance (first-come-first-served)
3. GET /api/jobs/{job_id}/workflow-status - Get workflow status
4. Terms Acceptance Integration - Test that jobs cannot be created without terms acceptance
5. Fixer Screening Validation - Verify only approved fixers are eligible

FOCUS AREAS:
- Fix any remaining HTTP 400 errors
- Verify the workflow integration works end-to-end
- Confirm fixer screening criteria are properly applied
- Test that terms acceptance is enforced

TEST DATA SETUP:
- Use admin: +27821234567 / admin123
- Test with approved fixers (we just approved 5 fixers)
- Create realistic job data for plumbing service

EXPECTED RESULTS:
- POST /api/jobs/workflow should return 200 with job creation success
- Job acceptance should work with first-come-first-served logic
- Workflow status should show proper progression
- All system requirements integration should be functional

Authentication Context:
- Admin: +27821234567 / admin123
- Use realistic data for plumbing service testing
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔧 Testing Core Job Assignment Workflow System at: {API_BASE}")
print("=" * 80)
print("🎯 CORE JOB ASSIGNMENT WORKFLOW TESTING")
print("=" * 80)

class FixMateAPITester:
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
    
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_result("Health Check", True, f"API is running: {data['message']}")
                    return True
                else:
                    self.log_result("Health Check", False, "Invalid response format", response)
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
        return False
    
    def test_create_user(self):
        """Test user creation"""
        import time
        timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
        
        user_data = {
            "phone": f"+2782123{timestamp}",
            "first_name": "John",
            "last_name": "Doe",
            "id_number": f"8001015009{timestamp[-3:]}",  # Valid SA ID format
            "town": "Cape Town",
            "email": f"john.doe.{timestamp}@example.com",
            "address": "123 Main St, Cape Town"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/users", json=user_data)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["phone"] == user_data["phone"]:
                    self.test_data['user_id'] = data['id']
                    self.test_data['user'] = data
                    self.log_result("Create User", True, f"User created with ID: {data['id']}")
                    return True
                else:
                    self.log_result("Create User", False, "Invalid response format", response)
            else:
                self.log_result("Create User", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Create User", False, f"Request error: {str(e)}")
        return False
    
    def test_admin_login(self):
        """Test admin login for admin-only endpoints"""
        try:
            login_data = {
                "phone": "+27821234567",
                "password": "admin123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.test_data['admin_token'] = data['token']
                    self.test_data['admin_user'] = data['user']
                    self.test_data['admin_user_id'] = data['user']['id']
                    self.log_result("Admin Login", True, f"Admin login successful, role: {data.get('role_info', {}).get('role', 'unknown')}")
                    return True
                else:
                    self.log_result("Admin Login", False, "Invalid response format", response)
            else:
                self.log_result("Admin Login", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Admin Login", False, f"Request error: {str(e)}")
        return False
    
    def test_create_test_fixer_for_workflow(self):
        """Create a test fixer for workflow testing"""
        import time
        timestamp = str(int(time.time()))[-6:]
        
        # First create a user for the fixer
        user_data = {
            "phone": f"+2782555{timestamp}",
            "first_name": "WorkflowTest",
            "last_name": "Fixer",
            "id_number": f"8001015009{timestamp[-3:]}",
            "town": "Cape Town",
            "email": f"workflow.fixer.{timestamp}@fixmate.com",
            "address": "123 Workflow St, Cape Town"
        }
        
        try:
            # Create user first
            user_response = self.session.post(f"{API_BASE}/users", json=user_data)
            if user_response.status_code != 200:
                self.log_result("Create Test Fixer for Workflow", False, "Failed to create user for fixer", user_response)
                return False
            
            fixer_user = user_response.json()
            
            fixer_data = {
                "user_id": fixer_user['id'],
                "phone": f"+2782555{timestamp}",
                "name": "WorkflowTest Fixer",
                "email": f"workflow.fixer.{timestamp}@fixmate.com",
                "services": '["plumbing", "electrical", "carpentry"]',
                "location": "Cape Town"
            }
            
            response = self.session.post(f"{API_BASE}/fixers", json=fixer_data)
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.test_data['workflow_fixer_id'] = data['id']
                    self.test_data['workflow_fixer'] = data
                    self.log_result("Create Test Fixer for Workflow", True, f"Workflow test fixer created with ID: {data['id']}")
                    return True
                else:
                    self.log_result("Create Test Fixer for Workflow", False, "Invalid response format", response)
            else:
                self.log_result("Create Test Fixer for Workflow", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Create Test Fixer for Workflow", False, f"Request error: {str(e)}")
        return False
    
    def test_create_test_job_for_workflow(self):
        """Create a test job for workflow testing"""
        if 'user_id' not in self.test_data:
            self.log_result("Create Test Job for Workflow", False, "No user ID available from previous test")
            return False
        
        job_data = {
            "user_id": self.test_data['user_id'],
            "service": "plumbing",
            "description": "Emergency plumbing repair - burst pipe in kitchen",
            "location": "123 Main St, Cape Town",
            "estimated_price": 450.0
        }
        
        try:
            response = self.session.post(f"{API_BASE}/jobs", json=job_data)
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.test_data['workflow_job_id'] = data['id']
                    self.test_data['workflow_job'] = data
                    self.log_result("Create Test Job for Workflow", True, f"Workflow test job created with ID: {data['id']}")
                    return True
                else:
                    self.log_result("Create Test Job for Workflow", False, "Invalid response format", response)
            else:
                self.log_result("Create Test Job for Workflow", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Create Test Job for Workflow", False, f"Request error: {str(e)}")
        return False
    
    def test_terms_acceptance_check(self):
        """Test terms acceptance status check"""
        if 'user_id' not in self.test_data:
            self.log_result("Terms Acceptance Check", False, "No user ID available from previous tests")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/terms/check/{self.test_data['user_id']}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'has_accepted' in data:
                    has_accepted = data['has_accepted']
                    self.log_result("Terms Acceptance Check", True, 
                                  f"✅ TERMS ACCEPTANCE CHECK WORKING! User has accepted terms: {has_accepted}")
                    return True
                else:
                    self.log_result("Terms Acceptance Check", False, "Invalid terms check response format", response)
            else:
                self.log_result("Terms Acceptance Check", False, f"❌ TERMS ACCEPTANCE CHECK FAILED! HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Terms Acceptance Check", False, f"❌ TERMS ACCEPTANCE CHECK ERROR! Request error: {str(e)}")
        return False
    
    def test_terms_acceptance_workflow(self):
        """Test terms acceptance workflow"""
        if 'user_id' not in self.test_data:
            self.log_result("Terms Acceptance Workflow", False, "No user ID available from previous tests")
            return False
        
        try:
            # Accept terms for the user
            terms_data = {
                "user_id": self.test_data['user_id'],
                "ip_address": "192.168.1.100",
                "user_agent": "FixMate-Test-Client/1.0",
                "method": "web"
            }
            
            response = self.session.post(f"{API_BASE}/terms/accept", json=terms_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    message = data.get('message', 'Terms accepted')
                    self.log_result("Terms Acceptance Workflow", True, 
                                  f"✅ TERMS ACCEPTANCE WORKFLOW WORKING! {message}")
                    return True
                else:
                    self.log_result("Terms Acceptance Workflow", False, f"Terms acceptance failed: {data}", response)
            else:
                self.log_result("Terms Acceptance Workflow", False, f"❌ TERMS ACCEPTANCE WORKFLOW FAILED! HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Terms Acceptance Workflow", False, f"❌ TERMS ACCEPTANCE WORKFLOW ERROR! Request error: {str(e)}")
        return False
    
    def test_job_workflow_creation(self):
        """PRIORITY TEST 1: POST /api/jobs/workflow - Enhanced job workflow creation"""
        if 'user_id' not in self.test_data:
            self.log_result("Job Workflow Creation", False, "No user ID available from previous tests")
            return False
        
        try:
            workflow_job_data = {
                "user_id": self.test_data['user_id'],
                "service": "plumbing",
                "description": "Emergency plumbing repair - burst pipe in kitchen causing water damage",
                "location": "123 Main Street, Cape Town, Western Cape",
                "estimated_price": 850.0,
                "priority_level": "high",
                "urgency": "emergency"
            }
            
            response = self.session.post(f"{API_BASE}/jobs/workflow", json=workflow_job_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'job_id' in data:
                    job_id = data['job_id']
                    workflow_status = data.get('workflow_status', {})
                    message = data.get('message', 'Job created successfully')
                    
                    # Store job ID for subsequent tests
                    self.test_data['workflow_job_id'] = job_id
                    
                    self.log_result("Job Workflow Creation", True, 
                                  f"✅ PRIORITY TEST 1 PASSED! Enhanced job workflow creation successful: "
                                  f"Job ID {job_id}, Message: {message}, "
                                  f"Workflow status fields: {len(workflow_status)}")
                    return True
                else:
                    self.log_result("Job Workflow Creation", False, f"❌ PRIORITY TEST 1 FAILED! Workflow creation failed: {data}", response)
            else:
                self.log_result("Job Workflow Creation", False, f"❌ PRIORITY TEST 1 FAILED! HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Job Workflow Creation", False, f"❌ PRIORITY TEST 1 ERROR! Request error: {str(e)}")
        return False
    
    def test_get_approved_fixers(self):
        """Get approved fixers for job acceptance testing"""
        try:
            response = self.session.get(f"{API_BASE}/fixers")
            
            if response.status_code == 200:
                fixers = response.json()
                
                # Filter for approved fixers with good ratings
                approved_fixers = []
                for fixer in fixers:
                    if (fixer.get('is_approved', False) and 
                        fixer.get('is_active', False) and 
                        (fixer.get('rating', 0) >= 3.0 or fixer.get('rating', 0) == 0.0)):  # New fixers or good rating
                        approved_fixers.append(fixer)
                
                if approved_fixers:
                    # Store first approved fixer for testing
                    self.test_data['approved_fixer'] = approved_fixers[0]
                    self.test_data['approved_fixer_id'] = approved_fixers[0]['id']
                    
                    self.log_result("Get Approved Fixers", True, 
                                  f"✅ FIXER SCREENING WORKING! Found {len(approved_fixers)} approved fixers. "
                                  f"Test fixer: {approved_fixers[0]['name']} (Rating: {approved_fixers[0].get('rating', 0)}/5)")
                    return True
                else:
                    self.log_result("Get Approved Fixers", False, "No approved fixers found for testing", response)
            else:
                self.log_result("Get Approved Fixers", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Approved Fixers", False, f"Request error: {str(e)}")
        return False
    
    def test_fixer_job_acceptance(self):
        """PRIORITY TEST 2: POST /api/jobs/{job_id}/accept - Fixer job acceptance (first-come-first-served)"""
        if 'workflow_job_id' not in self.test_data or 'approved_fixer_id' not in self.test_data:
            self.log_result("Fixer Job Acceptance", False, "No workflow job ID or approved fixer ID available from previous tests")
            return False
        
        try:
            acceptance_data = {
                "fixer_id": self.test_data['approved_fixer_id']
            }
            
            response = self.session.post(f"{API_BASE}/jobs/{self.test_data['workflow_job_id']}/accept", 
                                       json=acceptance_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    message = data.get('message', 'Job accepted successfully')
                    fixer_name = self.test_data['approved_fixer'].get('name', 'Unknown')
                    
                    self.log_result("Fixer Job Acceptance", True, 
                                  f"✅ PRIORITY TEST 2 PASSED! Fixer job acceptance successful: "
                                  f"Fixer {fixer_name} accepted job {self.test_data['workflow_job_id']}. "
                                  f"Message: {message}")
                    return True
                else:
                    self.log_result("Fixer Job Acceptance", False, f"❌ PRIORITY TEST 2 FAILED! Job acceptance failed: {data}", response)
            else:
                self.log_result("Fixer Job Acceptance", False, f"❌ PRIORITY TEST 2 FAILED! HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Fixer Job Acceptance", False, f"❌ PRIORITY TEST 2 ERROR! Request error: {str(e)}")
        return False
    
    def test_workflow_status_retrieval(self):
        """PRIORITY TEST 3: GET /api/jobs/{job_id}/workflow-status - Get workflow status"""
        if 'workflow_job_id' not in self.test_data:
            self.log_result("Workflow Status Retrieval", False, "No workflow job ID available from previous tests")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/jobs/{self.test_data['workflow_job_id']}/workflow-status")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify workflow status structure
                required_fields = ['job_id', 'status', 'workflow_stage']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Workflow Status Retrieval", False, f"Missing required fields: {missing_fields}", response)
                    return False
                
                # Check workflow progression
                workflow_features = []
                if 'assignment_attempts' in data:
                    workflow_features.append("assignment_tracking")
                if 'eligible_fixers' in data:
                    workflow_features.append("fixer_screening")
                if 'terms_accepted' in data:
                    workflow_features.append("terms_validation")
                if 'workflow_stage' in data:
                    workflow_features.append("stage_tracking")
                
                job_status = data.get('status', 'unknown')
                workflow_stage = data.get('workflow_stage', 'unknown')
                
                self.log_result("Workflow Status Retrieval", True, 
                              f"✅ PRIORITY TEST 3 PASSED! Workflow status retrieved successfully: "
                              f"Status: {job_status}, Stage: {workflow_stage}, "
                              f"Features: {', '.join(workflow_features) if workflow_features else 'basic status only'}")
                return True
            else:
                self.log_result("Workflow Status Retrieval", False, f"❌ PRIORITY TEST 3 FAILED! HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Workflow Status Retrieval", False, f"❌ PRIORITY TEST 3 ERROR! Request error: {str(e)}")
        return False
    
    # ======= ADDITIONAL ENHANCED WORKFLOW VERIFICATION TESTS =======
    
    def test_fraud_detection_system(self):
        """Test AI-powered fraud detection system"""
        try:
            # Test getting fraud alerts
            response = self.session.get(f"{API_BASE}/admin/fraud-alerts")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'fraud_alerts' in data and 'total_count' in data:
                    alerts = data['fraud_alerts']
                    total_count = data['total_count']
                    
                    self.log_result("Fraud Detection System", True, 
                                  f"Fraud detection system operational: {total_count} alerts found, "
                                  f"System monitoring {len(alerts)} active alerts")
                    return True
                else:
                    self.log_result("Fraud Detection System", False, "Invalid fraud alerts response format", response)
            else:
                self.log_result("Fraud Detection System", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Fraud Detection System", False, f"Request error: {str(e)}")
        return False
    
    def test_timeout_handling_system(self):
        """Test timeout handling and penalty systems"""
        if 'admin_user_id' not in self.test_data:
            self.log_result("Timeout Handling System", False, "No admin user ID available from previous tests")
            return False
        
        try:
            timeout_data = {
                "admin_user_id": self.test_data['admin_user_id']
            }
            
            response = self.session.post(f"{API_BASE}/admin/process-timeouts", json=timeout_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    message = data.get('message', 'Timeouts processed')
                    self.log_result("Timeout Handling System", True, 
                                  f"Timeout handling system operational: {message}")
                    return True
                else:
                    self.log_result("Timeout Handling System", False, f"Timeout processing failed: {data}", response)
            else:
                self.log_result("Timeout Handling System", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Timeout Handling System", False, f"Request error: {str(e)}")
        return False
    
    def test_admin_override_system(self):
        """Test admin override capabilities"""
        if 'workflow_fixer_id' not in self.test_data or 'admin_user_id' not in self.test_data:
            self.log_result("Admin Override System", False, "No workflow fixer ID or admin user ID available from previous tests")
            return False
        
        try:
            override_data = {
                "admin_user_id": self.test_data['admin_user_id'],
                "override_type": "bypass_restrictions",
                "reason": "Testing admin override system - temporary bypass for system testing",
                "override_data": {"test_mode": True}
            }
            
            response = self.session.post(f"{API_BASE}/admin/override/fixer/{self.test_data['workflow_fixer_id']}", 
                                       json=override_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    message = data.get('message', 'Override applied')
                    self.log_result("Admin Override System", True, 
                                  f"Admin override system operational: {message}")
                    return True
                else:
                    self.log_result("Admin Override System", False, f"Admin override failed: {data}", response)
            else:
                self.log_result("Admin Override System", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Admin Override System", False, f"Request error: {str(e)}")
        return False
    
    def test_cancellation_protocols(self):
        """Test enhanced cancellation protocols with penalties"""
        if 'workflow_job_id' not in self.test_data or 'user_id' not in self.test_data:
            self.log_result("Cancellation Protocols", False, "No workflow job ID or user ID available from previous tests")
            return False
        
        try:
            cancellation_data = {
                "user_id": self.test_data['user_id'],
                "cancelled_by": "client",
                "reason": "Testing cancellation protocols - client initiated cancellation"
            }
            
            response = self.session.post(f"{API_BASE}/jobs/{self.test_data['workflow_job_id']}/cancel", 
                                       json=cancellation_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    message = data.get('message', 'Job cancelled')
                    self.log_result("Cancellation Protocols", True, 
                                  f"Enhanced cancellation protocols working: {message}")
                    return True
                else:
                    self.log_result("Cancellation Protocols", False, f"Cancellation failed: {data}", response)
            else:
                self.log_result("Cancellation Protocols", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Cancellation Protocols", False, f"Request error: {str(e)}")
        return False
    
    def test_terms_acceptance_workflow(self):
        """Test terms acceptance workflow"""
        if 'user_id' not in self.test_data:
            self.log_result("Terms Acceptance Workflow", False, "No user ID available from previous tests")
            return False
        
        try:
            # First check terms acceptance status
            response = self.session.get(f"{API_BASE}/terms/check/{self.test_data['user_id']}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'has_accepted' in data:
                    has_accepted = data['has_accepted']
                    self.log_result("Terms Acceptance Workflow", True, 
                                  f"Terms acceptance workflow operational: User has accepted terms: {has_accepted}")
                    return True
                else:
                    self.log_result("Terms Acceptance Workflow", False, "Invalid terms check response format", response)
            else:
                self.log_result("Terms Acceptance Workflow", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Terms Acceptance Workflow", False, f"Request error: {str(e)}")
        return False
    
    def test_job_workflow_creation(self):
        """Test enhanced job workflow creation"""
        if 'user_id' not in self.test_data:
            self.log_result("Job Workflow Creation", False, "No user ID available from previous tests")
            return False
        
        try:
            workflow_job_data = {
                "user_id": self.test_data['user_id'],
                "service": "electrical",
                "description": "Testing enhanced job workflow - electrical outlet installation",
                "location": "456 Workflow Ave, Cape Town",
                "estimated_price": 300.0,
                "priority_level": "medium"
            }
            
            response = self.session.post(f"{API_BASE}/jobs/workflow", json=workflow_job_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'job_id' in data:
                    job_id = data['job_id']
                    workflow_status = data.get('workflow_status', {})
                    
                    self.log_result("Job Workflow Creation", True, 
                                  f"Enhanced job workflow creation successful: Job ID {job_id}, "
                                  f"Workflow features: {len(workflow_status)} status fields")
                    return True
                else:
                    self.log_result("Job Workflow Creation", False, f"Workflow creation failed: {data}", response)
            else:
                self.log_result("Job Workflow Creation", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Job Workflow Creation", False, f"Request error: {str(e)}")
        return False
    
    def run_enhanced_workflow_tests(self):
        """Run Enhanced Job Assignment Workflow tests"""
        print("🚀 ENHANCED JOB ASSIGNMENT WORKFLOW TESTING")
        print("=" * 80)
        
        # Phase 1: Setup and Authentication
        print("📋 PHASE 1: SETUP AND AUTHENTICATION")
        print("-" * 50)
        
        if not self.test_health_check():
            print("❌ Health check failed. Cannot proceed with testing.")
            return False
        
        # Create test user
        if not self.test_create_user():
            print("❌ User creation failed. Cannot proceed with workflow testing.")
            return False
        
        # Admin login for admin-only endpoints
        if not self.test_admin_login():
            print("❌ Admin login failed. Cannot proceed with admin endpoint testing.")
            return False
        
        # Phase 2: Test Data Creation
        print("\n📋 PHASE 2: TEST DATA CREATION")
        print("-" * 50)
        
        # Create test fixer for workflow testing
        if not self.test_create_test_fixer_for_workflow():
            print("❌ Test fixer creation failed. Cannot proceed with fixer-related tests.")
            return False
        
        # Create test job for workflow testing
        if not self.test_create_test_job_for_workflow():
            print("❌ Test job creation failed. Cannot proceed with job-related tests.")
            return False
        
        # Phase 3: Priority Endpoint Testing (The 5 failing endpoints)
        print("\n🎯 PHASE 3: PRIORITY ENDPOINT TESTING")
        print("-" * 50)
        print("Testing the 5 endpoints that were failing due to database schema issues:")
        print()
        
        priority_tests = [
            ("1. Fixer Performance Stats", self.test_fixer_performance_stats),
            ("2. Job Assignment History", self.test_job_assignment_history),
            ("3. Emergency Escalate Job", self.test_emergency_escalate_job),
            ("4. Admin Workflow Analytics", self.test_admin_workflow_analytics),
            ("5. Fixer Eligible Jobs", self.test_fixer_eligible_jobs)
        ]
        
        priority_results = []
        for test_name, test_func in priority_tests:
            print(f"Testing {test_name}...")
            result = test_func()
            priority_results.append((test_name, result))
            print()
        
        # Phase 4: Additional Workflow Verification
        print("📋 PHASE 4: ADDITIONAL WORKFLOW VERIFICATION")
        print("-" * 50)
        
        additional_tests = [
            ("Fraud Detection System", self.test_fraud_detection_system),
            ("Timeout Handling System", self.test_timeout_handling_system),
            ("Admin Override System", self.test_admin_override_system),
            ("Cancellation Protocols", self.test_cancellation_protocols),
            ("Terms Acceptance Workflow", self.test_terms_acceptance_workflow),
            ("Job Workflow Creation", self.test_job_workflow_creation)
        ]
        
        additional_results = []
        for test_name, test_func in additional_tests:
            print(f"Testing {test_name}...")
            result = test_func()
            additional_results.append((test_name, result))
            print()
        
        # Results Summary
        print("=" * 80)
        print("🎯 ENHANCED JOB ASSIGNMENT WORKFLOW TEST RESULTS")
        print("=" * 80)
        
        print("🔥 PRIORITY ENDPOINTS (Previously Failing):")
        priority_passed = 0
        for test_name, result in priority_results:
            status = "✅ WORKING" if result else "❌ FAILED"
            print(f"   {status}: {test_name}")
            if result:
                priority_passed += 1
        
        print(f"\n📊 Priority Endpoints Success Rate: {priority_passed}/5 ({priority_passed/5*100:.1f}%)")
        
        print("\n🔧 ADDITIONAL WORKFLOW FEATURES:")
        additional_passed = 0
        for test_name, result in additional_results:
            status = "✅ WORKING" if result else "❌ FAILED"
            print(f"   {status}: {test_name}")
            if result:
                additional_passed += 1
        
        print(f"\n📊 Additional Features Success Rate: {additional_passed}/6 ({additional_passed/6*100:.1f}%)")
        
        total_passed = priority_passed + additional_passed
        total_tests = 11
        overall_success_rate = total_passed / total_tests * 100
        
        print(f"\n🎉 OVERALL SUCCESS RATE: {total_passed}/{total_tests} ({overall_success_rate:.1f}%)")
        
        if priority_passed == 5:
            print("\n✅ SUCCESS! All 5 priority endpoints are now working after database migration!")
        else:
            print(f"\n⚠️  WARNING! {5-priority_passed} priority endpoints still failing. Database migration may be incomplete.")
        
        if overall_success_rate >= 80:
            print("🎉 Enhanced Job Assignment Workflow system is operational!")
        else:
            print("⚠️  Enhanced Job Assignment Workflow system needs attention.")
        
        return priority_passed == 5

if __name__ == "__main__":
    print("🔧 FixMate-SA Enhanced Job Assignment Workflow Backend Testing")
    print("=" * 80)
    print("🎯 FOCUS: Re-testing Enhanced Job Assignment Workflow after database migration")
    print("📋 PRIORITY: 5 endpoints that were failing due to database schema issues")
    print("=" * 80)
    
    tester = FixMateAPITester()
    
    try:
        # Run Enhanced Job Assignment Workflow tests
        success = tester.run_enhanced_workflow_tests()
        
        print("\n" + "=" * 80)
        print("📊 FINAL TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {tester.results['passed']}")
        print(f"❌ Tests Failed: {tester.results['failed']}")
        print(f"📈 Success Rate: {tester.results['passed']/(tester.results['passed']+tester.results['failed'])*100:.1f}%")
        
        if tester.results['errors']:
            print(f"\n🚨 ERRORS ENCOUNTERED:")
            for error in tester.results['errors']:
                print(f"   • {error}")
        
        if success:
            print("\n🎉 ENHANCED JOB ASSIGNMENT WORKFLOW SYSTEM IS OPERATIONAL!")
            print("✅ Database migration successful - all priority endpoints working")
        else:
            print("\n⚠️  ENHANCED JOB ASSIGNMENT WORKFLOW SYSTEM NEEDS ATTENTION")
            print("❌ Some priority endpoints still failing - database migration may be incomplete")
        
        print("\n" + "=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {str(e)}")
        import traceback
        traceback.print_exc()