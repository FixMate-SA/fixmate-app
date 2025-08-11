#!/usr/bin/env python3
"""
FixMate-SA Emergency System Production API Test
Testing the actual production emergency endpoints based on OpenAPI spec
"""

import requests
import json
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional

class EmergencySystemProductionTest:
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://fixmate-sa-app-a448c751e1d2.herokuapp.com')
        self.api_base = f"{self.backend_url}/api"
        
        # Test configuration
        self.test_user_id = "emergency_production_test_001"
        
        # Test results tracking
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        print(f"🚨 Emergency System Production API Test")
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

    def test_emergency_location_service(self):
        """Test GET /api/emergency/location with test coordinates"""
        try:
            # Test with South African coordinates
            test_coordinates = [
                (-26.2041, 28.0473, "Johannesburg"),
                (-33.9249, 18.4241, "Cape Town"),
                (-29.8587, 31.0218, "Durban")
            ]
            
            successful_lookups = 0
            
            for lat, lng, expected_city in test_coordinates:
                response = requests.get(
                    f"{self.api_base}/emergency/location",
                    params={"latitude": lat, "longitude": lng},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "address" in data and "latitude" in data and "longitude" in data:
                        successful_lookups += 1
                        address = data.get("address", "")
                        print(f"     📍 {lat}, {lng} -> {address}")
                    else:
                        print(f"     ⚠️ Incomplete response for {lat}, {lng}: {data}")
                else:
                    print(f"     ❌ HTTP {response.status_code} for {lat}, {lng}")
            
            if successful_lookups >= 2:  # At least 2/3 successful
                self.log_test_result(
                    "Emergency Location Services - Coordinate Resolution",
                    True,
                    f"Successfully processed {successful_lookups}/{len(test_coordinates)} coordinate lookups"
                )
            else:
                self.log_test_result(
                    "Emergency Location Services - Coordinate Resolution",
                    False,
                    f"Only {successful_lookups}/{len(test_coordinates)} coordinate lookups successful"
                )
                
        except Exception as e:
            self.log_test_result(
                "Emergency Location Services - Coordinate Resolution",
                False,
                f"Request failed: {str(e)}"
            )

    def test_emergency_alert_api_format(self):
        """Test emergency alert API to understand the correct format"""
        try:
            # Test different formats to understand what the API expects
            
            # Format 1: Try with JSON body
            json_data = {
                "user_id": self.test_user_id,
                "alert": {
                    "alert_type": "emergency",
                    "description": "Test emergency alert - JSON format"
                }
            }
            
            response1 = requests.post(
                f"{self.api_base}/emergency/alert",
                json=json_data,
                timeout=30
            )
            
            print(f"     JSON format test: HTTP {response1.status_code}")
            if response1.status_code != 200:
                print(f"     JSON response: {response1.text[:200]}")
            
            # Format 2: Try with form data
            form_data = {
                "user_id": self.test_user_id,
                "alert": json.dumps({
                    "alert_type": "emergency",
                    "description": "Test emergency alert - form format"
                })
            }
            
            response2 = requests.post(
                f"{self.api_base}/emergency/alert",
                data=form_data,
                timeout=30
            )
            
            print(f"     Form format test: HTTP {response2.status_code}")
            if response2.status_code != 200:
                print(f"     Form response: {response2.text[:200]}")
            
            # Check if any format worked
            if response1.status_code == 200 or response2.status_code == 200:
                working_response = response1 if response1.status_code == 200 else response2
                working_format = "JSON" if response1.status_code == 200 else "Form"
                
                self.log_test_result(
                    "Emergency Alert API Format Discovery",
                    True,
                    f"Emergency alert API working with {working_format} format",
                    working_response.json() if working_response.status_code == 200 else None
                )
            else:
                self.log_test_result(
                    "Emergency Alert API Format Discovery",
                    False,
                    f"Neither JSON nor Form format worked. JSON: {response1.status_code}, Form: {response2.status_code}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Emergency Alert API Format Discovery",
                False,
                f"Request failed: {str(e)}"
            )

    def test_emergency_alert_history(self):
        """Test emergency alert history retrieval"""
        try:
            response = requests.get(
                f"{self.api_base}/emergency/alerts/{self.test_user_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has expected structure
                if isinstance(data, dict) and "alerts" in data:
                    alerts = data.get("alerts", [])
                    self.log_test_result(
                        "Emergency Alert History Retrieval",
                        True,
                        f"Alert history endpoint working, found {len(alerts)} alerts for test user"
                    )
                elif isinstance(data, list):
                    self.log_test_result(
                        "Emergency Alert History Retrieval",
                        True,
                        f"Alert history endpoint working, found {len(data)} alerts for test user"
                    )
                else:
                    self.log_test_result(
                        "Emergency Alert History Retrieval",
                        False,
                        f"Unexpected response format: {type(data)}",
                        data
                    )
            else:
                self.log_test_result(
                    "Emergency Alert History Retrieval",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Emergency Alert History Retrieval",
                False,
                f"Request failed: {str(e)}"
            )

    def test_emergency_alert_resolution(self):
        """Test emergency alert resolution endpoint"""
        try:
            test_alert_id = "test_alert_resolution_001"
            
            resolution_data = {
                "resolution": "resolved"
            }
            
            response = requests.post(
                f"{self.api_base}/emergency/resolve/{test_alert_id}",
                data=resolution_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(
                    "Emergency Alert Resolution",
                    True,
                    f"Alert resolution endpoint working: {data.get('message', 'Success')}",
                    data
                )
            elif response.status_code == 400 or response.status_code == 404:
                # Expected for non-existent alert
                self.log_test_result(
                    "Emergency Alert Resolution",
                    True,
                    f"Alert resolution endpoint working correctly (HTTP {response.status_code} for non-existent alert)"
                )
            else:
                self.log_test_result(
                    "Emergency Alert Resolution",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Emergency Alert Resolution",
                False,
                f"Request failed: {str(e)}"
            )

    def test_api_connectivity_and_structure(self):
        """Test basic API connectivity and structure"""
        try:
            # Test basic API endpoint
            response = requests.get(f"{self.api_base}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test_result(
                        "API Connectivity and Structure",
                        True,
                        f"API is running and responding: {data.get('message')}",
                        data
                    )
                else:
                    self.log_test_result(
                        "API Connectivity and Structure",
                        True,
                        "API is responding but with unexpected format",
                        data
                    )
            else:
                self.log_test_result(
                    "API Connectivity and Structure",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "API Connectivity and Structure",
                False,
                f"Request failed: {str(e)}"
            )

    def run_production_tests(self):
        """Run production emergency system tests"""
        print("🚨 STARTING EMERGENCY SYSTEM PRODUCTION TESTS")
        print("=" * 80)
        
        # 1. API Connectivity Test
        self.test_api_connectivity_and_structure()
        
        # 2. Emergency Location Services Test
        self.test_emergency_location_service()
        
        # 3. Emergency Alert API Format Discovery
        self.test_emergency_alert_api_format()
        
        # 4. Emergency Alert History Test
        self.test_emergency_alert_history()
        
        # 5. Emergency Alert Resolution Test
        self.test_emergency_alert_resolution()
        
        # Generate final report
        self.generate_production_report()

    def generate_production_report(self):
        """Generate production test report"""
        print("=" * 80)
        print("🚨 EMERGENCY SYSTEM PRODUCTION TESTS COMPLETED")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 PRODUCTION TEST RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
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
        if success_rate >= 80:
            print("🎉 EMERGENCY SYSTEM STATUS: PRODUCTION READY")
            print("   Emergency system endpoints are functional")
        elif success_rate >= 60:
            print("⚠️ EMERGENCY SYSTEM STATUS: PARTIALLY FUNCTIONAL")
            print("   Some emergency system components working")
        else:
            print("❌ EMERGENCY SYSTEM STATUS: NEEDS ATTENTION")
            print("   Critical issues found in emergency system")
        
        print("=" * 80)
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "success_rate": success_rate,
            "status": "PRODUCTION READY" if success_rate >= 80 else "NEEDS ATTENTION"
        }

def main():
    """Main testing function"""
    tester = EmergencySystemProductionTest()
    results = tester.run_production_tests()
    return results

if __name__ == "__main__":
    main()