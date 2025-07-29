#!/usr/bin/env python3
"""
FixMate-SA Fixers Functionality Testing Script
Focused testing for fixers API endpoints and database verification
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

print(f"Testing fixers functionality at: {API_BASE}")

class FixersAPITester:
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
        """Test health check endpoint first"""
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
    
    def test_get_all_fixers(self):
        """Test GET /api/fixers endpoint - CRITICAL TEST"""
        try:
            response = self.session.get(f"{API_BASE}/fixers")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.test_data['existing_fixers'] = data
                    self.log_result("GET /api/fixers", True, f"Retrieved {len(data)} active fixers from database")
                    
                    # Verify response structure for each fixer
                    if len(data) > 0:
                        sample_fixer = data[0]
                        required_fields = ['id', 'name', 'location', 'services', 'is_active', 'rating']
                        missing_fields = [field for field in required_fields if field not in sample_fixer]
                        
                        if missing_fields:
                            self.log_result("Fixer Response Structure", False, f"Missing required fields: {missing_fields}")
                        else:
                            self.log_result("Fixer Response Structure", True, "All required fields present in fixer response")
                            
                            # Test services field JSON parsing
                            try:
                                services = json.loads(sample_fixer['services']) if isinstance(sample_fixer['services'], str) else sample_fixer['services']
                                if isinstance(services, list):
                                    self.log_result("Services Field JSON Format", True, f"Services field properly formatted as JSON array: {services}")
                                else:
                                    self.log_result("Services Field JSON Format", False, f"Services field is not a JSON array: {type(services)}")
                            except json.JSONDecodeError:
                                self.log_result("Services Field JSON Format", False, f"Services field is not valid JSON: {sample_fixer['services']}")
                    
                    return True
                else:
                    self.log_result("GET /api/fixers", False, "Response is not a list", response)
            else:
                self.log_result("GET /api/fixers", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("GET /api/fixers", False, f"Request error: {str(e)}")
        return False
    
    def test_database_fixers_verification(self):
        """Verify fixers exist in database with proper structure"""
        existing_fixers = self.test_data.get('existing_fixers', [])
        
        if len(existing_fixers) == 0:
            self.log_result("Database Fixers Verification", False, "No active fixers found in database")
            return False
        
        active_fixers = [f for f in existing_fixers if f.get('is_active', False)]
        
        if len(active_fixers) == 0:
            self.log_result("Database Active Fixers", False, "No fixers with is_active=True found")
            return False
        else:
            self.log_result("Database Active Fixers", True, f"Found {len(active_fixers)} active fixers")
        
        # Verify data structure for each active fixer
        for i, fixer in enumerate(active_fixers[:3]):  # Check first 3 fixers
            fixer_name = fixer.get('name', f'Fixer {i+1}')
            
            # Check required fields
            required_fields = ['id', 'name', 'location', 'services', 'phone', 'email']
            missing_fields = [field for field in required_fields if not fixer.get(field)]
            
            if missing_fields:
                self.log_result(f"Fixer Data Structure - {fixer_name}", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result(f"Fixer Data Structure - {fixer_name}", True, f"All required fields populated")
            
            # Verify services field
            services = fixer.get('services', '')
            if services:
                try:
                    parsed_services = json.loads(services) if isinstance(services, str) else services
                    if isinstance(parsed_services, list) and len(parsed_services) > 0:
                        self.log_result(f"Services Field - {fixer_name}", True, f"Services: {parsed_services}")
                    else:
                        self.log_result(f"Services Field - {fixer_name}", False, f"Services field empty or invalid: {services}")
                except json.JSONDecodeError:
                    self.log_result(f"Services Field - {fixer_name}", False, f"Services field not valid JSON: {services}")
            else:
                self.log_result(f"Services Field - {fixer_name}", False, "Services field is empty")
        
        return True
    
    def create_test_fixer(self, name, services, location, phone_suffix):
        """Helper method to create a test fixer"""
        import time
        timestamp = str(int(time.time()))[-6:]
        
        # First create a user for the fixer
        user_data = {
            "phone": f"+2782{phone_suffix}{timestamp}",
            "first_name": name.split()[0],
            "last_name": name.split()[1] if len(name.split()) > 1 else "Fixer",
            "id_number": f"8001015009{timestamp[-3:]}",
            "town": location,
            "email": f"{name.lower().replace(' ', '.')}.{timestamp}@fixmate.com",
            "address": f"123 {name} St, {location}"
        }
        
        try:
            # Create user first
            user_response = self.session.post(f"{API_BASE}/users", json=user_data)
            if user_response.status_code != 200:
                return None, f"Failed to create user for {name}"
            
            fixer_user = user_response.json()
            
            # Create fixer
            fixer_data = {
                "user_id": fixer_user['id'],
                "phone": user_data["phone"],
                "name": name,
                "email": user_data["email"],
                "services": json.dumps(services),  # Ensure JSON string format
                "location": location
            }
            
            fixer_response = self.session.post(f"{API_BASE}/fixers", json=fixer_data)
            if fixer_response.status_code == 200:
                return fixer_response.json(), None
            else:
                return None, f"Failed to create fixer {name}: HTTP {fixer_response.status_code}"
                
        except Exception as e:
            return None, f"Error creating fixer {name}: {str(e)}"
    
    def test_create_test_fixers_if_needed(self):
        """Create test fixers if database is empty or has insufficient data"""
        existing_fixers = self.test_data.get('existing_fixers', [])
        active_fixers = [f for f in existing_fixers if f.get('is_active', False)]
        
        if len(active_fixers) >= 3:
            self.log_result("Test Fixers Creation", True, f"Sufficient fixers already exist ({len(active_fixers)} active fixers)")
            return True
        
        # Create test fixers with different services and locations
        test_fixers = [
            {
                "name": "John Plumber",
                "services": ["plumbing", "pipe repair", "geyser installation"],
                "location": "Cape Town",
                "phone_suffix": "111"
            },
            {
                "name": "Mike Electrician", 
                "services": ["electrical", "wiring", "lighting installation"],
                "location": "Johannesburg",
                "phone_suffix": "222"
            },
            {
                "name": "Sarah Carpenter",
                "services": ["carpentry", "furniture repair", "cabinet installation"],
                "location": "Durban",
                "phone_suffix": "333"
            },
            {
                "name": "David Painter",
                "services": ["painting", "interior painting", "exterior painting"],
                "location": "Pretoria",
                "phone_suffix": "444"
            }
        ]
        
        created_count = 0
        for fixer_info in test_fixers:
            fixer, error = self.create_test_fixer(
                fixer_info["name"],
                fixer_info["services"],
                fixer_info["location"],
                fixer_info["phone_suffix"]
            )
            
            if fixer:
                created_count += 1
                self.log_result(f"Create Test Fixer - {fixer_info['name']}", True, f"Created fixer with services: {fixer_info['services']}")
            else:
                self.log_result(f"Create Test Fixer - {fixer_info['name']}", False, error)
        
        if created_count > 0:
            self.log_result("Test Fixers Creation Summary", True, f"Successfully created {created_count} test fixers")
            return True
        else:
            self.log_result("Test Fixers Creation Summary", False, "Failed to create any test fixers")
            return False
    
    def test_get_fixer_by_id(self):
        """Test GET /api/fixers/{fixer_id} endpoint"""
        existing_fixers = self.test_data.get('existing_fixers', [])
        if not existing_fixers:
            # Refresh fixers list
            response = self.session.get(f"{API_BASE}/fixers")
            if response.status_code == 200:
                existing_fixers = response.json()
            else:
                self.log_result("Get Fixer by ID", False, "No fixers available to test")
                return False
        
        if existing_fixers:
            test_fixer = existing_fixers[0]
            fixer_id = test_fixer['id']
            
            try:
                response = self.session.get(f"{API_BASE}/fixers/{fixer_id}")
                if response.status_code == 200:
                    data = response.json()
                    if data['id'] == fixer_id:
                        self.log_result("Get Fixer by ID", True, f"Retrieved fixer: {data['name']}")
                        return True
                    else:
                        self.log_result("Get Fixer by ID", False, "Fixer ID mismatch", response)
                else:
                    self.log_result("Get Fixer by ID", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("Get Fixer by ID", False, f"Request error: {str(e)}")
        else:
            self.log_result("Get Fixer by ID", False, "No fixers available to test")
        
        return False
    
    def test_get_fixers_by_service(self):
        """Test GET /api/fixers/by-service/{service} endpoint"""
        test_services = ["plumbing", "electrical", "carpentry", "painting"]
        
        for service in test_services:
            try:
                response = self.session.get(f"{API_BASE}/fixers/by-service/{service}")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_result(f"Get Fixers by Service - {service}", True, f"Retrieved {len(data)} {service} fixers")
                        
                        # Verify that returned fixers actually offer this service
                        for fixer in data:
                            services = fixer.get('services', '')
                            try:
                                parsed_services = json.loads(services) if isinstance(services, str) else services
                                if isinstance(parsed_services, list):
                                    if service.lower() in [s.lower() for s in parsed_services]:
                                        continue  # Service found
                                    else:
                                        self.log_result(f"Service Filter Accuracy - {service}", False, f"Fixer {fixer['name']} doesn't offer {service}: {parsed_services}")
                                        break
                            except:
                                self.log_result(f"Service Filter Accuracy - {service}", False, f"Invalid services format for {fixer['name']}: {services}")
                                break
                        else:
                            if len(data) > 0:
                                self.log_result(f"Service Filter Accuracy - {service}", True, f"All returned fixers offer {service}")
                    else:
                        self.log_result(f"Get Fixers by Service - {service}", False, "Response is not a list", response)
                else:
                    self.log_result(f"Get Fixers by Service - {service}", False, f"HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"Get Fixers by Service - {service}", False, f"Request error: {str(e)}")
    
    def test_frontend_compatibility(self):
        """Test that API response matches frontend FixerList component expectations"""
        try:
            response = self.session.get(f"{API_BASE}/fixers")
            if response.status_code == 200:
                fixers = response.json()
                if not fixers:
                    self.log_result("Frontend Compatibility", False, "No fixers available for compatibility testing")
                    return False
                
                sample_fixer = fixers[0]
                
                # Check fields that frontend FixerList component expects
                frontend_required_fields = [
                    'id', 'name', 'location', 'services', 'rating', 'is_active'
                ]
                
                missing_fields = [field for field in frontend_required_fields if field not in sample_fixer]
                
                if missing_fields:
                    self.log_result("Frontend Compatibility - Required Fields", False, f"Missing fields for frontend: {missing_fields}")
                else:
                    self.log_result("Frontend Compatibility - Required Fields", True, "All frontend required fields present")
                
                # Test services field parsing for frontend
                services = sample_fixer.get('services', '')
                try:
                    if isinstance(services, str):
                        parsed_services = json.loads(services)
                    else:
                        parsed_services = services
                    
                    if isinstance(parsed_services, list):
                        self.log_result("Frontend Compatibility - Services Parsing", True, f"Services can be parsed as array: {parsed_services}")
                    else:
                        self.log_result("Frontend Compatibility - Services Parsing", False, f"Services is not an array: {type(parsed_services)}")
                except json.JSONDecodeError:
                    self.log_result("Frontend Compatibility - Services Parsing", False, f"Services field cannot be parsed as JSON: {services}")
                
                # Check rating field
                rating = sample_fixer.get('rating')
                if rating is not None and isinstance(rating, (int, float)) and 0 <= rating <= 5:
                    self.log_result("Frontend Compatibility - Rating Field", True, f"Rating field valid: {rating}")
                else:
                    self.log_result("Frontend Compatibility - Rating Field", False, f"Rating field invalid: {rating}")
                
                # Check total_jobs field (if present)
                if 'total_jobs' in sample_fixer:
                    total_jobs = sample_fixer['total_jobs']
                    if isinstance(total_jobs, int) and total_jobs >= 0:
                        self.log_result("Frontend Compatibility - Total Jobs", True, f"Total jobs field valid: {total_jobs}")
                    else:
                        self.log_result("Frontend Compatibility - Total Jobs", False, f"Total jobs field invalid: {total_jobs}")
                else:
                    self.log_result("Frontend Compatibility - Total Jobs", True, "Total jobs field not required (will be calculated)")
                
                return True
            else:
                self.log_result("Frontend Compatibility", False, f"Failed to get fixers: HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Frontend Compatibility", False, f"Request error: {str(e)}")
        
        return False
    
    def test_error_handling(self):
        """Test error handling for fixers endpoints"""
        # Test invalid fixer ID
        try:
            response = self.session.get(f"{API_BASE}/fixers/invalid-fixer-id-12345")
            if response.status_code == 404:
                self.log_result("Error Handling - Invalid Fixer ID", True, "Correctly returned 404 for invalid fixer ID")
            else:
                self.log_result("Error Handling - Invalid Fixer ID", False, f"Expected 404 but got {response.status_code}")
        except Exception as e:
            self.log_result("Error Handling - Invalid Fixer ID", False, f"Request error: {str(e)}")
        
        # Test invalid service filter
        try:
            response = self.session.get(f"{API_BASE}/fixers/by-service/nonexistent-service-xyz")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) == 0:
                    self.log_result("Error Handling - Invalid Service", True, "Correctly returned empty list for non-existent service")
                else:
                    self.log_result("Error Handling - Invalid Service", False, f"Unexpected response for invalid service: {len(data)} results")
            else:
                self.log_result("Error Handling - Invalid Service", False, f"Expected 200 but got {response.status_code}")
        except Exception as e:
            self.log_result("Error Handling - Invalid Service", False, f"Request error: {str(e)}")
    
    def run_all_tests(self):
        """Run all fixer-related tests"""
        print("=" * 60)
        print("FIXMATE-SA FIXERS FUNCTIONALITY TESTING")
        print("=" * 60)
        print()
        
        # Test sequence
        tests = [
            self.test_health_check,
            self.test_get_all_fixers,
            self.test_database_fixers_verification,
            self.test_create_test_fixers_if_needed,
            self.test_get_fixer_by_id,
            self.test_get_fixers_by_service,
            self.test_frontend_compatibility,
            self.test_error_handling
        ]
        
        for test in tests:
            test()
        
        # Final summary
        print("=" * 60)
        print("FIXERS TESTING SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Total Tests: {self.results['passed'] + self.results['failed']}")
        
        if self.results['failed'] > 0:
            print("\n❌ FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   - {error}")
        
        print()
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = FixersAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)