#!/usr/bin/env python3
"""
Heroku Fixer Signup and Password Reset Testing
==============================================

This script tests the fixer signup and password reset endpoints specifically on the Heroku deployment
to diagnose the exact errors causing "registration failed" and "invalid reset code" messages.

Focus Areas:
1. POST /api/fixer/apply - Fixer application/signup
2. POST /api/auth/request-password-reset - Password reset request  
3. POST /api/auth/verify-reset-code - Reset code verification
4. Database schema verification
5. Error analysis and root cause identification
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Heroku Backend URL from frontend/.env
HEROKU_BACKEND_URL = "https://7ef742b6-84fb-4679-ad46-1746d9bdf7d5.preview.emergentagent.com"

class HerokuFixerPasswordTester:
    def __init__(self):
        self.backend_url = HEROKU_BACKEND_URL
        self.test_results = []
        self.errors_found = []
        
    def log_result(self, test_name, success, details, error_details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        if error_details:
            result["error"] = error_details
            self.errors_found.append(f"{test_name}: {error_details}")
        
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        print(f"   Details: {details}")
        if error_details:
            print(f"   Error: {error_details}")
        print()

    def test_fixer_signup_heroku(self):
        """Test POST /api/fixer/apply on Heroku deployment"""
        print("🔧 TESTING FIXER SIGNUP ON HEROKU")
        print("=" * 50)
        
        try:
            # First, create a test user to apply as fixer
            test_user_id = f"test_user_{uuid.uuid4()}"
            
            # Test fixer application data
            fixer_data = {
                'user_id': test_user_id,
                'services_offered': 'Plumbing, Electrical, General Maintenance',
                'experience_years': '5',
                'why_fixer': 'I have extensive experience in home repairs and want to help people fix their problems quickly and efficiently.',
                'qualifications': 'Certified Electrician, Plumbing License',
                'previous_work': 'Worked at ABC Repairs for 3 years, handled 200+ jobs'
            }
            
            # Test with missing user (should fail gracefully)
            print("Testing fixer application with non-existent user...")
            response = requests.post(
                f"{self.backend_url}/api/fixer/apply",
                data=fixer_data,
                timeout=30
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"Response Data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"Response Text: {response.text}")
            
            if response.status_code == 404:
                self.log_result(
                    "Fixer Signup - User Not Found Handling",
                    True,
                    f"Correctly returned 404 for non-existent user. Response: {response.text[:200]}"
                )
            else:
                self.log_result(
                    "Fixer Signup - User Not Found Handling", 
                    False,
                    f"Expected 404 but got {response.status_code}",
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
            
            # Test with missing required fields
            print("\nTesting fixer application with missing fields...")
            incomplete_data = {'user_id': test_user_id}
            
            response = requests.post(
                f"{self.backend_url}/api/fixer/apply",
                data=incomplete_data,
                timeout=30
            )
            
            print(f"Response Status: {response.status_code}")
            try:
                response_data = response.json()
                print(f"Response Data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"Response Text: {response.text}")
            
            if response.status_code == 400:
                self.log_result(
                    "Fixer Signup - Missing Fields Validation",
                    True,
                    f"Correctly returned 400 for missing fields. Response: {response.text[:200]}"
                )
            else:
                self.log_result(
                    "Fixer Signup - Missing Fields Validation",
                    False, 
                    f"Expected 400 but got {response.status_code}",
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Fixer Signup - Network Connection",
                False,
                "Failed to connect to Heroku backend",
                f"Network error: {str(e)}"
            )
        except Exception as e:
            self.log_result(
                "Fixer Signup - General Error",
                False,
                "Unexpected error during fixer signup test",
                f"Error: {str(e)}"
            )

    def test_password_reset_request_heroku(self):
        """Test POST /api/auth/request-password-reset on Heroku"""
        print("🔑 TESTING PASSWORD RESET REQUEST ON HEROKU")
        print("=" * 50)
        
        try:
            # Test with non-existent phone number
            print("Testing password reset request with non-existent phone...")
            reset_data = {'phone': '+27999999999'}
            
            response = requests.post(
                f"{self.backend_url}/api/auth/request-password-reset",
                data=reset_data,
                timeout=30
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"Response Data: {json.dumps(response_data, indent=2)}")
                
                if response.status_code == 200 and response_data.get('success'):
                    self.log_result(
                        "Password Reset Request - Non-existent User",
                        True,
                        f"Security-compliant response for non-existent user. Message: {response_data.get('message')}"
                    )
                else:
                    self.log_result(
                        "Password Reset Request - Non-existent User",
                        False,
                        f"Unexpected response for non-existent user",
                        f"Status: {response.status_code}, Data: {response_data}"
                    )
            except:
                print(f"Response Text: {response.text}")
                self.log_result(
                    "Password Reset Request - Response Format",
                    False,
                    "Could not parse JSON response",
                    f"Status: {response.status_code}, Text: {response.text[:200]}"
                )
            
            # Test with missing phone number
            print("\nTesting password reset request with missing phone...")
            response = requests.post(
                f"{self.backend_url}/api/auth/request-password-reset",
                data={},
                timeout=30
            )
            
            print(f"Response Status: {response.status_code}")
            try:
                response_data = response.json()
                print(f"Response Data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"Response Text: {response.text}")
            
            if response.status_code == 400:
                self.log_result(
                    "Password Reset Request - Missing Phone Validation",
                    True,
                    f"Correctly returned 400 for missing phone. Response: {response.text[:200]}"
                )
            else:
                self.log_result(
                    "Password Reset Request - Missing Phone Validation",
                    False,
                    f"Expected 400 but got {response.status_code}",
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Password Reset Request - Network Connection",
                False,
                "Failed to connect to Heroku backend",
                f"Network error: {str(e)}"
            )
        except Exception as e:
            self.log_result(
                "Password Reset Request - General Error",
                False,
                "Unexpected error during password reset request test",
                f"Error: {str(e)}"
            )

    def test_password_reset_verification_heroku(self):
        """Test POST /api/auth/verify-reset-code on Heroku"""
        print("🔐 TESTING PASSWORD RESET CODE VERIFICATION ON HEROKU")
        print("=" * 50)
        
        try:
            # Test with invalid reset code
            print("Testing reset code verification with invalid code...")
            verify_data = {
                'phone': '+27999999999',
                'reset_code': '123456'
            }
            
            response = requests.post(
                f"{self.backend_url}/api/auth/verify-reset-code",
                data=verify_data,
                timeout=30
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"Response Data: {json.dumps(response_data, indent=2)}")
                
                if response.status_code == 400:
                    self.log_result(
                        "Password Reset Verification - Invalid Code",
                        True,
                        f"Correctly returned 400 for invalid reset code. Message: {response_data.get('detail', 'No detail')}"
                    )
                else:
                    self.log_result(
                        "Password Reset Verification - Invalid Code",
                        False,
                        f"Expected 400 but got {response.status_code}",
                        f"Status: {response.status_code}, Data: {response_data}"
                    )
            except:
                print(f"Response Text: {response.text}")
                self.log_result(
                    "Password Reset Verification - Response Format",
                    False,
                    "Could not parse JSON response",
                    f"Status: {response.status_code}, Text: {response.text[:200]}"
                )
            
            # Test with missing fields
            print("\nTesting reset code verification with missing fields...")
            response = requests.post(
                f"{self.backend_url}/api/auth/verify-reset-code",
                data={'phone': '+27999999999'},  # Missing reset_code
                timeout=30
            )
            
            print(f"Response Status: {response.status_code}")
            try:
                response_data = response.json()
                print(f"Response Data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"Response Text: {response.text}")
            
            if response.status_code == 400:
                self.log_result(
                    "Password Reset Verification - Missing Fields",
                    True,
                    f"Correctly returned 400 for missing reset code. Response: {response.text[:200]}"
                )
            else:
                self.log_result(
                    "Password Reset Verification - Missing Fields",
                    False,
                    f"Expected 400 but got {response.status_code}",
                    f"Status: {response.status_code}, Response: {response.text[:200]}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                "Password Reset Verification - Network Connection",
                False,
                "Failed to connect to Heroku backend",
                f"Network error: {str(e)}"
            )
        except Exception as e:
            self.log_result(
                "Password Reset Verification - General Error",
                False,
                "Unexpected error during reset code verification test",
                f"Error: {str(e)}"
            )

    def test_database_schema_endpoints(self):
        """Test endpoints that reveal database schema information"""
        print("🗄️ TESTING DATABASE SCHEMA VERIFICATION")
        print("=" * 50)
        
        try:
            # Test health endpoint to see if it reveals database info
            print("Testing health endpoint...")
            response = requests.get(f"{self.backend_url}/api/health", timeout=30)
            
            print(f"Health Response Status: {response.status_code}")
            try:
                health_data = response.json()
                print(f"Health Data: {json.dumps(health_data, indent=2)}")
                
                if response.status_code == 200:
                    self.log_result(
                        "Database Schema - Health Check",
                        True,
                        f"Health endpoint accessible. Database status: {health_data.get('services', {}).get('database', 'unknown')}"
                    )
                else:
                    self.log_result(
                        "Database Schema - Health Check",
                        False,
                        f"Health endpoint returned {response.status_code}",
                        f"Response: {response.text[:200]}"
                    )
            except:
                print(f"Health Response Text: {response.text}")
                self.log_result(
                    "Database Schema - Health Check",
                    False,
                    "Could not parse health endpoint response",
                    f"Status: {response.status_code}, Text: {response.text[:200]}"
                )
                
        except Exception as e:
            self.log_result(
                "Database Schema - Health Check",
                False,
                "Failed to test health endpoint",
                f"Error: {str(e)}"
            )

    def test_existing_user_scenarios(self):
        """Test with known existing users from the system"""
        print("👤 TESTING WITH EXISTING USERS")
        print("=" * 50)
        
        # Test with known admin phone number
        known_phones = ['+27800000001', '+27800000002', '+27800000003']
        
        for phone in known_phones:
            try:
                print(f"\nTesting password reset with known phone: {phone}")
                reset_data = {'phone': phone}
                
                response = requests.post(
                    f"{self.backend_url}/api/auth/request-password-reset",
                    data=reset_data,
                    timeout=30
                )
                
                print(f"Response Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"Response Data: {json.dumps(response_data, indent=2)}")
                    
                    if response.status_code == 200 and response_data.get('success'):
                        dev_code = response_data.get('dev_code')
                        self.log_result(
                            f"Password Reset - Known User {phone}",
                            True,
                            f"Successfully generated reset code. Dev code: {dev_code}"
                        )
                        
                        # Test the verification with the dev code
                        if dev_code:
                            print(f"Testing verification with dev code: {dev_code}")
                            verify_response = requests.post(
                                f"{self.backend_url}/api/auth/verify-reset-code",
                                data={'phone': phone, 'reset_code': dev_code},
                                timeout=30
                            )
                            
                            print(f"Verify Response Status: {verify_response.status_code}")
                            try:
                                verify_data = verify_response.json()
                                print(f"Verify Data: {json.dumps(verify_data, indent=2)}")
                                
                                if verify_response.status_code == 200 and verify_data.get('success'):
                                    self.log_result(
                                        f"Password Reset Verification - Known User {phone}",
                                        True,
                                        f"Successfully verified reset code: {verify_data.get('message')}"
                                    )
                                else:
                                    self.log_result(
                                        f"Password Reset Verification - Known User {phone}",
                                        False,
                                        f"Failed to verify reset code",
                                        f"Status: {verify_response.status_code}, Data: {verify_data}"
                                    )
                            except:
                                print(f"Verify Response Text: {verify_response.text}")
                                self.log_result(
                                    f"Password Reset Verification - Known User {phone}",
                                    False,
                                    "Could not parse verification response",
                                    f"Status: {verify_response.status_code}, Text: {verify_response.text[:200]}"
                                )
                    else:
                        self.log_result(
                            f"Password Reset - Known User {phone}",
                            False,
                            f"Failed to generate reset code",
                            f"Status: {response.status_code}, Data: {response_data}"
                        )
                except:
                    print(f"Response Text: {response.text}")
                    self.log_result(
                        f"Password Reset - Known User {phone}",
                        False,
                        "Could not parse response",
                        f"Status: {response.status_code}, Text: {response.text[:200]}"
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Password Reset - Known User {phone}",
                    False,
                    "Error testing with known user",
                    f"Error: {str(e)}"
                )

    def run_all_tests(self):
        """Run all Heroku-specific tests"""
        print("🚀 STARTING HEROKU FIXER SIGNUP AND PASSWORD RESET TESTING")
        print("=" * 70)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print("=" * 70)
        
        # Run all test categories
        self.test_fixer_signup_heroku()
        self.test_password_reset_request_heroku()
        self.test_password_reset_verification_heroku()
        self.test_database_schema_endpoints()
        self.test_existing_user_scenarios()
        
        # Generate summary report
        self.generate_summary_report()

    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n" + "=" * 70)
        print("📊 HEROKU TESTING SUMMARY REPORT")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if self.errors_found:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED ({len(self.errors_found)}):")
            for i, error in enumerate(self.errors_found, 1):
                print(f"{i}. {error}")
        
        print(f"\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            print(f"   {result['details']}")
            if 'error' in result:
                print(f"   ERROR: {result['error']}")
        
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        if failed_tests == 0:
            print("✅ All tests passed - no critical issues detected")
        else:
            print("❌ Issues detected that need investigation:")
            print("1. Check if Heroku deployment has the latest backend code")
            print("2. Verify database tables exist (fixers, password_resets)")
            print("3. Check database connection and permissions")
            print("4. Verify environment variables are set correctly")
            print("5. Check if database schema matches local development")
        
        print(f"\n⏰ Test Completed: {datetime.now().isoformat()}")
        print("=" * 70)

if __name__ == "__main__":
    tester = HerokuFixerPasswordTester()
    tester.run_all_tests()