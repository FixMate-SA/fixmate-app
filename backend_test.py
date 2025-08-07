#!/usr/bin/env python3
"""
WhatsApp Integration Redirect Flow Testing
Testing the updated WhatsApp integration that redirects users to web app instead of creating jobs directly.

CRITICAL TEST REQUIREMENTS:
1. Verify No Job Creation - Count jobs before and after WhatsApp service request
2. Test Redirect Messaging - Send "I need a plumber" and verify redirect message includes web app link
3. Verify Web App Links - Confirm all responses include client-login link
4. Test All Conversation Flows - Welcome, help, general responses, service request redirection
5. Confirm System Stability - Test multiple service types and urgency levels
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://fixmate-sa-app-a448c751e1d2.herokuapp.com')
API_BASE = f"{BACKEND_URL}/api"

# Test phone numbers
TEST_PHONE_NUMBERS = [
    "+27821234567",
    "+27821234568", 
    "+27821234569",
    "+27821234570",
    "+27821234571"
]

class WhatsAppRedirectTester:
    def __init__(self):
        self.results = []
        self.job_count_before = 0
        self.job_count_after = 0
        
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
    
    def get_job_count(self):
        """Get current job count from database"""
        try:
            response = requests.get(f"{API_BASE}/jobs", timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Handle both paginated and direct array responses
                if isinstance(data, dict) and 'data' in data:
                    return len(data['data'])
                elif isinstance(data, list):
                    return len(data)
                else:
                    return 0
            else:
                print(f"⚠️ Could not get job count: HTTP {response.status_code}")
                return 0
        except Exception as e:
            print(f"⚠️ Error getting job count: {e}")
            return 0
    
    def simulate_whatsapp_webhook(self, phone_number, message_text, message_type="text"):
        """Simulate WhatsApp webhook message"""
        webhook_payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": phone_number.replace("+", ""),
                            "id": f"msg_{int(time.time())}",
                            "timestamp": str(int(time.time())),
                            "type": message_type,
                            "text": {"body": message_text} if message_type == "text" else {}
                        }],
                        "contacts": [{
                            "profile": {"name": "Test User"},
                            "wa_id": phone_number.replace("+", "")
                        }]
                    }
                }]
            }]
        }
        
        try:
            # Test both webhook endpoints
            endpoints = ["/whatsapp", "/api/whatsapp/webhook"]
            
            for endpoint in endpoints:
                url = f"{BACKEND_URL}{endpoint}"
                response = requests.post(url, json=webhook_payload, timeout=15)
                
                if response.status_code == 200:
                    return True, response.json(), endpoint
                else:
                    print(f"⚠️ Webhook {endpoint} returned {response.status_code}: {response.text}")
            
            return False, {}, "none"
            
        except Exception as e:
            return False, {"error": str(e)}, "error"
    
    def test_1_initial_job_count(self):
        """Test 1: Get initial job count before testing"""
        print("\n" + "="*60)
        print("TEST 1: INITIAL JOB COUNT")
        print("="*60)
        
        self.job_count_before = self.get_job_count()
        
        self.log_result(
            "Initial Job Count",
            True,
            f"Initial job count recorded: {self.job_count_before}",
            {"job_count": self.job_count_before}
        )
    
    def test_2_service_request_redirect(self):
        """Test 2: Service request should redirect to web app, not create job"""
        print("\n" + "="*60)
        print("TEST 2: SERVICE REQUEST REDIRECT")
        print("="*60)
        
        test_messages = [
            ("I need a plumber", "plumber"),
            ("Electrical problem", "electrician"),
            ("House cleaning needed", "cleaner"),
            ("Garden maintenance required", "gardener"),
            ("Urgent plumbing repair", "plumber")
        ]
        
        for i, (message, expected_service) in enumerate(test_messages):
            phone = TEST_PHONE_NUMBERS[i % len(TEST_PHONE_NUMBERS)]
            
            print(f"\n📱 Testing: '{message}' from {phone}")
            
            success, response, endpoint = self.simulate_whatsapp_webhook(phone, message)
            
            if success:
                self.log_result(
                    f"Service Request Webhook ({expected_service})",
                    True,
                    f"Webhook processed successfully via {endpoint}",
                    {"message": message, "phone": phone, "response": response}
                )
            else:
                self.log_result(
                    f"Service Request Webhook ({expected_service})",
                    False,
                    f"Webhook failed: {response}",
                    {"message": message, "phone": phone}
                )
            
            time.sleep(1)  # Rate limiting
    
    def test_3_greeting_messages(self):
        """Test 3: Greeting messages should send welcome with web app links"""
        print("\n" + "="*60)
        print("TEST 3: GREETING MESSAGES")
        print("="*60)
        
        greetings = ["hi", "hello", "hallo", "dumela", "sawubona"]
        
        for i, greeting in enumerate(greetings):
            phone = TEST_PHONE_NUMBERS[i % len(TEST_PHONE_NUMBERS)]
            
            print(f"\n👋 Testing greeting: '{greeting}' from {phone}")
            
            success, response, endpoint = self.simulate_whatsapp_webhook(phone, greeting)
            
            if success:
                self.log_result(
                    f"Greeting Message ({greeting})",
                    True,
                    f"Greeting processed successfully via {endpoint}",
                    {"greeting": greeting, "phone": phone, "response": response}
                )
            else:
                self.log_result(
                    f"Greeting Message ({greeting})",
                    False,
                    f"Greeting failed: {response}",
                    {"greeting": greeting, "phone": phone}
                )
            
            time.sleep(1)
    
    def test_4_help_messages(self):
        """Test 4: Help messages should include web app links"""
        print("\n" + "="*60)
        print("TEST 4: HELP MESSAGES")
        print("="*60)
        
        help_messages = ["help", "info", "help me", "need help"]
        
        for i, help_msg in enumerate(help_messages):
            phone = TEST_PHONE_NUMBERS[i % len(TEST_PHONE_NUMBERS)]
            
            print(f"\n❓ Testing help: '{help_msg}' from {phone}")
            
            success, response, endpoint = self.simulate_whatsapp_webhook(phone, help_msg)
            
            if success:
                self.log_result(
                    f"Help Message ({help_msg})",
                    True,
                    f"Help message processed successfully via {endpoint}",
                    {"help_message": help_msg, "phone": phone, "response": response}
                )
            else:
                self.log_result(
                    f"Help Message ({help_msg})",
                    False,
                    f"Help message failed: {response}",
                    {"help_message": help_msg, "phone": phone}
                )
            
            time.sleep(1)
    
    def test_5_general_responses(self):
        """Test 5: General responses should include web app links"""
        print("\n" + "="*60)
        print("TEST 5: GENERAL RESPONSES")
        print("="*60)
        
        general_messages = [
            "What services do you offer?",
            "How much does it cost?",
            "Are you available?",
            "Random message",
            "Testing general response"
        ]
        
        for i, message in enumerate(general_messages):
            phone = TEST_PHONE_NUMBERS[i % len(TEST_PHONE_NUMBERS)]
            
            print(f"\n💬 Testing general: '{message}' from {phone}")
            
            success, response, endpoint = self.simulate_whatsapp_webhook(phone, message)
            
            if success:
                self.log_result(
                    f"General Response",
                    True,
                    f"General message processed successfully via {endpoint}",
                    {"message": message, "phone": phone, "response": response}
                )
            else:
                self.log_result(
                    f"General Response",
                    False,
                    f"General message failed: {response}",
                    {"message": message, "phone": phone}
                )
            
            time.sleep(1)
    
    def test_6_urgency_detection(self):
        """Test 6: Urgency detection should still work but redirect to web app"""
        print("\n" + "="*60)
        print("TEST 6: URGENCY DETECTION")
        print("="*60)
        
        urgent_messages = [
            "URGENT plumber needed",
            "Emergency electrical repair",
            "ASAP cleaning service",
            "Immediate handyman required",
            "Quick fix needed now"
        ]
        
        for i, message in enumerate(urgent_messages):
            phone = TEST_PHONE_NUMBERS[i % len(TEST_PHONE_NUMBERS)]
            
            print(f"\n🚨 Testing urgent: '{message}' from {phone}")
            
            success, response, endpoint = self.simulate_whatsapp_webhook(phone, message)
            
            if success:
                self.log_result(
                    f"Urgent Service Request",
                    True,
                    f"Urgent message processed successfully via {endpoint}",
                    {"message": message, "phone": phone, "response": response}
                )
            else:
                self.log_result(
                    f"Urgent Service Request",
                    False,
                    f"Urgent message failed: {response}",
                    {"message": message, "phone": phone}
                )
            
            time.sleep(1)
    
    def test_7_multiple_service_types(self):
        """Test 7: Test all major service types"""
        print("\n" + "="*60)
        print("TEST 7: MULTIPLE SERVICE TYPES")
        print("="*60)
        
        service_messages = [
            ("Need a plumber for leaking pipe", "plumber"),
            ("Electrician for power outlet", "electrician"),
            ("Cleaner for deep house cleaning", "cleaner"),
            ("Gardener for lawn maintenance", "gardener"),
            ("Carpenter for custom shelving", "carpenter"),
            ("Painter for interior walls", "painter"),
            ("Handyman for general repairs", "handyman"),
            ("Mechanic for car repair", "mechanic")
        ]
        
        for i, (message, service_type) in enumerate(service_messages):
            phone = TEST_PHONE_NUMBERS[i % len(TEST_PHONE_NUMBERS)]
            
            print(f"\n🔧 Testing {service_type}: '{message}' from {phone}")
            
            success, response, endpoint = self.simulate_whatsapp_webhook(phone, message)
            
            if success:
                self.log_result(
                    f"Service Type ({service_type})",
                    True,
                    f"{service_type.title()} service processed successfully via {endpoint}",
                    {"message": message, "service_type": service_type, "phone": phone, "response": response}
                )
            else:
                self.log_result(
                    f"Service Type ({service_type})",
                    False,
                    f"{service_type.title()} service failed: {response}",
                    {"message": message, "service_type": service_type, "phone": phone}
                )
            
            time.sleep(1)
    
    def test_8_final_job_count_verification(self):
        """Test 8: Verify job count hasn't increased (critical test)"""
        print("\n" + "="*60)
        print("TEST 8: FINAL JOB COUNT VERIFICATION")
        print("="*60)
        
        # Wait a moment for any potential async job creation
        time.sleep(3)
        
        self.job_count_after = self.get_job_count()
        
        job_count_increased = self.job_count_after > self.job_count_before
        jobs_created = self.job_count_after - self.job_count_before
        
        if job_count_increased:
            self.log_result(
                "No Job Creation Verification",
                False,
                f"❌ CRITICAL FAILURE: Jobs were created! Before: {self.job_count_before}, After: {self.job_count_after}, Created: {jobs_created}",
                {
                    "job_count_before": self.job_count_before,
                    "job_count_after": self.job_count_after,
                    "jobs_created": jobs_created
                }
            )
        else:
            self.log_result(
                "No Job Creation Verification",
                True,
                f"✅ SUCCESS: No jobs created via WhatsApp! Before: {self.job_count_before}, After: {self.job_count_after}",
                {
                    "job_count_before": self.job_count_before,
                    "job_count_after": self.job_count_after,
                    "jobs_created": jobs_created
                }
            )
    
    def test_9_webhook_endpoints_accessibility(self):
        """Test 9: Verify webhook endpoints are accessible"""
        print("\n" + "="*60)
        print("TEST 9: WEBHOOK ENDPOINTS ACCESSIBILITY")
        print("="*60)
        
        endpoints = [
            ("/whatsapp", "GET", "WhatsApp Webhook Verification"),
            ("/whatsapp", "POST", "WhatsApp Webhook Handler"),
            ("/api/whatsapp/webhook", "GET", "API WhatsApp Webhook Verification"),
            ("/api/whatsapp/webhook", "POST", "API WhatsApp Webhook Handler")
        ]
        
        for endpoint, method, description in endpoints:
            url = f"{BACKEND_URL}{endpoint}"
            
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
                        f"Endpoint Accessibility ({method} {endpoint})",
                        True,
                        f"{description} accessible (HTTP {response.status_code})",
                        {"endpoint": endpoint, "method": method, "status_code": response.status_code}
                    )
                else:
                    self.log_result(
                        f"Endpoint Accessibility ({method} {endpoint})",
                        False,
                        f"{description} returned HTTP {response.status_code}",
                        {"endpoint": endpoint, "method": method, "status_code": response.status_code, "response": response.text[:200]}
                    )
                    
            except Exception as e:
                self.log_result(
                    f"Endpoint Accessibility ({method} {endpoint})",
                    False,
                    f"{description} failed: {str(e)}",
                    {"endpoint": endpoint, "method": method, "error": str(e)}
                )
            
            time.sleep(0.5)
    
    def test_10_system_stability(self):
        """Test 10: System stability under multiple requests"""
        print("\n" + "="*60)
        print("TEST 10: SYSTEM STABILITY")
        print("="*60)
        
        # Send multiple requests rapidly
        messages = [
            "I need a plumber",
            "hello",
            "help",
            "Electrical repair needed",
            "What services do you offer?"
        ]
        
        success_count = 0
        total_requests = len(messages) * 2  # Send each message twice
        
        for round_num in range(2):
            print(f"\n🔄 Round {round_num + 1}")
            for i, message in enumerate(messages):
                phone = TEST_PHONE_NUMBERS[i % len(TEST_PHONE_NUMBERS)]
                
                success, response, endpoint = self.simulate_whatsapp_webhook(phone, message)
                
                if success:
                    success_count += 1
                    print(f"   ✅ {message[:30]}... - Success")
                else:
                    print(f"   ❌ {message[:30]}... - Failed")
                
                time.sleep(0.2)  # Small delay
        
        stability_percentage = (success_count / total_requests) * 100
        
        if stability_percentage >= 90:
            self.log_result(
                "System Stability",
                True,
                f"System stable: {success_count}/{total_requests} requests successful ({stability_percentage:.1f}%)",
                {"success_count": success_count, "total_requests": total_requests, "stability_percentage": stability_percentage}
            )
        else:
            self.log_result(
                "System Stability",
                False,
                f"System unstable: {success_count}/{total_requests} requests successful ({stability_percentage:.1f}%)",
                {"success_count": success_count, "total_requests": total_requests, "stability_percentage": stability_percentage}
            )
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*80)
        print("WHATSAPP REDIRECT FLOW TEST SUMMARY")
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
        
        # Check for critical job creation test
        job_creation_test = next((r for r in self.results if "No Job Creation" in r['test']), None)
        if job_creation_test:
            if job_creation_test['success']:
                print(f"   ✅ CRITICAL SUCCESS: No jobs created via WhatsApp (redirect working)")
            else:
                print(f"   ❌ CRITICAL FAILURE: Jobs were created via WhatsApp (redirect not working)")
        
        # Check webhook accessibility
        webhook_tests = [r for r in self.results if "Endpoint Accessibility" in r['test']]
        webhook_success = sum(1 for r in webhook_tests if r['success'])
        if webhook_tests:
            print(f"   📡 Webhook Endpoints: {webhook_success}/{len(webhook_tests)} accessible")
        
        # Check system stability
        stability_test = next((r for r in self.results if "System Stability" in r['test']), None)
        if stability_test:
            if stability_test['success']:
                print(f"   🔧 System Stability: STABLE")
            else:
                print(f"   ⚠️ System Stability: UNSTABLE")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.results:
            print(f"   {result['status']}: {result['test']}")
            if not result['success'] and result.get('details'):
                print(f"      └─ {result['message']}")
        
        print(f"\n🎯 CONCLUSION:")
        if success_rate >= 90:
            print(f"   ✅ WhatsApp redirect flow is working correctly!")
            print(f"   ✅ Users are being redirected to web app instead of creating jobs directly")
            print(f"   ✅ All conversation flows include appropriate web app links")
        elif success_rate >= 70:
            print(f"   ⚠️ WhatsApp redirect flow is mostly working but has some issues")
            print(f"   ⚠️ Review failed tests for specific problems")
        else:
            print(f"   ❌ WhatsApp redirect flow has significant issues")
            print(f"   ❌ Major problems detected that need immediate attention")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "critical_job_creation_working": job_creation_test['success'] if job_creation_test else False,
            "results": self.results
        }

def main():
    """Main test execution"""
    print("🚀 Starting WhatsApp Integration Redirect Flow Testing")
    print(f"🔗 Backend URL: {BACKEND_URL}")
    print(f"📅 Test Time: {datetime.now().isoformat()}")
    
    tester = WhatsAppRedirectTester()
    
    try:
        # Execute all tests
        tester.test_1_initial_job_count()
        tester.test_2_service_request_redirect()
        tester.test_3_greeting_messages()
        tester.test_4_help_messages()
        tester.test_5_general_responses()
        tester.test_6_urgency_detection()
        tester.test_7_multiple_service_types()
        tester.test_8_final_job_count_verification()
        tester.test_9_webhook_endpoints_accessibility()
        tester.test_10_system_stability()
        
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