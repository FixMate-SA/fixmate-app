#!/usr/bin/env python3
"""
FixMate-SA Backend Testing Suite - Fixer Signup and Password Reset
Testing newly added backend endpoints for fixer application and password reset functionality
"""

import requests
import json
import time
from datetime import datetime
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
BACKEND_URL = "https://fixmate-deploy-2.preview.emergentagent.com/api"
TEST_USER_ID = "c417ef19-cdb6-44ee-80aa-8128e0ff8e75"  # TestFixer user
TEST_PHONE = "+27800000003"  # TestFixer phone number

class FixerSignupPasswordResetTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.dev_reset_code = None
        
    def log_test(self, test_name, success, details, response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        print()

    def test_fixer_application_valid_data(self):
        """Test fixer application with valid form data"""
        try:
            url = f"{self.backend_url}/fixer/apply"
            
            # Valid fixer application data
            form_data = {
                'services_offered': 'Plumbing, Electrical, General Maintenance',
                'experience_years': '5',
                'why_fixer': 'I have extensive experience in home repairs and want to help people fix their problems quickly and efficiently.',
                'user_id': TEST_USER_ID,
                'qualifications': 'Certified Electrician, Plumbing License',
                'previous_work': 'Worked at ABC Repairs for 3 years, freelance handyman for 2 years'
            }
            
            response = requests.post(url, data=form_data, timeout=30, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test(
                        "Fixer Application - Valid Data",
                        True,
                        f"Fixer application submitted successfully. Fixer ID: {data.get('fixer_id')}",
                        data
                    )
                    return data.get('fixer_id')
                else:
                    self.log_test(
                        "Fixer Application - Valid Data",
                        False,
                        f"Application failed: {data.get('message', 'Unknown error')}",
                        data
                    )
            else:
                self.log_test(
                    "Fixer Application - Valid Data",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                
        except Exception as e:
            self.log_test(
                "Fixer Application - Valid Data",
                False,
                f"Request failed: {str(e)}"
            )
        
        return None

    def test_fixer_application_missing_fields(self):
        """Test fixer application with missing required fields"""
        try:
            url = f"{self.backend_url}/fixer/apply"
            
            # Missing required fields
            form_data = {
                'services_offered': 'Plumbing',
                'experience_years': '3',
                # Missing 'why_fixer' and 'user_id'
            }
            
            response = requests.post(url, data=form_data, timeout=30, verify=False)
            
            if response.status_code == 400:
                data = response.json()
                if 'Missing required field' in data.get('detail', ''):
                    self.log_test(
                        "Fixer Application - Missing Fields Validation",
                        True,
                        f"Correctly rejected missing fields: {data.get('detail')}",
                        data
                    )
                else:
                    self.log_test(
                        "Fixer Application - Missing Fields Validation",
                        False,
                        f"Wrong error message: {data.get('detail')}",
                        data
                    )
            else:
                self.log_test(
                    "Fixer Application - Missing Fields Validation",
                    False,
                    f"Expected HTTP 400, got {response.status_code}: {response.text}",
                    response.text
                )
                
        except Exception as e:
            self.log_test(
                "Fixer Application - Missing Fields Validation",
                False,
                f"Request failed: {str(e)}"
            )

    def test_fixer_application_duplicate_prevention(self):
        """Test duplicate fixer application prevention"""
        try:
            url = f"{self.backend_url}/fixer/apply"
            
            # Try to apply again with same user_id
            form_data = {
                'services_offered': 'Carpentry, Painting',
                'experience_years': '2',
                'why_fixer': 'Second application attempt',
                'user_id': TEST_USER_ID
            }
            
            response = requests.post(url, data=form_data, timeout=30, verify=False)
            
            if response.status_code == 400:
                data = response.json()
                if 'already exists' in data.get('detail', '').lower():
                    self.log_test(
                        "Fixer Application - Duplicate Prevention",
                        True,
                        f"Correctly prevented duplicate application: {data.get('detail')}",
                        data
                    )
                else:
                    self.log_test(
                        "Fixer Application - Duplicate Prevention",
                        False,
                        f"Wrong error message: {data.get('detail')}",
                        data
                    )
            else:
                self.log_test(
                    "Fixer Application - Duplicate Prevention",
                    False,
                    f"Expected HTTP 400, got {response.status_code}: {response.text}",
                    response.text
                )
                
        except Exception as e:
            self.log_test(
                "Fixer Application - Duplicate Prevention",
                False,
                f"Request failed: {str(e)}"
            )

    def test_password_reset_request_existing_user(self):
        """Test password reset request with existing phone number"""
        try:
            url = f"{self.backend_url}/auth/request-password-reset"
            
            form_data = {
                'phone': TEST_PHONE
            }
            
            response = requests.post(url, data=form_data, timeout=30, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('dev_code'):
                    self.dev_reset_code = data.get('dev_code')
                    self.log_test(
                        "Password Reset Request - Existing User",
                        True,
                        f"Reset code generated successfully. Dev code: {self.dev_reset_code}",
                        data
                    )
                else:
                    self.log_test(
                        "Password Reset Request - Existing User",
                        False,
                        f"No dev_code returned: {data}",
                        data
                    )
            else:
                self.log_test(
                    "Password Reset Request - Existing User",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                
        except Exception as e:
            self.log_test(
                "Password Reset Request - Existing User",
                False,
                f"Request failed: {str(e)}"
            )

    def test_password_reset_request_nonexistent_user(self):
        """Test password reset request with non-existing phone number"""
        try:
            url = f"{self.backend_url}/auth/request-password-reset"
            
            form_data = {
                'phone': '+27999999999'  # Non-existent phone
            }
            
            response = requests.post(url, data=form_data, timeout=30, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'registered' in data.get('message', ''):
                    self.log_test(
                        "Password Reset Request - Non-existent User",
                        True,
                        f"Correctly returned success for security: {data.get('message')}",
                        data
                    )
                else:
                    self.log_test(
                        "Password Reset Request - Non-existent User",
                        False,
                        f"Unexpected response: {data}",
                        data
                    )
            else:
                self.log_test(
                    "Password Reset Request - Non-existent User",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                
        except Exception as e:
            self.log_test(
                "Password Reset Request - Non-existent User",
                False,
                f"Request failed: {str(e)}"
            )

    def test_verify_reset_code_valid(self):
        """Test reset code verification with valid code"""
        if not self.dev_reset_code:
            self.log_test(
                "Verify Reset Code - Valid Code",
                False,
                "No dev_reset_code available from previous test"
            )
            return
            
        try:
            url = f"{self.backend_url}/auth/verify-reset-code"
            
            form_data = {
                'phone': TEST_PHONE,
                'reset_code': self.dev_reset_code
            }
            
            response = requests.post(url, data=form_data, timeout=30, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test(
                        "Verify Reset Code - Valid Code",
                        True,
                        f"Reset code verified successfully: {data.get('message')}",
                        data
                    )
                else:
                    self.log_test(
                        "Verify Reset Code - Valid Code",
                        False,
                        f"Verification failed: {data}",
                        data
                    )
            else:
                self.log_test(
                    "Verify Reset Code - Valid Code",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                
        except Exception as e:
            self.log_test(
                "Verify Reset Code - Valid Code",
                False,
                f"Request failed: {str(e)}"
            )

    def test_verify_reset_code_invalid(self):
        """Test reset code verification with invalid code"""
        try:
            url = f"{self.backend_url}/auth/verify-reset-code"
            
            form_data = {
                'phone': TEST_PHONE,
                'reset_code': '000000'  # Invalid code
            }
            
            response = requests.post(url, data=form_data, timeout=30, verify=False)
            
            if response.status_code == 400:
                data = response.json()
                if 'Invalid reset code' in data.get('detail', ''):
                    self.log_test(
                        "Verify Reset Code - Invalid Code",
                        True,
                        f"Correctly rejected invalid code: {data.get('detail')}",
                        data
                    )
                else:
                    self.log_test(
                        "Verify Reset Code - Invalid Code",
                        False,
                        f"Wrong error message: {data.get('detail')}",
                        data
                    )
            else:
                self.log_test(
                    "Verify Reset Code - Invalid Code",
                    False,
                    f"Expected HTTP 400, got {response.status_code}: {response.text}",
                    response.text
                )
                
        except Exception as e:
            self.log_test(
                "Verify Reset Code - Invalid Code",
                False,
                f"Request failed: {str(e)}"
            )

    def test_reset_password_valid(self):
        """Test password reset with valid data"""
        if not self.dev_reset_code:
            self.log_test(
                "Reset Password - Valid Data",
                False,
                "No dev_reset_code available from previous test"
            )
            return
            
        try:
            url = f"{self.backend_url}/auth/reset-password"
            
            form_data = {
                'phone': TEST_PHONE,
                'reset_code': self.dev_reset_code,
                'new_password': 'newpassword123'
            }
            
            response = requests.post(url, data=form_data, timeout=30, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test(
                        "Reset Password - Valid Data",
                        True,
                        f"Password reset successfully: {data.get('message')}",
                        data
                    )
                else:
                    self.log_test(
                        "Reset Password - Valid Data",
                        False,
                        f"Password reset failed: {data}",
                        data
                    )
            else:
                self.log_test(
                    "Reset Password - Valid Data",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                
        except Exception as e:
            self.log_test(
                "Reset Password - Valid Data",
                False,
                f"Request failed: {str(e)}"
            )

    def test_reset_password_short_password(self):
        """Test password reset with password too short"""
        try:
            # First get a new reset code
            reset_url = f"{self.backend_url}/auth/request-password-reset"
            reset_response = requests.post(reset_url, data={'phone': TEST_PHONE}, timeout=30, verify=False)
            
            if reset_response.status_code != 200:
                self.log_test(
                    "Reset Password - Short Password",
                    False,
                    "Could not get reset code for test"
                )
                return
                
            reset_data = reset_response.json()
            new_reset_code = reset_data.get('dev_code')
            
            if not new_reset_code:
                self.log_test(
                    "Reset Password - Short Password",
                    False,
                    "No dev_code in reset response"
                )
                return
            
            url = f"{self.backend_url}/auth/reset-password"
            
            form_data = {
                'phone': TEST_PHONE,
                'reset_code': new_reset_code,
                'new_password': '123'  # Too short
            }
            
            response = requests.post(url, data=form_data, timeout=30, verify=False)
            
            if response.status_code == 400:
                data = response.json()
                if 'at least 6 characters' in data.get('detail', ''):
                    self.log_test(
                        "Reset Password - Short Password",
                        True,
                        f"Correctly rejected short password: {data.get('detail')}",
                        data
                    )
                else:
                    self.log_test(
                        "Reset Password - Short Password",
                        False,
                        f"Wrong error message: {data.get('detail')}",
                        data
                    )
            else:
                self.log_test(
                    "Reset Password - Short Password",
                    False,
                    f"Expected HTTP 400, got {response.status_code}: {response.text}",
                    response.text
                )
                
        except Exception as e:
            self.log_test(
                "Reset Password - Short Password",
                False,
                f"Request failed: {str(e)}"
            )

    def test_password_updated_in_database(self):
        """Test that password is actually updated in database by trying to login"""
        try:
            # Try to login with the new password
            login_url = f"{self.backend_url}/auth/login"
            
            login_data = {
                'phone': TEST_PHONE,
                'password': 'newpassword123'  # The password we set in reset test
            }
            
            response = requests.post(login_url, json=login_data, timeout=30, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('token'):
                    self.log_test(
                        "Password Database Update Verification",
                        True,
                        f"Successfully logged in with new password. User: {data.get('user', {}).get('display_name', 'Unknown')}",
                        data
                    )
                else:
                    self.log_test(
                        "Password Database Update Verification",
                        False,
                        f"Login failed with new password: {data}",
                        data
                    )
            else:
                self.log_test(
                    "Password Database Update Verification",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.text
                )
                
        except Exception as e:
            self.log_test(
                "Password Database Update Verification",
                False,
                f"Request failed: {str(e)}"
            )

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting FixMate-SA Fixer Signup and Password Reset Backend Testing")
        print(f"🔗 Backend URL: {self.backend_url}")
        print(f"👤 Test User ID: {TEST_USER_ID}")
        print(f"📱 Test Phone: {TEST_PHONE}")
        print("=" * 80)
        print()
        
        # Fixer Application Tests
        print("🔧 FIXER APPLICATION ENDPOINT TESTS")
        print("-" * 40)
        self.test_fixer_application_valid_data()
        self.test_fixer_application_missing_fields()
        self.test_fixer_application_duplicate_prevention()
        
        print()
        print("🔐 PASSWORD RESET ENDPOINT TESTS")
        print("-" * 40)
        
        # Password Reset Tests
        self.test_password_reset_request_existing_user()
        self.test_password_reset_request_nonexistent_user()
        self.test_verify_reset_code_valid()
        self.test_verify_reset_code_invalid()
        self.test_reset_password_valid()
        self.test_reset_password_short_password()
        self.test_password_updated_in_database()
        
        # Summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['details']}")
            print()
        
        print("🎯 ENDPOINT TESTING RESULTS:")
        print()
        
        # Fixer Application Results
        fixer_tests = [r for r in self.test_results if 'Fixer Application' in r['test']]
        fixer_passed = sum(1 for r in fixer_tests if r['success'])
        print(f"🔧 POST /api/fixer/apply: {fixer_passed}/{len(fixer_tests)} tests passed")
        
        # Password Reset Results
        reset_tests = [r for r in self.test_results if 'Password Reset' in r['test'] or 'Verify Reset' in r['test'] or 'Reset Password' in r['test'] or 'Password Database' in r['test']]
        reset_passed = sum(1 for r in reset_tests if r['success'])
        print(f"🔐 Password Reset Endpoints: {reset_passed}/{len(reset_tests)} tests passed")
        
        print()
        print("✨ Testing completed!")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = FixerSignupPasswordResetTester()
    results = tester.run_all_tests()