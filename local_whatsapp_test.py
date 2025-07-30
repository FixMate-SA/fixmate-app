#!/usr/bin/env python3
"""
Local WhatsApp Webhook Endpoints Testing Script
Tests the WhatsApp webhook endpoints locally to verify they work correctly.
"""

import requests
import json
import sys

# Test locally
BACKEND_URL = "http://localhost:8001"

print(f"🔧 Testing WhatsApp Webhook Endpoints locally at: {BACKEND_URL}")
print("=" * 80)
print("🎯 LOCAL WHATSAPP WEBHOOK TESTING")
print("=" * 80)

class LocalWhatsAppWebhookTester:
    def __init__(self):
        self.session = requests.Session()
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
    
    def test_whatsapp_webhook_get_facebook_verification(self):
        """Test GET /whatsapp endpoint for Facebook webhook verification"""
        try:
            # Test with Facebook verification parameters
            params = {
                'hub.mode': 'subscribe',
                'hub.challenge': 'test_challenge_12345',
                'hub.verify_token': 'test_verify_token'
            }
            response = self.session.get(f"{BACKEND_URL}/whatsapp", params=params)
            
            if response.status_code == 200:
                # Should return the challenge as plain text
                if response.text == 'test_challenge_12345':
                    self.log_result("WhatsApp GET /whatsapp - Facebook Verification", True, "Facebook webhook verification successful - returned challenge")
                    return True
                else:
                    self.log_result("WhatsApp GET /whatsapp - Facebook Verification", False, f"Expected challenge but got: {response.text}", response)
            else:
                self.log_result("WhatsApp GET /whatsapp - Facebook Verification", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("WhatsApp GET /whatsapp - Facebook Verification", False, f"Request error: {str(e)}")
        return False
    
    def test_whatsapp_webhook_get_without_params(self):
        """Test GET /whatsapp endpoint without Facebook parameters"""
        try:
            response = self.session.get(f"{BACKEND_URL}/whatsapp")
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data and "message" in data:
                    self.log_result("WhatsApp GET /whatsapp - No Params", True, f"Endpoint accessible: {data['message']}")
                    return True
                else:
                    self.log_result("WhatsApp GET /whatsapp - No Params", False, "Invalid response format", response)
            else:
                self.log_result("WhatsApp GET /whatsapp - No Params", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("WhatsApp GET /whatsapp - No Params", False, f"Request error: {str(e)}")
        return False
    
    def test_whatsapp_webhook_post_facebook_message(self):
        """Test POST /whatsapp endpoint for Facebook WhatsApp messages"""
        try:
            # Simulate a Facebook WhatsApp webhook message
            facebook_webhook_data = {
                "object": "whatsapp_business_account",
                "entry": [{
                    "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                    "changes": [{
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "27754466571",
                                "phone_number_id": "782642972933851"
                            },
                            "contacts": [{
                                "profile": {
                                    "name": "Test User"
                                },
                                "wa_id": "27821234567"
                            }],
                            "messages": [{
                                "from": "27821234567",
                                "id": "wamid.test123",
                                "timestamp": "1234567890",
                                "type": "text",
                                "text": {
                                    "body": "hello"
                                }
                            }]
                        },
                        "field": "messages"
                    }]
                }]
            }
            
            response = self.session.post(f"{BACKEND_URL}/whatsapp", json=facebook_webhook_data)
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data or "status" in data:
                    self.log_result("WhatsApp POST /whatsapp - Facebook Message", True, f"Facebook webhook message processed successfully")
                    return True
                else:
                    self.log_result("WhatsApp POST /whatsapp - Facebook Message", False, "Invalid response format", response)
            else:
                self.log_result("WhatsApp POST /whatsapp - Facebook Message", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("WhatsApp POST /whatsapp - Facebook Message", False, f"Request error: {str(e)}")
        return False
    
    def test_whatsapp_webhook_post_unified_system(self):
        """Test POST /whatsapp endpoint with unified WhatsApp system"""
        try:
            # Test the unified WhatsApp system integration
            unified_webhook_data = {
                "entry": [{
                    "changes": [{
                        "value": {
                            "messages": [{
                                "from": "27821234567",
                                "type": "text",
                                "text": {"body": "I need help with plumbing"}
                            }]
                        }
                    }]
                }]
            }
            
            response = self.session.post(f"{BACKEND_URL}/whatsapp", json=unified_webhook_data)
            
            if response.status_code == 200:
                data = response.json()
                # The unified system should process the message
                if "success" in data or "status" in data:
                    self.log_result("WhatsApp POST /whatsapp - Unified System", True, "Unified WhatsApp system processed message successfully")
                    return True
                else:
                    self.log_result("WhatsApp POST /whatsapp - Unified System", False, "Invalid response format", response)
            else:
                self.log_result("WhatsApp POST /whatsapp - Unified System", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("WhatsApp POST /whatsapp - Unified System", False, f"Request error: {str(e)}")
        return False
    
    def test_whatsapp_webhook_405_error_resolution(self):
        """Test that 405 Method Not Allowed errors are resolved"""
        try:
            # Test that both GET and POST methods are now allowed
            get_response = self.session.get(f"{BACKEND_URL}/whatsapp")
            post_response = self.session.post(f"{BACKEND_URL}/whatsapp", json={"test": "data"})
            
            get_success = get_response.status_code != 405
            post_success = post_response.status_code != 405
            
            if get_success and post_success:
                self.log_result("WhatsApp 405 Error Resolution", True, f"Both GET ({get_response.status_code}) and POST ({post_response.status_code}) methods allowed - 405 errors resolved")
                return True
            else:
                error_methods = []
                if not get_success:
                    error_methods.append(f"GET: {get_response.status_code}")
                if not post_success:
                    error_methods.append(f"POST: {post_response.status_code}")
                self.log_result("WhatsApp 405 Error Resolution", False, f"405 errors still present for: {', '.join(error_methods)}")
        except Exception as e:
            self.log_result("WhatsApp 405 Error Resolution", False, f"Request error: {str(e)}")
        return False
    
    def test_whatsapp_webhook_unified_service_integration(self):
        """Test unified WhatsApp service integration"""
        try:
            # Test that the unified service is properly integrated
            test_message = {
                "entry": [{
                    "changes": [{
                        "value": {
                            "messages": [{
                                "from": "27821234567",
                                "type": "text",
                                "text": {"body": "test unified service"}
                            }]
                        }
                    }]
                }]
            }
            
            response = self.session.post(f"{BACKEND_URL}/whatsapp", json=test_message)
            
            if response.status_code == 200:
                data = response.json()
                # Check if the response indicates unified service processing
                if "success" in data or "status" in data:
                    self.log_result("WhatsApp Unified Service Integration", True, "Unified WhatsApp service integration working correctly")
                    return True
                else:
                    self.log_result("WhatsApp Unified Service Integration", False, "Unified service not responding correctly", response)
            else:
                self.log_result("WhatsApp Unified Service Integration", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("WhatsApp Unified Service Integration", False, f"Request error: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all WhatsApp webhook tests"""
        print("🚀 LOCAL WHATSAPP WEBHOOK ENDPOINTS TESTING")
        print("-" * 50)
        
        tests = [
            ("WhatsApp GET /whatsapp - Facebook Verification", self.test_whatsapp_webhook_get_facebook_verification),
            ("WhatsApp GET /whatsapp - No Params", self.test_whatsapp_webhook_get_without_params),
            ("WhatsApp POST /whatsapp - Facebook Message", self.test_whatsapp_webhook_post_facebook_message),
            ("WhatsApp POST /whatsapp - Unified System", self.test_whatsapp_webhook_post_unified_system),
            ("WhatsApp 405 Error Resolution", self.test_whatsapp_webhook_405_error_resolution),
            ("WhatsApp Unified Service Integration", self.test_whatsapp_webhook_unified_service_integration)
        ]
        
        for test_name, test_func in tests:
            test_func()
        
        # Print summary
        print("=" * 60)
        print("LOCAL TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Total: {self.results['passed'] + self.results['failed']}")
        
        if self.results['errors']:
            print("\n🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        print()
        if self.results['failed'] == 0:
            print("🎉 ALL LOCAL WHATSAPP WEBHOOK TESTS PASSED! The endpoints are working correctly locally.")
            return True
        else:
            print("⚠️  Some local WhatsApp webhook tests failed. Please check the errors above.")
            return False

if __name__ == "__main__":
    tester = LocalWhatsAppWebhookTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)