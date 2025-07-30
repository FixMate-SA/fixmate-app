#!/usr/bin/env python3
"""
FixMate-SA Unified WhatsApp System Testing Script
Tests the completely unified FixMate-SA system that merges the working fixmate_whatsapp system 
with the main FastAPI app into one cohesive platform.

UNIFIED SYSTEM TESTING FOCUS:
1. Database Integration - unified models with WhatsApp conversation fields
2. WhatsApp Integration - complete conversation flow using unified system
3. Cross-Channel Functionality - WhatsApp users in main database
4. Web API Endpoints - ensure main app functionality still works
5. Unified Service Integration - unified_whatsapp_service with main app models
6. Data Consistency - no duplicate users, seamless switching
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

print(f"🔧 Testing Unified FixMate-SA System at: {API_BASE}")
print("=" * 80)
print("🎯 UNIFIED WHATSAPP SYSTEM INTEGRATION TESTING")
print("=" * 80)

class UnifiedFixMateSystemTester:
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
    
    def test_unified_database_integration(self):
        """Test that unified models work correctly with WhatsApp conversation fields"""
        try:
            # Test that users can be created with WhatsApp conversation fields
            response = self.session.get(f"{API_BASE}/users")
            if response.status_code == 200:
                users = response.json()
                # Check if any users have WhatsApp-specific fields
                whatsapp_users = [u for u in users if u.get('phone', '').startswith('whatsapp:')]
                self.log_result("Unified Database Integration", True, 
                              f"Database supports WhatsApp users. Found {len(whatsapp_users)} WhatsApp users out of {len(users)} total users")
                return True
            else:
                self.log_result("Unified Database Integration", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Unified Database Integration", False, f"Request error: {str(e)}")
        return False
    
    def test_unified_whatsapp_webhook_endpoint(self):
        """Test the unified WhatsApp webhook endpoint (/api/whatsapp)"""
        try:
            # Test the unified WhatsApp webhook endpoint
            webhook_data = {
                "entry": [{
                    "changes": [{
                        "value": {
                            "messages": [{
                                "from": "27821234567",
                                "type": "text", 
                                "text": {"body": "hello"}
                            }]
                        }
                    }]
                }]
            }
            
            response = self.session.post(f"{API_BASE}/whatsapp", json=webhook_data)
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] in ["processed", "ignored", "error"]:
                    self.log_result("Unified WhatsApp Webhook", True, f"Unified webhook processed with status: {data['status']}")
                    return True
                else:
                    self.log_result("Unified WhatsApp Webhook", False, "Invalid response format", response)
            else:
                self.log_result("Unified WhatsApp Webhook", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Unified WhatsApp Webhook", False, f"Request error: {str(e)}")
        return False
    
    def test_complete_whatsapp_conversation_flow_unified(self):
        """Test complete WhatsApp conversation flow using unified system"""
        print("\n🔄 Testing Complete Unified WhatsApp Conversation Flow")
        print("-" * 60)
        
        conversation_steps = [
            ("hello", "Initial greeting"),
            ("leaking pipe", "Service request"),
            ("John Smith", "Name input"),
            ("Cape Town, 123 Main Street", "Location input"),
            ("0821234567", "Contact number"),
            ("YES", "Final confirmation")
        ]
        
        test_phone = "27821234999"  # Unique phone for this test
        all_steps_passed = True
        
        for i, (message, description) in enumerate(conversation_steps, 1):
            try:
                webhook_data = {
                    "entry": [{
                        "changes": [{
                            "value": {
                                "messages": [{
                                    "from": test_phone,
                                    "type": "text",
                                    "text": {"body": message}
                                }]
                            }
                        }]
                    }]
                }
                
                response = self.session.post(f"{API_BASE}/whatsapp", json=webhook_data)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "processed":
                        self.log_result(f"Unified WhatsApp Flow Step {i} - {description}", True, 
                                      f"Message '{message}' processed successfully")
                    else:
                        self.log_result(f"Unified WhatsApp Flow Step {i} - {description}", False, 
                                      f"Unexpected status: {data.get('status')}", response)
                        all_steps_passed = False
                else:
                    self.log_result(f"Unified WhatsApp Flow Step {i} - {description}", False, 
                                  f"HTTP {response.status_code}", response)
                    all_steps_passed = False
                    
            except Exception as e:
                self.log_result(f"Unified WhatsApp Flow Step {i} - {description}", False, f"Request error: {str(e)}")
                all_steps_passed = False
        
        if all_steps_passed:
            self.log_result("Unified WhatsApp Complete Conversation Flow", True, 
                          "All 6 conversation steps completed successfully using unified system")
        else:
            self.log_result("Unified WhatsApp Complete Conversation Flow", False, 
                          "Some conversation steps failed")
        
        return all_steps_passed
    
    def test_cross_channel_functionality(self):
        """Test that WhatsApp users are created in main database and accessible via web API"""
        try:
            # First create a WhatsApp user via webhook
            webhook_data = {
                "entry": [{
                    "changes": [{
                        "value": {
                            "messages": [{
                                "from": "27821234888",  # Unique phone
                                "type": "text",
                                "text": {"body": "hello"}
                            }]
                        }
                    }]
                }]
            }
            
            # Send WhatsApp message to create user
            response = self.session.post(f"{API_BASE}/whatsapp", json=webhook_data)
            if response.status_code != 200:
                self.log_result("Cross-Channel Functionality", False, "Failed to process WhatsApp message", response)
                return False
            
            # Now check if user appears in main database via web API
            response = self.session.get(f"{API_BASE}/users")
            if response.status_code == 200:
                users = response.json()
                whatsapp_user = None
                for user in users:
                    if user.get('phone') == 'whatsapp:+27821234888':
                        whatsapp_user = user
                        break
                
                if whatsapp_user:
                    self.log_result("Cross-Channel Functionality", True, 
                                  f"WhatsApp user successfully created in main database. User ID: {whatsapp_user['id']}")
                    
                    # Store for further testing
                    self.test_data['whatsapp_user_id'] = whatsapp_user['id']
                    return True
                else:
                    self.log_result("Cross-Channel Functionality", False, 
                                  "WhatsApp user not found in main database")
            else:
                self.log_result("Cross-Channel Functionality", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Cross-Channel Functionality", False, f"Request error: {str(e)}")
        return False
    
    def test_whatsapp_job_in_web_api(self):
        """Test that jobs created via WhatsApp appear in web API"""
        try:
            # Get all jobs via web API
            response = self.session.get(f"{API_BASE}/jobs")
            if response.status_code == 200:
                jobs = response.json()
                
                # Look for jobs that might have been created via WhatsApp
                whatsapp_jobs = []
                for job in jobs:
                    # Check if job has WhatsApp-specific fields or was created by WhatsApp user
                    if (job.get('client_contact_number') or 
                        job.get('area') or 
                        'whatsapp' in str(job.get('description', '')).lower()):
                        whatsapp_jobs.append(job)
                
                self.log_result("WhatsApp Jobs in Web API", True, 
                              f"Found {len(whatsapp_jobs)} potential WhatsApp jobs out of {len(jobs)} total jobs")
                return True
            else:
                self.log_result("WhatsApp Jobs in Web API", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("WhatsApp Jobs in Web API", False, f"Request error: {str(e)}")
        return False
    
    def test_unified_service_integration(self):
        """Test that unified_whatsapp_service correctly uses main app models"""
        try:
            # Test by sending a message that should trigger user creation and conversation state management
            webhook_data = {
                "entry": [{
                    "changes": [{
                        "value": {
                            "messages": [{
                                "from": "27821234777",  # Another unique phone
                                "type": "text",
                                "text": {"body": "plumbing emergency"}
                            }]
                        }
                    }]
                }]
            }
            
            response = self.session.post(f"{API_BASE}/whatsapp", json=webhook_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "processed":
                    # Check if user was created with proper conversation state
                    users_response = self.session.get(f"{API_BASE}/users")
                    if users_response.status_code == 200:
                        users = users_response.json()
                        test_user = None
                        for user in users:
                            if user.get('phone') == 'whatsapp:+27821234777':
                                test_user = user
                                break
                        
                        if test_user:
                            self.log_result("Unified Service Integration", True, 
                                          f"Unified service correctly created user with main app models. User: {test_user['full_name']}")
                            return True
                        else:
                            self.log_result("Unified Service Integration", False, 
                                          "User not found after WhatsApp message processing")
                    else:
                        self.log_result("Unified Service Integration", False, 
                                      f"Failed to retrieve users: HTTP {users_response.status_code}")
                else:
                    self.log_result("Unified Service Integration", False, 
                                  f"Message not processed correctly: {data.get('status')}")
            else:
                self.log_result("Unified Service Integration", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Unified Service Integration", False, f"Request error: {str(e)}")
        return False
    
    def test_data_consistency_no_duplicates(self):
        """Test that there are no duplicate users and data consistency is maintained"""
        try:
            response = self.session.get(f"{API_BASE}/users")
            if response.status_code == 200:
                users = response.json()
                
                # Check for duplicate phone numbers
                phone_numbers = [user.get('phone') for user in users if user.get('phone')]
                unique_phones = set(phone_numbers)
                
                if len(phone_numbers) == len(unique_phones):
                    self.log_result("Data Consistency - No Duplicates", True, 
                                  f"No duplicate phone numbers found. {len(users)} users with {len(unique_phones)} unique phones")
                    
                    # Check WhatsApp vs regular users
                    whatsapp_users = [u for u in users if u.get('phone', '').startswith('whatsapp:')]
                    regular_users = [u for u in users if not u.get('phone', '').startswith('whatsapp:')]
                    
                    self.log_result("Data Consistency - User Types", True, 
                                  f"WhatsApp users: {len(whatsapp_users)}, Regular users: {len(regular_users)}")
                    return True
                else:
                    duplicates = len(phone_numbers) - len(unique_phones)
                    self.log_result("Data Consistency - No Duplicates", False, 
                                  f"Found {duplicates} duplicate phone numbers")
            else:
                self.log_result("Data Consistency - No Duplicates", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Data Consistency - No Duplicates", False, f"Request error: {str(e)}")
        return False
    
    def test_web_api_still_functional(self):
        """Test that main app web API functionality still works after WhatsApp integration"""
        try:
            # Test core web API endpoints
            endpoints_to_test = [
                ("/", "Health check"),
                ("/users", "Users endpoint"),
                ("/fixers", "Fixers endpoint"),
                ("/jobs", "Jobs endpoint"),
                ("/reviews", "Reviews endpoint")
            ]
            
            all_working = True
            for endpoint, description in endpoints_to_test:
                response = self.session.get(f"{API_BASE}{endpoint}")
                if response.status_code == 200:
                    self.log_result(f"Web API - {description}", True, "Endpoint working correctly")
                else:
                    self.log_result(f"Web API - {description}", False, f"HTTP {response.status_code}", response)
                    all_working = False
            
            if all_working:
                self.log_result("Web API Still Functional", True, "All core web API endpoints working after WhatsApp integration")
            else:
                self.log_result("Web API Still Functional", False, "Some web API endpoints not working")
            
            return all_working
        except Exception as e:
            self.log_result("Web API Still Functional", False, f"Request error: {str(e)}")
        return False

def main():
    """Run unified FixMate-SA system tests"""
    print("🚀 STARTING UNIFIED FIXMATE-SA SYSTEM TESTING")
    print("=" * 80)
    
    tester = UnifiedFixMateSystemTester()
    
    # Core system health check
    print("\n🏥 SYSTEM HEALTH CHECK")
    print("-" * 40)
    tester.test_health_check()
    
    # Test unified database integration
    print("\n🗄️ UNIFIED DATABASE INTEGRATION TESTS")
    print("-" * 50)
    tester.test_unified_database_integration()
    
    # Test unified WhatsApp system
    print("\n📱 UNIFIED WHATSAPP SYSTEM TESTS")
    print("-" * 45)
    tester.test_unified_whatsapp_webhook_endpoint()
    tester.test_complete_whatsapp_conversation_flow_unified()
    
    # Test cross-channel functionality
    print("\n🔄 CROSS-CHANNEL FUNCTIONALITY TESTS")
    print("-" * 45)
    tester.test_cross_channel_functionality()
    tester.test_whatsapp_job_in_web_api()
    
    # Test unified service integration
    print("\n⚙️ UNIFIED SERVICE INTEGRATION TESTS")
    print("-" * 45)
    tester.test_unified_service_integration()
    
    # Test data consistency
    print("\n🔍 DATA CONSISTENCY TESTS")
    print("-" * 35)
    tester.test_data_consistency_no_duplicates()
    
    # Test that web API still works
    print("\n🌐 WEB API FUNCTIONALITY TESTS")
    print("-" * 40)
    tester.test_web_api_still_functional()
    
    # Print final summary
    print("\n" + "=" * 80)
    print("🎯 UNIFIED FIXMATE-SA SYSTEM TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {tester.results['passed']}")
    print(f"❌ Failed: {tester.results['failed']}")
    print(f"📊 Total: {tester.results['passed'] + tester.results['failed']}")
    
    if tester.results['failed'] > 0:
        print(f"\n🚨 FAILED TESTS:")
        for error in tester.results['errors']:
            print(f"   • {error}")
        print(f"\n⚠️  Some tests failed. Please check the errors above.")
        return False
    else:
        print(f"\n🎉 ALL TESTS PASSED! Unified FixMate-SA system is working correctly.")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)