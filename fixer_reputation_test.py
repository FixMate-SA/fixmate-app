#!/usr/bin/env python3
"""
Fixer Reputation API Testing Script
Tests the newly added fixer reputation endpoints for FixMate-SA
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://service-pros-2.preview.emergentagent.com/api"
FIXER_USER_ID = "c417ef19-cdb6-44ee-80aa-8128e0ff8e75"  # Fixer that logs in with +27800000003
FIXER_LOGIN_PHONE = "+27800000003"
FIXER_LOGIN_PASSWORD = "fixer2024test"

class FixerReputationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def authenticate_fixer(self):
        """Authenticate as the test fixer user"""
        print("\n🔐 AUTHENTICATING FIXER USER...")
        
        try:
            login_data = {
                "phone": FIXER_LOGIN_PHONE,
                "password": FIXER_LOGIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    self.auth_token = data["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    
                    user_info = data.get("user", {})
                    self.log_test("Fixer Authentication", True, 
                                f"Logged in as {user_info.get('display_name', 'Unknown')} (Role: {user_info.get('role', 'Unknown')})")
                    return True
                else:
                    self.log_test("Fixer Authentication", False, f"Login failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                self.log_test("Fixer Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Fixer Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_get_fixer_reputation(self):
        """Test GET /api/fixer/{fixer_id}/reputation"""
        print("\n📊 TESTING GET FIXER REPUTATION...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/fixer/{FIXER_USER_ID}/reputation")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    reputation = data.get("reputation", {})
                    
                    # Verify required fields are present
                    required_fields = [
                        "fixer_id", "fixer_name", "tier", "reputation_score", 
                        "current_rating", "jobs_completed", "badges", "performance_metrics"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in reputation]
                    
                    if not missing_fields:
                        # Verify data types and ranges
                        validation_errors = []
                        
                        # Check tier is valid
                        valid_tiers = ["Bronze", "Silver", "Gold", "Platinum"]
                        if reputation.get("tier") not in valid_tiers:
                            validation_errors.append(f"Invalid tier: {reputation.get('tier')}")
                        
                        # Check reputation score is 0-100
                        score = reputation.get("reputation_score", -1)
                        if not (0 <= score <= 100):
                            validation_errors.append(f"Invalid reputation score: {score}")
                        
                        # Check rating is 0-5
                        rating = reputation.get("current_rating", -1)
                        if not (0 <= rating <= 5):
                            validation_errors.append(f"Invalid rating: {rating}")
                        
                        # Check performance metrics structure
                        metrics = reputation.get("performance_metrics", {})
                        expected_metrics = ["response_time", "completion_rate", "customer_satisfaction", "reliability"]
                        missing_metrics = [m for m in expected_metrics if m not in metrics]
                        if missing_metrics:
                            validation_errors.append(f"Missing performance metrics: {missing_metrics}")
                        
                        if not validation_errors:
                            self.log_test("GET Fixer Reputation - Data Structure", True, 
                                        f"Tier: {reputation.get('tier')}, Score: {reputation.get('reputation_score')}, Rating: {reputation.get('current_rating')}")
                            
                            # Test specific data values
                            self.log_test("GET Fixer Reputation - Fixer Name", 
                                        bool(reputation.get("fixer_name")), 
                                        f"Name: {reputation.get('fixer_name', 'Not provided')}")
                            
                            self.log_test("GET Fixer Reputation - Badges Array", 
                                        isinstance(reputation.get("badges"), list), 
                                        f"Badges: {reputation.get('badges', [])}")
                            
                            return True
                        else:
                            self.log_test("GET Fixer Reputation - Data Validation", False, 
                                        f"Validation errors: {validation_errors}")
                            return False
                    else:
                        self.log_test("GET Fixer Reputation - Required Fields", False, 
                                    f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_test("GET Fixer Reputation - API Response", False, 
                                f"API returned success=false: {data.get('message', 'Unknown error')}")
                    return False
            else:
                self.log_test("GET Fixer Reputation - HTTP Status", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET Fixer Reputation - Exception", False, f"Exception: {str(e)}")
            return False
    
    def test_initialize_fixer_reputation(self):
        """Test POST /api/fixer/{fixer_id}/reputation/initialize"""
        print("\n🚀 TESTING INITIALIZE FIXER REPUTATION...")
        
        try:
            response = self.session.post(f"{BACKEND_URL}/fixer/{FIXER_USER_ID}/reputation/initialize")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    self.log_test("POST Initialize Reputation - Success", True, 
                                f"Message: {data.get('message', 'No message')}")
                    return True
                else:
                    self.log_test("POST Initialize Reputation - API Response", False, 
                                f"API returned success=false: {data.get('message', 'Unknown error')}")
                    return False
            else:
                self.log_test("POST Initialize Reputation - HTTP Status", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST Initialize Reputation - Exception", False, f"Exception: {str(e)}")
            return False
    
    def test_update_fixer_reputation(self):
        """Test POST /api/fixer/{fixer_id}/reputation/update"""
        print("\n📈 TESTING UPDATE FIXER REPUTATION...")
        
        try:
            # Test with sample performance data
            performance_data = {
                "rating": 4.7,
                "reviews_count": 15
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/fixer/{FIXER_USER_ID}/reputation/update", 
                json=performance_data
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    self.log_test("POST Update Reputation - Success", True, 
                                f"Message: {data.get('message', 'No message')}")
                    
                    # Verify the update by getting reputation again
                    verify_response = self.session.get(f"{BACKEND_URL}/fixer/{FIXER_USER_ID}/reputation")
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        if verify_data.get("success"):
                            reputation = verify_data.get("reputation", {})
                            updated_rating = reputation.get("current_rating")
                            
                            # Check if rating was updated (allowing for some tolerance)
                            if abs(updated_rating - 4.7) < 0.1:
                                self.log_test("POST Update Reputation - Verification", True, 
                                            f"Rating updated to: {updated_rating}")
                            else:
                                self.log_test("POST Update Reputation - Verification", False, 
                                            f"Rating not updated correctly. Expected ~4.7, got {updated_rating}")
                        else:
                            self.log_test("POST Update Reputation - Verification", False, 
                                        "Could not verify update - reputation fetch failed")
                    
                    return True
                else:
                    self.log_test("POST Update Reputation - API Response", False, 
                                f"API returned success=false: {data.get('message', 'Unknown error')}")
                    return False
            else:
                self.log_test("POST Update Reputation - HTTP Status", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST Update Reputation - Exception", False, f"Exception: {str(e)}")
            return False
    
    def test_reputation_calculation_logic(self):
        """Test reputation calculation logic and tier assignment"""
        print("\n🧮 TESTING REPUTATION CALCULATION LOGIC...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/fixer/{FIXER_USER_ID}/reputation")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    reputation = data.get("reputation", {})
                    
                    # Test tier logic consistency
                    tier = reputation.get("tier")
                    rating = reputation.get("current_rating", 0)
                    completed_jobs = reputation.get("jobs_completed", 0)
                    
                    # Verify tier assignment logic
                    expected_tier = "Bronze"  # Default
                    if completed_jobs >= 50 and rating >= 4.8:
                        expected_tier = "Platinum"
                    elif completed_jobs >= 25 and rating >= 4.5:
                        expected_tier = "Gold"
                    elif completed_jobs >= 10 and rating >= 4.0:
                        expected_tier = "Silver"
                    
                    tier_correct = (tier == expected_tier)
                    self.log_test("Reputation Calculation - Tier Logic", tier_correct, 
                                f"Jobs: {completed_jobs}, Rating: {rating}, Tier: {tier} (Expected: {expected_tier})")
                    
                    # Test reputation score calculation
                    score = reputation.get("reputation_score", 0)
                    reviews_count = reputation.get("total_reviews", 0)
                    expected_score = min(100, int((rating * 15) + (completed_jobs * 2) + (reviews_count * 0.5)))
                    
                    score_correct = abs(score - expected_score) <= 1  # Allow 1 point tolerance
                    self.log_test("Reputation Calculation - Score Logic", score_correct, 
                                f"Score: {score} (Expected: {expected_score})")
                    
                    # Test completion rate calculation
                    total_jobs = reputation.get("total_jobs", 0)
                    completion_rate_str = reputation.get("performance_metrics", {}).get("completion_rate", "0%")
                    completion_rate = float(completion_rate_str.replace("%", ""))
                    
                    if total_jobs > 0:
                        expected_completion_rate = round((completed_jobs / total_jobs) * 100, 1)
                        rate_correct = abs(completion_rate - expected_completion_rate) <= 0.1
                        self.log_test("Reputation Calculation - Completion Rate", rate_correct, 
                                    f"Rate: {completion_rate}% (Expected: {expected_completion_rate}%)")
                    else:
                        self.log_test("Reputation Calculation - Completion Rate", True, 
                                    "No jobs to calculate completion rate")
                    
                    return tier_correct and score_correct
                else:
                    self.log_test("Reputation Calculation Logic", False, 
                                f"Could not fetch reputation data: {data.get('message')}")
                    return False
            else:
                self.log_test("Reputation Calculation Logic", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Reputation Calculation Logic", False, f"Exception: {str(e)}")
            return False
    
    def test_database_queries(self):
        """Test that database queries execute without errors"""
        print("\n🗄️ TESTING DATABASE QUERY EXECUTION...")
        
        # Test multiple calls to ensure no database connection issues
        success_count = 0
        total_calls = 3
        
        for i in range(total_calls):
            try:
                response = self.session.get(f"{BACKEND_URL}/fixer/{FIXER_USER_ID}/reputation")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        success_count += 1
            except Exception as e:
                print(f"   Database query {i+1} failed: {str(e)}")
        
        all_successful = (success_count == total_calls)
        self.log_test("Database Query Execution", all_successful, 
                    f"{success_count}/{total_calls} queries successful")
        
        return all_successful
    
    def test_error_handling(self):
        """Test error handling for invalid fixer IDs"""
        print("\n🚫 TESTING ERROR HANDLING...")
        
        # Test with non-existent fixer ID
        try:
            invalid_fixer_id = "non-existent-fixer-id"
            response = self.session.get(f"{BACKEND_URL}/fixer/{invalid_fixer_id}/reputation")
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return success=false for non-existent fixer
                if not data.get("success"):
                    self.log_test("Error Handling - Invalid Fixer ID", True, 
                                f"Correctly returned error: {data.get('message', 'No message')}")
                    return True
                else:
                    self.log_test("Error Handling - Invalid Fixer ID", False, 
                                "Should have returned error for non-existent fixer")
                    return False
            else:
                # 404 or other error status is also acceptable
                self.log_test("Error Handling - Invalid Fixer ID", True, 
                            f"Returned HTTP {response.status_code} for invalid fixer")
                return True
                
        except Exception as e:
            self.log_test("Error Handling - Invalid Fixer ID", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all reputation API tests"""
        print("🧪 STARTING FIXER REPUTATION API TESTING")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate_fixer():
            print("\n❌ AUTHENTICATION FAILED - CANNOT PROCEED WITH TESTS")
            return False
        
        # Run all tests
        tests = [
            self.test_get_fixer_reputation,
            self.test_initialize_fixer_reputation,
            self.test_update_fixer_reputation,
            self.test_reputation_calculation_logic,
            self.test_database_queries,
            self.test_error_handling
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 FIXER REPUTATION API TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 OVERALL RESULT: FIXER REPUTATION API IS WORKING WELL!")
        elif success_rate >= 60:
            print("⚠️ OVERALL RESULT: FIXER REPUTATION API HAS SOME ISSUES")
        else:
            print("❌ OVERALL RESULT: FIXER REPUTATION API NEEDS SIGNIFICANT FIXES")
        
        # Print detailed results
        print("\nDetailed Test Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = FixerReputationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)