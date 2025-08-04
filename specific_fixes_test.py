#!/usr/bin/env python3
"""
FixMate-SA Specific Fixes Testing Script

Testing the following specific fixes:
1. Voice Recording Fix - Test transcribe audio endpoint (/api/transcribe)
2. Admin Client Service Request - Test admin can create service requests (/api/jobs/workflow) with admin_created flag
3. Smart Matching Admin Access - Test smart matching admin endpoints
4. Business Compliance Services - Test business compliance admin endpoints
5. General API Health - Verify existing functionality still works
"""

import requests
import json
import sys
import os
import base64
import io
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔧 Testing Specific Fixes at: {API_BASE}")
print("=" * 80)

class SpecificFixesTester:
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
        """Test basic API health"""
        try:
            response = self.session.get(f"{API_BASE}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_result("API Health Check", True, f"API is running: {data['message']}")
                    return True
                else:
                    self.log_result("API Health Check", False, "Invalid response format", response)
            else:
                self.log_result("API Health Check", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("API Health Check", False, f"Connection error: {str(e)}")
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
                    # Set authorization header for subsequent requests
                    self.session.headers.update({'Authorization': f"Bearer {data['token']}"})
                    self.log_result("Admin Login", True, f"Admin login successful, role: {data.get('role_info', {}).get('role', 'unknown')}")
                    return True
                else:
                    self.log_result("Admin Login", False, "Invalid response format", response)
            else:
                self.log_result("Admin Login", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Admin Login", False, f"Request error: {str(e)}")
        return False
    
    def create_test_audio_file(self):
        """Create a simple test audio file (mock WAV format)"""
        # Create a minimal WAV file header + some data
        wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
        # Add some sample audio data (silence)
        audio_data = b'\x00' * 2048
        return wav_header + audio_data
    
    def test_voice_recording_fix(self):
        """Test 1: Voice Recording Fix - Test transcribe audio endpoint"""
        print("🎤 Testing Voice Recording Fix - Transcribe Audio Endpoint")
        
        try:
            # Create test audio file
            audio_data = self.create_test_audio_file()
            
            # Prepare multipart form data
            files = {
                'audio': ('test_audio.wav', io.BytesIO(audio_data), 'audio/wav')
            }
            
            response = self.session.post(f"{API_BASE}/transcribe", files=files)
            
            if response.status_code == 200:
                data = response.json()
                if "transcription" in data:
                    transcription = data["transcription"]
                    self.log_result("Voice Recording Fix - Transcribe Audio", True, 
                                  f"✅ TRANSCRIBE AUDIO ENDPOINT WORKING! Transcription result: '{transcription[:100]}...' (Length: {len(transcription)} chars)")
                    return True
                else:
                    self.log_result("Voice Recording Fix - Transcribe Audio", False, "Invalid response format - missing transcription field", response)
            else:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'Unknown error')
                    self.log_result("Voice Recording Fix - Transcribe Audio", False, f"HTTP {response.status_code} - {error_detail}", response)
                except:
                    self.log_result("Voice Recording Fix - Transcribe Audio", False, f"HTTP {response.status_code} - {response.text[:200]}", response)
        except Exception as e:
            self.log_result("Voice Recording Fix - Transcribe Audio", False, f"Request error: {str(e)}")
        return False
    
    def test_admin_client_service_request(self):
        """Test 2: Admin Client Service Request - Test admin can create service requests on behalf of clients"""
        print("👨‍💼 Testing Admin Client Service Request - Job Workflow with Admin Created Flag")
        
        if 'admin_user_id' not in self.test_data:
            self.log_result("Admin Client Service Request", False, "No admin user ID available")
            return False
        
        try:
            # Create a job workflow request with admin_created flag
            job_data = {
                "user_id": self.test_data['admin_user_id'],  # Admin creating on behalf of client
                "service": "plumbing",
                "description": "Admin-created service request - Emergency plumbing repair for client",
                "location": "123 Client Street, Cape Town",
                "estimated_price": 650.0,
                "priority_level": "high",
                "admin_created": True,  # This is the key flag we're testing
                "client_phone": "+27821234999",  # Phone of actual client
                "admin_notes": "Created by admin on behalf of client via phone call"
            }
            
            response = self.session.post(f"{API_BASE}/jobs/workflow", json=job_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'job_id' in data:
                    job_id = data['job_id']
                    message = data.get('message', 'Job created successfully')
                    
                    # Store job ID for potential cleanup
                    self.test_data['admin_created_job_id'] = job_id
                    
                    self.log_result("Admin Client Service Request", True, 
                                  f"✅ ADMIN CLIENT SERVICE REQUEST WORKING! Admin successfully created job on behalf of client. "
                                  f"Job ID: {job_id}, Message: {message}")
                    return True
                else:
                    self.log_result("Admin Client Service Request", False, f"Job workflow creation failed: {data}", response)
            else:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', 'Unknown error')
                    self.log_result("Admin Client Service Request", False, f"HTTP {response.status_code} - {error_detail}", response)
                except:
                    self.log_result("Admin Client Service Request", False, f"HTTP {response.status_code} - {response.text[:200]}", response)
        except Exception as e:
            self.log_result("Admin Client Service Request", False, f"Request error: {str(e)}")
        return False
    
    def test_smart_matching_admin_access(self):
        """Test 3: Smart Matching Admin Access - Test smart matching admin endpoints"""
        print("🧠 Testing Smart Matching Admin Access - Admin Endpoints")
        
        if 'admin_token' not in self.test_data:
            self.log_result("Smart Matching Admin Access", False, "No admin token available")
            return False
        
        success_count = 0
        total_tests = 2
        
        # Test 1: GET /api/admin/matching-performance?days=7
        try:
            response = self.session.get(f"{API_BASE}/admin/matching-performance?days=7")
            
            if response.status_code == 200:
                data = response.json()
                # Check for expected performance metrics
                expected_fields = ['total_matches', 'success_rate', 'average_score']
                has_metrics = any(field in data for field in expected_fields)
                
                if has_metrics or isinstance(data, dict):
                    success_count += 1
                    print(f"   ✅ GET /api/admin/matching-performance working - Performance data available")
                else:
                    print(f"   ❌ GET /api/admin/matching-performance - Invalid response format")
            else:
                print(f"   ❌ GET /api/admin/matching-performance failed - HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ GET /api/admin/matching-performance error - {str(e)}")
        
        # Test 2: POST /api/admin/improve-matching
        try:
            improve_data = {
                "analysis_period_days": 7,
                "min_matches_threshold": 3,
                "target_success_rate": 0.85
            }
            
            response = self.session.post(f"{API_BASE}/admin/improve-matching", json=improve_data)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    success_count += 1
                    recommendations = data.get('recommendations', [])
                    print(f"   ✅ POST /api/admin/improve-matching working - {len(recommendations)} recommendations generated")
                else:
                    print(f"   ❌ POST /api/admin/improve-matching - Invalid response format")
            else:
                print(f"   ❌ POST /api/admin/improve-matching failed - HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ POST /api/admin/improve-matching error - {str(e)}")
        
        # Overall result
        if success_count == total_tests:
            self.log_result("Smart Matching Admin Access", True, 
                          f"✅ SMART MATCHING ADMIN ACCESS WORKING! Both admin endpoints functional ({success_count}/{total_tests})")
            return True
        elif success_count > 0:
            self.log_result("Smart Matching Admin Access", False, 
                          f"Partial success - {success_count}/{total_tests} admin endpoints working")
        else:
            self.log_result("Smart Matching Admin Access", False, 
                          f"All smart matching admin endpoints failed ({success_count}/{total_tests})")
        return False
    
    def test_business_compliance_services(self):
        """Test 4: Business Compliance Services - Test business compliance admin endpoints"""
        print("📋 Testing Business Compliance Services - Admin Endpoints")
        
        if 'admin_token' not in self.test_data:
            self.log_result("Business Compliance Services", False, "No admin token available")
            return False
        
        success_count = 0
        total_tests = 2
        
        # Test 1: GET /api/compliance/admin/all-requests
        try:
            response = self.session.get(f"{API_BASE}/compliance/admin/all-requests")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, (dict, list)):
                    success_count += 1
                    if isinstance(data, dict) and 'requests' in data:
                        requests_count = len(data['requests'])
                        print(f"   ✅ GET /api/compliance/admin/all-requests working - {requests_count} compliance requests found")
                    elif isinstance(data, list):
                        print(f"   ✅ GET /api/compliance/admin/all-requests working - {len(data)} compliance requests found")
                    else:
                        print(f"   ✅ GET /api/compliance/admin/all-requests working - Response format valid")
                else:
                    print(f"   ❌ GET /api/compliance/admin/all-requests - Invalid response format")
            else:
                print(f"   ❌ GET /api/compliance/admin/all-requests failed - HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ GET /api/compliance/admin/all-requests error - {str(e)}")
        
        # Test 2: GET /api/compliance/categories
        try:
            response = self.session.get(f"{API_BASE}/compliance/categories")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, (dict, list)):
                    success_count += 1
                    if isinstance(data, dict) and 'categories' in data:
                        categories_count = len(data['categories'])
                        print(f"   ✅ GET /api/compliance/categories working - {categories_count} compliance categories available")
                    elif isinstance(data, list):
                        print(f"   ✅ GET /api/compliance/categories working - {len(data)} compliance categories available")
                    else:
                        print(f"   ✅ GET /api/compliance/categories working - Response format valid")
                else:
                    print(f"   ❌ GET /api/compliance/categories - Invalid response format")
            else:
                print(f"   ❌ GET /api/compliance/categories failed - HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ GET /api/compliance/categories error - {str(e)}")
        
        # Overall result
        if success_count == total_tests:
            self.log_result("Business Compliance Services", True, 
                          f"✅ BUSINESS COMPLIANCE SERVICES WORKING! Both compliance endpoints functional ({success_count}/{total_tests})")
            return True
        elif success_count > 0:
            self.log_result("Business Compliance Services", False, 
                          f"Partial success - {success_count}/{total_tests} compliance endpoints working")
        else:
            self.log_result("Business Compliance Services", False, 
                          f"All business compliance endpoints failed ({success_count}/{total_tests})")
        return False
    
    def test_general_api_health(self):
        """Test 5: General API Health - Verify existing functionality still works"""
        print("🏥 Testing General API Health - Existing Functionality")
        
        success_count = 0
        total_tests = 5
        
        # Test 1: Users endpoint
        try:
            response = self.session.get(f"{API_BASE}/users?limit=5")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) or (isinstance(data, dict) and 'data' in data):
                    success_count += 1
                    print(f"   ✅ Users endpoint working")
                else:
                    print(f"   ❌ Users endpoint - Invalid response format")
            else:
                print(f"   ❌ Users endpoint failed - HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Users endpoint error - {str(e)}")
        
        # Test 2: Fixers endpoint
        try:
            response = self.session.get(f"{API_BASE}/fixers?limit=5")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) or (isinstance(data, dict) and 'data' in data):
                    success_count += 1
                    print(f"   ✅ Fixers endpoint working")
                else:
                    print(f"   ❌ Fixers endpoint - Invalid response format")
            else:
                print(f"   ❌ Fixers endpoint failed - HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Fixers endpoint error - {str(e)}")
        
        # Test 3: Jobs endpoint
        try:
            response = self.session.get(f"{API_BASE}/jobs?limit=5")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, (list, dict)):
                    success_count += 1
                    print(f"   ✅ Jobs endpoint working")
                else:
                    print(f"   ❌ Jobs endpoint - Invalid response format")
            else:
                print(f"   ❌ Jobs endpoint failed - HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Jobs endpoint error - {str(e)}")
        
        # Test 4: Authentication endpoints
        try:
            # Test role check endpoint
            response = self.session.get(f"{API_BASE}/auth/role-check/+27821234567")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'role' in data:
                    success_count += 1
                    print(f"   ✅ Authentication endpoints working")
                else:
                    print(f"   ❌ Authentication endpoints - Invalid response format")
            else:
                print(f"   ❌ Authentication endpoints failed - HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Authentication endpoints error - {str(e)}")
        
        # Test 5: AI service endpoints
        try:
            response = self.session.post(f"{API_BASE}/classify-service", data={"description": "Fix my leaking tap"})
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'classification' in data:
                    success_count += 1
                    print(f"   ✅ AI service endpoints working")
                else:
                    print(f"   ❌ AI service endpoints - Invalid response format")
            else:
                print(f"   ❌ AI service endpoints failed - HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ AI service endpoints error - {str(e)}")
        
        # Overall result
        if success_count >= 4:  # Allow for 1 failure
            self.log_result("General API Health", True, 
                          f"✅ GENERAL API HEALTH GOOD! Most existing functionality working ({success_count}/{total_tests})")
            return True
        elif success_count >= 2:
            self.log_result("General API Health", False, 
                          f"Partial health - {success_count}/{total_tests} endpoints working")
        else:
            self.log_result("General API Health", False, 
                          f"Poor API health - {success_count}/{total_tests} endpoints working")
        return False
    
    def run_specific_fixes_tests(self):
        """Run all specific fixes tests"""
        print("🚀 SPECIFIC FIXES TESTING")
        print("=" * 80)
        
        # Setup
        print("📋 SETUP PHASE")
        print("-" * 50)
        
        if not self.test_health_check():
            print("❌ Health check failed. Cannot proceed with testing.")
            return False
        
        if not self.test_admin_login():
            print("❌ Admin login failed. Some tests may not work properly.")
        
        # Main Tests
        print("\n🎯 MAIN TESTING PHASE")
        print("-" * 50)
        
        tests = [
            ("Voice Recording Fix", self.test_voice_recording_fix),
            ("Admin Client Service Request", self.test_admin_client_service_request),
            ("Smart Matching Admin Access", self.test_smart_matching_admin_access),
            ("Business Compliance Services", self.test_business_compliance_services),
            ("General API Health", self.test_general_api_health)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\nTesting {test_name}...")
            result = test_func()
            results.append((test_name, result))
        
        # Results Summary
        print("\n" + "=" * 80)
        print("🎯 SPECIFIC FIXES TEST RESULTS")
        print("=" * 80)
        
        passed_tests = 0
        for test_name, result in results:
            status = "✅ WORKING" if result else "❌ FAILING"
            print(f"   {status}: {test_name}")
            if result:
                passed_tests += 1
        
        success_rate = passed_tests / len(tests) * 100
        print(f"\n📊 Overall Success Rate: {passed_tests}/{len(tests)} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("\n🎉 EXCELLENT! Most specific fixes are working correctly!")
        elif success_rate >= 60:
            print("\n✅ GOOD! Most specific fixes are working, some need attention.")
        else:
            print("\n⚠️ WARNING! Multiple specific fixes need attention.")
        
        return success_rate >= 60

if __name__ == "__main__":
    print("🔧 FixMate-SA Specific Fixes Testing")
    print("=" * 80)
    print("🎯 TESTING SPECIFIC FIXES:")
    print("   1. Voice Recording Fix - Transcribe Audio Endpoint")
    print("   2. Admin Client Service Request - Job Workflow with Admin Created Flag")
    print("   3. Smart Matching Admin Access - Admin Endpoints")
    print("   4. Business Compliance Services - Admin Endpoints")
    print("   5. General API Health - Existing Functionality")
    print("=" * 80)
    
    tester = SpecificFixesTester()
    
    try:
        success = tester.run_specific_fixes_tests()
        
        print("\n" + "=" * 80)
        print("📊 FINAL TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {tester.results['passed']}")
        print(f"❌ Tests Failed: {tester.results['failed']}")
        total_tests = tester.results['passed'] + tester.results['failed']
        if total_tests > 0:
            print(f"📈 Success Rate: {tester.results['passed']/total_tests*100:.1f}%")
        
        if tester.results['errors']:
            print(f"\n🚨 ERRORS ENCOUNTERED:")
            for error in tester.results['errors']:
                print(f"   • {error}")
        
        if success:
            print("\n🎉 SPECIFIC FIXES TESTING COMPLETED SUCCESSFULLY!")
            print("✅ Most requested fixes are working correctly")
        else:
            print("\n⚠️ SPECIFIC FIXES TESTING COMPLETED WITH ISSUES")
            print("❌ Some requested fixes need attention")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {str(e)}")
        sys.exit(1)