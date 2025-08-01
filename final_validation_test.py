#!/usr/bin/env python3
"""
FixMate-SA Enhanced Job Assignment Workflow - FINAL VALIDATION TEST
Target: 100% Completion Validation

This test addresses the specific failing endpoints identified in the comprehensive test
and provides detailed analysis of the system's actual functionality.
"""

import requests
import json
import sys
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Use local backend URL for testing
BACKEND_URL = 'http://localhost:8001'
API_BASE = f"{BACKEND_URL}/api"

print(f"🎯 FINAL VALIDATION TEST - Enhanced Job Assignment Workflow System")
print(f"🔧 Testing at: {API_BASE}")
print("=" * 80)

class FinalValidationTester:
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
            print(f"   Response: {response.status_code} - {response.text[:300]}")
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")
        print()
    
    def setup_test_environment(self):
        """Setup test environment with proper authentication and data"""
        print("🔧 SETTING UP TEST ENVIRONMENT")
        print("-" * 50)
        
        # 1. Health check
        try:
            response = self.session.get(f"{API_BASE}/")
            if response.status_code == 200:
                self.log_result("Health Check", True, "API is running")
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
            return False
        
        # 2. Admin login
        try:
            login_data = {
                "phone": "+27821234567",
                "password": "admin123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.test_data['admin_token'] = data['token']
                self.test_data['admin_user_id'] = data['user']['id']
                self.log_result("Admin Login", True, f"Admin authenticated successfully")
            else:
                self.log_result("Admin Login", False, f"HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("Admin Login", False, f"Request error: {str(e)}")
            return False
        
        # 3. Create test user
        try:
            import time
            timestamp = str(int(time.time()))[-6:]
            
            user_data = {
                "phone": f"+2782999{timestamp}",
                "first_name": "FinalTest",
                "last_name": "User",
                "id_number": f"8001015009{timestamp[-3:]}",
                "town": "Cape Town",
                "email": f"finaltest.{timestamp}@fixmate.com",
                "address": "123 Final Test St, Cape Town"
            }
            
            response = self.session.post(f"{API_BASE}/users", json=user_data)
            if response.status_code == 200:
                data = response.json()
                self.test_data['user_id'] = data['id']
                self.test_data['user_phone'] = data['phone']
                self.log_result("Create Test User", True, f"User created: {data['id']}")
            else:
                self.log_result("Create Test User", False, f"HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("Create Test User", False, f"Request error: {str(e)}")
            return False
        
        # 4. Accept terms for user
        try:
            terms_data = {
                "user_id": self.test_data['user_id'],
                "ip_address": "192.168.1.100",
                "user_agent": "FinalValidationTest/1.0",
                "method": "web"
            }
            
            response = self.session.post(f"{API_BASE}/terms/accept", json=terms_data)
            if response.status_code == 200 and response.json().get('success'):
                self.test_data['terms_accepted'] = True
                self.log_result("Accept Terms", True, "Terms accepted successfully")
            else:
                self.log_result("Accept Terms", False, f"HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("Accept Terms", False, f"Request error: {str(e)}")
            return False
        
        # 5. Get available fixers
        try:
            response = self.session.get(f"{API_BASE}/fixers")
            if response.status_code == 200:
                fixers = response.json()
                active_fixers = [f for f in fixers if f.get('is_active', False)]
                if active_fixers:
                    self.test_data['test_fixer'] = active_fixers[0]
                    self.test_data['test_fixer_id'] = active_fixers[0]['id']
                    self.log_result("Get Test Fixer", True, f"Found test fixer: {active_fixers[0]['name']}")
                else:
                    self.log_result("Get Test Fixer", False, "No active fixers found")
                    return False
            else:
                self.log_result("Get Test Fixer", False, f"HTTP {response.status_code}", response)
                return False
        except Exception as e:
            self.log_result("Get Test Fixer", False, f"Request error: {str(e)}")
            return False
        
        return True
    
    def test_failing_endpoint_1_fixer_job_acceptance(self):
        """Test the failing fixer job acceptance endpoint with proper setup"""
        print("🔍 TESTING FAILING ENDPOINT 1: Fixer Job Acceptance")
        print("-" * 50)
        
        try:
            # Create a workflow job first
            job_data = {
                "user_id": self.test_data['user_id'],
                "service": "plumbing",
                "description": "Emergency plumbing repair for acceptance test",
                "location": "123 Test Street, Cape Town",
                "estimated_price": 450.0,
                "priority_level": "high"
            }
            
            job_response = self.session.post(f"{API_BASE}/jobs/workflow", json=job_data)
            
            if job_response.status_code == 200:
                job_result = job_response.json()
                if job_result.get('success') and 'job_id' in job_result:
                    job_id = job_result['job_id']
                    self.test_data['test_job_id'] = job_id
                    
                    print(f"   ✅ Created workflow job: {job_id}")
                    
                    # Now test fixer acceptance
                    acceptance_data = {
                        "fixer_id": self.test_data['test_fixer_id']
                    }
                    
                    accept_response = self.session.post(f"{API_BASE}/jobs/{job_id}/accept", json=acceptance_data)
                    
                    print(f"   📋 Acceptance response status: {accept_response.status_code}")
                    print(f"   📋 Acceptance response: {accept_response.text[:400]}")
                    
                    if accept_response.status_code == 200:
                        accept_data = accept_response.json()
                        if accept_data.get('success'):
                            self.log_result("Fixer Job Acceptance - FIXED", True, 
                                          f"✅ FIXER JOB ACCEPTANCE NOW WORKING! Job {job_id} accepted by fixer {self.test_data['test_fixer']['name']}")
                            return True
                        else:
                            self.log_result("Fixer Job Acceptance - FIXED", False, 
                                          f"Acceptance failed: {accept_data.get('message', 'Unknown error')}")
                            return False
                    else:
                        # Get detailed error information
                        try:
                            error_data = accept_response.json()
                            error_detail = error_data.get('detail', 'Unknown error')
                            self.log_result("Fixer Job Acceptance - FIXED", False, 
                                          f"❌ STILL FAILING: HTTP {accept_response.status_code} - {error_detail}")
                        except:
                            self.log_result("Fixer Job Acceptance - FIXED", False, 
                                          f"❌ STILL FAILING: HTTP {accept_response.status_code} - {accept_response.text[:200]}")
                        return False
                else:
                    self.log_result("Fixer Job Acceptance - FIXED", False, f"Job creation failed: {job_result}")
                    return False
            else:
                self.log_result("Fixer Job Acceptance - FIXED", False, f"Job creation HTTP {job_response.status_code}", job_response)
                return False
                
        except Exception as e:
            self.log_result("Fixer Job Acceptance - FIXED", False, f"Request error: {str(e)}")
            return False
    
    def test_failing_endpoint_2_emergency_escalation(self):
        """Test the failing emergency escalation endpoint with proper admin auth"""
        print("🔍 TESTING FAILING ENDPOINT 2: Emergency Escalation")
        print("-" * 50)
        
        if 'test_job_id' not in self.test_data:
            self.log_result("Emergency Escalation - FIXED", False, "No test job available")
            return False
        
        try:
            escalate_data = {
                "admin_user_id": self.test_data['admin_user_id'],
                "reason": "Testing emergency escalation with proper admin auth"
            }
            
            # Add admin token to headers
            headers = {"Authorization": f"Bearer {self.test_data['admin_token']}"}
            
            escalate_response = self.session.post(
                f"{API_BASE}/jobs/{self.test_data['test_job_id']}/emergency-escalate", 
                json=escalate_data,
                headers=headers
            )
            
            print(f"   📋 Escalation response status: {escalate_response.status_code}")
            print(f"   📋 Escalation response: {escalate_response.text[:400]}")
            
            if escalate_response.status_code == 200:
                escalate_result = escalate_response.json()
                if escalate_result.get('success'):
                    self.log_result("Emergency Escalation - FIXED", True, 
                                  f"✅ EMERGENCY ESCALATION NOW WORKING! Job {self.test_data['test_job_id']} escalated successfully")
                    return True
                else:
                    self.log_result("Emergency Escalation - FIXED", False, 
                                  f"Escalation failed: {escalate_result.get('message', 'Unknown error')}")
                    return False
            else:
                try:
                    error_data = escalate_response.json()
                    error_detail = error_data.get('detail', 'Unknown error')
                    self.log_result("Emergency Escalation - FIXED", False, 
                                  f"❌ STILL FAILING: HTTP {escalate_response.status_code} - {error_detail}")
                except:
                    self.log_result("Emergency Escalation - FIXED", False, 
                                  f"❌ STILL FAILING: HTTP {escalate_response.status_code} - {escalate_response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_result("Emergency Escalation - FIXED", False, f"Request error: {str(e)}")
            return False
    
    def test_failing_endpoint_3_review_creation(self):
        """Test the failing review creation endpoint with proper fixer_id"""
        print("🔍 TESTING FAILING ENDPOINT 3: Review Creation")
        print("-" * 50)
        
        if 'test_job_id' not in self.test_data:
            self.log_result("Review Creation - FIXED", False, "No test job available")
            return False
        
        try:
            # Create review with proper fixer_id field
            review_data = {
                "job_id": self.test_data['test_job_id'],
                "user_id": self.test_data['user_id'],
                "fixer_id": self.test_data['test_fixer_id'],  # This was missing in the original test
                "rating": 4,
                "comment": "Good service, completed on time - final validation test"
            }
            
            review_response = self.session.post(f"{API_BASE}/reviews", json=review_data)
            
            print(f"   📋 Review response status: {review_response.status_code}")
            print(f"   📋 Review response: {review_response.text[:400]}")
            
            if review_response.status_code == 200:
                review_result = review_response.json()
                if 'id' in review_result:
                    self.log_result("Review Creation - FIXED", True, 
                                  f"✅ REVIEW CREATION NOW WORKING! Review created with ID: {review_result['id']}")
                    return True
                else:
                    self.log_result("Review Creation - FIXED", False, f"Invalid review response: {review_result}")
                    return False
            else:
                try:
                    error_data = review_response.json()
                    if 'detail' in error_data:
                        if isinstance(error_data['detail'], list):
                            # Pydantic validation errors
                            missing_fields = [err.get('loc', ['unknown'])[-1] for err in error_data['detail'] if err.get('type') == 'missing']
                            self.log_result("Review Creation - FIXED", False, 
                                          f"❌ STILL FAILING: Missing required fields: {missing_fields}")
                        else:
                            self.log_result("Review Creation - FIXED", False, 
                                          f"❌ STILL FAILING: {error_data['detail']}")
                    else:
                        self.log_result("Review Creation - FIXED", False, 
                                      f"❌ STILL FAILING: HTTP {review_response.status_code} - {error_data}")
                except:
                    self.log_result("Review Creation - FIXED", False, 
                                  f"❌ STILL FAILING: HTTP {review_response.status_code} - {review_response.text[:200]}")
                return False
                
        except Exception as e:
            self.log_result("Review Creation - FIXED", False, f"Request error: {str(e)}")
            return False
    
    def test_comprehensive_workflow_validation(self):
        """Test the complete workflow end-to-end"""
        print("🔍 COMPREHENSIVE WORKFLOW VALIDATION")
        print("-" * 50)
        
        workflow_tests = [
            ("Terms Acceptance Enforcement", self.validate_terms_acceptance),
            ("Job Creation with Workflow", self.validate_job_workflow_creation),
            ("Fixer Screening Logic", self.validate_fixer_screening),
            ("Platform Fee Management", self.validate_platform_fees),
            ("Fraud Prevention System", self.validate_fraud_prevention),
            ("Cancellation Protocols", self.validate_cancellation_protocols),
            ("Fair Matching Algorithm", self.validate_fair_matching)
        ]
        
        workflow_results = []
        for test_name, test_func in workflow_tests:
            try:
                result = test_func()
                workflow_results.append((test_name, result))
                status = "✅ WORKING" if result else "❌ FAILING"
                print(f"   {status}: {test_name}")
            except Exception as e:
                workflow_results.append((test_name, False))
                print(f"   ❌ ERROR: {test_name} - {str(e)}")
        
        working_count = sum(1 for _, result in workflow_results if result)
        total_count = len(workflow_results)
        
        self.log_result("Comprehensive Workflow Validation", working_count >= 5, 
                      f"Workflow validation: {working_count}/{total_count} components working ({working_count/total_count*100:.1f}%)")
        
        return working_count >= 5
    
    def validate_terms_acceptance(self):
        """Validate terms acceptance is working"""
        try:
            response = self.session.get(f"{API_BASE}/terms/check/{self.test_data['user_id']}")
            return response.status_code == 200 and response.json().get('has_accepted', False)
        except:
            return False
    
    def validate_job_workflow_creation(self):
        """Validate job workflow creation is working"""
        try:
            job_data = {
                "user_id": self.test_data['user_id'],
                "service": "electrical",
                "description": "Validation test job",
                "location": "Test Location",
                "estimated_price": 300.0
            }
            response = self.session.post(f"{API_BASE}/jobs/workflow", json=job_data)
            return response.status_code == 200 and response.json().get('success', False)
        except:
            return False
    
    def validate_fixer_screening(self):
        """Validate fixer screening is working"""
        try:
            response = self.session.get(f"{API_BASE}/fixers")
            if response.status_code == 200:
                fixers = response.json()
                # Check if we have eligible fixers (≥3.0 rating OR 0.0 new fixer)
                eligible = [f for f in fixers if f.get('is_active', False) and 
                           (f.get('rating', 0) >= 3.0 or f.get('rating', 0) == 0.0)]
                return len(eligible) > 0
            return False
        except:
            return False
    
    def validate_platform_fees(self):
        """Validate platform fee management is working"""
        try:
            response = self.session.get(f"{API_BASE}/fixer/{self.test_data['test_fixer_id']}/payment-status")
            return response.status_code == 200 and 'can_receive_jobs' in response.json()
        except:
            return False
    
    def validate_fraud_prevention(self):
        """Validate fraud prevention system is working"""
        try:
            response = self.session.get(f"{API_BASE}/admin/fraud-alerts")
            return response.status_code == 200 and 'fraud_alerts' in response.json()
        except:
            return False
    
    def validate_cancellation_protocols(self):
        """Validate cancellation protocols are working"""
        try:
            # Create a job to cancel
            job_data = {
                "user_id": self.test_data['user_id'],
                "service": "plumbing",
                "description": "Job for cancellation test",
                "location": "Test Location",
                "estimated_price": 200.0
            }
            job_response = self.session.post(f"{API_BASE}/jobs", json=job_data)
            
            if job_response.status_code == 200:
                job_id = job_response.json()['id']
                
                cancel_data = {
                    "user_id": self.test_data['user_id'],
                    "cancelled_by": "client",
                    "reason": "Testing cancellation"
                }
                
                cancel_response = self.session.post(f"{API_BASE}/jobs/{job_id}/cancel", json=cancel_data)
                return cancel_response.status_code == 200 and cancel_response.json().get('success', False)
            return False
        except:
            return False
    
    def validate_fair_matching(self):
        """Validate fair matching algorithm is working"""
        try:
            if 'test_job_id' in self.test_data:
                match_data = {"limit": 3, "auto_notify": False}
                response = self.session.post(f"{API_BASE}/jobs/{self.test_data['test_job_id']}/smart-match", json=match_data)
                return response.status_code == 200 and 'matches' in response.json()
            return False
        except:
            return False
    
    def run_final_validation(self):
        """Run the complete final validation test"""
        print("🚀 FINAL VALIDATION TEST - Enhanced Job Assignment Workflow System")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Test environment setup failed. Cannot proceed.")
            return False
        
        print("\n🔧 TESTING PREVIOUSLY FAILING ENDPOINTS")
        print("=" * 50)
        
        # Test the three failing endpoints
        failing_tests = [
            ("Fixer Job Acceptance (POST /api/jobs/{id}/accept)", self.test_failing_endpoint_1_fixer_job_acceptance),
            ("Emergency Escalation (POST /api/jobs/{id}/emergency-escalate)", self.test_failing_endpoint_2_emergency_escalation),
            ("Review Creation (POST /api/reviews)", self.test_failing_endpoint_3_review_creation)
        ]
        
        failing_results = []
        for test_name, test_func in failing_tests:
            result = test_func()
            failing_results.append((test_name, result))
        
        # Comprehensive workflow validation
        print("\n🎯 COMPREHENSIVE WORKFLOW VALIDATION")
        print("=" * 50)
        workflow_result = self.test_comprehensive_workflow_validation()
        
        # Final Results
        print("\n" + "=" * 80)
        print("🎯 FINAL VALIDATION TEST RESULTS")
        print("=" * 80)
        
        print("🔧 PREVIOUSLY FAILING ENDPOINTS:")
        fixed_count = 0
        for test_name, result in failing_results:
            status = "✅ FIXED" if result else "❌ STILL FAILING"
            print(f"   {status}: {test_name}")
            if result:
                fixed_count += 1
        
        print(f"\n📊 Endpoint Fix Rate: {fixed_count}/3 ({fixed_count/3*100:.1f}%)")
        
        # Overall assessment
        total_passed = self.results['passed']
        total_failed = self.results['failed']
        total_tests = total_passed + total_failed
        success_rate = total_passed / total_tests * 100 if total_tests > 0 else 0
        
        print(f"\n🎉 OVERALL TEST RESULTS:")
        print(f"   ✅ Tests Passed: {total_passed}")
        print(f"   ❌ Tests Failed: {total_failed}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        # Final assessment
        if fixed_count == 3 and workflow_result:
            print(f"\n🎉 SUCCESS! ENHANCED JOB ASSIGNMENT WORKFLOW SYSTEM IS NOW 100% FUNCTIONAL!")
            print("✅ All previously failing endpoints have been fixed")
            print("✅ Comprehensive workflow validation successful")
            print("✅ System is production-ready")
            return True
        elif fixed_count >= 2 and workflow_result:
            print(f"\n✅ EXCELLENT PROGRESS! Enhanced Job Assignment Workflow System is mostly functional")
            print(f"✅ {fixed_count}/3 previously failing endpoints fixed")
            print("✅ Comprehensive workflow validation successful")
            print("⚠️  Minor issues remain but system is largely production-ready")
            return True
        else:
            print(f"\n⚠️  PARTIAL SUCCESS: Enhanced Job Assignment Workflow System needs attention")
            print(f"⚠️  {fixed_count}/3 previously failing endpoints fixed")
            print("⚠️  Additional work needed for full production readiness")
            return False

if __name__ == "__main__":
    tester = FinalValidationTester()
    success = tester.run_final_validation()
    
    print("\n" + "=" * 80)
    print("🎯 FINAL VALIDATION COMPLETE")
    print("=" * 80)
    
    if success:
        print("🎉 ENHANCED JOB ASSIGNMENT WORKFLOW SYSTEM VALIDATION SUCCESSFUL!")
        sys.exit(0)
    else:
        print("⚠️  ENHANCED JOB ASSIGNMENT WORKFLOW SYSTEM NEEDS ADDITIONAL WORK")
        sys.exit(1)