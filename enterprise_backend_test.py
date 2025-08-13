#!/usr/bin/env python3
"""
FixMate-SA Enterprise Portal Backend Testing
Comprehensive testing of Enterprise Portal API endpoints and functionality
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class EnterprisePortalTester:
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://auto-job-match-1.preview.emergentagent.com')
        self.api_base = f"{self.backend_url}/api"
        
        # Test configuration - using existing test credentials
        self.test_phone = "+27800000002"  # Client test account
        self.test_password = "client2024test"
        self.auth_token = None
        
        # Test results tracking
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        # Test data storage
        self.created_team_members = []
        self.created_locations = []
        self.created_bookings = []
        self.created_invoices = []
        
        print(f"🏢 Enterprise Portal Testing Initialized")
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
        print(f"{status} {test_name}")
        if details:
            print(f"    📝 {details}")
        if not success and response_data:
            print(f"    📊 Response: {response_data}")
        print()

    def authenticate(self) -> bool:
        """Authenticate with the backend to get auth token"""
        try:
            print("🔐 Authenticating with Enterprise Portal...")
            
            login_data = {
                "phone": self.test_phone,
                "password": self.test_password
            }
            
            response = requests.post(
                f"{self.api_base}/auth/login",
                json=login_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('token'):
                    self.auth_token = data['token']
                    user_info = data.get('user', {})
                    self.log_test_result(
                        "Authentication", 
                        True, 
                        f"Successfully authenticated as {user_info.get('role', 'unknown')} user",
                        {"token_received": True, "user_role": user_info.get('role')}
                    )
                    return True
                else:
                    self.log_test_result(
                        "Authentication", 
                        False, 
                        f"Login failed: {data.get('message', 'Unknown error')}",
                        data
                    )
                    return False
            else:
                self.log_test_result(
                    "Authentication", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Authentication", 
                False, 
                f"Authentication error: {str(e)}",
                {"error": str(e)}
            )
            return False

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}

    def test_enterprise_overview(self) -> bool:
        """Test GET /api/enterprise/overview endpoint"""
        try:
            print("📊 Testing Enterprise Overview endpoint...")
            
            response = requests.get(
                f"{self.api_base}/enterprise/overview",
                headers=self.get_auth_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    overview_data = data.get('data', {})
                    analytics = overview_data.get('analytics', {})
                    
                    # Check for required analytics fields
                    required_fields = ['monthly_spend', 'total_bookings', 'jobs_completed', 'cost_savings']
                    missing_fields = [field for field in required_fields if field not in analytics]
                    
                    if not missing_fields:
                        self.log_test_result(
                            "Enterprise Overview", 
                            True, 
                            f"Overview data retrieved successfully with analytics: {list(analytics.keys())}",
                            {"analytics_fields": list(analytics.keys()), "has_recent_bookings": 'recent_bookings' in overview_data}
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Enterprise Overview", 
                            False, 
                            f"Missing required analytics fields: {missing_fields}",
                            data
                        )
                        return False
                else:
                    self.log_test_result(
                        "Enterprise Overview", 
                        False, 
                        f"API returned success=false: {data.get('message', 'Unknown error')}",
                        data
                    )
                    return False
            else:
                self.log_test_result(
                    "Enterprise Overview", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Enterprise Overview", 
                False, 
                f"Overview test error: {str(e)}",
                {"error": str(e)}
            )
            return False

    def test_bulk_booking_creation(self) -> bool:
        """Test POST /api/enterprise/bulk-booking endpoint"""
        try:
            print("📅 Testing Bulk Booking Creation endpoint...")
            
            # Test data for bulk booking
            booking_data = {
                "services": ["Cleaning", "Maintenance", "Security"],
                "locations": ["Head Office - Cape Town", "Branch Office - Johannesburg"],
                "schedule_type": "weekly",
                "start_date": "2024-01-15",
                "end_date": "2024-12-31",
                "notes": "Enterprise cleaning and maintenance services for all locations"
            }
            
            response = requests.post(
                f"{self.api_base}/enterprise/bulk-booking",
                json=booking_data,
                headers=self.get_auth_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    booking_id = data.get('booking_id')
                    total_amount = data.get('total_amount')
                    
                    if booking_id and total_amount is not None:
                        self.created_bookings.append(booking_id)
                        self.log_test_result(
                            "Bulk Booking Creation", 
                            True, 
                            f"Bulk booking created successfully. ID: {booking_id}, Amount: R{total_amount}",
                            {"booking_id": booking_id, "total_amount": total_amount}
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Bulk Booking Creation", 
                            False, 
                            "Missing booking_id or total_amount in response",
                            data
                        )
                        return False
                else:
                    self.log_test_result(
                        "Bulk Booking Creation", 
                        False, 
                        f"Booking creation failed: {data.get('message', 'Unknown error')}",
                        data
                    )
                    return False
            else:
                self.log_test_result(
                    "Bulk Booking Creation", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code}
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Bulk Booking Creation", 
                False, 
                f"Bulk booking test error: {str(e)}",
                {"error": str(e)}
            )
            return False

    def test_team_management(self) -> bool:
        """Test team management endpoints (GET, POST, DELETE)"""
        success_count = 0
        total_team_tests = 3
        
        # Test 1: GET team members
        try:
            print("👥 Testing Get Team Members endpoint...")
            
            response = requests.get(
                f"{self.api_base}/enterprise/team",
                headers=self.get_auth_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    team_members = data.get('team_members', [])
                    self.log_test_result(
                        "Get Team Members", 
                        True, 
                        f"Retrieved {len(team_members)} team members",
                        {"team_count": len(team_members)}
                    )
                    success_count += 1
                else:
                    self.log_test_result(
                        "Get Team Members", 
                        False, 
                        f"Failed to get team members: {data.get('message', 'Unknown error')}",
                        data
                    )
            else:
                self.log_test_result(
                    "Get Team Members", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code}
                )
                
        except Exception as e:
            self.log_test_result(
                "Get Team Members", 
                False, 
                f"Get team members error: {str(e)}",
                {"error": str(e)}
            )

        # Test 2: POST add team member
        try:
            print("➕ Testing Add Team Member endpoint...")
            
            member_data = {
                "name": "Sarah Johnson",
                "email": "sarah.johnson@enterprise.com",
                "role": "Operations Manager",
                "permissions": ["view_bookings", "manage_locations", "generate_reports"]
            }
            
            response = requests.post(
                f"{self.api_base}/enterprise/team",
                json=member_data,
                headers=self.get_auth_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    member_id = data.get('member_id')
                    if member_id:
                        self.created_team_members.append(member_id)
                        self.log_test_result(
                            "Add Team Member", 
                            True, 
                            f"Team member added successfully. ID: {member_id}",
                            {"member_id": member_id, "name": member_data["name"]}
                        )
                        success_count += 1
                    else:
                        self.log_test_result(
                            "Add Team Member", 
                            False, 
                            "Missing member_id in response",
                            data
                        )
                else:
                    self.log_test_result(
                        "Add Team Member", 
                        False, 
                        f"Failed to add team member: {data.get('message', 'Unknown error')}",
                        data
                    )
            else:
                self.log_test_result(
                    "Add Team Member", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code}
                )
                
        except Exception as e:
            self.log_test_result(
                "Add Team Member", 
                False, 
                f"Add team member error: {str(e)}",
                {"error": str(e)}
            )

        # Test 3: DELETE team member (if we have one to delete)
        if self.created_team_members:
            try:
                print("🗑️ Testing Remove Team Member endpoint...")
                
                member_id = self.created_team_members[0]
                response = requests.delete(
                    f"{self.api_base}/enterprise/team/{member_id}",
                    headers=self.get_auth_headers(),
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        self.log_test_result(
                            "Remove Team Member", 
                            True, 
                            f"Team member removed successfully. ID: {member_id}",
                            {"removed_member_id": member_id}
                        )
                        success_count += 1
                        self.created_team_members.remove(member_id)
                    else:
                        self.log_test_result(
                            "Remove Team Member", 
                            False, 
                            f"Failed to remove team member: {data.get('message', 'Unknown error')}",
                            data
                        )
                else:
                    self.log_test_result(
                        "Remove Team Member", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}",
                        {"status_code": response.status_code}
                    )
                    
            except Exception as e:
                self.log_test_result(
                    "Remove Team Member", 
                    False, 
                    f"Remove team member error: {str(e)}",
                    {"error": str(e)}
                )
        else:
            self.log_test_result(
                "Remove Team Member", 
                False, 
                "No team member available to delete (add team member test failed)",
                {"reason": "no_member_to_delete"}
            )

        return success_count == total_team_tests

    def test_location_management(self) -> bool:
        """Test location management endpoints"""
        success_count = 0
        total_location_tests = 3
        
        # Test 1: GET locations
        try:
            print("📍 Testing Get Locations endpoint...")
            
            response = requests.get(
                f"{self.api_base}/enterprise/locations",
                headers=self.get_auth_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    locations = data.get('locations', [])
                    self.log_test_result(
                        "Get Locations", 
                        True, 
                        f"Retrieved {len(locations)} locations",
                        {"location_count": len(locations)}
                    )
                    success_count += 1
                else:
                    self.log_test_result(
                        "Get Locations", 
                        False, 
                        f"Failed to get locations: {data.get('message', 'Unknown error')}",
                        data
                    )
            else:
                self.log_test_result(
                    "Get Locations", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code}
                )
                
        except Exception as e:
            self.log_test_result(
                "Get Locations", 
                False, 
                f"Get locations error: {str(e)}",
                {"error": str(e)}
            )

        # Test 2: POST add location
        try:
            print("🏢 Testing Add Location endpoint...")
            
            location_data = {
                "name": "Enterprise Branch Office",
                "address": "123 Business District, Cape Town, 8001",
                "contact_person": "Mike Thompson",
                "contact_phone": "+27214567890",
                "services_needed": ["Cleaning", "IT Support", "Maintenance"]
            }
            
            response = requests.post(
                f"{self.api_base}/enterprise/locations",
                json=location_data,
                headers=self.get_auth_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    location_id = data.get('location_id')
                    if location_id:
                        self.created_locations.append(location_id)
                        self.log_test_result(
                            "Add Location", 
                            True, 
                            f"Location added successfully. ID: {location_id}",
                            {"location_id": location_id, "name": location_data["name"]}
                        )
                        success_count += 1
                    else:
                        self.log_test_result(
                            "Add Location", 
                            False, 
                            "Missing location_id in response",
                            data
                        )
                else:
                    self.log_test_result(
                        "Add Location", 
                        False, 
                        f"Failed to add location: {data.get('message', 'Unknown error')}",
                        data
                    )
            else:
                self.log_test_result(
                    "Add Location", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code}
                )
                
        except Exception as e:
            self.log_test_result(
                "Add Location", 
                False, 
                f"Add location error: {str(e)}",
                {"error": str(e)}
            )

        # Test 3: POST book service for location
        if self.created_locations:
            try:
                print("🔧 Testing Book Service for Location endpoint...")
                
                location_id = self.created_locations[0]
                response = requests.post(
                    f"{self.api_base}/enterprise/locations/{location_id}/book-service",
                    headers=self.get_auth_headers(),
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        job_id = data.get('job_id')
                        self.log_test_result(
                            "Book Service for Location", 
                            True, 
                            f"Service booked successfully for location. Job ID: {job_id}",
                            {"job_id": job_id, "location_id": location_id}
                        )
                        success_count += 1
                    else:
                        self.log_test_result(
                            "Book Service for Location", 
                            False, 
                            f"Failed to book service: {data.get('message', 'Unknown error')}",
                            data
                        )
                else:
                    self.log_test_result(
                        "Book Service for Location", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}",
                        {"status_code": response.status_code}
                    )
                    
            except Exception as e:
                self.log_test_result(
                    "Book Service for Location", 
                    False, 
                    f"Book service error: {str(e)}",
                    {"error": str(e)}
                )
        else:
            self.log_test_result(
                "Book Service for Location", 
                False, 
                "No location available to book service (add location test failed)",
                {"reason": "no_location_to_book"}
            )

        return success_count == total_location_tests

    def test_invoicing_system(self) -> bool:
        """Test invoicing system endpoints"""
        success_count = 0
        total_invoice_tests = 3
        
        # Test 1: GET invoices
        try:
            print("🧾 Testing Get Invoices endpoint...")
            
            response = requests.get(
                f"{self.api_base}/enterprise/invoices",
                headers=self.get_auth_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    invoices = data.get('invoices', [])
                    self.log_test_result(
                        "Get Invoices", 
                        True, 
                        f"Retrieved {len(invoices)} invoices",
                        {"invoice_count": len(invoices)}
                    )
                    success_count += 1
                else:
                    self.log_test_result(
                        "Get Invoices", 
                        False, 
                        f"Failed to get invoices: {data.get('message', 'Unknown error')}",
                        data
                    )
            else:
                self.log_test_result(
                    "Get Invoices", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code}
                )
                
        except Exception as e:
            self.log_test_result(
                "Get Invoices", 
                False, 
                f"Get invoices error: {str(e)}",
                {"error": str(e)}
            )

        # Test 2: POST generate invoice
        try:
            print("📄 Testing Generate Invoice endpoint...")
            
            response = requests.post(
                f"{self.api_base}/enterprise/generate-invoice",
                headers=self.get_auth_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    invoice_id = data.get('invoice_id')
                    invoice_data = data.get('invoice', {})
                    if invoice_id:
                        self.created_invoices.append(invoice_id)
                        self.log_test_result(
                            "Generate Invoice", 
                            True, 
                            f"Invoice generated successfully. ID: {invoice_id}, Total: R{invoice_data.get('total_amount', 0)}",
                            {"invoice_id": invoice_id, "invoice_data": invoice_data}
                        )
                        success_count += 1
                    else:
                        self.log_test_result(
                            "Generate Invoice", 
                            False, 
                            "Missing invoice_id in response",
                            data
                        )
                else:
                    # Check if it's because no unbilled bookings exist
                    message = data.get('message', '')
                    if 'No unbilled bookings found' in message:
                        self.log_test_result(
                            "Generate Invoice", 
                            True, 
                            "No unbilled bookings available for invoice generation (expected behavior)",
                            {"message": message}
                        )
                        success_count += 1
                    else:
                        self.log_test_result(
                            "Generate Invoice", 
                            False, 
                            f"Failed to generate invoice: {message}",
                            data
                        )
            else:
                self.log_test_result(
                    "Generate Invoice", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code}
                )
                
        except Exception as e:
            self.log_test_result(
                "Generate Invoice", 
                False, 
                f"Generate invoice error: {str(e)}",
                {"error": str(e)}
            )

        # Test 3: GET specific invoice (Note: This endpoint doesn't exist in the backend)
        # We'll test this to verify it returns 404 as expected
        try:
            print("🔍 Testing Get Specific Invoice endpoint...")
            
            # Try to get a non-existent invoice to test endpoint availability
            test_invoice_id = "inv_test_12345"
            response = requests.get(
                f"{self.api_base}/enterprise/invoice/{test_invoice_id}",
                headers=self.get_auth_headers(),
                timeout=30
            )
            
            # This endpoint is not implemented, so we expect 404
            if response.status_code == 404:
                self.log_test_result(
                    "Get Specific Invoice", 
                    False, 
                    "Endpoint not implemented (GET /api/enterprise/invoice/{invoice_id} returns 404)",
                    {"status_code": response.status_code, "note": "endpoint_not_implemented"}
                )
            else:
                # If it returns something else, that's unexpected
                self.log_test_result(
                    "Get Specific Invoice", 
                    False, 
                    f"Unexpected response: HTTP {response.status_code}",
                    {"status_code": response.status_code}
                )
                
        except Exception as e:
            self.log_test_result(
                "Get Specific Invoice", 
                False, 
                f"Get specific invoice error: {str(e)}",
                {"error": str(e)}
            )

        # For invoicing, we consider 2/3 success as acceptable since one endpoint is not implemented
        return success_count >= 2

    def test_authentication_requirements(self) -> bool:
        """Test that all endpoints require proper authentication"""
        print("🔒 Testing Authentication Requirements...")
        
        endpoints_to_test = [
            ("GET", "/enterprise/overview"),
            ("POST", "/enterprise/bulk-booking"),
            ("GET", "/enterprise/team"),
            ("POST", "/enterprise/team"),
            ("GET", "/enterprise/locations"),
            ("POST", "/enterprise/locations"),
            ("GET", "/enterprise/invoices"),
            ("POST", "/enterprise/generate-invoice")
        ]
        
        success_count = 0
        
        for method, endpoint in endpoints_to_test:
            try:
                # Test without authentication
                if method == "GET":
                    response = requests.get(f"{self.api_base}{endpoint}", timeout=30)
                else:
                    response = requests.post(f"{self.api_base}{endpoint}", json={}, timeout=30)
                
                # Should return 401 Unauthorized
                if response.status_code == 401:
                    success_count += 1
                else:
                    self.log_test_result(
                        f"Auth Required - {method} {endpoint}", 
                        False, 
                        f"Expected 401, got {response.status_code}",
                        {"status_code": response.status_code}
                    )
                    
            except Exception as e:
                self.log_test_result(
                    f"Auth Required - {method} {endpoint}", 
                    False, 
                    f"Error testing auth requirement: {str(e)}",
                    {"error": str(e)}
                )
        
        auth_success = success_count == len(endpoints_to_test)
        self.log_test_result(
            "Authentication Requirements", 
            auth_success, 
            f"Authentication required for {success_count}/{len(endpoints_to_test)} endpoints",
            {"protected_endpoints": success_count, "total_endpoints": len(endpoints_to_test)}
        )
        
        return auth_success

    def run_comprehensive_test(self):
        """Run all Enterprise Portal tests"""
        print("🚀 Starting Comprehensive Enterprise Portal Backend Testing")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with testing.")
            return self.generate_summary()
        
        # Step 2: Test authentication requirements
        self.test_authentication_requirements()
        
        # Step 3: Test Enterprise Overview
        self.test_enterprise_overview()
        
        # Step 4: Test Bulk Booking Management
        self.test_bulk_booking_creation()
        
        # Step 5: Test Team Management
        self.test_team_management()
        
        # Step 6: Test Location Management
        self.test_location_management()
        
        # Step 7: Test Invoicing System
        self.test_invoicing_system()
        
        # Generate final summary
        return self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("=" * 80)
        print("🏢 ENTERPRISE PORTAL BACKEND TESTING SUMMARY")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 Overall Results: {self.passed_tests}/{self.total_tests} tests passed ({success_rate:.1f}%)")
        print()
        
        # Group results by category
        categories = {
            "Authentication": [],
            "Enterprise Overview": [],
            "Bulk Booking": [],
            "Team Management": [],
            "Location Management": [],
            "Invoicing System": [],
            "Security": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Auth" in test_name or "auth" in test_name.lower():
                categories["Authentication"].append(result)
            elif "Overview" in test_name:
                categories["Enterprise Overview"].append(result)
            elif "Bulk" in test_name or "Booking" in test_name:
                categories["Bulk Booking"].append(result)
            elif "Team" in test_name:
                categories["Team Management"].append(result)
            elif "Location" in test_name:
                categories["Location Management"].append(result)
            elif "Invoice" in test_name:
                categories["Invoicing System"].append(result)
            else:
                categories["Security"].append(result)
        
        for category, results in categories.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                print(f"📋 {category}: {passed}/{total} tests passed")
                
                for result in results:
                    status = "✅" if result["success"] else "❌"
                    print(f"   {status} {result['test']}")
                    if result["details"]:
                        print(f"      📝 {result['details']}")
                print()
        
        # Critical Issues
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print("🚨 CRITICAL ISSUES FOUND:")
            for result in failed_tests:
                print(f"   ❌ {result['test']}: {result['details']}")
            print()
        
        # Missing Endpoints
        missing_endpoints = []
        for result in self.test_results:
            if "endpoint_not_implemented" in str(result.get("response_data", {})):
                missing_endpoints.append(result["test"])
        
        if missing_endpoints:
            print("⚠️ MISSING ENDPOINTS:")
            for endpoint in missing_endpoints:
                print(f"   🔍 {endpoint}")
            print()
        
        # Summary
        if success_rate >= 80:
            print("🎉 ENTERPRISE PORTAL BACKEND IS MOSTLY FUNCTIONAL!")
            print("   Most endpoints are working correctly with proper authentication.")
        elif success_rate >= 60:
            print("⚠️ ENTERPRISE PORTAL BACKEND HAS SOME ISSUES")
            print("   Core functionality works but some endpoints need attention.")
        else:
            print("❌ ENTERPRISE PORTAL BACKEND HAS MAJOR ISSUES")
            print("   Multiple critical endpoints are not working properly.")
        
        print("=" * 80)
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "success_rate": success_rate,
            "test_results": self.test_results,
            "critical_issues": [r["test"] for r in failed_tests],
            "missing_endpoints": missing_endpoints
        }

def main():
    """Main function to run Enterprise Portal backend tests"""
    tester = EnterprisePortalTester()
    return tester.run_comprehensive_test()

if __name__ == "__main__":
    main()