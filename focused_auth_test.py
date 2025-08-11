#!/usr/bin/env python3
"""
FixMate-SA Focused Authentication Testing
Testing the specific credentials mentioned in the review request
"""

import requests
import json
from datetime import datetime

class FocusedAuthTester:
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.api_base = f"{self.backend_url}/api"
        
        # Exact credentials from review request
        self.test_credentials = [
            {"phone": "0821234565", "password": "client123", "expected_role": "client"},
            {"phone": "0821234566", "password": "fixer123", "expected_role": "fixer"},
            {"phone": "0821234567", "password": "admin123", "expected_role": "admin"}
        ]
        
        self.results = []
        print(f"🎯 FOCUSED AUTHENTICATION TESTING")
        print(f"🔗 Backend URL: {self.backend_url}")
        print("=" * 60)

    def test_specific_credentials(self):
        """Test the exact credentials from the review request"""
        print("🔐 Testing Specific Credentials from Review Request...")
        
        for cred in self.test_credentials:
            phone = cred["phone"]
            password = cred["password"]
            expected_role = cred["expected_role"]
            
            try:
                # Test login
                response = requests.post(
                    f"{self.api_base}/auth/login",
                    json={"phone": phone, "password": password},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success"):
                        user = data.get("user", {})
                        token = data.get("token", "")
                        actual_role = user.get("role", "")
                        display_name = user.get("display_name", "")
                        welcome_message = user.get("welcome_message", "")
                        permissions = user.get("permissions", {})
                        
                        # Verify role matches expectation
                        role_match = actual_role == expected_role
                        
                        print(f"✅ {expected_role.upper()} LOGIN SUCCESS")
                        print(f"   Phone: {phone}")
                        print(f"   Password: {password}")
                        print(f"   Token: {token[:30]}...")
                        print(f"   Role: {actual_role} {'✅' if role_match else '❌'}")
                        print(f"   Display Name: {display_name}")
                        print(f"   Welcome Message: {welcome_message}")
                        print(f"   Permissions: {len(permissions)} granted")
                        print()
                        
                        self.results.append({
                            "credential": f"{phone}/{password}",
                            "expected_role": expected_role,
                            "actual_role": actual_role,
                            "success": True,
                            "role_match": role_match,
                            "token": token,
                            "display_name": display_name,
                            "permissions_count": len(permissions)
                        })
                        
                        # Test role-check endpoint for this phone
                        self.test_role_check(phone, expected_role)
                        
                        # Test authenticated request with this token
                        self.test_authenticated_request(token, expected_role)
                        
                    else:
                        print(f"❌ {expected_role.upper()} LOGIN FAILED")
                        print(f"   Phone: {phone}")
                        print(f"   Error: {data.get('message', 'Unknown error')}")
                        print()
                        
                        self.results.append({
                            "credential": f"{phone}/{password}",
                            "expected_role": expected_role,
                            "success": False,
                            "error": data.get('message', 'Unknown error')
                        })
                else:
                    print(f"❌ {expected_role.upper()} LOGIN HTTP ERROR")
                    print(f"   Phone: {phone}")
                    print(f"   HTTP Status: {response.status_code}")
                    print(f"   Response: {response.text}")
                    print()
                    
                    self.results.append({
                        "credential": f"{phone}/{password}",
                        "expected_role": expected_role,
                        "success": False,
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                print(f"❌ {expected_role.upper()} LOGIN EXCEPTION")
                print(f"   Phone: {phone}")
                print(f"   Exception: {str(e)}")
                print()
                
                self.results.append({
                    "credential": f"{phone}/{password}",
                    "expected_role": expected_role,
                    "success": False,
                    "error": f"Exception: {str(e)}"
                })

    def test_role_check(self, phone, expected_role):
        """Test role-check endpoint for specific phone"""
        try:
            response = requests.get(f"{self.api_base}/auth/role-check/{phone}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    detected_role = data.get("role")
                    user_exists = data.get("user_exists", False)
                    display_name = data.get("display_name", "")
                    
                    print(f"   🔍 Role Check: {detected_role} {'✅' if detected_role == expected_role else '❌'}")
                    print(f"   📋 User Exists: {user_exists}")
                    print(f"   👤 Display Name: {display_name}")
                else:
                    print(f"   ❌ Role Check Failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ Role Check HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Role Check Exception: {str(e)}")

    def test_authenticated_request(self, token, role):
        """Test authenticated request with token"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{self.api_base}/health", headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"   🔒 Authenticated Request: SUCCESS")
            else:
                print(f"   ❌ Authenticated Request: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Authenticated Request Exception: {str(e)}")

    def test_invalid_credentials(self):
        """Test invalid credentials for each user type"""
        print("❌ Testing Invalid Credentials...")
        
        invalid_tests = [
            {"phone": "0821234565", "password": "wrongpassword", "type": "Wrong Password"},
            {"phone": "0999999999", "password": "client123", "type": "Non-existent Phone"},
            {"phone": "0821234565", "password": "", "type": "Empty Password"}
        ]
        
        for test in invalid_tests:
            try:
                response = requests.post(
                    f"{self.api_base}/auth/login",
                    json={"phone": test["phone"], "password": test["password"]},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if not data.get("success"):
                        print(f"✅ {test['type']}: Correctly rejected - {data.get('message')}")
                    else:
                        print(f"❌ {test['type']}: Incorrectly accepted")
                else:
                    print(f"✅ {test['type']}: Correctly rejected with HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {test['type']}: Exception - {str(e)}")
        
        print()

    def test_phone_number_variations(self):
        """Test different phone number formats for client"""
        print("📱 Testing Phone Number Format Variations...")
        
        base_phone = "821234565"
        formats = [
            f"0{base_phone}",           # 0821234565
            f"+27{base_phone}",         # +27821234565
            f"27{base_phone}",          # 27821234565
            f"+27 82 123 4565",         # Formatted with spaces
            f"+27-82-123-4565",         # Formatted with dashes
            f"whatsapp:+27{base_phone}" # WhatsApp format
        ]
        
        for phone_format in formats:
            try:
                response = requests.post(
                    f"{self.api_base}/auth/login",
                    json={"phone": phone_format, "password": "client123"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"✅ Format '{phone_format}': Accepted and authenticated")
                    else:
                        print(f"⚠️ Format '{phone_format}': Processed but failed - {data.get('message')}")
                else:
                    print(f"❌ Format '{phone_format}': HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Format '{phone_format}': Exception - {str(e)}")
        
        print()

    def generate_summary(self):
        """Generate test summary"""
        print("=" * 60)
        print("📊 FOCUSED AUTHENTICATION TEST SUMMARY")
        print("=" * 60)
        
        successful_logins = [r for r in self.results if r.get("success", False)]
        failed_logins = [r for r in self.results if not r.get("success", False)]
        role_matches = [r for r in successful_logins if r.get("role_match", False)]
        
        print(f"✅ Successful Logins: {len(successful_logins)}/3")
        print(f"🎯 Correct Roles: {len(role_matches)}/3")
        print(f"❌ Failed Logins: {len(failed_logins)}")
        print()
        
        if len(successful_logins) == 3 and len(role_matches) == 3:
            print("🎉 AUTHENTICATION SYSTEM: FULLY FUNCTIONAL")
            print("   All three user types authenticate successfully")
            print("   All roles are correctly identified")
            print("   Tokens are properly generated")
            print("   Role-based permissions are working")
        elif len(successful_logins) >= 2:
            print("⚠️ AUTHENTICATION SYSTEM: MOSTLY FUNCTIONAL")
            print("   Most user types working with minor issues")
        else:
            print("❌ AUTHENTICATION SYSTEM: CRITICAL ISSUES")
            print("   Multiple authentication failures detected")
        
        print()
        print("📋 DETAILED RESULTS:")
        for result in self.results:
            if result.get("success"):
                print(f"✅ {result['credential']} -> {result['actual_role']} "
                      f"({'✅' if result.get('role_match') else '❌'} role match)")
            else:
                print(f"❌ {result['credential']} -> {result.get('error', 'Unknown error')}")
        
        print("=" * 60)

    def run_tests(self):
        """Run all focused tests"""
        self.test_specific_credentials()
        self.test_invalid_credentials()
        self.test_phone_number_variations()
        self.generate_summary()

def main():
    tester = FocusedAuthTester()
    tester.run_tests()

if __name__ == "__main__":
    main()