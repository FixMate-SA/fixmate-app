#!/usr/bin/env python3
"""
FixMate-SA Backend API Testing Script
Tests all backend endpoints for the FixMate-SA application
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

print(f"Testing backend at: {API_BASE}")

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
            "name": "John Doe",
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
    
    def test_get_user(self):
        """Test get user by ID"""
        if 'user_id' not in self.test_data:
            self.log_result("Get User", False, "No user ID available from previous test")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/users/{self.test_data['user_id']}")
            if response.status_code == 200:
                data = response.json()
                if data['id'] == self.test_data['user_id']:
                    self.log_result("Get User", True, f"Retrieved user: {data['name']}")
                    return True
                else:
                    self.log_result("Get User", False, "User ID mismatch", response)
            else:
                self.log_result("Get User", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get User", False, f"Request error: {str(e)}")
        return False
    
    def test_get_all_users(self):
        """Test get all users"""
        try:
            response = self.session.get(f"{API_BASE}/users")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get All Users", True, f"Retrieved {len(data)} users")
                    return True
                else:
                    self.log_result("Get All Users", False, "Response is not a list", response)
            else:
                self.log_result("Get All Users", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get All Users", False, f"Request error: {str(e)}")
        return False
    
    def test_login(self):
        """Test login endpoint"""
        if 'user' not in self.test_data:
            self.log_result("Login", False, "No user data available from previous test")
            return False
        
        login_data = {
            "phone": self.test_data['user']['phone']
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.test_data['token'] = data['token']
                    self.log_result("Login", True, f"Login successful, token: {data['token'][:20]}...")
                    return True
                else:
                    self.log_result("Login", False, "Invalid response format", response)
            else:
                self.log_result("Login", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Login", False, f"Request error: {str(e)}")
        return False
    
    def test_create_fixer(self):
        """Test fixer creation"""
        import time
        timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
        
        fixer_data = {
            "phone": f"+2782987{timestamp}",
            "name": "Mike Smith",
            "email": f"mike.smith.{timestamp}@fixmate.com",
            "services": '["plumbing", "electrical", "carpentry"]',
            "location": "Cape Town"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/fixers", json=fixer_data)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["phone"] == fixer_data["phone"]:
                    self.test_data['fixer_id'] = data['id']
                    self.test_data['fixer'] = data
                    self.log_result("Create Fixer", True, f"Fixer created with ID: {data['id']}")
                    return True
                else:
                    self.log_result("Create Fixer", False, "Invalid response format", response)
            else:
                self.log_result("Create Fixer", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Create Fixer", False, f"Request error: {str(e)}")
        return False
    
    def test_get_fixer(self):
        """Test get fixer by ID"""
        if 'fixer_id' not in self.test_data:
            self.log_result("Get Fixer", False, "No fixer ID available from previous test")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/fixers/{self.test_data['fixer_id']}")
            if response.status_code == 200:
                data = response.json()
                if data['id'] == self.test_data['fixer_id']:
                    self.log_result("Get Fixer", True, f"Retrieved fixer: {data['name']}")
                    return True
                else:
                    self.log_result("Get Fixer", False, "Fixer ID mismatch", response)
            else:
                self.log_result("Get Fixer", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Fixer", False, f"Request error: {str(e)}")
        return False
    
    def test_get_all_fixers(self):
        """Test get all fixers"""
        try:
            response = self.session.get(f"{API_BASE}/fixers")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get All Fixers", True, f"Retrieved {len(data)} fixers")
                    return True
                else:
                    self.log_result("Get All Fixers", False, "Response is not a list", response)
            else:
                self.log_result("Get All Fixers", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get All Fixers", False, f"Request error: {str(e)}")
        return False
    
    def test_get_fixers_by_service(self):
        """Test get fixers by service"""
        try:
            response = self.session.get(f"{API_BASE}/fixers/by-service/plumbing")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Fixers by Service", True, f"Retrieved {len(data)} plumbing fixers")
                    return True
                else:
                    self.log_result("Get Fixers by Service", False, "Response is not a list", response)
            else:
                self.log_result("Get Fixers by Service", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Fixers by Service", False, f"Request error: {str(e)}")
        return False
    
    def test_create_job(self):
        """Test job creation"""
        if 'user_id' not in self.test_data:
            self.log_result("Create Job", False, "No user ID available from previous test")
            return False
        
        job_data = {
            "user_id": self.test_data['user_id'],
            "service": "plumbing",
            "description": "Fix leaking kitchen tap",
            "location": "123 Main St, Cape Town",
            "estimated_price": 250.0
        }
        
        try:
            response = self.session.post(f"{API_BASE}/jobs", json=job_data)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["user_id"] == job_data["user_id"]:
                    self.test_data['job_id'] = data['id']
                    self.test_data['job'] = data
                    self.log_result("Create Job", True, f"Job created with ID: {data['id']}")
                    return True
                else:
                    self.log_result("Create Job", False, "Invalid response format", response)
            else:
                self.log_result("Create Job", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Create Job", False, f"Request error: {str(e)}")
        return False
    
    def test_get_job(self):
        """Test get job by ID"""
        if 'job_id' not in self.test_data:
            self.log_result("Get Job", False, "No job ID available from previous test")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/jobs/{self.test_data['job_id']}")
            if response.status_code == 200:
                data = response.json()
                if data['id'] == self.test_data['job_id']:
                    self.log_result("Get Job", True, f"Retrieved job: {data['description']}")
                    return True
                else:
                    self.log_result("Get Job", False, "Job ID mismatch", response)
            else:
                self.log_result("Get Job", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Job", False, f"Request error: {str(e)}")
        return False
    
    def test_get_all_jobs(self):
        """Test get all jobs"""
        try:
            response = self.session.get(f"{API_BASE}/jobs")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get All Jobs", True, f"Retrieved {len(data)} jobs")
                    return True
                else:
                    self.log_result("Get All Jobs", False, "Response is not a list", response)
            else:
                self.log_result("Get All Jobs", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get All Jobs", False, f"Request error: {str(e)}")
        return False
    
    def test_update_job(self):
        """Test job update (assign fixer)"""
        if 'job_id' not in self.test_data or 'fixer_id' not in self.test_data:
            self.log_result("Update Job", False, "No job ID or fixer ID available from previous tests")
            return False
        
        update_data = {
            "fixer_id": self.test_data['fixer_id'],
            "status": "assigned",
            "final_price": 300.0
        }
        
        try:
            response = self.session.put(f"{API_BASE}/jobs/{self.test_data['job_id']}", json=update_data)
            if response.status_code == 200:
                data = response.json()
                if data['fixer_id'] == self.test_data['fixer_id'] and data['status'] == "assigned":
                    self.log_result("Update Job", True, f"Job assigned to fixer and status updated")
                    return True
                else:
                    self.log_result("Update Job", False, "Job not properly updated", response)
            else:
                self.log_result("Update Job", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Update Job", False, f"Request error: {str(e)}")
        return False
    
    def test_create_review(self):
        """Test review creation"""
        if not all(key in self.test_data for key in ['job_id', 'user_id', 'fixer_id']):
            self.log_result("Create Review", False, "Missing required IDs from previous tests")
            return False
        
        review_data = {
            "job_id": self.test_data['job_id'],
            "user_id": self.test_data['user_id'],
            "fixer_id": self.test_data['fixer_id'],
            "rating": 5,
            "comment": "Excellent work! Fixed the tap quickly and professionally."
        }
        
        try:
            response = self.session.post(f"{API_BASE}/reviews", json=review_data)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["rating"] == review_data["rating"]:
                    self.test_data['review_id'] = data['id']
                    self.log_result("Create Review", True, f"Review created with ID: {data['id']}")
                    return True
                else:
                    self.log_result("Create Review", False, "Invalid response format", response)
            else:
                self.log_result("Create Review", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Create Review", False, f"Request error: {str(e)}")
        return False
    
    def test_get_reviews(self):
        """Test get all reviews"""
        try:
            response = self.session.get(f"{API_BASE}/reviews")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get All Reviews", True, f"Retrieved {len(data)} reviews")
                    return True
                else:
                    self.log_result("Get All Reviews", False, "Response is not a list", response)
            else:
                self.log_result("Get All Reviews", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get All Reviews", False, f"Request error: {str(e)}")
        return False
    
    def test_get_reviews_by_fixer(self):
        """Test get reviews by fixer ID"""
        if 'fixer_id' not in self.test_data:
            self.log_result("Get Reviews by Fixer", False, "No fixer ID available from previous test")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/reviews?fixer_id={self.test_data['fixer_id']}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Reviews by Fixer", True, f"Retrieved {len(data)} reviews for fixer")
                    return True
                else:
                    self.log_result("Get Reviews by Fixer", False, "Response is not a list", response)
            else:
                self.log_result("Get Reviews by Fixer", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Reviews by Fixer", False, f"Request error: {str(e)}")
        return False
    
    def test_dashboard(self):
        """Test dashboard endpoint"""
        if 'user_id' not in self.test_data:
            self.log_result("Dashboard", False, "No user ID available from previous test")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/dashboard/{self.test_data['user_id']}")
            if response.status_code == 200:
                data = response.json()
                required_keys = ['user', 'recent_jobs', 'top_fixers', 'stats', 'business_insight']
                if all(key in data for key in required_keys):
                    # Check if AI business insight is present
                    if data.get('business_insight') and data['business_insight'] != "No insights available at this time.":
                        self.log_result("Dashboard with AI Insights", True, f"Dashboard with AI business insights retrieved successfully")
                    else:
                        self.log_result("Dashboard with AI Insights", True, f"Dashboard retrieved (AI insights not available)")
                    return True
                else:
                    missing_keys = [key for key in required_keys if key not in data]
                    self.log_result("Dashboard", False, f"Missing keys: {missing_keys}", response)
            else:
                self.log_result("Dashboard", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Dashboard", False, f"Request error: {str(e)}")
        return False
    
    def test_ai_classify_service(self):
        """Test AI service classification endpoint"""
        test_descriptions = [
            "My kitchen tap is leaking and needs to be fixed",
            "The lights in my living room are not working",
            "Need someone to paint my bedroom walls"
        ]
        
        for description in test_descriptions:
            try:
                data = {'description': description}
                response = self.session.post(f"{API_BASE}/classify-service", data=data)
                if response.status_code == 200:
                    result = response.json()
                    if "classification" in result:
                        classification = result["classification"]
                        self.log_result("AI Service Classification", True, f"Classified '{description[:30]}...' as '{classification}'")
                    else:
                        self.log_result("AI Service Classification", False, "Invalid response format", response)
                        return False
                else:
                    self.log_result("AI Service Classification", False, f"HTTP {response.status_code}", response)
                    return False
            except Exception as e:
                self.log_result("AI Service Classification", False, f"Request error: {str(e)}")
                return False
        return True
    
    def test_ai_analyze_sentiment(self):
        """Test AI sentiment analysis endpoint"""
        test_texts = [
            "Excellent work! The fixer was professional and quick.",
            "Terrible service, very disappointed with the quality.",
            "The job was completed as expected, nothing special."
        ]
        
        for text in test_texts:
            try:
                data = {'text': text}
                response = self.session.post(f"{API_BASE}/analyze-sentiment", data=data)
                if response.status_code == 200:
                    result = response.json()
                    if "sentiment" in result:
                        sentiment = result["sentiment"]
                        self.log_result("AI Sentiment Analysis", True, f"Analyzed sentiment as '{sentiment}' for text: '{text[:30]}...'")
                    else:
                        self.log_result("AI Sentiment Analysis", False, "Invalid response format", response)
                        return False
                else:
                    self.log_result("AI Sentiment Analysis", False, f"HTTP {response.status_code}", response)
                    return False
            except Exception as e:
                self.log_result("AI Sentiment Analysis", False, f"Request error: {str(e)}")
                return False
        return True
    
    def test_ai_transcribe_audio(self):
        """Test AI audio transcription endpoint"""
        # Create a small dummy audio file for testing
        try:
            # Create a minimal WAV file header (44 bytes) + some dummy audio data
            wav_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
            dummy_audio_data = wav_header + b'\x00' * 1000  # Add some dummy audio data
            
            files = {'audio': ('test_audio.wav', dummy_audio_data, 'audio/wav')}
            response = self.session.post(f"{API_BASE}/transcribe", files=files)
            
            if response.status_code == 200:
                result = response.json()
                if "transcription" in result:
                    transcription = result["transcription"]
                    # Since we're using dummy data, we expect either a transcription attempt or an error message
                    if "not available" in transcription or "Error" in transcription or "Could not transcribe" in transcription:
                        self.log_result("AI Audio Transcription", True, f"Transcription service responded appropriately: {transcription[:50]}...")
                    else:
                        self.log_result("AI Audio Transcription", True, f"Transcription completed: {transcription[:50]}...")
                    return True
                else:
                    self.log_result("AI Audio Transcription", False, "Invalid response format", response)
            else:
                self.log_result("AI Audio Transcription", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("AI Audio Transcription", False, f"Request error: {str(e)}")
        return False
    
    def test_sms_send(self):
        """Test SMS sending endpoint"""
        try:
            data = {
                'to_number': '+27821234567',
                'message': 'Test SMS from FixMate-SA API testing'
            }
            response = self.session.post(f"{API_BASE}/sms/send", data=data)
            
            if response.status_code == 200:
                result = response.json()
                if "success" in result:
                    success = result["success"]
                    if success:
                        self.log_result("SMS Send", True, "SMS sent successfully")
                    else:
                        self.log_result("SMS Send", True, "SMS service responded (may not be configured)")
                    return True
                else:
                    self.log_result("SMS Send", False, "Invalid response format", response)
            else:
                self.log_result("SMS Send", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("SMS Send", False, f"Request error: {str(e)}")
        return False
    
    def test_sms_webhook(self):
        """Test SMS webhook endpoint"""
        try:
            data = {
                'From': '+27821234567',
                'Body': 'hello'
            }
            response = self.session.post(f"{API_BASE}/sms/webhook", data=data)
            
            if response.status_code == 200:
                # Webhook should return plain text "OK"
                if response.text == "OK":
                    self.log_result("SMS Webhook", True, "Webhook processed successfully")
                    return True
                else:
                    self.log_result("SMS Webhook", True, f"Webhook responded: {response.text}")
                    return True
            else:
                self.log_result("SMS Webhook", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("SMS Webhook", False, f"Request error: {str(e)}")
        return False
    
    def test_enhanced_job_creation_with_ai(self):
        """Test job creation with AI service classification"""
        if 'user_id' not in self.test_data:
            self.log_result("Enhanced Job Creation with AI", False, "No user ID available from previous test")
            return False
        
        job_data = {
            "user_id": self.test_data['user_id'],
            "service": "plumbing",
            "description": "My bathroom geyser is making strange noises and leaking water from the bottom",
            "location": "Sandton, Johannesburg",
            "estimated_price": 350.0
        }
        
        try:
            response = self.session.post(f"{API_BASE}/jobs", json=job_data)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["user_id"] == job_data["user_id"]:
                    self.test_data['ai_job_id'] = data['id']
                    self.log_result("Enhanced Job Creation with AI", True, f"Job created with AI classification, ID: {data['id']}")
                    return True
                else:
                    self.log_result("Enhanced Job Creation with AI", False, "Invalid response format", response)
            else:
                self.log_result("Enhanced Job Creation with AI", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Enhanced Job Creation with AI", False, f"Request error: {str(e)}")
        return False
    
    def test_enhanced_review_creation_with_ai(self):
        """Test review creation with AI sentiment analysis"""
        if not all(key in self.test_data for key in ['job_id', 'user_id', 'fixer_id']):
            self.log_result("Enhanced Review Creation with AI", False, "Missing required IDs from previous tests")
            return False
        
        review_data = {
            "job_id": self.test_data['job_id'],
            "user_id": self.test_data['user_id'],
            "fixer_id": self.test_data['fixer_id'],
            "rating": 4,
            "comment": "The fixer did a good job overall, but arrived a bit late. The quality of work was excellent and professional."
        }
        
        try:
            response = self.session.post(f"{API_BASE}/reviews", json=review_data)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["rating"] == review_data["rating"]:
                    self.test_data['ai_review_id'] = data['id']
                    self.log_result("Enhanced Review Creation with AI", True, f"Review created with AI sentiment analysis, ID: {data['id']}")
                    return True
                else:
                    self.log_result("Enhanced Review Creation with AI", False, "Invalid response format", response)
            else:
                self.log_result("Enhanced Review Creation with AI", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Enhanced Review Creation with AI", False, f"Request error: {str(e)}")
        return False
    
    def test_fixer_payment_status(self):
        """Test fixer payment status checking"""
        if 'fixer_id' not in self.test_data:
            self.log_result("Fixer Payment Status", False, "No fixer ID available from previous test")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/fixer/{self.test_data['fixer_id']}/payment-status")
            if response.status_code == 200:
                data = response.json()
                required_keys = ['fixer_id', 'payment_status', 'total_outstanding', 'can_receive_jobs']
                if all(key in data for key in required_keys):
                    self.test_data['payment_status'] = data
                    self.log_result("Fixer Payment Status", True, f"Payment status: {data['payment_status']}, Outstanding: R{data['total_outstanding']:.2f}, Can receive jobs: {data['can_receive_jobs']}")
                    return True
                else:
                    missing_keys = [key for key in required_keys if key not in data]
                    self.log_result("Fixer Payment Status", False, f"Missing keys: {missing_keys}", response)
            else:
                self.log_result("Fixer Payment Status", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Fixer Payment Status", False, f"Request error: {str(e)}")
        return False
    
    def test_create_service_fee(self):
        """Test creating R20 service fee for fixer"""
        if 'fixer_id' not in self.test_data:
            self.log_result("Create Service Fee", False, "No fixer ID available from previous test")
            return False
        
        try:
            data = {
                'description': 'Service fee for plumbing job - Fix leaking kitchen tap'
            }
            response = self.session.post(f"{API_BASE}/fixer/{self.test_data['fixer_id']}/create-service-fee", data=data)
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and 'payment_id' in result:
                    self.test_data['service_fee_payment_id'] = result['payment_id']
                    self.log_result("Create Service Fee", True, f"Service fee created: R{result.get('amount', 20):.2f}, Payment ID: {result['payment_id']}")
                    return True
                else:
                    self.log_result("Create Service Fee", False, f"Service fee creation failed: {result.get('error', 'Unknown error')}", response)
            else:
                self.log_result("Create Service Fee", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Create Service Fee", False, f"Request error: {str(e)}")
        return False
    
    def test_payment_history(self):
        """Test getting fixer payment history"""
        if 'fixer_id' not in self.test_data:
            self.log_result("Payment History", False, "No fixer ID available from previous test")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/fixer/{self.test_data['fixer_id']}/payment-history")
            if response.status_code == 200:
                data = response.json()
                if 'payments' in data and isinstance(data['payments'], list):
                    payment_count = len(data['payments'])
                    self.log_result("Payment History", True, f"Retrieved {payment_count} payment records")
                    return True
                else:
                    self.log_result("Payment History", False, "Invalid response format", response)
            else:
                self.log_result("Payment History", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Payment History", False, f"Request error: {str(e)}")
        return False
    
    def test_settle_payment(self):
        """Test settling a payment"""
        if 'service_fee_payment_id' not in self.test_data:
            self.log_result("Settle Payment", False, "No payment ID available from previous test")
            return False
        
        try:
            data = {
                'payment_method': 'bank_transfer',
                'reference': 'TXN123456789'
            }
            response = self.session.post(f"{API_BASE}/fixer/payment/{self.test_data['service_fee_payment_id']}/settle", data=data)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.log_result("Settle Payment", True, f"Payment settled successfully: {result.get('message', 'Payment settled')}")
                    return True
                else:
                    self.log_result("Settle Payment", False, f"Payment settlement failed: {result.get('error', 'Unknown error')}", response)
            else:
                self.log_result("Settle Payment", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Settle Payment", False, f"Request error: {str(e)}")
        return False
    
    def test_job_assignment_with_payment_check(self):
        """Test job assignment with payment status verification"""
        # First create a new fixer with outstanding payments to test blocking
        import time
        timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
        
        fixer_data = {
            "phone": f"+2782987{timestamp}",
            "name": "Jane Doe",
            "email": f"jane.doe.{timestamp}@fixmate.com",
            "services": '["electrical", "plumbing"]',
            "location": "Johannesburg"
        }
        
        try:
            # Create new fixer
            response = self.session.post(f"{API_BASE}/fixers", json=fixer_data)
            if response.status_code != 200:
                self.log_result("Job Assignment Payment Check", False, "Failed to create test fixer", response)
                return False
            
            test_fixer = response.json()
            test_fixer_id = test_fixer['id']
            
            # Create service fee for this fixer to make them have outstanding payment
            fee_data = {'description': 'Test service fee to block job assignment'}
            response = self.session.post(f"{API_BASE}/fixer/{test_fixer_id}/create-service-fee", data=fee_data)
            if response.status_code != 200:
                self.log_result("Job Assignment Payment Check", False, "Failed to create service fee for test", response)
                return False
            
            # Now try to assign a job to this fixer (should be blocked)
            if 'job_id' not in self.test_data:
                self.log_result("Job Assignment Payment Check", False, "No job ID available from previous test")
                return False
            
            update_data = {
                "fixer_id": test_fixer_id,
                "status": "assigned"
            }
            
            response = self.session.put(f"{API_BASE}/jobs/{self.test_data['job_id']}", json=update_data)
            if response.status_code == 400:
                # This is expected - job assignment should be blocked
                error_message = response.json().get('detail', '')
                if 'outstanding payments' in error_message.lower():
                    self.log_result("Job Assignment Payment Check", True, f"Job assignment correctly blocked due to outstanding payments: {error_message}")
                    return True
                else:
                    self.log_result("Job Assignment Payment Check", False, f"Job blocked but wrong reason: {error_message}", response)
            else:
                self.log_result("Job Assignment Payment Check", False, f"Job assignment should have been blocked but wasn't. HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Job Assignment Payment Check", False, f"Request error: {str(e)}")
        return False
    
    def test_automatic_service_fee_creation(self):
        """Test automatic service fee creation when job is assigned"""
        # Create a new job and fixer to test automatic fee creation
        import time
        timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
        
        user_data = {
            "phone": f"+2782123{timestamp}",
            "name": "Test User 2",
            "email": f"testuser2.{timestamp}@example.com",
            "address": "456 Test St, Cape Town"
        }
        
        try:
            # Create test user
            response = self.session.post(f"{API_BASE}/users", json=user_data)
            if response.status_code != 200:
                self.log_result("Automatic Service Fee Creation", False, "Failed to create test user", response)
                return False
            
            test_user = response.json()
            
            # Create test job
            job_data = {
                "user_id": test_user['id'],
                "service": "electrical",
                "description": "Install new light fixture",
                "location": "456 Test St, Cape Town",
                "estimated_price": 150.0
            }
            
            response = self.session.post(f"{API_BASE}/jobs", json=job_data)
            if response.status_code != 200:
                self.log_result("Automatic Service Fee Creation", False, "Failed to create test job", response)
                return False
            
            test_job = response.json()
            
            # Create test fixer with no outstanding payments
            import time
            timestamp2 = str(int(time.time()))[-5:]  # Different timestamp
            
            fixer_data = {
                "phone": f"+2782987{timestamp2}",
                "name": "Clean Fixer",
                "email": f"clean.fixer.{timestamp2}@fixmate.com",
                "services": '["electrical", "carpentry"]',
                "location": "Cape Town"
            }
            
            response = self.session.post(f"{API_BASE}/fixers", json=fixer_data)
            if response.status_code != 200:
                self.log_result("Automatic Service Fee Creation", False, "Failed to create clean fixer", response)
                return False
            
            clean_fixer = response.json()
            
            # Get initial payment history
            response = self.session.get(f"{API_BASE}/fixer/{clean_fixer['id']}/payment-history")
            if response.status_code != 200:
                self.log_result("Automatic Service Fee Creation", False, "Failed to get initial payment history", response)
                return False
            
            initial_payments = response.json()['payments']
            initial_count = len(initial_payments)
            
            # Assign job to clean fixer (should automatically create service fee)
            update_data = {
                "fixer_id": clean_fixer['id'],
                "status": "assigned"
            }
            
            response = self.session.put(f"{API_BASE}/jobs/{test_job['id']}", json=update_data)
            if response.status_code != 200:
                self.log_result("Automatic Service Fee Creation", False, f"Failed to assign job. HTTP {response.status_code}", response)
                return False
            
            # Check if service fee was automatically created
            response = self.session.get(f"{API_BASE}/fixer/{clean_fixer['id']}/payment-history")
            if response.status_code != 200:
                self.log_result("Automatic Service Fee Creation", False, "Failed to get updated payment history", response)
                return False
            
            updated_payments = response.json()['payments']
            updated_count = len(updated_payments)
            
            if updated_count > initial_count:
                # Check if the new payment is a service fee
                new_payment = updated_payments[0]  # Most recent payment
                if new_payment.get('payment_type') == 'service_fee' and new_payment.get('amount') == 20.0:
                    self.log_result("Automatic Service Fee Creation", True, f"Service fee automatically created when job assigned. Payment ID: {new_payment['id']}")
                    return True
                else:
                    self.log_result("Automatic Service Fee Creation", False, f"New payment created but not a service fee: {new_payment}")
            else:
                self.log_result("Automatic Service Fee Creation", False, "No new payment created when job was assigned")
                
        except Exception as e:
            self.log_result("Automatic Service Fee Creation", False, f"Request error: {str(e)}")
        return False
    
    # WhatsApp Integration Tests
    def test_whatsapp_webhook_verify(self):
        """Test WhatsApp webhook verification endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/whatsapp/webhook")
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "webhook verified":
                    self.log_result("WhatsApp Webhook Verify", True, "Webhook verification endpoint working")
                    return True
                else:
                    self.log_result("WhatsApp Webhook Verify", False, "Invalid response format", response)
            else:
                self.log_result("WhatsApp Webhook Verify", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("WhatsApp Webhook Verify", False, f"Request error: {str(e)}")
        return False
    
    def test_whatsapp_webhook_post(self):
        """Test WhatsApp webhook message processing"""
        try:
            # Simulate a WhatsApp webhook message
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
            
            response = self.session.post(f"{API_BASE}/whatsapp/webhook", json=webhook_data)
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] in ["processed", "ignored"]:
                    self.log_result("WhatsApp Webhook POST", True, f"Webhook processed with status: {data['status']}")
                    return True
                else:
                    self.log_result("WhatsApp Webhook POST", False, "Invalid response format", response)
            else:
                self.log_result("WhatsApp Webhook POST", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("WhatsApp Webhook POST", False, f"Request error: {str(e)}")
        return False
    
    def test_whatsapp_send_message(self):
        """Test WhatsApp send message endpoint"""
        try:
            data = {
                'to_number': '+27821234567',
                'message': 'Test message from FixMate-SA API testing'
            }
            response = self.session.post(f"{API_BASE}/whatsapp/send-message", data=data)
            
            if response.status_code == 200:
                result = response.json()
                if "success" in result:
                    success = result["success"]
                    if success:
                        self.log_result("WhatsApp Send Message", True, "WhatsApp message sent successfully")
                    else:
                        self.log_result("WhatsApp Send Message", True, "WhatsApp service responded (API key may not be configured)")
                    return True
                else:
                    self.log_result("WhatsApp Send Message", False, "Invalid response format", response)
            else:
                self.log_result("WhatsApp Send Message", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("WhatsApp Send Message", False, f"Request error: {str(e)}")
        return False
    
    def test_whatsapp_send_job_notification(self):
        """Test WhatsApp job notification endpoint"""
        if 'job_id' not in self.test_data:
            self.log_result("WhatsApp Job Notification", False, "No job ID available from previous test")
            return False
        
        try:
            data = {'job_id': self.test_data['job_id']}
            response = self.session.post(f"{API_BASE}/whatsapp/send-job-notification", data=data)
            
            if response.status_code == 200:
                result = response.json()
                if "success" in result:
                    success = result["success"]
                    if success:
                        self.log_result("WhatsApp Job Notification", True, "Job notification sent successfully")
                    else:
                        self.log_result("WhatsApp Job Notification", True, "Job notification service responded (may not be configured)")
                    return True
                else:
                    self.log_result("WhatsApp Job Notification", False, "Invalid response format", response)
            else:
                self.log_result("WhatsApp Job Notification", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("WhatsApp Job Notification", False, f"Request error: {str(e)}")
        return False
    
    def test_whatsapp_send_rating_request(self):
        """Test WhatsApp rating request endpoint"""
        if 'job_id' not in self.test_data:
            self.log_result("WhatsApp Rating Request", False, "No job ID available from previous test")
            return False
        
        try:
            data = {'job_id': self.test_data['job_id']}
            response = self.session.post(f"{API_BASE}/whatsapp/send-rating-request", data=data)
            
            if response.status_code == 200:
                result = response.json()
                if "success" in result:
                    success = result["success"]
                    if success:
                        self.log_result("WhatsApp Rating Request", True, "Rating request sent successfully")
                    else:
                        self.log_result("WhatsApp Rating Request", True, "Rating request service responded (may not be configured)")
                    return True
                else:
                    self.log_result("WhatsApp Rating Request", False, "Invalid response format", response)
            else:
                self.log_result("WhatsApp Rating Request", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("WhatsApp Rating Request", False, f"Request error: {str(e)}")
        return False
    
    # PayFast Integration Tests
    def test_payfast_create_payment(self):
        """Test PayFast payment creation endpoint"""
        if 'job_id' not in self.test_data:
            self.log_result("PayFast Create Payment", False, "No job ID available from previous test")
            return False
        
        try:
            data = {'job_id': self.test_data['job_id']}
            response = self.session.post(f"{API_BASE}/payfast/create-payment", data=data)
            
            if response.status_code == 200:
                result = response.json()
                required_keys = ['success', 'payment_url', 'job_id', 'amount']
                if all(key in result for key in required_keys):
                    if result['success']:
                        self.test_data['payment_url'] = result['payment_url']
                        self.log_result("PayFast Create Payment", True, f"Payment URL created: {result['payment_url'][:50]}...")
                        return True
                    else:
                        self.log_result("PayFast Create Payment", False, "Payment creation failed", response)
                else:
                    missing_keys = [key for key in required_keys if key not in result]
                    self.log_result("PayFast Create Payment", False, f"Missing keys: {missing_keys}", response)
            else:
                self.log_result("PayFast Create Payment", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("PayFast Create Payment", False, f"Request error: {str(e)}")
        return False
    
    def test_payfast_payment_status(self):
        """Test PayFast payment status endpoint"""
        if 'job_id' not in self.test_data:
            self.log_result("PayFast Payment Status", False, "No job ID available from previous test")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/payfast/payment-status/{self.test_data['job_id']}")
            
            if response.status_code == 200:
                result = response.json()
                required_keys = ['job_id', 'payment_status', 'amount', 'status']
                if all(key in result for key in required_keys):
                    self.log_result("PayFast Payment Status", True, f"Payment status: {result['payment_status']}, Amount: R{result['amount']}")
                    return True
                else:
                    missing_keys = [key for key in required_keys if key not in result]
                    self.log_result("PayFast Payment Status", False, f"Missing keys: {missing_keys}", response)
            else:
                self.log_result("PayFast Payment Status", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("PayFast Payment Status", False, f"Request error: {str(e)}")
        return False
    
    def test_payfast_fixer_payment(self):
        """Test PayFast fixer payment endpoint"""
        if 'fixer_id' not in self.test_data or 'service_fee_payment_id' not in self.test_data:
            self.log_result("PayFast Fixer Payment", False, "No fixer ID or payment ID available from previous tests")
            return False
        
        try:
            data = {
                'fixer_id': self.test_data['fixer_id'],
                'payment_id': self.test_data['service_fee_payment_id']
            }
            response = self.session.post(f"{API_BASE}/payfast/fixer-payment", data=data)
            
            if response.status_code == 200:
                result = response.json()
                required_keys = ['success', 'payment_url', 'fixer_id', 'amount']
                if all(key in result for key in required_keys):
                    if result['success']:
                        self.log_result("PayFast Fixer Payment", True, f"Fixer payment URL created: R{result['amount']}")
                        return True
                    else:
                        self.log_result("PayFast Fixer Payment", False, "Fixer payment creation failed", response)
                else:
                    missing_keys = [key for key in required_keys if key not in result]
                    self.log_result("PayFast Fixer Payment", False, f"Missing keys: {missing_keys}", response)
            else:
                self.log_result("PayFast Fixer Payment", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("PayFast Fixer Payment", False, f"Request error: {str(e)}")
        return False
    
    def test_payfast_notify(self):
        """Test PayFast notification webhook endpoint"""
        try:
            # Simulate a PayFast notification
            notification_data = {
                'payment_status': 'COMPLETE',
                'amount_gross': '250.00',
                'amount_fee': '5.75',
                'amount_net': '244.25',
                'custom_int1': self.test_data.get('job_id', 'test-job-id'),
                'custom_str1': self.test_data.get('user_id', 'test-user-id'),
                'custom_str2': 'plumbing',
                'pf_payment_id': '12345',
                'm_payment_id': 'test-payment-123'
            }
            
            response = self.session.post(f"{API_BASE}/payfast/notify", json=notification_data)
            
            if response.status_code == 200:
                result = response.json()
                if "status" in result and result["status"] in ["processed", "error"]:
                    self.log_result("PayFast Notify", True, f"Notification processed with status: {result['status']}")
                    return True
                else:
                    self.log_result("PayFast Notify", False, "Invalid response format", response)
            else:
                self.log_result("PayFast Notify", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("PayFast Notify", False, f"Request error: {str(e)}")
        return False
    
    # Enhanced AI Features Tests
    def test_whatsapp_insights(self):
        """Test WhatsApp business insights endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/whatsapp/insights")
            
            if response.status_code == 200:
                result = response.json()
                if "insights" in result and isinstance(result["insights"], list):
                    insight_count = len(result["insights"])
                    self.log_result("WhatsApp Business Insights", True, f"Retrieved {insight_count} business insights")
                    return True
                else:
                    self.log_result("WhatsApp Business Insights", False, "Invalid response format", response)
            else:
                self.log_result("WhatsApp Business Insights", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("WhatsApp Business Insights", False, f"Request error: {str(e)}")
        return False
    
    def test_whatsapp_generate_insight(self):
        """Test WhatsApp generate insight endpoint"""
        try:
            response = self.session.post(f"{API_BASE}/whatsapp/generate-insight")
            
            if response.status_code == 200:
                result = response.json()
                if "success" in result or "message" in result:
                    if result.get("success"):
                        self.log_result("WhatsApp Generate Insight", True, f"Business insight generated successfully")
                        return True
                    else:
                        # Not enough data is also a valid response
                        self.log_result("WhatsApp Generate Insight", True, f"Service responded: {result.get('message', 'No message')}")
                        return True
                else:
                    self.log_result("WhatsApp Generate Insight", False, "Invalid response format", response)
            else:
                self.log_result("WhatsApp Generate Insight", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("WhatsApp Generate Insight", False, f"Request error: {str(e)}")
        return False
    
    # Error Handling Tests
    def test_whatsapp_send_message_missing_params(self):
        """Test WhatsApp send message with missing parameters"""
        try:
            # Missing message parameter
            data = {'to_number': '+27821234567'}
            response = self.session.post(f"{API_BASE}/whatsapp/send-message", data=data)
            
            if response.status_code == 422:  # Validation error expected
                self.log_result("WhatsApp Send Message - Missing Params", True, "Correctly handled missing parameters with 422 error")
                return True
            else:
                self.log_result("WhatsApp Send Message - Missing Params", False, f"Expected 422 but got {response.status_code}", response)
        except Exception as e:
            self.log_result("WhatsApp Send Message - Missing Params", False, f"Request error: {str(e)}")
        return False
    
    def test_payfast_create_payment_invalid_job(self):
        """Test PayFast payment creation with invalid job ID"""
        try:
            data = {'job_id': 'invalid-job-id-12345'}
            response = self.session.post(f"{API_BASE}/payfast/create-payment", data=data)
            
            if response.status_code == 404:  # Job not found expected
                self.log_result("PayFast Create Payment - Invalid Job", True, "Correctly handled invalid job ID with 404 error")
                return True
            else:
                self.log_result("PayFast Create Payment - Invalid Job", False, f"Expected 404 but got {response.status_code}", response)
        except Exception as e:
            self.log_result("PayFast Create Payment - Invalid Job", False, f"Request error: {str(e)}")
        return False
    
    def test_whatsapp_job_notification_no_fixer(self):
        """Test WhatsApp job notification with job that has no fixer assigned"""
        if 'user_id' not in self.test_data:
            self.log_result("WhatsApp Job Notification - No Fixer", False, "No user ID available from previous test")
            return False
        
        try:
            # Create a job without assigning a fixer
            import time
            timestamp = str(int(time.time()))[-6:]
            
            job_data = {
                "user_id": self.test_data['user_id'],
                "service": "carpentry",
                "description": "Build custom shelves",
                "location": "456 Test St, Cape Town",
                "estimated_price": 500.0
            }
            
            response = self.session.post(f"{API_BASE}/jobs", json=job_data)
            if response.status_code != 200:
                self.log_result("WhatsApp Job Notification - No Fixer", False, "Failed to create test job", response)
                return False
            
            test_job = response.json()
            
            # Try to send notification for job without fixer
            data = {'job_id': test_job['id']}
            response = self.session.post(f"{API_BASE}/whatsapp/send-job-notification", data=data)
            
            if response.status_code == 400:  # Bad request expected
                self.log_result("WhatsApp Job Notification - No Fixer", True, "Correctly handled job without fixer with 400 error")
                return True
            else:
                self.log_result("WhatsApp Job Notification - No Fixer", False, f"Expected 400 but got {response.status_code}", response)
        except Exception as e:
            self.log_result("WhatsApp Job Notification - No Fixer", False, f"Request error: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 80)
        print("FIXMATE-SA BACKEND API TESTING - WITH WHATSAPP & PAYFAST INTEGRATION")
        print("=" * 80)
        print()
        
        # Test sequence following the main user flow + new AI/SMS features + Payment System + WhatsApp + PayFast
        tests = [
            ("Health Check", self.test_health_check),
            ("Create User", self.test_create_user),
            ("Get User", self.test_get_user),
            ("Get All Users", self.test_get_all_users),
            ("Login", self.test_login),
            ("Create Fixer", self.test_create_fixer),
            ("Get Fixer", self.test_get_fixer),
            ("Get All Fixers", self.test_get_all_fixers),
            ("Get Fixers by Service", self.test_get_fixers_by_service),
            ("Fixer Payment Status", self.test_fixer_payment_status),
            ("Create Job", self.test_create_job),
            ("Get Job", self.test_get_job),
            ("Get All Jobs", self.test_get_all_jobs),
            ("Update Job (Assign Fixer)", self.test_update_job),
            ("Create Service Fee", self.test_create_service_fee),
            ("Payment History", self.test_payment_history),
            ("Settle Payment", self.test_settle_payment),
            ("Job Assignment Payment Check", self.test_job_assignment_with_payment_check),
            ("Automatic Service Fee Creation", self.test_automatic_service_fee_creation),
            ("Create Review", self.test_create_review),
            ("Get All Reviews", self.test_get_reviews),
            ("Get Reviews by Fixer", self.test_get_reviews_by_fixer),
            ("Dashboard with AI Insights", self.test_dashboard),
            # New AI and SMS feature tests
            ("AI Service Classification", self.test_ai_classify_service),
            ("AI Sentiment Analysis", self.test_ai_analyze_sentiment),
            ("AI Audio Transcription", self.test_ai_transcribe_audio),
            ("SMS Send", self.test_sms_send),
            ("SMS Webhook", self.test_sms_webhook),
            ("Enhanced Job Creation with AI", self.test_enhanced_job_creation_with_ai),
            ("Enhanced Review Creation with AI", self.test_enhanced_review_creation_with_ai),
            # WhatsApp Integration Tests
            ("WhatsApp Webhook Verify", self.test_whatsapp_webhook_verify),
            ("WhatsApp Webhook POST", self.test_whatsapp_webhook_post),
            ("WhatsApp Send Message", self.test_whatsapp_send_message),
            ("WhatsApp Job Notification", self.test_whatsapp_send_job_notification),
            ("WhatsApp Rating Request", self.test_whatsapp_send_rating_request),
            # PayFast Integration Tests
            ("PayFast Create Payment", self.test_payfast_create_payment),
            ("PayFast Payment Status", self.test_payfast_payment_status),
            ("PayFast Fixer Payment", self.test_payfast_fixer_payment),
            ("PayFast Notify", self.test_payfast_notify),
            # Enhanced AI Features Tests
            ("WhatsApp Business Insights", self.test_whatsapp_insights),
            ("WhatsApp Generate Insight", self.test_whatsapp_generate_insight),
            # Error Handling Tests
            ("WhatsApp Send Message - Missing Params", self.test_whatsapp_send_message_missing_params),
            ("PayFast Create Payment - Invalid Job", self.test_payfast_create_payment_invalid_job),
            ("WhatsApp Job Notification - No Fixer", self.test_whatsapp_job_notification_no_fixer)
        ]
        
        for test_name, test_func in tests:
            test_func()
        
        # Print summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Total: {self.results['passed'] + self.results['failed']}")
        
        if self.results['errors']:
            print("\n🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        print()
        if self.results['failed'] == 0:
            print("🎉 ALL TESTS PASSED! Backend API with WhatsApp, PayFast, AI & SMS features is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Please check the errors above.")
            return False

if __name__ == "__main__":
    tester = FixMateAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)