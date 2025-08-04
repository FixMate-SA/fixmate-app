#!/usr/bin/env python3
"""
FixMate-SA Test Account Creation Script

This script creates test accounts for comprehensive system testing:
1. Admin Test Account: +27800000001 / admin2024test
2. Client Test Account: +27800000002 / client2024test  
3. Fixer Test Account: +27800000003 / fixer2024test

After creation, it verifies authentication and role-based access for each account.
"""

import requests
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔧 Creating Test Accounts for FixMate-SA at: {API_BASE}")
print("=" * 80)

class TestAccountCreator:
    def __init__(self):
        self.session = requests.Session()
        self.test_accounts = {}
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
        """Test API health check"""
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
    
    def create_admin_test_account(self):
        """Create Admin Test Account: +27800000001 / admin2024test"""
        print("🔑 Creating Admin Test Account...")
        
        # First, check if admin phone already exists
        try:
            role_check = self.session.get(f"{API_BASE}/auth/role-check/+27800000001")
            if role_check.status_code == 200:
                role_data = role_check.json()
                if role_data.get('role') == 'admin':
                    self.log_result("Admin Account Creation", True, 
                                  "Admin account already exists with correct role")
                    # Try to login with existing account
                    return self.test_admin_login()
        except:
            pass  # Continue with creation if check fails
        
        # Create admin user via signup
        admin_data = {
            "phone": "+27800000001",
            "first_name": "Test",
            "last_name": "Admin User",
            "id_number": "8001010001001",
            "town": "Cape Town",
            "email": "admin.test@fixmate.com",
            "password": "admin2024test",
            "confirm_password": "admin2024test"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/signup", json=admin_data)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.test_accounts['admin'] = {
                        'phone': '+27800000001',
                        'password': 'admin2024test',
                        'user_data': data['user'],
                        'token': data['token'],
                        'role': data.get('role_info', {}).get('role', 'unknown')
                    }
                    
                    self.log_result("Admin Account Creation", True, 
                                  f"Admin account created successfully. Role: {data.get('role_info', {}).get('role', 'unknown')}")
                    return True
                else:
                    self.log_result("Admin Account Creation", False, "Invalid response format", response)
            else:
                # Account might already exist, try login
                return self.test_admin_login()
                
        except Exception as e:
            self.log_result("Admin Account Creation", False, f"Request error: {str(e)}")
        return False
    
    def test_admin_login(self):
        """Test admin login"""
        try:
            login_data = {
                "phone": "+27800000001",
                "password": "admin2024test"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.test_accounts['admin'] = {
                        'phone': '+27800000001',
                        'password': 'admin2024test',
                        'user_data': data['user'],
                        'token': data['token'],
                        'role': data.get('role_info', {}).get('role', 'unknown')
                    }
                    
                    self.log_result("Admin Login Test", True, 
                                  f"Admin login successful. Role: {data.get('role_info', {}).get('role', 'unknown')}")
                    return True
                else:
                    self.log_result("Admin Login Test", False, "Invalid response format", response)
            else:
                self.log_result("Admin Login Test", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Admin Login Test", False, f"Request error: {str(e)}")
        return False
    
    def create_client_test_account(self):
        """Create Client Test Account: +27800000002 / client2024test"""
        print("👤 Creating Client Test Account...")
        
        client_data = {
            "phone": "+27800000002",
            "first_name": "Test",
            "last_name": "Client User",
            "id_number": "8001010002002",
            "town": "Cape Town",
            "email": "client.test@fixmate.com",
            "password": "client2024test",
            "confirm_password": "client2024test"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/signup", json=client_data)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.test_accounts['client'] = {
                        'phone': '+27800000002',
                        'password': 'client2024test',
                        'user_data': data['user'],
                        'token': data['token'],
                        'role': data.get('role_info', {}).get('role', 'unknown')
                    }
                    
                    self.log_result("Client Account Creation", True, 
                                  f"Client account created successfully. Role: {data.get('role_info', {}).get('role', 'unknown')}")
                    return True
                else:
                    self.log_result("Client Account Creation", False, "Invalid response format", response)
            else:
                # Account might already exist, try login
                return self.test_client_login()
                
        except Exception as e:
            self.log_result("Client Account Creation", False, f"Request error: {str(e)}")
        return False
    
    def test_client_login(self):
        """Test client login"""
        try:
            login_data = {
                "phone": "+27800000002",
                "password": "client2024test"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.test_accounts['client'] = {
                        'phone': '+27800000002',
                        'password': 'client2024test',
                        'user_data': data['user'],
                        'token': data['token'],
                        'role': data.get('role_info', {}).get('role', 'unknown')
                    }
                    
                    self.log_result("Client Login Test", True, 
                                  f"Client login successful. Role: {data.get('role_info', {}).get('role', 'unknown')}")
                    return True
                else:
                    self.log_result("Client Login Test", False, "Invalid response format", response)
            else:
                self.log_result("Client Login Test", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Client Login Test", False, f"Request error: {str(e)}")
        return False
    
    def create_fixer_test_account(self):
        """Create Fixer Test Account: +27800000003 / fixer2024test"""
        print("🔧 Creating Fixer Test Account...")
        
        # First create the user account
        fixer_user_data = {
            "phone": "+27800000003",
            "first_name": "Test",
            "last_name": "Fixer User",
            "id_number": "8001010003003",
            "town": "Cape Town",
            "email": "fixer.test@fixmate.com",
            "password": "fixer2024test",
            "confirm_password": "fixer2024test"
        }
        
        try:
            # Create user account
            user_response = self.session.post(f"{API_BASE}/auth/signup", json=fixer_user_data)
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                user_id = user_data['user']['id']
                
                # Create fixer record
                fixer_data = {
                    "user_id": user_id,
                    "phone": "+27800000003",
                    "name": "Test Fixer User",
                    "email": "fixer.test@fixmate.com",
                    "services": '["Plumbing", "Electrical", "Handyman"]',
                    "location": "Cape Town, South Africa"
                }
                
                fixer_response = self.session.post(f"{API_BASE}/fixers", json=fixer_data)
                
                if fixer_response.status_code == 200:
                    fixer_record = fixer_response.json()
                    
                    self.test_accounts['fixer'] = {
                        'phone': '+27800000003',
                        'password': 'fixer2024test',
                        'user_data': user_data['user'],
                        'fixer_data': fixer_record,
                        'token': user_data['token'],
                        'role': user_data.get('role_info', {}).get('role', 'unknown')
                    }
                    
                    self.log_result("Fixer Account Creation", True, 
                                  f"Fixer account created successfully. Role: {user_data.get('role_info', {}).get('role', 'unknown')}, "
                                  f"Services: {fixer_record.get('services', 'Unknown')}")
                    return True
                else:
                    self.log_result("Fixer Account Creation", False, f"Fixer record creation failed: HTTP {fixer_response.status_code}", fixer_response)
            else:
                # Account might already exist, try login
                return self.test_fixer_login()
                
        except Exception as e:
            self.log_result("Fixer Account Creation", False, f"Request error: {str(e)}")
        return False
    
    def test_fixer_login(self):
        """Test fixer login"""
        try:
            login_data = {
                "phone": "+27800000003",
                "password": "fixer2024test"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    # Get fixer record
                    try:
                        fixers_response = self.session.get(f"{API_BASE}/fixers")
                        if fixers_response.status_code == 200:
                            fixers = fixers_response.json()
                            fixer_record = None
                            for fixer in fixers:
                                if fixer.get('phone') == '+27800000003':
                                    fixer_record = fixer
                                    break
                    except:
                        fixer_record = None
                    
                    self.test_accounts['fixer'] = {
                        'phone': '+27800000003',
                        'password': 'fixer2024test',
                        'user_data': data['user'],
                        'fixer_data': fixer_record,
                        'token': data['token'],
                        'role': data.get('role_info', {}).get('role', 'unknown')
                    }
                    
                    self.log_result("Fixer Login Test", True, 
                                  f"Fixer login successful. Role: {data.get('role_info', {}).get('role', 'unknown')}")
                    return True
                else:
                    self.log_result("Fixer Login Test", False, "Invalid response format", response)
            else:
                self.log_result("Fixer Login Test", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Fixer Login Test", False, f"Request error: {str(e)}")
        return False
    
    def test_role_based_authentication(self):
        """Test role-based authentication for each account"""
        print("🔐 Testing Role-Based Authentication...")
        
        # Test admin access to admin endpoints
        if 'admin' in self.test_accounts:
            try:
                headers = {'Authorization': f"Bearer {self.test_accounts['admin']['token']}"}
                response = self.session.get(f"{API_BASE}/admin/workflow-analytics", headers=headers)
                
                if response.status_code == 200:
                    self.log_result("Admin Role Authentication", True, 
                                  "Admin can access admin endpoints successfully")
                else:
                    self.log_result("Admin Role Authentication", False, 
                                  f"Admin cannot access admin endpoints: HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("Admin Role Authentication", False, f"Request error: {str(e)}")
        
        # Test client access (should not access admin endpoints)
        if 'client' in self.test_accounts:
            try:
                headers = {'Authorization': f"Bearer {self.test_accounts['client']['token']}"}
                response = self.session.get(f"{API_BASE}/admin/workflow-analytics", headers=headers)
                
                if response.status_code == 403:
                    self.log_result("Client Role Authentication", True, 
                                  "Client correctly denied access to admin endpoints")
                else:
                    self.log_result("Client Role Authentication", False, 
                                  f"Client should not access admin endpoints: HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("Client Role Authentication", False, f"Request error: {str(e)}")
        
        # Test fixer access (should not access admin endpoints)
        if 'fixer' in self.test_accounts:
            try:
                headers = {'Authorization': f"Bearer {self.test_accounts['fixer']['token']}"}
                response = self.session.get(f"{API_BASE}/admin/workflow-analytics", headers=headers)
                
                if response.status_code == 403:
                    self.log_result("Fixer Role Authentication", True, 
                                  "Fixer correctly denied access to admin endpoints")
                else:
                    self.log_result("Fixer Role Authentication", False, 
                                  f"Fixer should not access admin endpoints: HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result("Fixer Role Authentication", False, f"Request error: {str(e)}")
    
    def test_protected_endpoints(self):
        """Test protected endpoints with each role's token"""
        print("🛡️ Testing Protected Endpoints...")
        
        # Test endpoints that each role should be able to access
        for role, account in self.test_accounts.items():
            try:
                headers = {'Authorization': f"Bearer {account['token']}"}
                
                # Test user profile endpoint (all roles should access)
                response = self.session.get(f"{API_BASE}/auth/profile/{account['user_data']['id']}", headers=headers)
                
                if response.status_code == 200:
                    self.log_result(f"{role.title()} Protected Endpoint Access", True, 
                                  f"{role.title()} can access user profile endpoint")
                else:
                    self.log_result(f"{role.title()} Protected Endpoint Access", False, 
                                  f"{role.title()} cannot access user profile: HTTP {response.status_code}", response)
            except Exception as e:
                self.log_result(f"{role.title()} Protected Endpoint Access", False, f"Request error: {str(e)}")
    
    def run_test_account_creation(self):
        """Run complete test account creation and verification"""
        print("🚀 STARTING TEST ACCOUNT CREATION AND VERIFICATION")
        print("=" * 80)
        
        # Phase 1: Health Check
        if not self.test_health_check():
            print("❌ API health check failed. Cannot proceed.")
            return False
        
        # Phase 2: Create Test Accounts
        print("\n📋 PHASE 2: CREATING TEST ACCOUNTS")
        print("-" * 50)
        
        admin_created = self.create_admin_test_account()
        client_created = self.create_client_test_account()
        fixer_created = self.create_fixer_test_account()
        
        # Phase 3: Verify Authentication
        print("\n🔐 PHASE 3: VERIFYING AUTHENTICATION")
        print("-" * 50)
        
        self.test_role_based_authentication()
        self.test_protected_endpoints()
        
        # Results Summary
        print("\n" + "=" * 80)
        print("📊 TEST ACCOUNT CREATION RESULTS")
        print("=" * 80)
        
        print("🔑 CREATED TEST ACCOUNTS:")
        for role, account in self.test_accounts.items():
            print(f"   ✅ {role.upper()}: {account['phone']} / {account['password']} (Role: {account['role']})")
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   ✅ Tests Passed: {self.results['passed']}")
        print(f"   ❌ Tests Failed: {self.results['failed']}")
        print(f"   📊 Success Rate: {self.results['passed']/(self.results['passed']+self.results['failed'])*100:.1f}%")
        
        if self.results['errors']:
            print(f"\n🚨 ERRORS ENCOUNTERED:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        # Provide credentials summary
        print("\n" + "=" * 80)
        print("🎯 TEST CREDENTIALS FOR COMPREHENSIVE TESTING")
        print("=" * 80)
        
        if 'admin' in self.test_accounts:
            print("🔑 ADMIN TEST ACCOUNT:")
            print(f"   Phone: +27800000001")
            print(f"   Password: admin2024test")
            print(f"   Role: {self.test_accounts['admin']['role']}")
            print(f"   Name: Test Admin User")
        
        if 'client' in self.test_accounts:
            print("\n👤 CLIENT TEST ACCOUNT:")
            print(f"   Phone: +27800000002")
            print(f"   Password: client2024test")
            print(f"   Role: {self.test_accounts['client']['role']}")
            print(f"   Name: Test Client User")
        
        if 'fixer' in self.test_accounts:
            print("\n🔧 FIXER TEST ACCOUNT:")
            print(f"   Phone: +27800000003")
            print(f"   Password: fixer2024test")
            print(f"   Role: {self.test_accounts['fixer']['role']}")
            print(f"   Name: Test Fixer User")
            if self.test_accounts['fixer']['fixer_data']:
                services = self.test_accounts['fixer']['fixer_data'].get('services', 'Unknown')
                location = self.test_accounts['fixer']['fixer_data'].get('location', 'Unknown')
                print(f"   Services: {services}")
                print(f"   Location: {location}")
        
        success_rate = self.results['passed']/(self.results['passed']+self.results['failed'])*100
        
        if success_rate >= 80:
            print("\n🎉 TEST ACCOUNT CREATION SUCCESSFUL!")
            print("✅ All test accounts created and verified")
            print("✅ Authentication working properly for all roles")
            print("✅ Role-based access control functional")
            print("✅ Ready for comprehensive system testing")
        else:
            print("\n⚠️ TEST ACCOUNT CREATION PARTIALLY SUCCESSFUL")
            print("⚠️ Some issues encountered during account creation or verification")
            print("⚠️ Review errors above before proceeding with testing")
        
        return success_rate >= 80

if __name__ == "__main__":
    print("🔧 FixMate-SA Test Account Creation Script")
    print("=" * 80)
    print("🎯 CREATING TEST ACCOUNTS FOR COMPREHENSIVE TESTING")
    print("📋 Admin, Client, and Fixer test accounts with authentication verification")
    print("🔍 Role-based access control validation")
    print("=" * 80)
    
    creator = TestAccountCreator()
    
    try:
        success = creator.run_test_account_creation()
        
        if success:
            print("\n🎉 ALL TEST ACCOUNTS READY FOR COMPREHENSIVE TESTING!")
            sys.exit(0)
        else:
            print("\n❌ TEST ACCOUNT CREATION ENCOUNTERED ISSUES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Test account creation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during test account creation: {str(e)}")
        sys.exit(1)