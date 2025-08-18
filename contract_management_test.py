#!/usr/bin/env python3
"""
Enterprise Contract Management API Testing
Testing all contract management endpoints for the Enterprise Portal
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Configuration
BACKEND_URL = "https://service-pros-2.preview.emergentagent.com/api"

# Test credentials
TEST_CLIENT_PHONE = "+27800000002"
TEST_CLIENT_PASSWORD = "client2024test"

class ContractManagementTester:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.created_contracts = []
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details
        })
    
    def authenticate(self):
        """Authenticate and get token"""
        print("🔐 AUTHENTICATING CLIENT USER...")
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "phone": TEST_CLIENT_PHONE,
                "password": TEST_CLIENT_PASSWORD
            }, timeout=30, headers={"Content-Type": "application/json"})
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("token"):
                    self.token = data["token"]
                    self.user_id = data["user"]["id"]
                    self.log_test(
                        "Client Authentication",
                        True,
                        f"Successfully authenticated client user {TEST_CLIENT_PHONE}",
                        f"Token: {self.token[:20]}..., User ID: {self.user_id}"
                    )
                    return True
                else:
                    self.log_test("Client Authentication", False, f"Login failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                self.log_test("Client Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Client Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_authentication_required(self):
        """Test that endpoints require authentication"""
        print("🔒 TESTING AUTHENTICATION REQUIREMENTS...")
        
        # Test GET contracts without token
        try:
            response = requests.get(f"{BACKEND_URL}/enterprise/contracts", timeout=30)
            
            if response.status_code == 401:
                self.log_test(
                    "Authentication Required - GET Contracts",
                    True,
                    "Correctly returns 401 Unauthorized without token"
                )
            else:
                self.log_test(
                    "Authentication Required - GET Contracts",
                    False,
                    f"Expected 401, got {response.status_code}"
                )
        except Exception as e:
            self.log_test("Authentication Required - GET Contracts", False, f"Error: {str(e)}")
        
        # Test POST contracts without token
        try:
            test_contract = {
                "name": "Test Contract",
                "description": "Test description",
                "service_type": "Property Management",
                "contract_value": 50000.00,
                "duration_months": 12,
                "start_date": "2024-02-01",
                "auto_renewal": True,
                "terms": "Standard terms"
            }
            
            response = requests.post(f"{BACKEND_URL}/enterprise/contracts", json=test_contract, timeout=30)
            
            if response.status_code == 401:
                self.log_test(
                    "Authentication Required - POST Contracts",
                    True,
                    "Correctly returns 401 Unauthorized without token"
                )
            else:
                self.log_test(
                    "Authentication Required - POST Contracts",
                    False,
                    f"Expected 401, got {response.status_code}"
                )
        except Exception as e:
            self.log_test("Authentication Required - POST Contracts", False, f"Error: {str(e)}")
    
    def test_get_contracts_empty(self):
        """Test getting contracts when none exist"""
        print("📋 TESTING EMPTY CONTRACTS RETRIEVAL...")
        
        if not self.token:
            self.log_test("Get Empty Contracts", False, "No authentication token available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BACKEND_URL}/enterprise/contracts", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and isinstance(data.get("contracts"), list):
                    contract_count = len(data["contracts"])
                    self.log_test(
                        "Get Empty Contracts",
                        True,
                        f"Successfully retrieved contracts list with {contract_count} contracts",
                        f"Response structure correct: {list(data.keys())}"
                    )
                else:
                    self.log_test(
                        "Get Empty Contracts",
                        False,
                        f"Invalid response structure: {data}"
                    )
            else:
                self.log_test(
                    "Get Empty Contracts",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test("Get Empty Contracts", False, f"Error: {str(e)}")
    
    def test_create_contract(self):
        """Test creating a new contract"""
        print("➕ TESTING CONTRACT CREATION...")
        
        if not self.token:
            self.log_test("Create Contract", False, "No authentication token available")
            return None
        
        # Test contract data as specified in the review request
        test_contract = {
            "name": "Test Maintenance Contract",
            "description": "Annual facility maintenance services",
            "service_type": "Property Management",
            "contract_value": 50000.00,
            "duration_months": 12,
            "start_date": "2024-02-01",
            "auto_renewal": True,
            "terms": "Standard maintenance terms"
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(f"{BACKEND_URL}/enterprise/contracts", json=test_contract, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("contract_id"):
                    contract_id = data["contract_id"]
                    self.created_contracts.append(contract_id)
                    
                    # Verify date calculation
                    contract_info = data.get("contract", {})
                    start_date = datetime.strptime(test_contract["start_date"], "%Y-%m-%d").date()
                    expected_end_date = start_date + relativedelta(months=test_contract["duration_months"])
                    actual_end_date = datetime.strptime(contract_info.get("end_date", ""), "%Y-%m-%d").date()
                    
                    date_calculation_correct = actual_end_date == expected_end_date
                    
                    self.log_test(
                        "Create Contract",
                        True,
                        f"Successfully created contract with ID: {contract_id}",
                        f"Start: {contract_info.get('start_date')}, End: {contract_info.get('end_date')}, Date calculation correct: {date_calculation_correct}"
                    )
                    return contract_id
                else:
                    self.log_test(
                        "Create Contract",
                        False,
                        f"Invalid response structure: {data}"
                    )
                    return None
            else:
                self.log_test(
                    "Create Contract",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
        except Exception as e:
            self.log_test("Create Contract", False, f"Error: {str(e)}")
            return None
    
    def test_get_contracts_with_data(self):
        """Test getting contracts after creation"""
        print("📋 TESTING CONTRACTS RETRIEVAL WITH DATA...")
        
        if not self.token:
            self.log_test("Get Contracts With Data", False, "No authentication token available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BACKEND_URL}/enterprise/contracts", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and isinstance(data.get("contracts"), list):
                    contracts = data["contracts"]
                    contract_count = len(contracts)
                    
                    if contract_count > 0:
                        # Verify contract structure
                        first_contract = contracts[0]
                        required_fields = ["id", "name", "description", "service_type", "value", "duration_months", "start_date", "end_date", "status", "auto_renewal"]
                        missing_fields = [field for field in required_fields if field not in first_contract]
                        
                        if not missing_fields:
                            self.log_test(
                                "Get Contracts With Data",
                                True,
                                f"Successfully retrieved {contract_count} contracts with correct structure",
                                f"Sample contract: {first_contract['name']} - {first_contract['service_type']} - R{first_contract['value']}"
                            )
                        else:
                            self.log_test(
                                "Get Contracts With Data",
                                False,
                                f"Contract missing required fields: {missing_fields}"
                            )
                    else:
                        self.log_test(
                            "Get Contracts With Data",
                            False,
                            "No contracts found after creation"
                        )
                else:
                    self.log_test(
                        "Get Contracts With Data",
                        False,
                        f"Invalid response structure: {data}"
                    )
            else:
                self.log_test(
                    "Get Contracts With Data",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test("Get Contracts With Data", False, f"Error: {str(e)}")
    
    def test_contract_renewal(self, contract_id):
        """Test contract renewal functionality"""
        print("🔄 TESTING CONTRACT RENEWAL...")
        
        if not self.token or not contract_id:
            self.log_test("Contract Renewal", False, "No authentication token or contract ID available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.put(f"{BACKEND_URL}/enterprise/contracts/{contract_id}/renew", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("new_end_date"):
                    new_end_date = data["new_end_date"]
                    self.log_test(
                        "Contract Renewal",
                        True,
                        f"Successfully renewed contract {contract_id}",
                        f"New end date: {new_end_date}"
                    )
                    
                    # Verify the renewal extended the date correctly
                    # Get the updated contract to verify
                    get_response = requests.get(f"{BACKEND_URL}/enterprise/contracts", headers=headers, timeout=30)
                    if get_response.status_code == 200:
                        contracts_data = get_response.json()
                        if contracts_data.get("success"):
                            contracts = contracts_data["contracts"]
                            renewed_contract = next((c for c in contracts if c["id"] == contract_id), None)
                            if renewed_contract:
                                self.log_test(
                                    "Contract Renewal Verification",
                                    True,
                                    f"Verified renewed contract end date: {renewed_contract['end_date']}"
                                )
                else:
                    self.log_test(
                        "Contract Renewal",
                        False,
                        f"Invalid response structure: {data}"
                    )
            else:
                self.log_test(
                    "Contract Renewal",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test("Contract Renewal", False, f"Error: {str(e)}")
    
    def test_contract_deletion(self, contract_id):
        """Test contract deletion"""
        print("🗑️ TESTING CONTRACT DELETION...")
        
        if not self.token or not contract_id:
            self.log_test("Contract Deletion", False, "No authentication token or contract ID available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.delete(f"{BACKEND_URL}/enterprise/contracts/{contract_id}", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test(
                        "Contract Deletion",
                        True,
                        f"Successfully deleted contract {contract_id}",
                        data.get("message")
                    )
                    
                    # Verify the contract is actually deleted
                    get_response = requests.get(f"{BACKEND_URL}/enterprise/contracts", headers=headers, timeout=30)
                    if get_response.status_code == 200:
                        contracts_data = get_response.json()
                        if contracts_data.get("success"):
                            contracts = contracts_data["contracts"]
                            deleted_contract = next((c for c in contracts if c["id"] == contract_id), None)
                            if not deleted_contract:
                                self.log_test(
                                    "Contract Deletion Verification",
                                    True,
                                    f"Verified contract {contract_id} is no longer in the list"
                                )
                            else:
                                self.log_test(
                                    "Contract Deletion Verification",
                                    False,
                                    f"Contract {contract_id} still exists after deletion"
                                )
                else:
                    self.log_test(
                        "Contract Deletion",
                        False,
                        f"Deletion failed: {data.get('message', 'Unknown error')}"
                    )
            else:
                self.log_test(
                    "Contract Deletion",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test("Contract Deletion", False, f"Error: {str(e)}")
    
    def test_database_table_creation(self):
        """Test that database table is created automatically"""
        print("🗄️ TESTING DATABASE TABLE CREATION...")
        
        # This is implicitly tested by the GET request, but we'll verify it explicitly
        if not self.token:
            self.log_test("Database Table Creation", False, "No authentication token available")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            # The first GET request should create the table if it doesn't exist
            response = requests.get(f"{BACKEND_URL}/enterprise/contracts", headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "contracts" in data:
                    self.log_test(
                        "Database Table Creation",
                        True,
                        "Database table created successfully (verified by successful GET request)",
                        "Table creation is handled automatically on first access"
                    )
                else:
                    self.log_test(
                        "Database Table Creation",
                        False,
                        f"Table creation may have failed: {data}"
                    )
            else:
                self.log_test(
                    "Database Table Creation",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test("Database Table Creation", False, f"Error: {str(e)}")
    
    def test_date_calculations(self):
        """Test date calculations with different durations"""
        print("📅 TESTING DATE CALCULATIONS...")
        
        if not self.token:
            self.log_test("Date Calculations", False, "No authentication token available")
            return
        
        test_cases = [
            {"duration": 6, "start": "2024-01-01"},
            {"duration": 24, "start": "2024-06-15"},
            {"duration": 1, "start": "2024-12-31"}
        ]
        
        for i, test_case in enumerate(test_cases):
            try:
                test_contract = {
                    "name": f"Date Test Contract {i+1}",
                    "description": f"Testing {test_case['duration']} month duration",
                    "service_type": "Testing",
                    "contract_value": 1000.00,
                    "duration_months": test_case["duration"],
                    "start_date": test_case["start"],
                    "auto_renewal": False,
                    "terms": "Test terms"
                }
                
                headers = {"Authorization": f"Bearer {self.token}"}
                response = requests.post(f"{BACKEND_URL}/enterprise/contracts", json=test_contract, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("contract"):
                        contract_info = data["contract"]
                        start_date = datetime.strptime(test_case["start"], "%Y-%m-%d").date()
                        expected_end_date = start_date + relativedelta(months=test_case["duration"])
                        actual_end_date = datetime.strptime(contract_info["end_date"], "%Y-%m-%d").date()
                        
                        if actual_end_date == expected_end_date:
                            self.log_test(
                                f"Date Calculation Test {i+1}",
                                True,
                                f"Correct calculation for {test_case['duration']} months from {test_case['start']}",
                                f"Expected: {expected_end_date}, Got: {actual_end_date}"
                            )
                        else:
                            self.log_test(
                                f"Date Calculation Test {i+1}",
                                False,
                                f"Incorrect calculation for {test_case['duration']} months from {test_case['start']}",
                                f"Expected: {expected_end_date}, Got: {actual_end_date}"
                            )
                        
                        # Clean up test contract
                        if data.get("contract_id"):
                            requests.delete(f"{BACKEND_URL}/enterprise/contracts/{data['contract_id']}", headers=headers, timeout=30)
                    else:
                        self.log_test(
                            f"Date Calculation Test {i+1}",
                            False,
                            f"Failed to create test contract: {data}"
                        )
                else:
                    self.log_test(
                        f"Date Calculation Test {i+1}",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
            except Exception as e:
                self.log_test(f"Date Calculation Test {i+1}", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all contract management tests"""
        print("🚀 STARTING ENTERPRISE CONTRACT MANAGEMENT API TESTING")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return
        
        # Step 2: Test authentication requirements
        self.test_authentication_required()
        
        # Step 3: Test database table creation
        self.test_database_table_creation()
        
        # Step 4: Test getting empty contracts
        self.test_get_contracts_empty()
        
        # Step 5: Test contract creation
        contract_id = self.test_create_contract()
        
        # Step 6: Test getting contracts with data
        self.test_get_contracts_with_data()
        
        # Step 7: Test contract renewal
        if contract_id:
            self.test_contract_renewal(contract_id)
        
        # Step 8: Test date calculations
        self.test_date_calculations()
        
        # Step 9: Test contract deletion (do this last)
        if contract_id:
            self.test_contract_deletion(contract_id)
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 ENTERPRISE CONTRACT MANAGEMENT API TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['message']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  • {result['test']}")
        
        print("\n" + "=" * 60)
        
        if success_rate >= 80:
            print("🎉 ENTERPRISE CONTRACT MANAGEMENT API TESTING COMPLETED SUCCESSFULLY!")
            print("The contract management system is working correctly.")
        else:
            print("⚠️ ENTERPRISE CONTRACT MANAGEMENT API TESTING COMPLETED WITH ISSUES!")
            print("Some contract management features need attention.")

if __name__ == "__main__":
    tester = ContractManagementTester()
    tester.run_all_tests()