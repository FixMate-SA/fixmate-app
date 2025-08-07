#!/usr/bin/env python3
"""
FixMate-SA WhatsApp Integration Testing Suite
Testing the enhanced 360Dialog WhatsApp integration for FixMate-SA

WhatsApp Business Number: 27754466571
Channel ID: KYS4TkCH  
API Key: fAZcu5FIR9j4xexivP2sry3gAK (configured)
Callback URL: https://fixmate-sa-app-a448c751e1d2.herokuapp.com/whatsapp
"""

import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List

class WhatsAppIntegrationTester:
    def __init__(self):
        # Use the correct Heroku backend URL
        self.base_url = "https://fixmate-sa-app-a448c751e1d2.herokuapp.com"
        self.api_base = f"{self.base_url}/api"
        
        # WhatsApp Integration Details
        self.whatsapp_business_number = "27754466571"
        self.channel_id = "KYS4TkCH"
        self.callback_url = f"{self.base_url}/whatsapp"
        
        # Test phone numbers (South African format)
        self.test_phones = [
            "+27821234567",  # Standard format
            "27821234568",   # Without +
            "0821234569",    # Local format
            "+27 82 123 4570", # Formatted
            "+27-82-123-4571"  # Dashed format
        ]
        
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FixMate-SA-WhatsApp-Tester/1.0'
        })
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()

    def test_webhook_verification_get(self):
        """Test 1: Webhook Verification (GET /whatsapp)"""
        print("🔍 Testing Webhook Verification (GET /whatsapp)...")
        
        # Test 1a: Webhook verification with challenge
        try:
            params = {
                'hub.mode': 'subscribe',
                'hub.challenge': 'test_challenge_12345',
                'hub.verify_token': 'test_verify_token'
            }
            
            response = self.session.get(f"{self.base_url}/whatsapp", params=params)
            
            if response.status_code == 200 and response.text == 'test_challenge_12345':
                self.log_test(
                    "Webhook Challenge Response", 
                    True, 
                    f"Correctly returned challenge: {response.text}"
                )
            else:
                self.log_test(
                    "Webhook Challenge Response", 
                    False, 
                    f"Expected challenge echo, got: {response.text}", 
                    response.status_code
                )
        except Exception as e:
            self.log_test("Webhook Challenge Response", False, f"Exception: {str(e)}")
        
        # Test 1b: Health check without verification params
        try:
            response = self.session.get(f"{self.base_url}/whatsapp")
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ['success', 'message', 'business_number', 'channel_id', 'status']
                
                if all(field in data for field in expected_fields):
                    if data.get('business_number') == self.whatsapp_business_number:
                        self.log_test(
                            "Webhook Health Check", 
                            True, 
                            f"Health check successful with correct business number: {data.get('business_number')}"
                        )
                    else:
                        self.log_test(
                            "Webhook Health Check", 
                            False, 
                            f"Wrong business number: {data.get('business_number')}", 
                            data
                        )
                else:
                    self.log_test(
                        "Webhook Health Check", 
                        False, 
                        f"Missing required fields in response", 
                        data
                    )
            else:
                self.log_test(
                    "Webhook Health Check", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
        except Exception as e:
            self.log_test("Webhook Health Check", False, f"Exception: {str(e)}")

    def test_message_processing_post(self):
        """Test 2: Message Processing (POST /whatsapp)"""
        print("📨 Testing Message Processing (POST /whatsapp)...")
        
        # Test 2a: Text message processing
        test_messages = [
            {
                "name": "Service Request - Plumber",
                "payload": {
                    "entry": [{
                        "changes": [{
                            "value": {
                                "messages": [{
                                    "from": "27821234567",
                                    "id": f"msg_{uuid.uuid4()}",
                                    "timestamp": str(int(time.time())),
                                    "type": "text",
                                    "text": {"body": "I need a plumber for a leaking pipe"}
                                }],
                                "contacts": [{
                                    "profile": {"name": "John Test"},
                                    "wa_id": "27821234567"
                                }]
                            }
                        }]
                    }]
                },
                "expected_services": ["plumber"]
            },
            {
                "name": "Service Request - Electrician",
                "payload": {
                    "entry": [{
                        "changes": [{
                            "value": {
                                "messages": [{
                                    "from": "27821234568",
                                    "id": f"msg_{uuid.uuid4()}",
                                    "timestamp": str(int(time.time())),
                                    "type": "text",
                                    "text": {"body": "Urgent! My power is out, need an electrician"}
                                }],
                                "contacts": [{
                                    "profile": {"name": "Sarah Test"},
                                    "wa_id": "27821234568"
                                }]
                            }
                        }]
                    }]
                },
                "expected_services": ["electrician"],
                "expected_urgent": True
            },
            {
                "name": "Greeting Message",
                "payload": {
                    "entry": [{
                        "changes": [{
                            "value": {
                                "messages": [{
                                    "from": "27821234569",
                                    "id": f"msg_{uuid.uuid4()}",
                                    "timestamp": str(int(time.time())),
                                    "type": "text",
                                    "text": {"body": "Hello, I need help"}
                                }],
                                "contacts": [{
                                    "profile": {"name": "Mike Test"},
                                    "wa_id": "27821234569"
                                }]
                            }
                        }]
                    }]
                },
                "expected_greeting": True
            },
            {
                "name": "Help Request",
                "payload": {
                    "entry": [{
                        "changes": [{
                            "value": {
                                "messages": [{
                                    "from": "27821234570",
                                    "id": f"msg_{uuid.uuid4()}",
                                    "timestamp": str(int(time.time())),
                                    "type": "text",
                                    "text": {"body": "What services do you offer?"}
                                }],
                                "contacts": [{
                                    "profile": {"name": "Lisa Test"},
                                    "wa_id": "27821234570"
                                }]
                            }
                        }]
                    }]
                }
            }
        ]
        
        for test_case in test_messages:
            try:
                response = self.session.post(f"{self.base_url}/whatsapp", json=test_case["payload"])
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('status') == 'success' or data.get('status') == 'processed':
                        self.log_test(
                            f"Message Processing - {test_case['name']}", 
                            True, 
                            f"Message processed successfully"
                        )
                    else:
                        self.log_test(
                            f"Message Processing - {test_case['name']}", 
                            False, 
                            f"Processing failed", 
                            data
                        )
                else:
                    self.log_test(
                        f"Message Processing - {test_case['name']}", 
                        False, 
                        f"HTTP {response.status_code}", 
                        response.text
                    )
            except Exception as e:
                self.log_test(f"Message Processing - {test_case['name']}", False, f"Exception: {str(e)}")

    def test_whatsapp_api_endpoints(self):
        """Test 3: WhatsApp API Testing"""
        print("🔧 Testing WhatsApp API Endpoints...")
        
        # Test 3a: Send message endpoint
        try:
            payload = {
                "to_number": "+27821234567",
                "message": "Test message from FixMate-SA API"
            }
            
            # Use form data for this endpoint
            response = requests.post(f"{self.api_base}/whatsapp/send-message", data=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test(
                        "Send WhatsApp Message", 
                        True, 
                        f"Message sent successfully"
                    )
                else:
                    self.log_test(
                        "Send WhatsApp Message", 
                        False, 
                        f"Send failed: {data.get('error', 'Unknown error')}", 
                        data
                    )
            else:
                self.log_test(
                    "Send WhatsApp Message", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
        except Exception as e:
            self.log_test("Send WhatsApp Message", False, f"Exception: {str(e)}")
        
        # Test 3b: Phone number formatting
        for phone in self.test_phones:
            try:
                payload = {
                    "to_number": phone,
                    "message": f"Test formatting for {phone}"
                }
                
                response = self.session.post(f"{self.api_base}/whatsapp/send-message", data=payload)
                
                if response.status_code == 200:
                    self.log_test(
                        f"Phone Format Test - {phone}", 
                        True, 
                        f"Format accepted"
                    )
                else:
                    self.log_test(
                        f"Phone Format Test - {phone}", 
                        False, 
                        f"HTTP {response.status_code}"
                    )
            except Exception as e:
                self.log_test(f"Phone Format Test - {phone}", False, f"Exception: {str(e)}")
        
        # Test 3c: Job notification endpoint
        try:
            payload = {
                "job_id": "test_job_123",
                "phone_number": "+27821234567"
            }
            
            response = self.session.post(f"{self.api_base}/whatsapp/send-job-notification", data=payload)
            
            if response.status_code == 200:
                self.log_test(
                    "Job Notification", 
                    True, 
                    f"Job notification sent successfully"
                )
            else:
                self.log_test(
                    "Job Notification", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
        except Exception as e:
            self.log_test("Job Notification", False, f"Exception: {str(e)}")

    def test_service_request_workflow(self):
        """Test 4: Service Request Workflow"""
        print("🔄 Testing Service Request Workflow...")
        
        # Test 4a: Complete conversation flow simulation
        conversation_steps = [
            {
                "step": "Initial Service Request",
                "message": "I need a plumber for urgent pipe repair",
                "expected_response_contains": ["plumber", "service"]
            },
            {
                "step": "Follow-up Information",
                "message": "The pipe is leaking in my kitchen",
                "expected_response_contains": ["kitchen", "location"]
            }
        ]
        
        test_phone = "+27821234567"
        
        for step in conversation_steps:
            try:
                webhook_payload = {
                    "entry": [{
                        "changes": [{
                            "value": {
                                "messages": [{
                                    "from": test_phone.replace("+", ""),
                                    "id": f"msg_{uuid.uuid4()}",
                                    "timestamp": str(int(time.time())),
                                    "type": "text",
                                    "text": {"body": step["message"]}
                                }],
                                "contacts": [{
                                    "profile": {"name": "Test User"},
                                    "wa_id": test_phone.replace("+", "")
                                }]
                            }
                        }]
                    }]
                }
                
                response = self.session.post(f"{self.base_url}/whatsapp", json=webhook_payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success' or data.get('status') == 'processed':
                        self.log_test(
                            f"Workflow - {step['step']}", 
                            True, 
                            f"Step processed successfully"
                        )
                    else:
                        self.log_test(
                            f"Workflow - {step['step']}", 
                            False, 
                            f"Step processing failed", 
                            data
                        )
                else:
                    self.log_test(
                        f"Workflow - {step['step']}", 
                        False, 
                        f"HTTP {response.status_code}", 
                        response.text
                    )
                
                # Small delay between steps
                time.sleep(1)
                
            except Exception as e:
                self.log_test(f"Workflow - {step['step']}", False, f"Exception: {str(e)}")

    def test_error_handling(self):
        """Test 5: Error Handling"""
        print("⚠️ Testing Error Handling...")
        
        # Test 5a: Malformed webhook payload
        try:
            malformed_payload = {"invalid": "structure"}
            
            response = self.session.post(f"{self.base_url}/whatsapp", json=malformed_payload)
            
            # Should still return 200 to avoid retries but handle gracefully
            if response.status_code == 200:
                data = response.json()
                if ('error_handled' in data.get('status', '') or 
                    data.get('status') == 'success' or 
                    data.get('status') == 'ignored'):
                    self.log_test(
                        "Malformed Payload Handling", 
                        True, 
                        f"Gracefully handled malformed payload: {data.get('status')}"
                    )
                else:
                    self.log_test(
                        "Malformed Payload Handling", 
                        False, 
                        f"Unexpected response", 
                        data
                    )
            else:
                self.log_test(
                    "Malformed Payload Handling", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
        except Exception as e:
            self.log_test("Malformed Payload Handling", False, f"Exception: {str(e)}")
        
        # Test 5b: Empty message payload
        try:
            empty_payload = {
                "entry": [{
                    "changes": [{
                        "value": {
                            "messages": [],
                            "contacts": []
                        }
                    }]
                }]
            }
            
            response = self.session.post(f"{self.base_url}/whatsapp", json=empty_payload)
            
            if response.status_code == 200:
                self.log_test(
                    "Empty Message Handling", 
                    True, 
                    f"Handled empty message payload gracefully"
                )
            else:
                self.log_test(
                    "Empty Message Handling", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
        except Exception as e:
            self.log_test("Empty Message Handling", False, f"Exception: {str(e)}")
        
        # Test 5c: Invalid phone number format
        try:
            payload = {
                "to_number": "invalid_phone",
                "message": "Test message"
            }
            
            response = self.session.post(f"{self.api_base}/whatsapp/send-message", data=payload)
            
            # Should handle gracefully, either succeed with formatting or fail gracefully
            if response.status_code in [200, 400]:
                self.log_test(
                    "Invalid Phone Format Handling", 
                    True, 
                    f"Handled invalid phone format appropriately"
                )
            else:
                self.log_test(
                    "Invalid Phone Format Handling", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
        except Exception as e:
            self.log_test("Invalid Phone Format Handling", False, f"Exception: {str(e)}")

    def test_business_webhook_endpoints(self):
        """Test 6: Business Webhook Endpoints"""
        print("🏢 Testing Business Webhook Endpoints...")
        
        # Test 6a: Business webhook GET
        try:
            response = self.session.get(f"{self.api_base}/whatsapp/business/webhook")
            
            if response.status_code == 200:
                self.log_test(
                    "Business Webhook GET", 
                    True, 
                    f"Business webhook GET endpoint accessible"
                )
            else:
                self.log_test(
                    "Business Webhook GET", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
        except Exception as e:
            self.log_test("Business Webhook GET", False, f"Exception: {str(e)}")
        
        # Test 6b: Business webhook POST
        try:
            business_payload = {
                "entry": [{
                    "changes": [{
                        "value": {
                            "messages": [{
                                "from": "27821234567",
                                "id": f"msg_{uuid.uuid4()}",
                                "timestamp": str(int(time.time())),
                                "type": "text",
                                "text": {"body": "I need business compliance help"}
                            }],
                            "contacts": [{
                                "profile": {"name": "Business User"},
                                "wa_id": "27821234567"
                            }]
                        }
                    }]
                }]
            }
            
            response = self.session.post(f"{self.api_base}/whatsapp/business/webhook", json=business_payload)
            
            if response.status_code == 200:
                self.log_test(
                    "Business Webhook POST", 
                    True, 
                    f"Business webhook POST processed successfully"
                )
            else:
                self.log_test(
                    "Business Webhook POST", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
        except Exception as e:
            self.log_test("Business Webhook POST", False, f"Exception: {str(e)}")

    def test_api_connectivity(self):
        """Test 7: API Connectivity and Configuration"""
        print("🌐 Testing API Connectivity...")
        
        # Test 7a: Backend health check
        try:
            response = self.session.get(f"{self.api_base}/")
            
            if response.status_code == 200:
                self.log_test(
                    "Backend API Health", 
                    True, 
                    f"Backend API is accessible"
                )
            else:
                self.log_test(
                    "Backend API Health", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
        except Exception as e:
            self.log_test("Backend API Health", False, f"Exception: {str(e)}")
        
        # Test 7b: WhatsApp insights endpoint
        try:
            response = self.session.get(f"{self.api_base}/whatsapp/insights")
            
            if response.status_code == 200:
                self.log_test(
                    "WhatsApp Insights Endpoint", 
                    True, 
                    f"Insights endpoint accessible"
                )
            else:
                self.log_test(
                    "WhatsApp Insights Endpoint", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.text
                )
        except Exception as e:
            self.log_test("WhatsApp Insights Endpoint", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all WhatsApp integration tests"""
        print("🚀 Starting FixMate-SA WhatsApp Integration Testing Suite")
        print(f"📱 Business Number: {self.whatsapp_business_number}")
        print(f"🔗 Channel ID: {self.channel_id}")
        print(f"🌐 Callback URL: {self.callback_url}")
        print(f"⚡ Backend URL: {self.base_url}")
        print("=" * 80)
        
        start_time = datetime.now()
        
        # Run all test suites
        self.test_webhook_verification_get()
        self.test_message_processing_post()
        self.test_whatsapp_api_endpoints()
        self.test_service_request_workflow()
        self.test_error_handling()
        self.test_business_webhook_endpoints()
        self.test_api_connectivity()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Generate summary
        self.generate_test_summary(duration)

    def generate_test_summary(self, duration: float):
        """Generate comprehensive test summary"""
        print("=" * 80)
        print("📊 WHATSAPP INTEGRATION TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"⏱️  Total Duration: {duration:.2f} seconds")
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print()
        
        # Critical issues
        critical_failures = [
            result for result in self.test_results 
            if not result['success'] and any(keyword in result['test_name'].lower() 
                                           for keyword in ['webhook', 'verification', 'message processing'])
        ]
        
        if critical_failures:
            print("🚨 CRITICAL ISSUES FOUND:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test_name']}: {failure['details']}")
            print()
        
        # Detailed results
        print("📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test_name']}")
            if result['details']:
                print(f"      {result['details']}")
        
        print()
        print("=" * 80)
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: WhatsApp integration is working excellently!")
        elif success_rate >= 75:
            print("✅ GOOD: WhatsApp integration is working well with minor issues.")
        elif success_rate >= 50:
            print("⚠️  MODERATE: WhatsApp integration has some issues that need attention.")
        else:
            print("🚨 CRITICAL: WhatsApp integration has major issues requiring immediate attention.")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = WhatsAppIntegrationTester()
    tester.run_all_tests()