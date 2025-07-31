#!/usr/bin/env python3
"""
FixMate-SA Phase 3: Automation & Engagement Backend Testing Script
Tests the Phase 3 backend systems after critical authentication fixes have been applied.

PRIORITY FOCUS: Test the 5 previously failing endpoints with authentication issues:

Real-Time Job Tracking Endpoints (Authentication Fixes Applied):
1. POST /api/jobs/{job_id}/tracking/start - Fixed User-Fixer relationship lookup
2. POST /api/jobs/{job_id}/tracking/location - Fixed User-Fixer relationship lookup  
3. POST /api/jobs/{job_id}/tracking/complete - Fixed User-Fixer relationship lookup

Gamification System Endpoints (Authentication Fixes Applied):
4. POST /api/fixer/{fixer_id}/reputation/initialize - Fixed ownership validation
5. POST /api/fixer/{fixer_id}/reputation/update - Fixed ownership validation

Also verify the working endpoints remain stable:
- GET /api/jobs/{job_id}/tracking/status (was working)
- GET /api/fixer/{fixer_id}/reputation (was working)
- All 5 AI Multilingual Assistant endpoints (were working)
- All 2 Admin Analytics endpoints (were working)

Authentication Context:
- Admin: +27821234567 / admin123
- The fixes ensure endpoints query Fixer table by current_user.id to find associated fixer record
- Services now receive actual Fixer.id instead of User.id
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

print(f"🔧 Testing Phase 3: Automation & Engagement System at: {API_BASE}")
print("=" * 80)
print("🎯 PHASE 3 AUTHENTICATION FIXES TESTING")
print("=" * 80)

class Phase3APITester:
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
                    self.log_result("Admin Login", True, f"Admin login successful, role: {data.get('role_info', {}).get('role', 'unknown')}")
                    return True
                else:
                    self.log_result("Admin Login", False, "Invalid response format", response)
            else:
                self.log_result("Admin Login", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Admin Login", False, f"Request error: {str(e)}")
        return False
    
    def setup_fixer_user_for_testing(self):
        """Create a fixer user for testing authentication fixes"""
        import time
        timestamp = str(int(time.time()))[-6:]
        
        # Create user first
        user_data = {
            "phone": f"+2782987{timestamp}",
            "first_name": "Test",
            "last_name": "Fixer",
            "id_number": f"8001015009{timestamp[-3:]}",
            "town": "Cape Town",
            "email": f"test.fixer.{timestamp}@fixmate.com",
            "address": "123 Fixer St, Cape Town"
        }
        
        try:
            # Create user
            user_response = self.session.post(f"{API_BASE}/users", json=user_data)
            if user_response.status_code != 200:
                self.log_result("Setup Fixer User", False, "Failed to create user for fixer", user_response)
                return False
            
            fixer_user = user_response.json()
            
            # Set password for the user
            set_password_data = {
                "phone": fixer_user['phone'],
                "password": "fixer123",
                "confirm_password": "fixer123"
            }
            
            password_response = self.session.post(f"{API_BASE}/auth/set-password", json=set_password_data)
            if password_response.status_code != 200:
                self.log_result("Setup Fixer User", False, "Failed to set password for fixer user", password_response)
                return False
            
            # Create fixer record
            fixer_data = {
                "user_id": fixer_user['id'],
                "phone": f"+2782987{timestamp}",
                "name": "Test Fixer",
                "email": f"test.fixer.{timestamp}@fixmate.com",
                "services": '["plumbing", "electrical", "carpentry"]',
                "location": "Cape Town"
            }
            
            fixer_response = self.session.post(f"{API_BASE}/fixers", json=fixer_data)
            if fixer_response.status_code != 200:
                self.log_result("Setup Fixer User", False, "Failed to create fixer record", fixer_response)
                return False
            
            fixer = fixer_response.json()
            
            # Login as fixer to get token
            login_data = {
                "phone": fixer_user['phone'],
                "password": "fixer123"
            }
            
            login_response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if login_response.status_code != 200:
                self.log_result("Setup Fixer User", False, "Failed to login as fixer", login_response)
                return False
            
            login_result = login_response.json()
            
            # Store test data
            self.test_data['fixer_user'] = fixer_user
            self.test_data['fixer'] = fixer
            self.test_data['fixer_token'] = login_result['token']
            self.test_data['fixer_id'] = fixer['id']
            self.test_data['fixer_user_id'] = fixer_user['id']
            
            self.log_result("Setup Fixer User", True, f"Fixer user created and logged in. User ID: {fixer_user['id']}, Fixer ID: {fixer['id']}")
            return True
            
        except Exception as e:
            self.log_result("Setup Fixer User", False, f"Request error: {str(e)}")
        return False
    
    def setup_test_job(self):
        """Create a test job for tracking tests"""
        if 'fixer_user_id' not in self.test_data:
            self.log_result("Setup Test Job", False, "No fixer user available")
            return False
        
        job_data = {
            "user_id": self.test_data['fixer_user_id'],
            "service": "plumbing",
            "description": "Fix leaking kitchen tap for tracking test",
            "location": "123 Test St, Cape Town",
            "estimated_price": 250.0
        }
        
        try:
            response = self.session.post(f"{API_BASE}/jobs", json=job_data)
            if response.status_code == 200:
                job = response.json()
                
                # Assign the job to the fixer
                update_data = {
                    "fixer_id": self.test_data['fixer_id'],
                    "status": "assigned"
                }
                
                update_response = self.session.put(f"{API_BASE}/jobs/{job['id']}", json=update_data)
                if update_response.status_code == 200:
                    updated_job = update_response.json()
                    self.test_data['test_job'] = updated_job
                    self.test_data['job_id'] = updated_job['id']
                    self.log_result("Setup Test Job", True, f"Test job created and assigned. Job ID: {updated_job['id']}")
                    return True
                else:
                    self.log_result("Setup Test Job", False, "Failed to assign job to fixer", update_response)
            else:
                self.log_result("Setup Test Job", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Setup Test Job", False, f"Request error: {str(e)}")
        return False
    
    # ======= PHASE 3: REAL-TIME TRACKING TESTS (AUTHENTICATION FIXES) =======
    
    def test_job_tracking_start(self):
        """Test POST /api/jobs/{job_id}/tracking/start - Fixed User-Fixer relationship lookup"""
        if not all(key in self.test_data for key in ['job_id', 'fixer_token']):
            self.log_result("Job Tracking Start", False, "Missing job ID or fixer token")
            return False
        
        try:
            tracking_data = {
                "latitude": -33.9249,
                "longitude": 18.4241,
                "notes": "Starting job - arrived at location"
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['fixer_token']}"}
            response = self.session.post(f"{API_BASE}/jobs/{self.test_data['job_id']}/tracking/start", 
                                       json=tracking_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("Job Tracking Start", True, 
                                  f"Job tracking started successfully. Status: {data.get('status', 'unknown')}")
                    return True
                else:
                    self.log_result("Job Tracking Start", False, "Tracking start failed", response)
            else:
                self.log_result("Job Tracking Start", False, f"HTTP {response.status_code} - Authentication fix may not be working", response)
        except Exception as e:
            self.log_result("Job Tracking Start", False, f"Request error: {str(e)}")
        return False
    
    def test_job_tracking_location(self):
        """Test POST /api/jobs/{job_id}/tracking/location - Fixed User-Fixer relationship lookup"""
        if not all(key in self.test_data for key in ['job_id', 'fixer_token']):
            self.log_result("Job Tracking Location", False, "Missing job ID or fixer token")
            return False
        
        try:
            location_data = {
                "location": {
                    "lat": -33.9250,
                    "lng": 18.4242
                },
                "accuracy": 5.0
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['fixer_token']}"}
            response = self.session.post(f"{API_BASE}/jobs/{self.test_data['job_id']}/tracking/location", 
                                       json=location_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("Job Tracking Location", True, 
                                  f"Location updated successfully. Status: {data.get('tracking_status', 'unknown')}")
                    return True
                else:
                    self.log_result("Job Tracking Location", False, "Location update failed", response)
            else:
                self.log_result("Job Tracking Location", False, f"HTTP {response.status_code} - Authentication fix may not be working", response)
        except Exception as e:
            self.log_result("Job Tracking Location", False, f"Request error: {str(e)}")
        return False
    
    def test_job_tracking_complete(self):
        """Test POST /api/jobs/{job_id}/tracking/complete - Fixed User-Fixer relationship lookup"""
        if not all(key in self.test_data for key in ['job_id', 'fixer_token']):
            self.log_result("Job Tracking Complete", False, "Missing job ID or fixer token")
            return False
        
        try:
            completion_data = {
                "latitude": -33.9249,
                "longitude": 18.4241,
                "completion_notes": "Job completed successfully - tap fixed",
                "duration_minutes": 45,
                "final_status": "completed"
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['fixer_token']}"}
            response = self.session.post(f"{API_BASE}/jobs/{self.test_data['job_id']}/tracking/complete", 
                                       json=completion_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("Job Tracking Complete", True, 
                                  f"Job tracking completed successfully. Final status: {data.get('final_status', 'unknown')}")
                    return True
                else:
                    self.log_result("Job Tracking Complete", False, "Tracking completion failed", response)
            else:
                self.log_result("Job Tracking Complete", False, f"HTTP {response.status_code} - Authentication fix may not be working", response)
        except Exception as e:
            self.log_result("Job Tracking Complete", False, f"Request error: {str(e)}")
        return False
    
    def test_job_tracking_status(self):
        """Test GET /api/jobs/{job_id}/tracking/status - Should remain working"""
        if 'job_id' not in self.test_data:
            self.log_result("Job Tracking Status", False, "Missing job ID")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/jobs/{self.test_data['job_id']}/tracking/status")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'tracking' in data:
                    tracking = data['tracking']
                    if tracking:
                        self.log_result("Job Tracking Status", True, 
                                      f"Tracking status retrieved: {tracking.get('status', 'unknown')}")
                    else:
                        self.log_result("Job Tracking Status", True, "No tracking information available")
                    return True
                else:
                    self.log_result("Job Tracking Status", False, "Invalid response format", response)
            else:
                self.log_result("Job Tracking Status", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Job Tracking Status", False, f"Request error: {str(e)}")
        return False
    
    # ======= PHASE 3: GAMIFICATION SYSTEM TESTS (AUTHENTICATION FIXES) =======
    
    def test_fixer_reputation_initialize(self):
        """Test POST /api/fixer/{fixer_id}/reputation/initialize - Fixed ownership validation"""
        if not all(key in self.test_data for key in ['fixer_id', 'fixer_token']):
            self.log_result("Fixer Reputation Initialize", False, "Missing fixer ID or token")
            return False
        
        try:
            init_data = {
                "initial_tier": "bronze",
                "starting_points": 0,
                "specializations": ["plumbing", "electrical"]
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['fixer_token']}"}
            response = self.session.post(f"{API_BASE}/fixer/{self.test_data['fixer_id']}/reputation/initialize", 
                                       json=init_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("Fixer Reputation Initialize", True, 
                                  f"Reputation initialized successfully. Tier: {data.get('tier', 'unknown')}")
                    return True
                else:
                    self.log_result("Fixer Reputation Initialize", False, "Reputation initialization failed", response)
            else:
                self.log_result("Fixer Reputation Initialize", False, f"HTTP {response.status_code} - Authentication fix may not be working", response)
        except Exception as e:
            self.log_result("Fixer Reputation Initialize", False, f"Request error: {str(e)}")
        return False
    
    def test_fixer_reputation_update(self):
        """Test POST /api/fixer/{fixer_id}/reputation/update - Fixed ownership validation"""
        if not all(key in self.test_data for key in ['fixer_id', 'fixer_token']):
            self.log_result("Fixer Reputation Update", False, "Missing fixer ID or token")
            return False
        
        try:
            update_data = {
                "action": "job_completed",
                "points": 10,
                "job_id": self.test_data.get('job_id'),
                "quality_rating": 5,
                "bonus_reason": "excellent_work"
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['fixer_token']}"}
            response = self.session.post(f"{API_BASE}/fixer/{self.test_data['fixer_id']}/reputation/update", 
                                       json=update_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("Fixer Reputation Update", True, 
                                  f"Reputation updated successfully. New points: {data.get('total_points', 'unknown')}")
                    return True
                else:
                    self.log_result("Fixer Reputation Update", False, "Reputation update failed", response)
            else:
                self.log_result("Fixer Reputation Update", False, f"HTTP {response.status_code} - Authentication fix may not be working", response)
        except Exception as e:
            self.log_result("Fixer Reputation Update", False, f"Request error: {str(e)}")
        return False
    
    def test_fixer_reputation_get(self):
        """Test GET /api/fixer/{fixer_id}/reputation - Should remain working"""
        if 'fixer_id' not in self.test_data:
            self.log_result("Fixer Reputation Get", False, "Missing fixer ID")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/fixer/{self.test_data['fixer_id']}/reputation")
            
            if response.status_code == 200:
                data = response.json()
                if 'reputation' in data:
                    reputation = data['reputation']
                    self.log_result("Fixer Reputation Get", True, 
                                  f"Reputation retrieved: Tier {reputation.get('tier', 'unknown')}, Points {reputation.get('total_points', 0)}")
                    return True
                else:
                    self.log_result("Fixer Reputation Get", False, "Invalid response format", response)
            else:
                self.log_result("Fixer Reputation Get", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Fixer Reputation Get", False, f"Request error: {str(e)}")
        return False
    
    # ======= PHASE 3: AI MULTILINGUAL ASSISTANT TESTS (SHOULD REMAIN STABLE) =======
    
    def test_ai_assistant_start_conversation(self):
        """Test POST /api/ai-chat/start"""
        try:
            conversation_data = {
                "language": "english",
                "user_type": "client"
            }
            
            headers = {"Authorization": f"Bearer {self.test_data.get('fixer_token', '')}"}
            response = self.session.post(f"{API_BASE}/ai-chat/start", json=conversation_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'conversation_id' in data:
                    self.test_data['conversation_id'] = data['conversation_id']
                    self.test_data['session_id'] = data.get('session_id')
                    self.log_result("AI Assistant Start Conversation", True, 
                                  f"Conversation started. ID: {data['conversation_id']}")
                    return True
                else:
                    self.log_result("AI Assistant Start Conversation", False, "Invalid response format", response)
            else:
                self.log_result("AI Assistant Start Conversation", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("AI Assistant Start Conversation", False, f"Request error: {str(e)}")
        return False
    
    def test_ai_assistant_send_message(self):
        """Test POST /api/ai-chat/{session_id}/message"""
        if 'session_id' not in self.test_data:
            self.log_result("AI Assistant Send Message", False, "No session ID available")
            return False
        
        try:
            message_data = {
                "message": "My kitchen tap is leaking water constantly",
                "language": "english"
            }
            
            response = self.session.post(f"{API_BASE}/ai-chat/{self.test_data['session_id']}/message", 
                                       json=message_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'response' in data:
                    self.log_result("AI Assistant Send Message", True, 
                                  f"Message processed. Response: {data['response'][:50]}...")
                    return True
                else:
                    self.log_result("AI Assistant Send Message", False, "Invalid response format", response)
            else:
                self.log_result("AI Assistant Send Message", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("AI Assistant Send Message", False, f"Request error: {str(e)}")
        return False
    
    def test_ai_assistant_get_history(self):
        """Test GET /api/ai-assistant/conversation/{conversation_id}/history"""
        if 'conversation_id' not in self.test_data:
            self.log_result("AI Assistant Get History", False, "No conversation ID available")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/ai-assistant/conversation/{self.test_data['conversation_id']}/history")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'messages' in data:
                    messages = data['messages']
                    self.log_result("AI Assistant Get History", True, 
                                  f"Retrieved {len(messages)} conversation messages")
                    return True
                else:
                    self.log_result("AI Assistant Get History", False, "Invalid response format", response)
            else:
                self.log_result("AI Assistant Get History", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("AI Assistant Get History", False, f"Request error: {str(e)}")
        return False
    
    def test_ai_assistant_end_conversation(self):
        """Test POST /api/ai-assistant/conversation/{conversation_id}/end"""
        if 'conversation_id' not in self.test_data:
            self.log_result("AI Assistant End Conversation", False, "No conversation ID available")
            return False
        
        try:
            end_data = {
                "satisfaction_rating": 5,
                "feedback": "Very helpful assistant"
            }
            
            response = self.session.post(f"{API_BASE}/ai-assistant/conversation/{self.test_data['conversation_id']}/end", 
                                       json=end_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("AI Assistant End Conversation", True, 
                                  f"Conversation ended successfully. Duration: {data.get('duration_minutes', 0)} minutes")
                    return True
                else:
                    self.log_result("AI Assistant End Conversation", False, "Failed to end conversation", response)
            else:
                self.log_result("AI Assistant End Conversation", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("AI Assistant End Conversation", False, f"Request error: {str(e)}")
        return False
    
    def test_ai_assistant_anonymous_chat(self):
        """Test POST /api/ai-assistant/anonymous-chat"""
        try:
            chat_data = {
                "message": "What are common causes of leaking taps?",
                "language": "english"
            }
            
            response = self.session.post(f"{API_BASE}/ai-assistant/anonymous-chat", json=chat_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'response' in data:
                    self.log_result("AI Assistant Anonymous Chat", True, 
                                  f"Anonymous chat working. Response: {data['response'][:50]}...")
                    return True
                else:
                    self.log_result("AI Assistant Anonymous Chat", False, "Invalid response format", response)
            else:
                self.log_result("AI Assistant Anonymous Chat", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("AI Assistant Anonymous Chat", False, f"Request error: {str(e)}")
        return False
    
    # ======= PHASE 3: ADMIN ANALYTICS TESTS (SHOULD REMAIN STABLE) =======
    
    def test_admin_gamification_analytics(self):
        """Test GET /api/admin/analytics/gamification"""
        if 'admin_token' not in self.test_data:
            self.log_result("Admin Gamification Analytics", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.test_data['admin_token']}"}
            response = self.session.get(f"{API_BASE}/admin/analytics/gamification", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'analytics' in data:
                    analytics = data['analytics']
                    self.log_result("Admin Gamification Analytics", True, 
                                  f"Analytics retrieved. Total fixers: {analytics.get('total_fixers', 0)}")
                    return True
                else:
                    self.log_result("Admin Gamification Analytics", False, "Invalid response format", response)
            else:
                self.log_result("Admin Gamification Analytics", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Admin Gamification Analytics", False, f"Request error: {str(e)}")
        return False
    
    def test_admin_ai_chat_analytics(self):
        """Test GET /api/admin/analytics/ai-chat"""
        if 'admin_token' not in self.test_data:
            self.log_result("Admin AI Chat Analytics", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.test_data['admin_token']}"}
            response = self.session.get(f"{API_BASE}/admin/analytics/ai-chat", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'analytics' in data:
                    analytics = data['analytics']
                    self.log_result("Admin AI Chat Analytics", True, 
                                  f"AI Chat analytics retrieved. Total conversations: {analytics.get('total_conversations', 0)}")
                    return True
                else:
                    self.log_result("Admin AI Chat Analytics", False, "Invalid response format", response)
            else:
                self.log_result("Admin AI Chat Analytics", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Admin AI Chat Analytics", False, f"Request error: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all Phase 3 tests in order"""
        print("🚀 Starting Phase 3: Automation & Engagement Testing")
        print("=" * 60)
        
        # Basic setup tests
        if not self.test_health_check():
            print("❌ Health check failed - aborting tests")
            return
        
        if not self.test_admin_login():
            print("❌ Admin login failed - some tests may not work")
        
        if not self.setup_fixer_user_for_testing():
            print("❌ Fixer user setup failed - authentication tests will fail")
            return
        
        if not self.setup_test_job():
            print("❌ Test job setup failed - tracking tests will fail")
        
        print("\n🎯 TESTING PRIORITY ENDPOINTS (AUTHENTICATION FIXES)")
        print("=" * 60)
        
        # Priority tests - Previously failing endpoints with authentication fixes
        print("\n📍 Real-Time Job Tracking Endpoints:")
        self.test_job_tracking_start()
        self.test_job_tracking_location()
        self.test_job_tracking_complete()
        
        print("\n🏆 Gamification System Endpoints:")
        self.test_fixer_reputation_initialize()
        self.test_fixer_reputation_update()
        
        print("\n✅ TESTING STABLE ENDPOINTS (SHOULD REMAIN WORKING)")
        print("=" * 60)
        
        # Stable endpoints that should continue working
        print("\n📊 Tracking Status (was working):")
        self.test_job_tracking_status()
        
        print("\n🏅 Reputation Get (was working):")
        self.test_fixer_reputation_get()
        
        print("\n🤖 AI Multilingual Assistant (all 5 endpoints):")
        self.test_ai_assistant_start_conversation()
        self.test_ai_assistant_send_message()
        self.test_ai_assistant_get_history()
        self.test_ai_assistant_end_conversation()
        self.test_ai_assistant_anonymous_chat()
        
        print("\n📈 Admin Analytics (both endpoints):")
        self.test_admin_gamification_analytics()
        self.test_admin_ai_chat_analytics()
        
        # Print final results
        print("\n" + "=" * 80)
        print("🏁 PHASE 3 TESTING RESULTS")
        print("=" * 80)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print(f"\n❌ Failed Tests:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        print("\n🎯 AUTHENTICATION FIXES SUMMARY:")
        
        # Check if the priority endpoints (authentication fixes) are working
        priority_tests = [
            "Job Tracking Start",
            "Job Tracking Location", 
            "Job Tracking Complete",
            "Fixer Reputation Initialize",
            "Fixer Reputation Update"
        ]
        
        priority_failures = [error for error in self.results['errors'] if any(test in error for test in priority_tests)]
        
        if not priority_failures:
            print("✅ All 5 priority authentication fixes are working correctly!")
        else:
            print(f"❌ {len(priority_failures)} priority authentication fixes still failing:")
            for failure in priority_failures:
                print(f"   • {failure}")
        
        return self.results

if __name__ == "__main__":
    tester = Phase3APITester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results['failed'] == 0 else 1)