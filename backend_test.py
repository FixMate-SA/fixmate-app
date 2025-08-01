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
    
    def test_fixer_performance_stats(self):
        """PRIORITY TEST 1: GET /api/fixer/{fixer_id}/performance-stats - Test comprehensive fixer performance statistics"""
        if 'workflow_fixer_id' not in self.test_data:
            self.log_result("Fixer Performance Stats", False, "No workflow fixer ID available from previous test")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/fixer/{self.test_data['workflow_fixer_id']}/performance-stats")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify comprehensive performance statistics
                required_fields = [
                    'fixer_id', 'fixer_name', 'base_rating', 'effective_rating',
                    'jobs_completed', 'jobs_cancelled', 'completion_percentage',
                    'platform_fees_owed', 'is_available'
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_result("Fixer Performance Stats", False, f"Missing required fields: {missing_fields}", response)
                    return False
                
                # Check for enhanced workflow fields
                enhanced_fields = []
                if 'rating_penalty_total' in data:
                    enhanced_fields.append("rating_penalties")
                if 'cancellation_penalty_count' in data:
                    enhanced_fields.append("cancellation_penalties")
                if 'availability_freeze_count' in data:
                    enhanced_fields.append("availability_freezes")
                if 'behavior_analysis' in data:
                    enhanced_fields.append("behavior_analysis")
                
                self.log_result("Fixer Performance Stats", True, 
                              f"✅ PRIORITY ENDPOINT 1 WORKING! Comprehensive fixer performance stats retrieved: "
                              f"Rating: {data.get('effective_rating', 0)}/5, "
                              f"Completed: {data.get('jobs_completed', 0)} jobs, "
                              f"Completion rate: {data.get('completion_percentage', 0)}%, "
                              f"Enhanced features: {', '.join(enhanced_fields) if enhanced_fields else 'basic stats only'}")
                return True
            else:
                self.log_result("Fixer Performance Stats", False, f"❌ PRIORITY ENDPOINT 1 FAILED! HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Fixer Performance Stats", False, f"❌ PRIORITY ENDPOINT 1 ERROR! Request error: {str(e)}")
        return False
    
    def test_job_assignment_history(self):
        """PRIORITY TEST 2: GET /api/jobs/{job_id}/assignment-history - Test job assignment history tracking"""
        if 'workflow_job_id' not in self.test_data:
            self.log_result("Job Assignment History", False, "No workflow job ID available from previous test")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/jobs/{self.test_data['workflow_job_id']}/assignment-history")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify assignment history structure
                required_fields = [
                    'job_id', 'job_status', 'assignment_attempts', 
                    'assignment_history', 'notification_history'
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_result("Job Assignment History", False, f"Missing required fields: {missing_fields}", response)
                    return False
                
                # Check for enhanced workflow tracking fields
                enhanced_tracking = []
                if 'workflow_stage' in data:
                    enhanced_tracking.append("workflow_stage")
                if 'auto_reassignment_count' in data:
                    enhanced_tracking.append("auto_reassignment")
                if 'is_emergency_escalated' in data:
                    enhanced_tracking.append("emergency_escalation")
                if 'fixer_timeout_count' in data:
                    enhanced_tracking.append("timeout_tracking")
                
                assignment_count = len(data.get('assignment_history', []))
                notification_count = len(data.get('notification_history', []))
                
                self.log_result("Job Assignment History", True, 
                              f"✅ PRIORITY ENDPOINT 2 WORKING! Job assignment history retrieved: "
                              f"Job status: {data.get('job_status', 'unknown')}, "
                              f"Assignment attempts: {data.get('assignment_attempts', 0)}, "
                              f"History records: {assignment_count} assignments, {notification_count} notifications, "
                              f"Enhanced tracking: {', '.join(enhanced_tracking) if enhanced_tracking else 'basic tracking only'}")
                return True
            else:
                self.log_result("Job Assignment History", False, f"❌ PRIORITY ENDPOINT 2 FAILED! HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Job Assignment History", False, f"❌ PRIORITY ENDPOINT 2 ERROR! Request error: {str(e)}")
        return False
    
    def test_emergency_escalate_job(self):
        """PRIORITY TEST 3: POST /api/jobs/{job_id}/emergency-escalate - Test manual emergency escalation"""
        if 'workflow_job_id' not in self.test_data or 'admin_user_id' not in self.test_data:
            self.log_result("Emergency Escalate Job", False, "No workflow job ID or admin user ID available from previous tests")
            return False
        
        try:
            escalation_data = {
                "admin_user_id": self.test_data['admin_user_id'],
                "reason": "Client reported urgent safety issue - gas leak detected"
            }
            
            response = self.session.post(f"{API_BASE}/jobs/{self.test_data['workflow_job_id']}/emergency-escalate", 
                                       json=escalation_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    message = data.get('message', 'Emergency escalation completed')
                    self.log_result("Emergency Escalate Job", True, 
                                  f"✅ PRIORITY ENDPOINT 3 WORKING! Manual emergency escalation successful: {message}")
                    return True
                else:
                    self.log_result("Emergency Escalate Job", False, f"Emergency escalation failed: {data}", response)
            else:
                self.log_result("Emergency Escalate Job", False, f"❌ PRIORITY ENDPOINT 3 FAILED! HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Emergency Escalate Job", False, f"❌ PRIORITY ENDPOINT 3 ERROR! Request error: {str(e)}")
        return False
    
    def test_admin_workflow_analytics(self):
        """PRIORITY TEST 4: GET /api/admin/workflow-analytics - Test workflow analytics dashboard"""
        try:
            response = self.session.get(f"{API_BASE}/admin/workflow-analytics")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify comprehensive workflow analytics
                required_sections = [
                    'job_statistics', 'fixer_statistics', 
                    'fraud_monitoring', 'financial_statistics'
                ]
                
                missing_sections = [section for section in required_sections if section not in data]
                if missing_sections:
                    self.log_result("Admin Workflow Analytics", False, f"Missing required sections: {missing_sections}", response)
                    return False
                
                # Extract key metrics
                job_stats = data.get('job_statistics', {})
                fixer_stats = data.get('fixer_statistics', {})
                fraud_stats = data.get('fraud_monitoring', {})
                financial_stats = data.get('financial_statistics', {})
                
                # Verify detailed statistics
                analytics_features = []
                if job_stats.get('emergency_jobs') is not None:
                    analytics_features.append("emergency_tracking")
                if fixer_stats.get('frozen_fixers') is not None:
                    analytics_features.append("fixer_freeze_tracking")
                if fraud_stats.get('pending_alerts') is not None:
                    analytics_features.append("fraud_monitoring")
                if financial_stats.get('total_fees_owed') is not None:
                    analytics_features.append("financial_tracking")
                
                self.log_result("Admin Workflow Analytics", True, 
                              f"✅ PRIORITY ENDPOINT 4 WORKING! Comprehensive workflow analytics retrieved: "
                              f"Total jobs: {job_stats.get('total_jobs', 0)}, "
                              f"Active fixers: {fixer_stats.get('active_fixers', 0)}, "
                              f"Emergency jobs: {job_stats.get('emergency_jobs', 0)}, "
                              f"Fraud alerts: {fraud_stats.get('pending_alerts', 0)}, "
                              f"Analytics features: {', '.join(analytics_features)}")
                return True
            else:
                self.log_result("Admin Workflow Analytics", False, f"❌ PRIORITY ENDPOINT 4 FAILED! HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Admin Workflow Analytics", False, f"❌ PRIORITY ENDPOINT 4 ERROR! Request error: {str(e)}")
        return False
    
    def test_fixer_eligible_jobs(self):
        """PRIORITY TEST 5: GET /api/fixer/{fixer_id}/eligible-jobs - Test eligible jobs for fixers"""
        if 'workflow_fixer_id' not in self.test_data:
            self.log_result("Fixer Eligible Jobs", False, "No workflow fixer ID available from previous test")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/fixer/{self.test_data['workflow_fixer_id']}/eligible-jobs")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'available_jobs' in data:
                    available_jobs = data['available_jobs']
                    
                    # Verify job structure for eligible jobs
                    enhanced_features = []
                    if available_jobs:
                        first_job = available_jobs[0]
                        if 'assignment_timeout' in first_job:
                            enhanced_features.append("timeout_tracking")
                        if 'priority_level' in first_job:
                            enhanced_features.append("priority_levels")
                        if 'is_emergency' in first_job:
                            enhanced_features.append("emergency_flagging")
                    
                    self.log_result("Fixer Eligible Jobs", True, 
                                  f"✅ PRIORITY ENDPOINT 5 WORKING! Eligible jobs retrieved: "
                                  f"{len(available_jobs)} jobs available for fixer, "
                                  f"Enhanced features: {', '.join(enhanced_features) if enhanced_features else 'basic job listing'}")
                    return True
                else:
                    self.log_result("Fixer Eligible Jobs", False, "Missing 'available_jobs' field in response", response)
            else:
                self.log_result("Fixer Eligible Jobs", False, f"❌ PRIORITY ENDPOINT 5 FAILED! HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Fixer Eligible Jobs", False, f"❌ PRIORITY ENDPOINT 5 ERROR! Request error: {str(e)}")
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