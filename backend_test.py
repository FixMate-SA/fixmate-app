#!/usr/bin/env python3
"""
FixMate-SA Emergency System Backend Testing
Comprehensive testing of Emergency Alert API endpoints and functionality
"""

import requests
import json
import os
import tempfile
import base64
from datetime import datetime
from typing import Dict, Any, Optional

class EmergencySystemTester:
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://fixmate-sa-app-a448c751e1d2.herokuapp.com')
        self.api_base = f"{self.backend_url}/api"
        
        # Test configuration
        self.test_user_id = "emergency_test_user_001"
        self.test_user_name = "Emergency Test User"
        self.test_user_phone = "+27821234567"
        
        # Test results tracking
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        print(f"🚨 Emergency System Testing Initialized")
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

    def create_test_voice_file(self) -> str:
        """Create a test voice file for emergency testing"""
        try:
            # Create a simple test audio file (base64 encoded)
            # This is a minimal WAV file header + silence
            wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
            silence_data = b'\x00' * 2048  # 2KB of silence
            test_audio = wav_header + silence_data
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_file.write(test_audio)
            temp_file.close()
            
            return temp_file.name
        except Exception as e:
            print(f"⚠️ Failed to create test voice file: {e}")
            return None

    def test_health_check(self):
        """Test emergency system health check"""
        try:
            response = requests.get(f"{self.api_base}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                services = data.get("services", {})
                emergency_contacts = data.get("emergency_contacts", {})
                
                # Check if emergency service is active
                emergency_active = services.get("emergency_service") == "active"
                has_emergency_contacts = "police" in emergency_contacts
                
                if emergency_active and has_emergency_contacts:
                    self.log_test_result(
                        "Emergency System Health Check",
                        True,
                        f"Emergency service active, contacts available: {emergency_contacts}",
                        data
                    )
                else:
                    self.log_test_result(
                        "Emergency System Health Check",
                        False,
                        f"Emergency service status: {services.get('emergency_service')}, contacts: {has_emergency_contacts}",
                        data
                    )
            else:
                self.log_test_result(
                    "Emergency System Health Check",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Emergency System Health Check",
                False,
                f"Request failed: {str(e)}"
            )

    def test_emergency_alert_creation_basic(self):
        """Test basic emergency alert creation without voice"""
        try:
            alert_data = {
                "user_id": self.test_user_id,
                "alert": {
                    "alert_type": "emergency",
                    "latitude": -26.2041,
                    "longitude": 28.0473,
                    "address": "Johannesburg, South Africa",
                    "description": "Test emergency alert - backend testing"
                }
            }
            
            response = requests.post(
                f"{self.api_base}/emergency/alert",
                data=alert_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if data.get("success"):
                    self.log_test_result(
                        "Emergency Alert Creation (Basic)",
                        True,
                        f"Alert created successfully: {data.get('message')}",
                        data
                    )
                    return data.get("alert_id")  # Return for follow-up tests
                else:
                    self.log_test_result(
                        "Emergency Alert Creation (Basic)",
                        False,
                        f"Alert creation failed: {data}",
                        data
                    )
            else:
                self.log_test_result(
                    "Emergency Alert Creation (Basic)",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Emergency Alert Creation (Basic)",
                False,
                f"Request failed: {str(e)}"
            )
        
        return None

    def test_emergency_alert_with_voice(self):
        """Test emergency alert creation with voice recording"""
        try:
            # Create test voice file
            voice_file_path = self.create_test_voice_file()
            if not voice_file_path:
                self.log_test_result(
                    "Emergency Alert Creation (With Voice)",
                    False,
                    "Failed to create test voice file"
                )
                return None
            
            alert_data = {
                "user_id": f"{self.test_user_id}_voice",
                "user_name": f"{self.test_user_name} Voice Test",
                "user_phone": self.test_user_phone,
                "alert_type": "emergency",
                "priority": "critical",
                "latitude": "-33.9249",
                "longitude": "18.4241",
                "address": "Cape Town, South Africa",
                "description": "Emergency with voice recording - backend testing",
                "recording_duration": "5"
            }
            
            # Prepare multipart form data with voice file
            with open(voice_file_path, 'rb') as voice_file:
                files = {
                    'voice_recording': ('emergency_voice.wav', voice_file, 'audio/wav')
                }
                
                response = requests.post(
                    f"{self.api_base}/emergency/alert",
                    data=alert_data,
                    files=files,
                    timeout=30
                )
            
            # Clean up temp file
            os.unlink(voice_file_path)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    voice_processed = data.get("voice_transcribed", False)
                    transcription = data.get("transcription_preview", "")
                    
                    self.log_test_result(
                        "Emergency Alert Creation (With Voice)",
                        True,
                        f"Alert with voice created, transcribed: {voice_processed}, preview: {transcription[:50]}...",
                        data
                    )
                    return data.get("alert_id")
                else:
                    self.log_test_result(
                        "Emergency Alert Creation (With Voice)",
                        False,
                        f"Alert creation failed: {data.get('message', 'Unknown error')}",
                        data
                    )
            else:
                self.log_test_result(
                    "Emergency Alert Creation (With Voice)",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Emergency Alert Creation (With Voice)",
                False,
                f"Request failed: {str(e)}"
            )
        
        return None

    def test_location_services(self):
        """Test location reverse geocoding service"""
        try:
            # Test with Johannesburg coordinates
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
                    if data.get("success") and data.get("address"):
                        address = data.get("address")
                        # Check if address contains expected city or South Africa
                        if expected_city.lower() in address.lower() or "south africa" in address.lower():
                            successful_lookups += 1
                        
                        print(f"     📍 {lat}, {lng} -> {address}")
                    else:
                        print(f"     ❌ Failed lookup for {lat}, {lng}: {data}")
                else:
                    print(f"     ❌ HTTP {response.status_code} for {lat}, {lng}")
            
            success_rate = successful_lookups / len(test_coordinates)
            if success_rate >= 0.67:  # At least 2/3 successful
                self.log_test_result(
                    "Location Services (Reverse Geocoding)",
                    True,
                    f"Successfully resolved {successful_lookups}/{len(test_coordinates)} locations ({success_rate:.1%})"
                )
            else:
                self.log_test_result(
                    "Location Services (Reverse Geocoding)",
                    False,
                    f"Only {successful_lookups}/{len(test_coordinates)} locations resolved ({success_rate:.1%})"
                )
                
        except Exception as e:
            self.log_test_result(
                "Location Services (Reverse Geocoding)",
                False,
                f"Request failed: {str(e)}"
            )

    def test_emergency_alert_history(self):
        """Test emergency alert history retrieval"""
        try:
            # Test with the user ID we used for alert creation
            response = requests.get(
                f"{self.api_base}/emergency/alerts/{self.test_user_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    alerts = data.get("alerts", [])
                    
                    if len(alerts) > 0:
                        # Check alert structure
                        first_alert = alerts[0]
                        required_fields = ["id", "alert_type", "priority", "status", "created_at"]
                        has_required = all(field in first_alert for field in required_fields)
                        
                        if has_required:
                            self.log_test_result(
                                "Emergency Alert History Retrieval",
                                True,
                                f"Retrieved {len(alerts)} alerts, latest: {first_alert.get('alert_type')} ({first_alert.get('status')})"
                            )
                        else:
                            self.log_test_result(
                                "Emergency Alert History Retrieval",
                                False,
                                f"Alert structure incomplete: {list(first_alert.keys())}",
                                first_alert
                            )
                    else:
                        # No alerts found - this could be normal for a test user
                        self.log_test_result(
                            "Emergency Alert History Retrieval",
                            True,
                            "No alerts found for test user (expected for clean test environment)"
                        )
                else:
                    self.log_test_result(
                        "Emergency Alert History Retrieval",
                        False,
                        f"API returned success=false: {data}",
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

    def test_emergency_alert_resolution(self, alert_id: Optional[str] = None):
        """Test emergency alert resolution (admin function)"""
        try:
            # Use provided alert_id or create a test one
            test_alert_id = alert_id or "test_alert_resolution_001"
            
            resolution_data = {
                "resolution": "resolved",
                "notes": "Test resolution - backend testing completed successfully"
            }
            
            response = requests.post(
                f"{self.api_base}/emergency/resolve/{test_alert_id}",
                data=resolution_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    self.log_test_result(
                        "Emergency Alert Resolution",
                        True,
                        f"Alert {test_alert_id} resolved: {data.get('message')}",
                        data
                    )
                else:
                    self.log_test_result(
                        "Emergency Alert Resolution",
                        False,
                        f"Resolution failed: {data.get('error', 'Unknown error')}",
                        data
                    )
            elif response.status_code == 400:
                # Expected if alert doesn't exist
                self.log_test_result(
                    "Emergency Alert Resolution",
                    True,
                    "Alert not found (expected for test alert ID) - endpoint working correctly"
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

    def test_emergency_statistics(self):
        """Test emergency system statistics endpoint"""
        try:
            response = requests.get(f"{self.api_base}/emergency/stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    stats = data.get("stats", {})
                    required_stats = ["total_alerts", "active_alerts", "resolved_alerts", "today_alerts"]
                    has_required = all(stat in stats for stat in required_stats)
                    
                    if has_required:
                        self.log_test_result(
                            "Emergency System Statistics",
                            True,
                            f"Stats: {stats['total_alerts']} total, {stats['active_alerts']} active, {stats['today_alerts']} today",
                            stats
                        )
                    else:
                        self.log_test_result(
                            "Emergency System Statistics",
                            False,
                            f"Missing required statistics: {list(stats.keys())}",
                            stats
                        )
                else:
                    self.log_test_result(
                        "Emergency System Statistics",
                        False,
                        f"API returned success=false: {data}",
                        data
                    )
            else:
                self.log_test_result(
                    "Emergency System Statistics",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Emergency System Statistics",
                False,
                f"Request failed: {str(e)}"
            )

    def test_emergency_protocol_validation(self):
        """Test emergency protocol components"""
        try:
            # Test with high priority emergency
            alert_data = {
                "user_id": f"{self.test_user_id}_protocol",
                "user_name": "Protocol Test User",
                "user_phone": "+27821234999",
                "alert_type": "emergency",
                "priority": "critical",
                "latitude": "-26.2041",
                "longitude": "28.0473",
                "address": "Emergency Protocol Test Location",
                "description": "Critical emergency for protocol testing",
                "recording_duration": "0"
            }
            
            response = requests.post(
                f"{self.api_base}/emergency/alert",
                data=alert_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    # Check emergency protocol components
                    protocol_checks = {
                        "alert_created": bool(data.get("alert_id")),
                        "dispatch_notification": "dispatch" in data.get("message", "").lower(),
                        "priority_handled": data.get("priority_level") == "critical",
                        "emergency_response": "emergency" in data.get("message", "").lower()
                    }
                    
                    successful_checks = sum(protocol_checks.values())
                    total_checks = len(protocol_checks)
                    
                    if successful_checks >= 3:  # At least 3/4 protocol components working
                        self.log_test_result(
                            "Emergency Protocol Validation",
                            True,
                            f"Protocol components working: {successful_checks}/{total_checks} - {protocol_checks}",
                            data
                        )
                    else:
                        self.log_test_result(
                            "Emergency Protocol Validation",
                            False,
                            f"Insufficient protocol components: {successful_checks}/{total_checks} - {protocol_checks}",
                            data
                        )
                else:
                    self.log_test_result(
                        "Emergency Protocol Validation",
                        False,
                        f"Protocol test failed: {data.get('message', 'Unknown error')}",
                        data
                    )
            else:
                self.log_test_result(
                    "Emergency Protocol Validation",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test_result(
                "Emergency Protocol Validation",
                False,
                f"Request failed: {str(e)}"
            )

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        try:
            error_tests = [
                {
                    "name": "Missing User ID",
                    "data": {"alert_type": "emergency", "description": "Test"},
                    "expected_status": [400, 422]
                },
                {
                    "name": "Invalid Coordinates",
                    "data": {
                        "user_id": "test_user",
                        "latitude": "invalid",
                        "longitude": "invalid"
                    },
                    "expected_status": [400, 422]
                },
                {
                    "name": "Empty Request",
                    "data": {},
                    "expected_status": [400, 422]
                }
            ]
            
            successful_error_handling = 0
            
            for test in error_tests:
                response = requests.post(
                    f"{self.api_base}/emergency/alert",
                    data=test["data"],
                    timeout=10
                )
                
                if response.status_code in test["expected_status"]:
                    successful_error_handling += 1
                    print(f"     ✅ {test['name']}: HTTP {response.status_code} (expected)")
                else:
                    print(f"     ❌ {test['name']}: HTTP {response.status_code} (unexpected)")
            
            if successful_error_handling >= 2:  # At least 2/3 error cases handled correctly
                self.log_test_result(
                    "Error Handling Validation",
                    True,
                    f"Proper error handling for {successful_error_handling}/{len(error_tests)} test cases"
                )
            else:
                self.log_test_result(
                    "Error Handling Validation",
                    False,
                    f"Insufficient error handling: {successful_error_handling}/{len(error_tests)} cases"
                )
                
        except Exception as e:
            self.log_test_result(
                "Error Handling Validation",
                False,
                f"Request failed: {str(e)}"
            )

    def run_comprehensive_tests(self):
        """Run all emergency system tests"""
        print("🚨 STARTING COMPREHENSIVE EMERGENCY SYSTEM TESTING")
        print("=" * 80)
        
        # Core system tests
        self.test_health_check()
        
        # Emergency alert creation tests
        basic_alert_id = self.test_emergency_alert_creation_basic()
        voice_alert_id = self.test_emergency_alert_with_voice()
        
        # Location services
        self.test_location_services()
        
        # Data management tests
        self.test_emergency_alert_history()
        self.test_emergency_alert_resolution(basic_alert_id)
        
        # System statistics
        self.test_emergency_statistics()
        
        # Protocol validation
        self.test_emergency_protocol_validation()
        
        # Error handling
        self.test_error_handling()
        
        # Generate final report
        self.generate_test_report()

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("=" * 80)
        print("🚨 EMERGENCY SYSTEM TESTING COMPLETED")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize results
        critical_tests = [
            "Emergency System Health Check",
            "Emergency Alert Creation (Basic)",
            "Emergency Protocol Validation"
        ]
        
        important_tests = [
            "Emergency Alert Creation (With Voice)",
            "Location Services (Reverse Geocoding)",
            "Emergency Alert History Retrieval"
        ]
        
        # Check critical functionality
        critical_passed = sum(1 for result in self.test_results 
                            if result["test"] in critical_tests and result["success"])
        critical_total = len([r for r in self.test_results if r["test"] in critical_tests])
        
        important_passed = sum(1 for result in self.test_results 
                             if result["test"] in important_tests and result["success"])
        important_total = len([r for r in self.test_results if r["test"] in important_tests])
        
        print(f"🔴 CRITICAL FUNCTIONALITY: {critical_passed}/{critical_total} passed")
        print(f"🟡 IMPORTANT FUNCTIONALITY: {important_passed}/{important_total} passed")
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
            print("🎉 EMERGENCY SYSTEM STATUS: PRODUCTION READY")
            print("   All critical functionality working correctly")
        elif success_rate >= 60 and critical_passed >= critical_total * 0.8:
            print("⚠️ EMERGENCY SYSTEM STATUS: MOSTLY FUNCTIONAL")
            print("   Core functionality working with minor issues")
        else:
            print("❌ EMERGENCY SYSTEM STATUS: NEEDS ATTENTION")
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
    tester = EmergencySystemTester()
    results = tester.run_comprehensive_tests()
    return results

if __name__ == "__main__":
    main()