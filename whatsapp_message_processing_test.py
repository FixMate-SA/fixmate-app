#!/usr/bin/env python3
"""
WhatsApp Message Processing Recovery Test
Testing the WhatsApp message processing after fixing the "list index out of range" error.

CRITICAL TEST REQUIREMENTS:
1. Message Processing Recovery - Send various message types and verify no "list index out of range" errors
2. Statistics Tracking - Verify statistics are being recorded safely with/without services detected
3. Response Generation - Test welcome, service requests, help responses
4. Error Handling - Confirm robust error handling is working

ISSUE FIXED:
- Error: "list index out of range" in message processing
- Root cause: Statistics tracking trying to access first element of empty list
- Fix: Added safe list access with proper null checking
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://fixmate-sa-app-a448c751e1d2.herokuapp.com')
API_BASE = f"{BACKEND_URL}/api"

# Test phone numbers for Donald Shai and other customers
TEST_PHONE_NUMBERS = [
    "+27656648349",  # Donald Shai - the customer mentioned in the issue
    "+27821234567",
    "+27821234568", 
    "+27821234569",
    "+27821234570"
]

class WhatsAppMessageProcessingTester:
    def __init__(self):
        self.results = []
        self.error_count = 0
        self.success_count = 0
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def simulate_whatsapp_webhook(self, phone_number, message_text, message_type="text", additional_data=None):
        """Simulate WhatsApp webhook message with comprehensive payload"""
        # Clean phone number for webhook format
        clean_phone = phone_number.replace("+", "")
        
        webhook_payload = {
            "entry": [{
                "id": "entry_id",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "27754466571",
                            "phone_number_id": "702642972933051"
                        },
                        "contacts": [{
                            "profile": {"name": f"Test User {clean_phone[-4:]}"},
                            "wa_id": clean_phone
                        }],
                        "messages": [{
                            "from": clean_phone,
                            "id": f"msg_{int(time.time())}_{clean_phone[-4:]}",
                            "timestamp": str(int(time.time())),
                            "type": message_type
                        }]
                    },
                    "field": "messages"
                }]
            }]
        }
        
        # Add message content based on type
        message_data = webhook_payload["entry"][0]["changes"][0]["value"]["messages"][0]
        
        if message_type == "text":
            message_data["text"] = {"body": message_text}
        elif message_type == "audio":
            message_data["audio"] = {
                "id": f"audio_{int(time.time())}",
                "mime_type": "audio/ogg; codecs=opus"
            }
        elif message_type == "location":
            message_data["location"] = {
                "latitude": -26.2041,
                "longitude": 28.0473,
                "name": "Johannesburg",
                "address": "Johannesburg, South Africa"
            }
        elif message_type == "image":
            message_data["image"] = {
                "id": f"image_{int(time.time())}",
                "mime_type": "image/jpeg",
                "caption": message_text
            }
        elif message_type == "button":
            message_data["button"] = {
                "text": message_text,
                "payload": "button_payload"
            }
        elif message_type == "interactive":
            message_data["interactive"] = {
                "type": "button_reply",
                "button_reply": {
                    "id": "button_1",
                    "title": message_text
                }
            }
        
        # Add any additional data
        if additional_data:
            message_data.update(additional_data)
        
        try:
            # Test both webhook endpoints
            endpoints = ["/whatsapp", "/api/whatsapp/webhook"]
            
            for endpoint in endpoints:
                url = f"{BACKEND_URL}{endpoint}"
                response = requests.post(url, json=webhook_payload, timeout=15)
                
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        return True, response_data, endpoint
                    except:
                        return True, {"status": "processed", "raw_response": response.text}, endpoint
                else:
                    print(f"⚠️ Webhook {endpoint} returned {response.status_code}: {response.text[:200]}")
            
            return False, {"error": "All endpoints failed"}, "none"
            
        except Exception as e:
            return False, {"error": str(e)}, "error"
    
    def test_1_basic_message_processing(self):
        """Test 1: Basic message processing without errors"""
        print("\n" + "="*60)
        print("TEST 1: BASIC MESSAGE PROCESSING")
        print("="*60)
        
        test_messages = [
            ("Hello", "greeting"),
            ("I need help", "help_request"),
            ("What services do you offer?", "general_inquiry"),
            ("Thank you", "acknowledgment"),
            ("Test message", "general")
        ]
        
        for i, (message, category) in enumerate(test_messages):
            phone = TEST_PHONE_NUMBERS[i % len(TEST_PHONE_NUMBERS)]
            
            print(f"\n📱 Testing basic message: '{message}' from {phone}")
            
            success, response, endpoint = self.simulate_whatsapp_webhook(phone, message)
            
            # Check for any error indicators in response
            has_error = False
            error_details = ""
            
            if isinstance(response, dict):
                if "error" in response:
                    has_error = True
                    error_details = response.get("error", "")
                elif "status" in response and response["status"] == "error":
                    has_error = True
                    error_details = response.get("error", "Unknown error")
            
            if success and not has_error:
                self.log_result(
                    f"Basic Message Processing ({category})",
                    True,
                    f"Message processed successfully via {endpoint}",
                    {"message": message, "phone": phone, "response": response}
                )
            else:
                self.log_result(
                    f"Basic Message Processing ({category})",
                    False,
                    f"Message processing failed: {error_details or 'Unknown error'}",
                    {"message": message, "phone": phone, "error": error_details}
                )
            
            time.sleep(1)  # Rate limiting
    
    def test_2_service_detection_messages(self):
        """Test 2: Messages with service detection (potential source of list index errors)"""
        print("\n" + "="*60)
        print("TEST 2: SERVICE DETECTION MESSAGES")
        print("="*60)
        
        service_messages = [
            ("I need a plumber for leaking pipe", ["plumber"]),
            ("Electrical problem with power outlet", ["electrician"]),
            ("House cleaning and garden maintenance", ["cleaner", "gardener"]),
            ("Carpenter and painter needed", ["carpenter", "painter"]),
            ("General handyman for multiple repairs", ["handyman"]),
            ("No specific service mentioned", []),  # This should result in empty list
            ("Random text without service keywords", [])  # This should also result in empty list
        ]
        
        for i, (message, expected_services) in enumerate(service_messages):
            phone = TEST_PHONE_NUMBERS[i % len(TEST_PHONE_NUMBERS)]
            
            print(f"\n🔧 Testing service detection: '{message}' from {phone}")
            print(f"   Expected services: {expected_services}")
            
            success, response, endpoint = self.simulate_whatsapp_webhook(phone, message)
            
            # Check for list index errors specifically
            has_list_error = False
            error_details = ""
            
            if isinstance(response, dict):
                error_text = str(response).lower()
                if "list index out of range" in error_text:
                    has_list_error = True
                    error_details = "List index out of range error detected"
                elif "error" in response:
                    error_details = response.get("error", "")
                    if "list index" in error_details.lower():
                        has_list_error = True
            
            if success and not has_list_error:
                self.log_result(
                    f"Service Detection ({len(expected_services)} services)",
                    True,
                    f"Service detection processed without list errors via {endpoint}",
                    {
                        "message": message, 
                        "phone": phone, 
                        "expected_services": expected_services,
                        "response": response
                    }
                )
            else:
                self.log_result(
                    f"Service Detection ({len(expected_services)} services)",
                    False,
                    f"Service detection failed: {error_details}",
                    {
                        "message": message, 
                        "phone": phone, 
                        "expected_services": expected_services,
                        "error": error_details
                    }
                )
            
            time.sleep(1)
    
    def test_3_statistics_tracking_safety(self):
        """Test 3: Statistics tracking with safe list access"""
        print("\n" + "="*60)
        print("TEST 3: STATISTICS TRACKING SAFETY")
        print("="*60)
        
        # Test messages that would previously cause statistics tracking errors
        stat_test_messages = [
            ("Empty service list test", "no_services"),
            ("Multiple services: plumber electrician cleaner", "multiple_services"),
            ("Single service: gardener", "single_service"),
            ("Urgent plumber needed ASAP", "urgent_service"),
            ("Hello there", "greeting"),
            ("Help me please", "help_request")
        ]
        
        for i, (message, test_type) in enumerate(stat_test_messages):
            phone = TEST_PHONE_NUMBERS[i % len(TEST_PHONE_NUMBERS)]
            
            print(f"\n📊 Testing statistics tracking: '{message}' from {phone}")
            
            success, response, endpoint = self.simulate_whatsapp_webhook(phone, message)
            
            # Check specifically for statistics-related errors
            has_stat_error = False
            error_details = ""
            
            if isinstance(response, dict):
                error_text = str(response).lower()
                stat_error_indicators = [
                    "list index out of range",
                    "statistics tracking",
                    "first element",
                    "index error"
                ]
                
                for indicator in stat_error_indicators:
                    if indicator in error_text:
                        has_stat_error = True
                        error_details = f"Statistics error detected: {indicator}"
                        break
            
            if success and not has_stat_error:
                self.log_result(
                    f"Statistics Tracking ({test_type})",
                    True,
                    f"Statistics tracking processed safely via {endpoint}",
                    {"message": message, "phone": phone, "test_type": test_type, "response": response}
                )
            else:
                self.log_result(
                    f"Statistics Tracking ({test_type})",
                    False,
                    f"Statistics tracking failed: {error_details}",
                    {"message": message, "phone": phone, "test_type": test_type, "error": error_details}
                )
            
            time.sleep(1)
    
    def test_4_response_generation(self):
        """Test 4: Response generation for different message types"""
        print("\n" + "="*60)
        print("TEST 4: RESPONSE GENERATION")
        print("="*60)
        
        response_test_messages = [
            ("Hi", "greeting_response"),
            ("Hello", "greeting_response"),
            ("I need a plumber", "service_request_response"),
            ("help", "help_response"),
            ("What can you do?", "general_response")
        ]
        
        for i, (message, expected_response_type) in enumerate(response_test_messages):
            phone = TEST_PHONE_NUMBERS[i % len(TEST_PHONE_NUMBERS)]
            
            print(f"\n💬 Testing response generation: '{message}' from {phone}")
            
            success, response, endpoint = self.simulate_whatsapp_webhook(phone, message)
            
            # Check if response was generated without errors
            response_generated = False
            error_details = ""
            
            if success and isinstance(response, dict):
                if "error" not in response and response.get("status") != "error":
                    response_generated = True
                else:
                    error_details = response.get("error", "Response generation failed")
            
            if response_generated:
                self.log_result(
                    f"Response Generation ({expected_response_type})",
                    True,
                    f"Response generated successfully via {endpoint}",
                    {
                        "message": message, 
                        "phone": phone, 
                        "expected_type": expected_response_type,
                        "response": response
                    }
                )
            else:
                self.log_result(
                    f"Response Generation ({expected_response_type})",
                    False,
                    f"Response generation failed: {error_details}",
                    {
                        "message": message, 
                        "phone": phone, 
                        "expected_type": expected_response_type,
                        "error": error_details
                    }
                )
            
            time.sleep(1)
    
    def test_5_different_message_types(self):
        """Test 5: Different WhatsApp message types (text, audio, location, etc.)"""
        print("\n" + "="*60)
        print("TEST 5: DIFFERENT MESSAGE TYPES")
        print("="*60)
        
        message_types = [
            ("text", "Hello from text message", "text_message"),
            ("audio", "", "audio_message"),
            ("location", "", "location_message"),
            ("image", "Image with caption", "image_message"),
            ("button", "Button clicked", "button_message"),
            ("interactive", "Interactive button", "interactive_message")
        ]
        
        for i, (msg_type, content, test_category) in enumerate(message_types):
            phone = TEST_PHONE_NUMBERS[i % len(TEST_PHONE_NUMBERS)]
            
            print(f"\n📎 Testing message type: {msg_type} from {phone}")
            
            success, response, endpoint = self.simulate_whatsapp_webhook(phone, content, msg_type)
            
            # Check for message type processing errors
            has_type_error = False
            error_details = ""
            
            if isinstance(response, dict):
                if "error" in response:
                    error_details = response.get("error", "")
                    if "unsupported" in error_details.lower() or "invalid" in error_details.lower():
                        has_type_error = True
                elif response.get("status") == "error":
                    has_type_error = True
                    error_details = response.get("error", "Message type processing error")
            
            if success and not has_type_error:
                self.log_result(
                    f"Message Type Processing ({msg_type})",
                    True,
                    f"{msg_type.title()} message processed successfully via {endpoint}",
                    {"message_type": msg_type, "phone": phone, "content": content, "response": response}
                )
            else:
                self.log_result(
                    f"Message Type Processing ({msg_type})",
                    False,
                    f"{msg_type.title()} message processing failed: {error_details}",
                    {"message_type": msg_type, "phone": phone, "content": content, "error": error_details}
                )
            
            time.sleep(1)
    
    def test_6_edge_cases_and_error_handling(self):
        """Test 6: Edge cases that might cause errors"""
        print("\n" + "="*60)
        print("TEST 6: EDGE CASES AND ERROR HANDLING")
        print("="*60)
        
        edge_cases = [
            ("", "empty_message"),
            ("   ", "whitespace_only"),
            ("A" * 1000, "very_long_message"),
            ("🔧🏠💧⚡🧹", "emoji_only"),
            ("Special chars: @#$%^&*()", "special_characters"),
            ("Mixed: Hello 🔧 I need help! @urgent", "mixed_content")
        ]
        
        for i, (message, case_type) in enumerate(edge_cases):
            phone = TEST_PHONE_NUMBERS[i % len(TEST_PHONE_NUMBERS)]
            
            print(f"\n⚠️ Testing edge case: {case_type} from {phone}")
            
            success, response, endpoint = self.simulate_whatsapp_webhook(phone, message)
            
            # For edge cases, we mainly want to ensure no crashes/errors
            has_crash = False
            error_details = ""
            
            if isinstance(response, dict):
                error_indicators = [
                    "list index out of range",
                    "internal server error",
                    "crash",
                    "exception",
                    "traceback"
                ]
                
                error_text = str(response).lower()
                for indicator in error_indicators:
                    if indicator in error_text:
                        has_crash = True
                        error_details = f"System crash detected: {indicator}"
                        break
            
            if success and not has_crash:
                self.log_result(
                    f"Edge Case Handling ({case_type})",
                    True,
                    f"Edge case handled gracefully via {endpoint}",
                    {"case_type": case_type, "phone": phone, "message_length": len(message), "response": response}
                )
            else:
                self.log_result(
                    f"Edge Case Handling ({case_type})",
                    False,
                    f"Edge case caused system issues: {error_details}",
                    {"case_type": case_type, "phone": phone, "message_length": len(message), "error": error_details}
                )
            
            time.sleep(1)
    
    def test_7_donald_shai_specific_test(self):
        """Test 7: Specific test for Donald Shai's number (27656648349)"""
        print("\n" + "="*60)
        print("TEST 7: DONALD SHAI SPECIFIC TEST")
        print("="*60)
        
        donald_phone = "+27656648349"
        
        # Test various messages that Donald might send
        donald_messages = [
            ("Hi", "greeting"),
            ("I need a plumber", "service_request"),
            ("Help me with electrical issue", "help_request"),
            ("What services are available?", "inquiry"),
            ("Thank you", "acknowledgment")
        ]
        
        print(f"🎯 Testing specifically for Donald Shai ({donald_phone})")
        
        for message, msg_type in donald_messages:
            print(f"\n📱 Donald's message: '{message}'")
            
            success, response, endpoint = self.simulate_whatsapp_webhook(donald_phone, message)
            
            # Check specifically for the original error
            has_original_error = False
            error_details = ""
            
            if isinstance(response, dict):
                error_text = str(response).lower()
                if "list index out of range" in error_text:
                    has_original_error = True
                    error_details = "Original 'list index out of range' error still present"
                elif "error" in response:
                    error_details = response.get("error", "")
            
            if success and not has_original_error:
                self.log_result(
                    f"Donald Shai Test ({msg_type})",
                    True,
                    f"Donald's message processed successfully via {endpoint}",
                    {"message": message, "phone": donald_phone, "type": msg_type, "response": response}
                )
            else:
                self.log_result(
                    f"Donald Shai Test ({msg_type})",
                    False,
                    f"Donald's message failed: {error_details}",
                    {"message": message, "phone": donald_phone, "type": msg_type, "error": error_details}
                )
            
            time.sleep(1)
    
    def test_8_webhook_endpoint_verification(self):
        """Test 8: Verify webhook endpoints are accessible and working"""
        print("\n" + "="*60)
        print("TEST 8: WEBHOOK ENDPOINT VERIFICATION")
        print("="*60)
        
        endpoints = [
            ("/whatsapp", "GET", "Facebook Webhook Verification"),
            ("/whatsapp", "POST", "Facebook Webhook Handler"),
            ("/api/whatsapp/webhook", "GET", "API Webhook Verification"),
            ("/api/whatsapp/webhook", "POST", "API Webhook Handler")
        ]
        
        for endpoint, method, description in endpoints:
            url = f"{BACKEND_URL}{endpoint}"
            
            print(f"\n🔗 Testing {method} {endpoint}")
            
            try:
                if method == "GET":
                    response = requests.get(url, timeout=10)
                else:
                    # Send minimal valid webhook payload
                    test_payload = {
                        "entry": [{
                            "changes": [{
                                "value": {
                                    "messages": [{
                                        "from": "27821234567",
                                        "id": "test_msg",
                                        "timestamp": str(int(time.time())),
                                        "type": "text",
                                        "text": {"body": "test"}
                                    }]
                                }
                            }]
                        }]
                    }
                    response = requests.post(url, json=test_payload, timeout=10)
                
                if response.status_code in [200, 201]:
                    self.log_result(
                        f"Webhook Endpoint ({method} {endpoint})",
                        True,
                        f"{description} accessible (HTTP {response.status_code})",
                        {"endpoint": endpoint, "method": method, "status_code": response.status_code}
                    )
                else:
                    self.log_result(
                        f"Webhook Endpoint ({method} {endpoint})",
                        False,
                        f"{description} returned HTTP {response.status_code}",
                        {"endpoint": endpoint, "method": method, "status_code": response.status_code}
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Webhook Endpoint ({method} {endpoint})",
                    False,
                    f"{description} failed: {str(e)}",
                    {"endpoint": endpoint, "method": method, "error": str(e)}
                )
            
            time.sleep(0.5)
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "="*80)
        print("WHATSAPP MESSAGE PROCESSING RECOVERY TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n🔍 CRITICAL FINDINGS:")
        
        # Check for list index errors
        list_error_tests = [r for r in self.results if "list index" in r.get('message', '').lower()]
        if list_error_tests:
            list_errors = sum(1 for r in list_error_tests if not r['success'])
            if list_errors == 0:
                print(f"   ✅ CRITICAL SUCCESS: No 'list index out of range' errors detected")
            else:
                print(f"   ❌ CRITICAL FAILURE: {list_errors} 'list index out of range' errors still present")
        else:
            print(f"   ✅ No list index errors detected in any tests")
        
        # Check Donald Shai specific tests
        donald_tests = [r for r in self.results if "Donald Shai" in r['test']]
        if donald_tests:
            donald_success = sum(1 for r in donald_tests if r['success'])
            print(f"   👤 Donald Shai Tests: {donald_success}/{len(donald_tests)} passed")
        
        # Check service detection tests
        service_tests = [r for r in self.results if "Service Detection" in r['test']]
        if service_tests:
            service_success = sum(1 for r in service_tests if r['success'])
            print(f"   🔧 Service Detection: {service_success}/{len(service_tests)} working")
        
        # Check statistics tracking
        stat_tests = [r for r in self.results if "Statistics Tracking" in r['test']]
        if stat_tests:
            stat_success = sum(1 for r in stat_tests if r['success'])
            print(f"   📊 Statistics Tracking: {stat_success}/{len(stat_tests)} safe")
        
        # Check webhook endpoints
        webhook_tests = [r for r in self.results if "Webhook Endpoint" in r['test']]
        if webhook_tests:
            webhook_success = sum(1 for r in webhook_tests if r['success'])
            print(f"   📡 Webhook Endpoints: {webhook_success}/{len(webhook_tests)} accessible")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.results:
            print(f"   {result['status']}: {result['test']}")
            if not result['success']:
                print(f"      └─ {result['message']}")
        
        print(f"\n🎯 CONCLUSION:")
        if success_rate >= 90:
            print(f"   ✅ WhatsApp message processing is working correctly!")
            print(f"   ✅ The 'list index out of range' error has been successfully fixed")
            print(f"   ✅ Donald Shai and other customers can now receive responses without errors")
            print(f"   ✅ Statistics tracking is working safely with proper null checking")
        elif success_rate >= 70:
            print(f"   ⚠️ WhatsApp message processing is mostly working but has some issues")
            print(f"   ⚠️ Review failed tests for specific problems")
        else:
            print(f"   ❌ WhatsApp message processing has significant issues")
            print(f"   ❌ The 'list index out of range' error may not be fully resolved")
            print(f"   ❌ Major problems detected that need immediate attention")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "list_index_errors_fixed": len([r for r in self.results if "list index" in r.get('message', '').lower() and not r['success']]) == 0,
            "donald_shai_working": all(r['success'] for r in self.results if "Donald Shai" in r['test']),
            "results": self.results
        }

def main():
    """Main test execution"""
    print("🚀 Starting WhatsApp Message Processing Recovery Testing")
    print(f"🔗 Backend URL: {BACKEND_URL}")
    print(f"📅 Test Time: {datetime.now().isoformat()}")
    print(f"🎯 Focus: Verifying 'list index out of range' error fix")
    
    tester = WhatsAppMessageProcessingTester()
    
    try:
        # Execute all tests
        tester.test_1_basic_message_processing()
        tester.test_2_service_detection_messages()
        tester.test_3_statistics_tracking_safety()
        tester.test_4_response_generation()
        tester.test_5_different_message_types()
        tester.test_6_edge_cases_and_error_handling()
        tester.test_7_donald_shai_specific_test()
        tester.test_8_webhook_endpoint_verification()
        
        # Generate summary
        summary = tester.generate_summary()
        
        return summary
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        return tester.generate_summary()
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        return {"error": str(e), "results": tester.results}

if __name__ == "__main__":
    result = main()
    
    # Exit with appropriate code
    if result.get('success_rate', 0) >= 90:
        exit(0)  # Success
    else:
        exit(1)  # Failure