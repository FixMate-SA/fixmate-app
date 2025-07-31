#!/usr/bin/env python3
"""
FixMate-SA Phase 3: Automation & Engagement Testing Script
Tests the Phase 3 features: Real-Time Tracking, Gamification, and AI Assistant
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

print(f"🚀 Testing FixMate-SA Phase 3 Features at: {API_BASE}")
print("=" * 80)
print("🎯 PHASE 3: AUTOMATION & ENGAGEMENT SYSTEM TESTING")
print("=" * 80)

class Phase3Tester:
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
            try:
                error_data = response.json()
                print(f"   Response: {response.status_code} - {error_data}")
            except:
                print(f"   Response: {response.status_code} - {response.text[:200]}")
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")
        print()
    
    def setup_test_data(self):
        """Setup required test data for Phase 3 tests"""
        print("🔧 Setting up test data...")
        
        # Create test user
        import time
        timestamp = str(int(time.time()))[-6:]
        
        user_data = {
            "phone": f"+2782123{timestamp}",
            "first_name": "TestUser",
            "last_name": "Phase3",
            "id_number": f"8001015009{timestamp[-3:]}",
            "town": "Cape Town",
            "email": f"testuser.{timestamp}@example.com",
            "address": "123 Test St, Cape Town"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/users", json=user_data)
            if response.status_code == 200:
                user = response.json()
                self.test_data['user_id'] = user['id']
                self.test_data['user'] = user
                print(f"✅ Test user created: {user['id']}")
                
                # Set password and login
                set_password_data = {
                    "phone": user_data["phone"],
                    "password": "testpass123",
                    "confirm_password": "testpass123"
                }
                
                password_response = self.session.post(f"{API_BASE}/auth/set-password", json=set_password_data)
                if password_response.status_code == 200:
                    # Login
                    login_data = {
                        "phone": user_data["phone"],
                        "password": "testpass123"
                    }
                    
                    login_response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                    if login_response.status_code == 200:
                        login_result = login_response.json()
                        self.test_data['token'] = login_result['token']
                        print(f"✅ User logged in with token")
                    else:
                        print(f"❌ Login failed: {login_response.status_code}")
                        return False
                else:
                    print(f"❌ Set password failed: {password_response.status_code}")
                    return False
            else:
                print(f"❌ User creation failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Setup error: {str(e)}")
            return False
        
        # Create test fixer
        try:
            fixer_user_data = {
                "phone": f"+2782987{timestamp}",
                "first_name": "TestFixer",
                "last_name": "Phase3",
                "id_number": f"8001015009{timestamp[-2:]}1",
                "town": "Cape Town",
                "email": f"testfixer.{timestamp}@fixmate.com",
                "address": "456 Fixer St, Cape Town"
            }
            
            fixer_user_response = self.session.post(f"{API_BASE}/users", json=fixer_user_data)
            if fixer_user_response.status_code == 200:
                fixer_user = fixer_user_response.json()
                
                fixer_data = {
                    "user_id": fixer_user['id'],
                    "phone": f"+2782987{timestamp}",
                    "name": "TestFixer Phase3",
                    "email": f"testfixer.{timestamp}@fixmate.com",
                    "services": '["plumbing", "electrical"]',
                    "location": "Cape Town"
                }
                
                fixer_response = self.session.post(f"{API_BASE}/fixers", json=fixer_data)
                if fixer_response.status_code == 200:
                    fixer = fixer_response.json()
                    self.test_data['fixer_id'] = fixer['id']
                    self.test_data['fixer'] = fixer
                    print(f"✅ Test fixer created: {fixer['id']}")
                else:
                    print(f"❌ Fixer creation failed: {fixer_response.status_code}")
                    return False
            else:
                print(f"❌ Fixer user creation failed: {fixer_user_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Fixer setup error: {str(e)}")
            return False
        
        # Create test job
        try:
            job_data = {
                "user_id": self.test_data['user_id'],
                "service": "plumbing",
                "description": "Fix leaking kitchen tap for Phase 3 testing",
                "location": "123 Test St, Cape Town",
                "estimated_price": 250.0,
                "latitude": -33.9249,
                "longitude": 18.4241
            }
            
            job_response = self.session.post(f"{API_BASE}/jobs", json=job_data)
            if job_response.status_code == 200:
                job = job_response.json()
                self.test_data['job_id'] = job['id']
                self.test_data['job'] = job
                print(f"✅ Test job created: {job['id']}")
                
                # Assign fixer to job
                update_data = {
                    "fixer_id": self.test_data['fixer_id'],
                    "status": "assigned"
                }
                
                update_response = self.session.put(f"{API_BASE}/jobs/{job['id']}", json=update_data)
                if update_response.status_code == 200:
                    print(f"✅ Fixer assigned to job")
                else:
                    print(f"⚠️ Fixer assignment failed: {update_response.status_code}")
            else:
                print(f"❌ Job creation failed: {job_response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Job setup error: {str(e)}")
            return False
        
        # Setup admin login
        try:
            admin_login_data = {
                "phone": "+27821234567",
                "password": "admin123"
            }
            
            admin_response = self.session.post(f"{API_BASE}/auth/login", json=admin_login_data)
            if admin_response.status_code == 200:
                admin_result = admin_response.json()
                self.test_data['admin_token'] = admin_result['token']
                print(f"✅ Admin logged in")
            else:
                print(f"⚠️ Admin login failed: {admin_response.status_code}")
        except Exception as e:
            print(f"⚠️ Admin setup error: {str(e)}")
        
        print("✅ Test data setup complete!")
        print()
        return True
    
    # ======= PHASE 3: REAL-TIME TRACKING TESTS =======
    
    def test_start_job_tracking(self):
        """Test starting real-time job tracking"""
        try:
            tracking_data = {
                "departure_location": {
                    "lat": -33.9249,
                    "lng": 18.4241
                }
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['token']}"}
            response = self.session.post(f"{API_BASE}/jobs/{self.test_data['job_id']}/tracking/start", 
                                       json=tracking_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'tracking_id' in data:
                    self.test_data['tracking_id'] = data['tracking_id']
                    self.log_result("Start Job Tracking", True, 
                                  f"Job tracking started successfully. Tracking ID: {data['tracking_id']}")
                    return True
                else:
                    self.log_result("Start Job Tracking", False, "Invalid response format", response)
            else:
                self.log_result("Start Job Tracking", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Start Job Tracking", False, f"Request error: {str(e)}")
        return False
    
    def test_update_fixer_location(self):
        """Test updating fixer location during tracking"""
        try:
            location_data = {
                "location": {
                    "lat": -33.9200,
                    "lng": 18.4300
                },
                "accuracy": 10.0
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['token']}"}
            response = self.session.post(f"{API_BASE}/jobs/{self.test_data['job_id']}/tracking/location", 
                                       json=location_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("Update Fixer Location", True, 
                                  f"Location updated successfully. Status: {data.get('tracking_status')}")
                    return True
                else:
                    self.log_result("Update Fixer Location", False, "Location update failed", response)
            else:
                self.log_result("Update Fixer Location", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Update Fixer Location", False, f"Request error: {str(e)}")
        return False
    
    def test_get_job_tracking_status(self):
        """Test getting job tracking status"""
        try:
            response = self.session.get(f"{API_BASE}/jobs/{self.test_data['job_id']}/tracking/status")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    tracking = data.get('tracking')
                    if tracking:
                        self.log_result("Get Job Tracking Status", True, 
                                      f"Tracking status retrieved. Status: {tracking.get('status')}")
                    else:
                        self.log_result("Get Job Tracking Status", True, "No tracking information available")
                    return True
                else:
                    self.log_result("Get Job Tracking Status", False, "Invalid response format", response)
            else:
                self.log_result("Get Job Tracking Status", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Job Tracking Status", False, f"Request error: {str(e)}")
        return False
    
    def test_complete_job_tracking(self):
        """Test completing job tracking"""
        try:
            headers = {"Authorization": f"Bearer {self.test_data['token']}"}
            response = self.session.post(f"{API_BASE}/jobs/{self.test_data['job_id']}/tracking/complete", 
                                       headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("Complete Job Tracking", True, 
                                  f"Job tracking completed successfully. Duration: {data.get('total_duration', 'N/A')} minutes")
                    return True
                else:
                    self.log_result("Complete Job Tracking", False, "Tracking completion failed", response)
            else:
                self.log_result("Complete Job Tracking", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Complete Job Tracking", False, f"Request error: {str(e)}")
        return False
    
    # ======= PHASE 3: GAMIFICATION & REPUTATION TESTS =======
    
    def test_get_fixer_reputation(self):
        """Test getting fixer reputation information"""
        try:
            response = self.session.get(f"{API_BASE}/fixer/{self.test_data['fixer_id']}/reputation")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    reputation = data.get('reputation')
                    if reputation:
                        self.log_result("Get Fixer Reputation", True, 
                                      f"Reputation retrieved. Tier: {reputation.get('current_tier')}, Points: {reputation.get('tier_points')}")
                    else:
                        self.log_result("Get Fixer Reputation", True, "No reputation information found")
                    return True
                else:
                    self.log_result("Get Fixer Reputation", False, "Invalid response format", response)
            else:
                self.log_result("Get Fixer Reputation", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Fixer Reputation", False, f"Request error: {str(e)}")
        return False
    
    def test_initialize_fixer_reputation(self):
        """Test initializing fixer reputation"""
        try:
            headers = {"Authorization": f"Bearer {self.test_data['token']}"}
            response = self.session.post(f"{API_BASE}/fixer/{self.test_data['fixer_id']}/reputation/initialize", 
                                       headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("Initialize Fixer Reputation", True, 
                                  f"Reputation initialized. Tier: {data.get('tier')}, Points: {data.get('points')}")
                    return True
                else:
                    self.log_result("Initialize Fixer Reputation", False, "Reputation initialization failed", response)
            else:
                self.log_result("Initialize Fixer Reputation", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Initialize Fixer Reputation", False, f"Request error: {str(e)}")
        return False
    
    def test_update_fixer_performance(self):
        """Test updating fixer performance metrics"""
        try:
            performance_data = {
                "job_completed": True
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['token']}"}
            response = self.session.post(f"{API_BASE}/fixer/{self.test_data['fixer_id']}/reputation/update", 
                                       json=performance_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("Update Fixer Performance", True, 
                                  f"Performance updated. Tier: {data.get('current_tier')}, Jobs: {data.get('jobs_completed')}, New badges: {len(data.get('new_badges', []))}")
                    return True
                else:
                    self.log_result("Update Fixer Performance", False, "Performance update failed", response)
            else:
                self.log_result("Update Fixer Performance", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Update Fixer Performance", False, f"Request error: {str(e)}")
        return False
    
    # ======= PHASE 3: AI MULTILINGUAL ASSISTANT TESTS =======
    
    def test_start_ai_conversation(self):
        """Test starting AI conversation"""
        try:
            conversation_data = {
                "language": "english",
                "user_type": "client"
            }
            
            headers = {"Authorization": f"Bearer {self.test_data['token']}"}
            response = self.session.post(f"{API_BASE}/ai-chat/start", 
                                       json=conversation_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'session_id' in data:
                    self.test_data['ai_session_id'] = data['session_id']
                    self.log_result("Start AI Conversation", True, 
                                  f"AI conversation started. Session ID: {data['session_id']}")
                    return True
                else:
                    self.log_result("Start AI Conversation", False, "Invalid response format", response)
            else:
                self.log_result("Start AI Conversation", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Start AI Conversation", False, f"Request error: {str(e)}")
        return False
    
    def test_send_ai_message(self):
        """Test sending message to AI assistant"""
        try:
            message_data = {
                "message": "Hello, I need help with booking a plumber for my kitchen tap",
                "context": {"location": "Cape Town"}
            }
            
            response = self.session.post(f"{API_BASE}/ai-chat/{self.test_data['ai_session_id']}/message", 
                                       json=message_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'message' in data:
                    self.log_result("Send AI Message", True, 
                                  f"AI responded successfully. Intent: {data.get('intent')}, Confidence: {data.get('confidence')}")
                    return True
                else:
                    self.log_result("Send AI Message", False, "Invalid response format", response)
            else:
                self.log_result("Send AI Message", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Send AI Message", False, f"Request error: {str(e)}")
        return False
    
    def test_end_ai_conversation(self):
        """Test ending AI conversation"""
        try:
            end_data = {
                "satisfaction_rating": 4,
                "resolved_query": True
            }
            
            response = self.session.post(f"{API_BASE}/ai-chat/{self.test_data['ai_session_id']}/end", 
                                       json=end_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_result("End AI Conversation", True, 
                                  f"AI conversation ended successfully. Duration: {data.get('duration_minutes', 'N/A')} minutes")
                    return True
                else:
                    self.log_result("End AI Conversation", False, "Conversation end failed", response)
            else:
                self.log_result("End AI Conversation", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("End AI Conversation", False, f"Request error: {str(e)}")
        return False
    
    def test_get_ai_conversation_history(self):
        """Test getting AI conversation history"""
        try:
            headers = {"Authorization": f"Bearer {self.test_data['token']}"}
            response = self.session.get(f"{API_BASE}/ai-chat/{self.test_data['ai_session_id']}/history", 
                                      headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'conversation' in data:
                    conversation = data['conversation']
                    self.log_result("Get AI Conversation History", True, 
                                  f"Conversation history retrieved. Messages: {conversation.get('statistics', {}).get('total_messages', 0)}")
                    return True
                else:
                    self.log_result("Get AI Conversation History", False, "Invalid response format", response)
            else:
                self.log_result("Get AI Conversation History", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get AI Conversation History", False, f"Request error: {str(e)}")
        return False
    
    def test_start_anonymous_ai_conversation(self):
        """Test starting anonymous AI conversation"""
        try:
            conversation_data = {
                "language": "english"
            }
            
            response = self.session.post(f"{API_BASE}/ai-chat/anonymous/start", 
                                       json=conversation_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'session_id' in data:
                    self.test_data['anonymous_session_id'] = data['session_id']
                    self.log_result("Start Anonymous AI Conversation", True, 
                                  f"Anonymous AI conversation started. Session ID: {data['session_id']}")
                    return True
                else:
                    self.log_result("Start Anonymous AI Conversation", False, "Invalid response format", response)
            else:
                self.log_result("Start Anonymous AI Conversation", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Start Anonymous AI Conversation", False, f"Request error: {str(e)}")
        return False
    
    # ======= PHASE 3: ADMIN ANALYTICS TESTS =======
    
    def test_admin_gamification_stats(self):
        """Test getting gamification statistics (admin only)"""
        if 'admin_token' not in self.test_data:
            self.log_result("Admin Gamification Stats", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.test_data['admin_token']}"}
            response = self.session.get(f"{API_BASE}/admin/gamification/stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    tier_distribution = data.get('tier_distribution', {})
                    top_performers = data.get('top_performers', [])
                    self.log_result("Admin Gamification Stats", True, 
                                  f"Gamification stats retrieved. Tiers: {len(tier_distribution)}, Top performers: {len(top_performers)}")
                    return True
                else:
                    self.log_result("Admin Gamification Stats", False, "Invalid response format", response)
            else:
                self.log_result("Admin Gamification Stats", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Admin Gamification Stats", False, f"Request error: {str(e)}")
        return False
    
    def test_admin_ai_chat_analytics(self):
        """Test getting AI chat analytics (admin only)"""
        if 'admin_token' not in self.test_data:
            self.log_result("Admin AI Chat Analytics", False, "No admin token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.test_data['admin_token']}"}
            response = self.session.get(f"{API_BASE}/admin/ai-chat/analytics?days=7", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    total_conversations = data.get('total_conversations', 0)
                    completion_rate = data.get('completion_rate', 0)
                    self.log_result("Admin AI Chat Analytics", True, 
                                  f"AI chat analytics retrieved. Conversations: {total_conversations}, Completion rate: {completion_rate}%")
                    return True
                else:
                    self.log_result("Admin AI Chat Analytics", False, "Invalid response format", response)
            else:
                self.log_result("Admin AI Chat Analytics", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Admin AI Chat Analytics", False, f"Request error: {str(e)}")
        return False
    
    def run_phase3_tests(self):
        """Run all Phase 3 tests"""
        if not self.setup_test_data():
            print("❌ Test setup failed - stopping tests")
            return False
        
        print("🚀 PHASE 3: REAL-TIME TRACKING TESTS")
        print("-" * 50)
        self.test_start_job_tracking()
        self.test_update_fixer_location()
        self.test_get_job_tracking_status()
        self.test_complete_job_tracking()
        print()
        
        print("🏆 PHASE 3: GAMIFICATION & REPUTATION TESTS")
        print("-" * 50)
        self.test_get_fixer_reputation()
        self.test_initialize_fixer_reputation()
        self.test_update_fixer_performance()
        print()
        
        print("🤖 PHASE 3: AI MULTILINGUAL ASSISTANT TESTS")
        print("-" * 50)
        self.test_start_ai_conversation()
        self.test_send_ai_message()
        self.test_end_ai_conversation()
        self.test_get_ai_conversation_history()
        self.test_start_anonymous_ai_conversation()
        print()
        
        print("📊 PHASE 3: ADMIN ANALYTICS TESTS")
        print("-" * 50)
        self.test_admin_gamification_stats()
        self.test_admin_ai_chat_analytics()
        print()
        
        # Print summary
        print("=" * 80)
        print("🎯 PHASE 3 TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {self.results['passed']}")
        print(f"❌ Tests Failed: {self.results['failed']}")
        print(f"📊 Success Rate: {(self.results['passed'] / max(1, self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🔍 Failed Tests:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        print()
        if self.results['failed'] == 0:
            print("🎉 ALL PHASE 3 TESTS PASSED! Automation & Engagement system is working correctly!")
        else:
            print("⚠️  Some Phase 3 tests failed. Please review the errors above.")
        print("=" * 80)
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = Phase3Tester()
    success = tester.run_phase3_tests()
    sys.exit(0 if success else 1)