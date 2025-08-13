#!/usr/bin/env python3
"""
FixMate-SA Job Creation API Backend Testing
Comprehensive testing of Job Creation API endpoints as requested in review
"""

import requests
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

class JobCreationTester:
    def __init__(self):
        # Test both local and production URLs
        self.backend_url = "https://fixmate-sa-app-a448c751e1d2.herokuapp.com"
        self.api_base = f"{self.backend_url}/api"
        
        # Test configuration
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        # Test authentication data
        self.admin_auth = {
            "phone": "+27800000001",
            "password": "admin2024test"
        }
        
        self.client_auth = {
            "phone": "+27800000002", 
            "password": "client2024test"
        }
        
        self.auth_token = None
        self.test_user_id = None
        
        print(f"🔧 Job Creation API Testing Initialized")
        print(f"🔗 Backend URL: {self.backend_url}")
        print(f"🔗 API Base: {self.api_base}")
        print("=" * 80)

    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result with details"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        print(f"{status} | {test_name}")
        if details:
            print(f"     Details: {details}")
        if not success and response_data:
            print(f"     Response: {response_data}")
        print()

    def authenticate_user(self):
        """Authenticate test user and get token"""
        try:
            response = requests.post(
                f"{self.api_base}/auth/login",
                json=self.client_auth,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    self.auth_token = data["token"]
                    self.test_user_id = data["user"]["id"]
                    
                    self.log_test_result(
                        "User Authentication for Job Creation",
                        True,
                        f"Authenticated as {data['user']['display_name']} (Role: {data['user']['role']})",
                        {"user_id": self.test_user_id, "role": data['user']['role']}
                    )
                    return True
                else:
                    self.log_test_result(
                        "User Authentication for Job Creation",
                        False,
                        f"Authentication failed: {data.get('message', 'Unknown error')}",
                        data
                    )
            else:
                self.log_test_result(
                    "User Authentication for Job Creation",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "User Authentication for Job Creation",
                False,
                f"Request failed: {str(e)}"
            )
        
        return False

    def test_job_creation_endpoint(self):
        """Test POST /api/jobs - Job Creation Endpoint"""
        try:
            if not self.auth_token:
                self.log_test_result(
                    "Job Creation API - POST /api/jobs",
                    False,
                    "No authentication token available"
                )
                return None
            
            # Create realistic job data
            job_data = {
                "title": "Kitchen Plumbing Repair",
                "description": "Need urgent repair of kitchen sink leak. Water is dripping constantly and causing damage to cabinet.",
                "location": "Sandton, Johannesburg, Gauteng",
                "urgency": "high",
                "budget_min": 300.0,
                "budget_max": 800.0,
                "preferred_date": "2025-01-15",
                "preferred_time": "09:00",
                "category": "plumbing",  # Frontend uses 'category'
                "images": [],
                "communication_preference": "phone",
                "whatsapp_notifications": True,
                "client_id": self.test_user_id  # Frontend uses 'client_id'
            }
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.api_base}/jobs",
                json=job_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("job_id"):
                    job_id = data["job_id"]
                    
                    self.log_test_result(
                        "Job Creation API - POST /api/jobs",
                        True,
                        f"Job created successfully with ID: {job_id}",
                        {"job_id": job_id, "message": data.get("message")}
                    )
                    return job_id
                else:
                    self.log_test_result(
                        "Job Creation API - POST /api/jobs",
                        False,
                        f"Job creation failed: {data.get('message', 'Unknown error')}",
                        data
                    )
            else:
                self.log_test_result(
                    "Job Creation API - POST /api/jobs",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Job Creation API - POST /api/jobs",
                False,
                f"Request failed: {str(e)}"
            )
        
        return None

    def test_job_list_endpoint(self):
        """Test GET /api/jobs - Job List Endpoint"""
        try:
            # Test without authentication first (should work according to spec)
            response = requests.get(
                f"{self.api_base}/jobs",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "jobs" in data:
                    jobs = data["jobs"]
                    
                    self.log_test_result(
                        "Job List API - GET /api/jobs (No Auth)",
                        True,
                        f"Retrieved {len(jobs)} jobs successfully",
                        {"job_count": len(jobs)}
                    )
                    
                    # Test with client filtering
                    if self.test_user_id:
                        response_filtered = requests.get(
                            f"{self.api_base}/jobs",
                            params={"client_id": self.test_user_id},
                            timeout=10
                        )
                        
                        if response_filtered.status_code == 200:
                            filtered_data = response_filtered.json()
                            if filtered_data.get("success"):
                                filtered_jobs = filtered_data["jobs"]
                                
                                self.log_test_result(
                                    "Job List API - GET /api/jobs (Client Filter)",
                                    True,
                                    f"Retrieved {len(filtered_jobs)} jobs for client {self.test_user_id}",
                                    {"filtered_job_count": len(filtered_jobs)}
                                )
                            else:
                                self.log_test_result(
                                    "Job List API - GET /api/jobs (Client Filter)",
                                    False,
                                    f"Filtered request failed: {filtered_data}",
                                    filtered_data
                                )
                        else:
                            self.log_test_result(
                                "Job List API - GET /api/jobs (Client Filter)",
                                False,
                                f"HTTP {response_filtered.status_code}",
                                response_filtered.text
                            )
                    
                    return jobs
                else:
                    self.log_test_result(
                        "Job List API - GET /api/jobs (No Auth)",
                        False,
                        f"Invalid response structure: {data}",
                        data
                    )
            else:
                self.log_test_result(
                    "Job List API - GET /api/jobs (No Auth)",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Job List API - GET /api/jobs (No Auth)",
                False,
                f"Request failed: {str(e)}"
            )
        
        return []

    def test_job_details_endpoint(self, job_id: str):
        """Test GET /api/jobs/{job_id} - Job Details Endpoint"""
        try:
            response = requests.get(
                f"{self.api_base}/jobs/{job_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("job"):
                    job = data["job"]
                    required_fields = ["id", "title", "description", "location", "status"]
                    has_required = all(field in job for field in required_fields)
                    
                    if has_required:
                        self.log_test_result(
                            "Job Details API - GET /api/jobs/{job_id}",
                            True,
                            f"Retrieved job details for {job_id}: {job.get('title', 'No title')}",
                            {"job_id": job["id"], "status": job.get("status")}
                        )
                        return job
                    else:
                        self.log_test_result(
                            "Job Details API - GET /api/jobs/{job_id}",
                            False,
                            f"Missing required fields in job object: {list(job.keys())}",
                            job
                        )
                else:
                    self.log_test_result(
                        "Job Details API - GET /api/jobs/{job_id}",
                        False,
                        f"Invalid response structure: {data}",
                        data
                    )
            elif response.status_code == 404:
                self.log_test_result(
                    "Job Details API - GET /api/jobs/{job_id}",
                    False,
                    f"Job {job_id} not found (404)",
                    response.text
                )
            else:
                self.log_test_result(
                    "Job Details API - GET /api/jobs/{job_id}",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Job Details API - GET /api/jobs/{job_id}",
                False,
                f"Request failed: {str(e)}"
            )
        
        return None

    def test_field_mapping(self):
        """Test Field Mapping (category→service, client_id→user_id)"""
        try:
            if not self.auth_token:
                self.log_test_result(
                    "Field Mapping Test (category→service, client_id→user_id)",
                    False,
                    "No authentication token available"
                )
                return
            
            # Create job with frontend field names
            job_data = {
                "title": "Electrical Outlet Installation",
                "description": "Install new electrical outlet in home office for computer setup.",
                "location": "Cape Town, Western Cape",
                "urgency": "medium",
                "budget_min": 200.0,
                "budget_max": 500.0,
                "category": "electrical",  # Should map to 'service'
                "client_id": self.test_user_id  # Should map to 'user_id'
            }
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.api_base}/jobs",
                json=job_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("job_id"):
                    job_id = data["job_id"]
                    
                    # Retrieve the job to verify field mapping
                    job_response = requests.get(f"{self.api_base}/jobs/{job_id}", timeout=10)
                    
                    if job_response.status_code == 200:
                        job_data_response = job_response.json()
                        
                        if job_data_response.get("success"):
                            job = job_data_response["job"]
                            
                            # Check if mapping worked
                            category_mapped = job.get("category") == "electrical"  # Should be mapped back
                            client_mapped = job.get("client_id") == self.test_user_id  # Should be mapped back
                            
                            if category_mapped and client_mapped:
                                self.log_test_result(
                                    "Field Mapping Test (category→service, client_id→user_id)",
                                    True,
                                    f"Field mapping working correctly: category={job.get('category')}, client_id={job.get('client_id')}",
                                    {"job_id": job_id, "category": job.get("category"), "client_id": job.get("client_id")}
                                )
                            else:
                                self.log_test_result(
                                    "Field Mapping Test (category→service, client_id→user_id)",
                                    False,
                                    f"Field mapping failed: category={job.get('category')}, client_id={job.get('client_id')}",
                                    job
                                )
                        else:
                            self.log_test_result(
                                "Field Mapping Test (category→service, client_id→user_id)",
                                False,
                                f"Failed to retrieve created job for mapping verification",
                                job_data_response
                            )
                    else:
                        self.log_test_result(
                            "Field Mapping Test (category→service, client_id→user_id)",
                            False,
                            f"Failed to retrieve job for mapping verification: HTTP {job_response.status_code}",
                            job_response.text
                        )
                else:
                    self.log_test_result(
                        "Field Mapping Test (category→service, client_id→user_id)",
                        False,
                        f"Job creation for mapping test failed: {data.get('message', 'Unknown error')}",
                        data
                    )
            else:
                self.log_test_result(
                    "Field Mapping Test (category→service, client_id→user_id)",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Field Mapping Test (category→service, client_id→user_id)",
                False,
                f"Request failed: {str(e)}"
            )

    def test_authentication_requirements(self):
        """Test Authentication Requirements for Job Creation"""
        try:
            # Test job creation without authentication
            job_data = {
                "title": "Test Job Without Auth",
                "description": "This should fail without authentication",
                "location": "Test Location",
                "category": "testing",
                "client_id": "test_user"
            }
            
            response = requests.post(
                f"{self.api_base}/jobs",
                json=job_data,
                timeout=10
            )
            
            # Should fail with 401 or 403 if authentication is required
            if response.status_code in [401, 403]:
                self.log_test_result(
                    "Authentication Test - Job Creation Without Token",
                    True,
                    f"Correctly rejected unauthenticated request: HTTP {response.status_code}",
                    {"status_code": response.status_code}
                )
            elif response.status_code == 200:
                # If it succeeds, authentication is optional (as per spec)
                self.log_test_result(
                    "Authentication Test - Job Creation Without Token",
                    True,
                    "Job creation works without authentication (optional auth confirmed)",
                    {"status_code": response.status_code}
                )
            else:
                self.log_test_result(
                    "Authentication Test - Job Creation Without Token",
                    False,
                    f"Unexpected response: HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Authentication Test - Job Creation Without Token",
                False,
                f"Request failed: {str(e)}"
            )

    def test_production_deployment(self):
        """Test Production Deployment Verification"""
        try:
            # Test if endpoints are available on production
            endpoints_to_test = [
                "/api/jobs",
                "/api/health"
            ]
            
            production_available = 0
            
            for endpoint in endpoints_to_test:
                response = requests.get(
                    f"{self.backend_url}{endpoint}",
                    timeout=10
                )
                
                if response.status_code in [200, 401, 403]:  # Available endpoints
                    production_available += 1
                    print(f"     ✅ {endpoint}: HTTP {response.status_code} (available)")
                else:
                    print(f"     ❌ {endpoint}: HTTP {response.status_code} (not available)")
            
            if production_available == len(endpoints_to_test):
                self.log_test_result(
                    "Production Deployment Verification",
                    True,
                    f"All {production_available}/{len(endpoints_to_test)} endpoints available on production",
                    {"backend_url": self.backend_url}
                )
            else:
                self.log_test_result(
                    "Production Deployment Verification",
                    False,
                    f"Only {production_available}/{len(endpoints_to_test)} endpoints available on production",
                    {"backend_url": self.backend_url}
                )
                
        except Exception as e:
            self.log_test_result(
                "Production Deployment Verification",
                False,
                f"Request failed: {str(e)}"
            )

    def run_comprehensive_tests(self):
        """Run all job creation API tests"""
        print("🔧 STARTING COMPREHENSIVE JOB CREATION API TESTING")
        print("=" * 80)
        
        # Authentication
        auth_success = self.authenticate_user()
        
        # Production deployment check
        self.test_production_deployment()
        
        # Core job creation functionality
        created_job_id = self.test_job_creation_endpoint()
        
        # Job listing
        jobs_list = self.test_job_list_endpoint()
        
        # Job details (use created job or first from list)
        test_job_id = created_job_id or (jobs_list[0]["id"] if jobs_list else "test_job_id")
        if test_job_id:
            self.test_job_details_endpoint(test_job_id)
        
        # Field mapping test
        if auth_success:
            self.test_field_mapping()
        
        # Authentication requirements
        self.test_authentication_requirements()
        
        # Generate final report
        self.generate_test_report()

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("=" * 80)
        print("🔧 JOB CREATION API TESTING COMPLETED")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        # Critical tests for job creation
        critical_tests = [
            "Job Creation API - POST /api/jobs",
            "Job List API - GET /api/jobs (No Auth)",
            "Production Deployment Verification"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result["test"] in critical_tests and result["success"])
        critical_total = len([r for r in self.test_results if r["test"] in critical_tests])
        
        print(f"🔴 CRITICAL FUNCTIONALITY: {critical_passed}/{critical_total} passed")
        print()
        
        # Detailed results
        print("📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['test']}")
            if result["details"]:
                print(f"      {result['details']}")
        
        print()
        
        # Final assessment
        if success_rate >= 80 and critical_passed == critical_total:
            print("🎉 JOB CREATION API STATUS: PRODUCTION READY")
            print("   All critical job creation functionality working correctly")
        elif success_rate >= 60:
            print("⚠️ JOB CREATION API STATUS: MOSTLY FUNCTIONAL")
            print("   Core functionality working with minor issues")
        else:
            print("❌ JOB CREATION API STATUS: NEEDS ATTENTION")
            print("   Critical issues found that require fixing")
        
        print("=" * 80)
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "success_rate": success_rate,
            "critical_passed": critical_passed,
            "critical_total": critical_total,
            "status": "PRODUCTION READY" if success_rate >= 80 and critical_passed == critical_total else "NEEDS ATTENTION"
        }

def main():
    """Main testing function"""
    tester = JobCreationTester()
    results = tester.run_comprehensive_tests()
    return results

if __name__ == "__main__":
    main()