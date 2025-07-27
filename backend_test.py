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
        user_data = {
            "phone": "+27821234567",
            "name": "John Doe",
            "email": "john.doe@example.com",
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
        fixer_data = {
            "phone": "+27829876543",
            "name": "Mike Smith",
            "email": "mike.smith@fixmate.com",
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
                required_keys = ['user', 'recent_jobs', 'top_fixers', 'stats']
                if all(key in data for key in required_keys):
                    self.log_result("Dashboard", True, f"Dashboard data retrieved successfully")
                    return True
                else:
                    missing_keys = [key for key in required_keys if key not in data]
                    self.log_result("Dashboard", False, f"Missing keys: {missing_keys}", response)
            else:
                self.log_result("Dashboard", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Dashboard", False, f"Request error: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 60)
        print("FIXMATE-SA BACKEND API TESTING")
        print("=" * 60)
        print()
        
        # Test sequence following the main user flow
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
            ("Create Job", self.test_create_job),
            ("Get Job", self.test_get_job),
            ("Get All Jobs", self.test_get_all_jobs),
            ("Update Job (Assign Fixer)", self.test_update_job),
            ("Create Review", self.test_create_review),
            ("Get All Reviews", self.test_get_reviews),
            ("Get Reviews by Fixer", self.test_get_reviews_by_fixer),
            ("Dashboard", self.test_dashboard)
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
            print("🎉 ALL TESTS PASSED! Backend API is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Please check the errors above.")
            return False

if __name__ == "__main__":
    tester = FixMateAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)