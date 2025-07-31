#!/usr/bin/env python3
"""
FixMate-SA Phase 2: Trust & Reliability System Testing Script
Tests the newly implemented Phase 2 features:
1. Photo Verification System
2. Dispute Resolution System  
3. Enhanced Job Completion
"""

import requests
import json
import sys
from datetime import datetime, timedelta
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔧 Testing Phase 2: Trust & Reliability System at: {API_BASE}")
print("=" * 80)
print("🎯 PHASE 2: TRUST & RELIABILITY SYSTEM TESTING")
print("=" * 80)

class Phase2Tester:
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
    
    def setup_test_data(self):
        """Setup basic test data needed for Phase 2 tests"""
        try:
            # Create test user
            import time
            timestamp = str(int(time.time()))[-6:]
            
            user_data = {
                "phone": f"+2782123{timestamp}",
                "first_name": "John",
                "last_name": "TestUser",
                "id_number": f"8001015009{timestamp[-3:]}",
                "town": "Cape Town",
                "email": f"john.test.{timestamp}@example.com",
                "address": "123 Test St, Cape Town"
            }
            
            response = self.session.post(f"{API_BASE}/users", json=user_data)
            if response.status_code == 200:
                user = response.json()
                self.test_data['user_id'] = user['id']
                self.test_data['user'] = user
                
                # Set password and login
                set_password_data = {
                    "phone": user_data["phone"],
                    "password": "testpass123",
                    "confirm_password": "testpass123"
                }
                
                password_response = self.session.post(f"{API_BASE}/auth/set-password", json=set_password_data)
                if password_response.status_code == 200:
                    # Login to get token
                    login_data = {
                        "phone": user_data["phone"],
                        "password": "testpass123"
                    }
                    
                    login_response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                    if login_response.status_code == 200:
                        login_result = login_response.json()
                        self.test_data['token'] = login_result['token']
                        self.log_result("Setup Test User", True, f"Test user created and authenticated. ID: {user['id']}")
                        return True
            
            self.log_result("Setup Test User", False, "Failed to create test user")
            return False
            
        except Exception as e:
            self.log_result("Setup Test User", False, f"Error: {str(e)}")
            return False
    
    def setup_admin_user(self):
        """Setup admin user for admin-only tests"""
        try:
            # Try to login as admin
            login_data = {
                "phone": "+27821234567",
                "password": "admin123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("role_info", {}).get("role") == "admin":
                    self.test_data['admin_token'] = data['token']
                    self.test_data['admin_user'] = data['user']
                    self.log_result("Setup Admin User", True, "Admin user authenticated successfully")
                    return True
                else:
                    self.log_result("Setup Admin User", False, f"User is not admin: {data.get('role_info', {}).get('role')}")
            else:
                self.log_result("Setup Admin User", False, f"Admin login failed: HTTP {response.status_code}")
            return False
            
        except Exception as e:
            self.log_result("Setup Admin User", False, f"Error: {str(e)}")
            return False
    
    def create_test_job(self):
        """Create a test job for photo verification and dispute testing"""
        if 'user_id' not in self.test_data:
            return False
        
        try:
            job_data = {
                "user_id": self.test_data['user_id'],
                "service": "plumbing",
                "description": "Fix leaking kitchen tap - urgent repair needed",
                "location": "123 Test St, Cape Town",
                "estimated_price": 250.0
            }
            
            response = self.session.post(f"{API_BASE}/jobs", json=job_data)
            if response.status_code == 200:
                job = response.json()
                self.test_data['job_id'] = job['id']
                self.test_data['job'] = job
                self.log_result("Create Test Job", True, f"Test job created. ID: {job['id']}")
                return True
            else:
                self.log_result("Create Test Job", False, f"HTTP {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_result("Create Test Job", False, f"Error: {str(e)}")
            return False
    
    # ======= PHOTO VERIFICATION SYSTEM TESTS =======
    
    def test_photo_submission_before_photos(self):
        """Test submitting before photos for a job"""
        if 'job_id' not in self.test_data or 'token' not in self.test_data:
            self.log_result("Photo Submission - Before Photos", False, "No job ID or token available")
            return False
        
        try:
            # Create sample base64 image data (minimal PNG)
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
            base64_image = base64.b64encode(png_data).decode('utf-8')
            
            photo_data = {
                "photo_type": "before",
                "photos": [base64_image, base64_image]  # Just the base64 strings
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['token']}"}
            response = self.session.post(f"{API_BASE}/jobs/{self.test_data['job_id']}/photos", 
                                       json=photo_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'verification_id' in data.get('data', {}):
                    self.test_data['verification_id'] = data['data']['verification_id']
                    self.log_result("Photo Submission - Before Photos", True, 
                                  f"Before photos submitted successfully. Verification ID: {data['data']['verification_id']}")
                    return True
                else:
                    self.log_result("Photo Submission - Before Photos", False, "Invalid response format", response)
            else:
                self.log_result("Photo Submission - Before Photos", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Photo Submission - Before Photos", False, f"Request error: {str(e)}")
            if response:
                try:
                    error_detail = response.json()
                    print(f"   Error details: {error_detail}")
                except:
                    print(f"   Response text: {response.text[:500]}")
        return False
    
    def test_photo_submission_after_photos(self):
        """Test submitting after photos for a job"""
        if 'job_id' not in self.test_data or 'token' not in self.test_data:
            self.log_result("Photo Submission - After Photos", False, "No job ID or token available")
            return False
        
        try:
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
            base64_image = base64.b64encode(png_data).decode('utf-8')
            
            photo_data = {
                "photo_type": "after",
                "photos": [base64_image]  # Just the base64 string
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['token']}"}
            response = self.session.post(f"{API_BASE}/jobs/{self.test_data['job_id']}/photos", 
                                       json=photo_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("Photo Submission - After Photos", True, 
                                  f"After photos submitted successfully. Photos count: {data.get('data', {}).get('photos_count', 0)}")
                    return True
                else:
                    self.log_result("Photo Submission - After Photos", False, "Invalid response format", response)
            else:
                self.log_result("Photo Submission - After Photos", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Photo Submission - After Photos", False, f"Request error: {str(e)}")
        return False
    
    def test_photo_submission_invalid_type(self):
        """Test photo submission with invalid photo type"""
        if 'job_id' not in self.test_data or 'token' not in self.test_data:
            self.log_result("Photo Submission - Invalid Type", False, "No job ID or token available")
            return False
        
        try:
            photo_data = {
                "photo_type": "invalid_type",
                "photos": [{"data": "test", "filename": "test.png"}]
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['token']}"}
            response = self.session.post(f"{API_BASE}/jobs/{self.test_data['job_id']}/photos", 
                                       json=photo_data, headers=headers)
            
            if response.status_code == 400:
                self.log_result("Photo Submission - Invalid Type", True, "Invalid photo type correctly rejected")
                return True
            else:
                self.log_result("Photo Submission - Invalid Type", False, f"Expected 400 but got HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Photo Submission - Invalid Type", False, f"Request error: {str(e)}")
        return False
    
    def test_get_photo_verification_status(self):
        """Test getting photo verification status for a job"""
        if 'job_id' not in self.test_data:
            self.log_result("Get Photo Verification Status", False, "No job ID available")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/jobs/{self.test_data['job_id']}/photo-verification")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    verification = data.get('verification')
                    if verification:
                        self.log_result("Get Photo Verification Status", True, 
                                      f"Photo verification found. Status: {verification.get('status', 'unknown')}")
                    else:
                        self.log_result("Get Photo Verification Status", True, "No photo verification found for job")
                    return True
                else:
                    self.log_result("Get Photo Verification Status", False, "Invalid response format", response)
            else:
                self.log_result("Get Photo Verification Status", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Photo Verification Status", False, f"Request error: {str(e)}")
        return False
    
    def test_get_verification_photos(self):
        """Test getting photo data from verification"""
        if 'verification_id' not in self.test_data:
            self.log_result("Get Verification Photos", False, "No verification ID available")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/verification/{self.test_data['verification_id']}/photos/before")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    photos = data.get('photos', [])
                    self.log_result("Get Verification Photos", True, 
                                  f"Retrieved {len(photos)} before photos from verification")
                    return True
                else:
                    self.log_result("Get Verification Photos", False, "Invalid response format", response)
            else:
                self.log_result("Get Verification Photos", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Verification Photos", False, f"Request error: {str(e)}")
        return False
    
    def test_admin_verify_photos(self):
        """Test admin photo verification"""
        if 'verification_id' not in self.test_data or 'admin_token' not in self.test_data:
            self.log_result("Admin Verify Photos", False, "No verification ID or admin token available")
            return False
        
        try:
            verification_data = {
                "decision": "approved",
                "comments": "Photos clearly show the work completed satisfactorily"
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['admin_token']}"}
            response = self.session.post(f"{API_BASE}/admin/photo-verification/{self.test_data['verification_id']}/verify", 
                                       json=verification_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("Admin Verify Photos", True, 
                                  f"Photos verified successfully. Decision: {data.get('decision')}")
                    return True
                else:
                    self.log_result("Admin Verify Photos", False, "Verification failed", response)
            else:
                self.log_result("Admin Verify Photos", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Admin Verify Photos", False, f"Request error: {str(e)}")
        return False
    
    def test_get_pending_photo_verifications(self):
        """Test getting pending photo verifications (admin only)"""
        if 'admin_token' not in self.test_data:
            self.log_result("Get Pending Photo Verifications", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.test_data['admin_token']}"}
            response = self.session.get(f"{API_BASE}/admin/photo-verifications/pending", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    pending_count = data.get('count', 0)
                    self.log_result("Get Pending Photo Verifications", True, 
                                  f"Retrieved {pending_count} pending photo verifications")
                    return True
                else:
                    self.log_result("Get Pending Photo Verifications", False, "Invalid response format", response)
            else:
                self.log_result("Get Pending Photo Verifications", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Pending Photo Verifications", False, f"Request error: {str(e)}")
        return False
    
    # ======= DISPUTE RESOLUTION SYSTEM TESTS =======
    
    def test_create_dispute_quality_issue(self):
        """Test creating a dispute for quality issues"""
        if 'job_id' not in self.test_data or 'token' not in self.test_data:
            self.log_result("Create Dispute - Quality Issue", False, "No job ID or token available")
            return False
        
        try:
            dispute_data = {
                "dispute_type": "quality",
                "description": "The fixer did not complete the work to the agreed standard. The tap is still leaking.",
                "evidence": "Photos show continued leaking after repair",
                "requested_resolution": "Refund or redo the work properly"
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['token']}"}
            response = self.session.post(f"{API_BASE}/jobs/{self.test_data['job_id']}/dispute", 
                                       json=dispute_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'dispute_id' in data:
                    self.test_data['dispute_id'] = data['dispute_id']
                    self.log_result("Create Dispute - Quality Issue", True, 
                                  f"Quality dispute created successfully. ID: {data['dispute_id']}")
                    return True
                else:
                    self.log_result("Create Dispute - Quality Issue", False, "Invalid response format", response)
            else:
                self.log_result("Create Dispute - Quality Issue", False, f"HTTP {response.status_code}", response)
                try:
                    error_detail = response.json()
                    print(f"   Error details: {error_detail}")
                except:
                    print(f"   Response text: {response.text[:500]}")
        except Exception as e:
            self.log_result("Create Dispute - Quality Issue", False, f"Request error: {str(e)}")
        return False
    
    def test_add_dispute_message(self):
        """Test adding messages to a dispute"""
        if 'dispute_id' not in self.test_data or 'token' not in self.test_data:
            self.log_result("Add Dispute Message", False, "No dispute ID or token available")
            return False
        
        try:
            message_data = {
                "message": "I have additional photos showing the poor quality of work",
                "message_type": "evidence",
                "attachments": ["photo_evidence_1.jpg", "photo_evidence_2.jpg"]
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['token']}"}
            response = self.session.post(f"{API_BASE}/disputes/{self.test_data['dispute_id']}/messages", 
                                       json=message_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'message_id' in data:
                    self.log_result("Add Dispute Message", True, 
                                  f"Message added to dispute successfully. Message ID: {data['message_id']}")
                    return True
                else:
                    self.log_result("Add Dispute Message", False, "Invalid response format", response)
            else:
                self.log_result("Add Dispute Message", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Add Dispute Message", False, f"Request error: {str(e)}")
        return False
    
    def test_get_dispute_details(self):
        """Test getting complete dispute details"""
        if 'dispute_id' not in self.test_data or 'token' not in self.test_data:
            self.log_result("Get Dispute Details", False, "No dispute ID or token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.test_data['token']}"}
            response = self.session.get(f"{API_BASE}/disputes/{self.test_data['dispute_id']}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'dispute' in data:
                    dispute = data['dispute']
                    messages_count = len(dispute.get('messages', []))
                    self.log_result("Get Dispute Details", True, 
                                  f"Dispute details retrieved. Status: {dispute.get('status')}, Messages: {messages_count}")
                    return True
                else:
                    self.log_result("Get Dispute Details", False, "Invalid response format", response)
            else:
                self.log_result("Get Dispute Details", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Dispute Details", False, f"Request error: {str(e)}")
        return False
    
    def test_admin_resolve_dispute(self):
        """Test admin dispute resolution"""
        if 'dispute_id' not in self.test_data or 'admin_token' not in self.test_data:
            self.log_result("Admin Resolve Dispute", False, "No dispute ID or admin token available")
            return False
        
        try:
            resolution_data = {
                "resolution_action": "partial_refund",
                "resolution": "After reviewing the evidence, we find that the work was partially completed. Client will receive 50% refund and fixer will redo the remaining work.",
                "refund_amount": 125.0,
                "requires_rework": True,
                "admin_notes": "Quality issue confirmed through photo evidence"
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['admin_token']}"}
            response = self.session.post(f"{API_BASE}/admin/disputes/{self.test_data['dispute_id']}/resolve", 
                                       json=resolution_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("Admin Resolve Dispute", True, 
                                  f"Dispute resolved successfully. Action: {data.get('resolution_action')}")
                    return True
                else:
                    self.log_result("Admin Resolve Dispute", False, "Resolution failed", response)
            else:
                self.log_result("Admin Resolve Dispute", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Admin Resolve Dispute", False, f"Request error: {str(e)}")
        return False
    
    def test_get_pending_disputes(self):
        """Test getting pending disputes (admin only)"""
        if 'admin_token' not in self.test_data:
            self.log_result("Get Pending Disputes", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.test_data['admin_token']}"}
            response = self.session.get(f"{API_BASE}/admin/disputes/pending", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    pending_count = data.get('count', 0)
                    self.log_result("Get Pending Disputes", True, 
                                  f"Retrieved {pending_count} pending disputes")
                    return True
                else:
                    self.log_result("Get Pending Disputes", False, "Invalid response format", response)
            else:
                self.log_result("Get Pending Disputes", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Pending Disputes", False, f"Request error: {str(e)}")
        return False
    
    def test_admin_auto_escalate_disputes(self):
        """Test admin auto-escalation of disputes"""
        if 'admin_token' not in self.test_data:
            self.log_result("Admin Auto-Escalate Disputes", False, "No admin token available")
            return False
        
        try:
            escalation_data = {
                "escalation_criteria": {
                    "age_hours": 24,
                    "dispute_types": ["quality", "no_show"],
                    "priority_threshold": "high"
                }
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['admin_token']}"}
            response = self.session.post(f"{API_BASE}/admin/disputes/auto-escalate", 
                                       json=escalation_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    escalated_count = data.get('escalated_count', 0)
                    self.log_result("Admin Auto-Escalate Disputes", True, 
                                  f"Auto-escalation completed. {escalated_count} disputes escalated")
                    return True
                else:
                    self.log_result("Admin Auto-Escalate Disputes", False, "Auto-escalation failed", response)
            else:
                self.log_result("Admin Auto-Escalate Disputes", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Admin Auto-Escalate Disputes", False, f"Request error: {str(e)}")
        return False
    
    # ======= ENHANCED JOB COMPLETION TESTS =======
    
    def test_complete_job_with_photos(self):
        """Test enhanced job completion with photo verification"""
        if 'job_id' not in self.test_data or 'token' not in self.test_data:
            self.log_result("Complete Job with Photos", False, "No job ID or token available")
            return False
        
        try:
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
            base64_image = base64.b64encode(png_data).decode('utf-8')
            
            completion_data = {
                "completion_notes": "Job completed successfully. Tap is no longer leaking.",
                "final_price": 275.0,
                "before_photos": [base64_image],  # List of base64 strings
                "after_photos": [base64_image],   # List of base64 strings
                "quality_checklist": {
                    "work_completed": True,
                    "area_cleaned": True,
                    "customer_satisfied": True,
                    "warranty_provided": True
                }
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['token']}"}
            response = self.session.post(f"{API_BASE}/jobs/{self.test_data['job_id']}/complete-with-photos", 
                                       json=completion_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("Complete Job with Photos", True, 
                                  f"Job completed with photo verification. Status: {data.get('status')}")
                    return True
                else:
                    self.log_result("Complete Job with Photos", False, "Job completion failed", response)
            else:
                self.log_result("Complete Job with Photos", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Complete Job with Photos", False, f"Request error: {str(e)}")
        return False
    
    # ======= SECURITY TESTS =======
    
    def test_unauthorized_admin_access(self):
        """Test that non-admin users cannot access admin endpoints"""
        if 'token' not in self.test_data:
            self.log_result("Unauthorized Admin Access", False, "No user token available")
            return False
        
        try:
            # Try to access admin endpoint with regular user token
            headers = {"Authorization": f"Bearer {self.test_data['token']}"}
            response = self.session.get(f"{API_BASE}/admin/photo-verifications/pending", headers=headers)
            
            if response.status_code == 403:
                self.log_result("Unauthorized Admin Access", True, "Non-admin user correctly denied access to admin endpoint")
                return True
            else:
                self.log_result("Unauthorized Admin Access", False, f"Expected 403 but got HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Unauthorized Admin Access", False, f"Request error: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all Phase 2 tests"""
        print("🚀 Starting Phase 2: Trust & Reliability System testing...")
        print()
        
        # Setup
        if not self.setup_test_data():
            print("❌ Failed to setup test data. Aborting tests.")
            return
        
        if not self.setup_admin_user():
            print("⚠️  Failed to setup admin user. Admin tests will be skipped.")
        
        if not self.create_test_job():
            print("⚠️  Failed to create test job. Some tests may be skipped.")
        
        # Photo Verification System Tests
        print("\n📸 PHOTO VERIFICATION SYSTEM TESTS")
        print("-" * 50)
        self.test_photo_submission_before_photos()
        self.test_photo_submission_after_photos()
        self.test_photo_submission_invalid_type()
        self.test_get_photo_verification_status()
        self.test_get_verification_photos()
        
        if 'admin_token' in self.test_data:
            self.test_admin_verify_photos()
            self.test_get_pending_photo_verifications()
        
        # Dispute Resolution System Tests
        print("\n⚖️  DISPUTE RESOLUTION SYSTEM TESTS")
        print("-" * 50)
        self.test_create_dispute_quality_issue()
        self.test_add_dispute_message()
        self.test_get_dispute_details()
        
        if 'admin_token' in self.test_data:
            self.test_admin_resolve_dispute()
            self.test_get_pending_disputes()
            self.test_admin_auto_escalate_disputes()
        
        # Enhanced Job Completion Tests
        print("\n✅ ENHANCED JOB COMPLETION TESTS")
        print("-" * 50)
        self.test_complete_job_with_photos()
        
        # Security Tests
        print("\n🔒 SECURITY TESTS")
        print("-" * 50)
        self.test_unauthorized_admin_access()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎯 PHASE 2: TRUST & RELIABILITY TESTING SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {self.results['passed']}")
        print(f"❌ Tests Failed: {self.results['failed']}")
        total_tests = self.results['passed'] + self.results['failed']
        if total_tests > 0:
            print(f"📊 Success Rate: {(self.results['passed'] / total_tests * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        print("\n🎉 Phase 2: Trust & Reliability system testing completed!")
        print("=" * 80)

if __name__ == "__main__":
    tester = Phase2Tester()
    tester.run_all_tests()