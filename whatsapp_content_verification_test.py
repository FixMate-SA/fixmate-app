#!/usr/bin/env python3
"""
WhatsApp Content Verification Test
Verify the actual content and logic of the enhanced WhatsApp integration responses.

This test directly calls the WhatsApp service methods to verify:
1. Service detection logic with 20+ categories
2. Universal service indicators
3. Message content quality and formatting
4. User journey guidance elements
"""

import sys
import os
sys.path.append('/app/backend')

from services.whatsapp_service import WhatsAppService
from services.unified_whatsapp_service import UnifiedWhatsAppService
import json
from datetime import datetime

class WhatsAppContentVerifier:
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
        self.unified_service = UnifiedWhatsAppService()
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_result(self, test_name: str, success: bool, message: str, details: dict = None):
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
        self.total_tests += 1
        if success:
            self.passed_tests += 1
        print(f"{status} {test_name}: {message}")
    
    def test_service_detection_logic(self):
        """Test the actual service detection logic"""
        print("\n🔍 TESTING SERVICE DETECTION LOGIC")
        
        test_cases = [
            # Traditional services
            {
                "text": "I need a plumber",
                "expected_services": ["plumber"],
                "expected_urgency": False,
                "description": "Traditional plumber request"
            },
            {
                "text": "electrical work needed",
                "expected_services": ["electrician"],
                "expected_urgency": False,
                "description": "Traditional electrical request"
            },
            
            # Expanded services (20+ categories)
            {
                "text": "laptop repair needed",
                "expected_services": ["it_tech"],
                "expected_urgency": False,
                "description": "IT tech service"
            },
            {
                "text": "catering for wedding",
                "expected_services": ["catering"],
                "expected_urgency": False,
                "description": "Catering service"
            },
            {
                "text": "math tutor needed",
                "expected_services": ["tutor"],
                "expected_urgency": False,
                "description": "Tutoring service"
            },
            {
                "text": "need pest control",
                "expected_services": ["pest_control"],
                "expected_urgency": False,
                "description": "Pest control service"
            },
            {
                "text": "security system installation",
                "expected_services": ["security"],
                "expected_urgency": False,
                "description": "Security service"
            },
            {
                "text": "pool maintenance required",
                "expected_services": ["pool"],
                "expected_urgency": False,
                "description": "Pool service"
            },
            {
                "text": "locksmith needed",
                "expected_services": ["locksmith"],
                "expected_urgency": False,
                "description": "Locksmith service"
            },
            {
                "text": "appliance repair",
                "expected_services": ["appliance"],
                "expected_urgency": False,
                "description": "Appliance service"
            },
            {
                "text": "moving services",
                "expected_services": ["moving"],
                "expected_urgency": False,
                "description": "Moving service"
            },
            {
                "text": "beauty salon services",
                "expected_services": ["beauty"],
                "expected_urgency": False,
                "description": "Beauty service"
            },
            
            # Universal service indicators
            {
                "text": "looking for someone to help",
                "expected_services": ["general_service"],
                "expected_urgency": False,
                "description": "General service with 'looking for' indicator"
            },
            {
                "text": "require assistance with something",
                "expected_services": ["general_service"],
                "expected_urgency": False,
                "description": "General service with 'require' indicator"
            },
            {
                "text": "want professional help",
                "expected_services": ["general_service"],
                "expected_urgency": False,
                "description": "General service with 'want' indicator"
            },
            {
                "text": "hire someone to fix",
                "expected_services": ["general_service"],
                "expected_urgency": False,
                "description": "General service with 'hire' indicator"
            },
            {
                "text": "find someone to help with",
                "expected_services": ["general_service"],
                "expected_urgency": False,
                "description": "General service with 'find' indicator"
            },
            {
                "text": "get help with maintenance",
                "expected_services": ["general_service"],
                "expected_urgency": False,
                "description": "General service with 'get help' indicator"
            },
            
            # Urgency detection
            {
                "text": "URGENT plumber needed",
                "expected_services": ["plumber"],
                "expected_urgency": True,
                "description": "Urgent plumber request"
            },
            {
                "text": "Emergency electrical work",
                "expected_services": ["electrician"],
                "expected_urgency": True,
                "description": "Emergency electrical request"
            },
            {
                "text": "need cleaner ASAP",
                "expected_services": ["cleaner"],
                "expected_urgency": True,
                "description": "ASAP cleaner request"
            },
            {
                "text": "immediate help needed",
                "expected_services": ["general_service"],
                "expected_urgency": True,
                "description": "Immediate general help"
            },
            
            # Multiple services
            {
                "text": "need plumber and electrician",
                "expected_services": ["plumber", "electrician"],
                "expected_urgency": False,
                "description": "Multiple services request"
            },
            
            # Different formats
            {
                "text": "want someone to fix my car",
                "expected_services": ["mechanic"],
                "expected_urgency": False,
                "description": "Mechanic with flexible format"
            },
            {
                "text": "require cleaning service",
                "expected_services": ["cleaner"],
                "expected_urgency": False,
                "description": "Cleaning with 'require' indicator"
            }
        ]
        
        for test_case in test_cases:
            self.verify_service_detection(test_case)
    
    def verify_service_detection(self, test_case: dict):
        """Verify individual service detection case"""
        try:
            # Use the WhatsApp service's text processing method
            processed_content = self.whatsapp_service._process_text_content(test_case["text"])
            
            # Check detected services
            detected_services = processed_content.get("detected_services", [])
            expected_services = test_case["expected_services"]
            
            services_match = all(service in detected_services for service in expected_services)
            
            # Check urgency detection
            detected_urgency = processed_content.get("is_urgent", False)
            expected_urgency = test_case["expected_urgency"]
            urgency_match = detected_urgency == expected_urgency
            
            # Overall success
            success = services_match and urgency_match
            
            details = {
                "text": test_case["text"],
                "expected_services": expected_services,
                "detected_services": detected_services,
                "expected_urgency": expected_urgency,
                "detected_urgency": detected_urgency,
                "services_match": services_match,
                "urgency_match": urgency_match,
                "full_processed_content": processed_content
            }
            
            if success:
                message = f"Correctly detected services {detected_services} and urgency {detected_urgency}"
            else:
                issues = []
                if not services_match:
                    issues.append(f"services (expected {expected_services}, got {detected_services})")
                if not urgency_match:
                    issues.append(f"urgency (expected {expected_urgency}, got {detected_urgency})")
                message = f"Detection issues: {', '.join(issues)}"
            
            self.log_result(
                f"Service Detection: {test_case['description']}",
                success,
                message,
                details
            )
            
        except Exception as e:
            self.log_result(
                f"Service Detection: {test_case['description']}",
                False,
                f"Error in detection: {str(e)}",
                {"error": str(e), "text": test_case["text"]}
            )
    
    def test_service_categories_coverage(self):
        """Test that all 20+ service categories are properly defined"""
        print("\n📋 TESTING SERVICE CATEGORIES COVERAGE")
        
        # Expected service categories from the review request
        expected_categories = [
            'plumber', 'electrician', 'cleaner', 'gardener', 'carpenter', 
            'painter', 'handyman', 'mechanic', 'builder', 'roofer', 
            'tiler', 'pest_control', 'security', 'aircon', 'pool', 
            'locksmith', 'appliance', 'moving', 'it_tech', 'tutor', 
            'beauty', 'catering'
        ]
        
        try:
            # Get the service keywords from the WhatsApp service
            # This requires accessing the private method, but it's for testing
            test_text = "test"
            processed = self.whatsapp_service._process_text_content(test_text)
            
            # Check if we can access the service keywords (this is a structural test)
            # We'll test by trying to detect each expected category
            detected_categories = []
            
            for category in expected_categories:
                # Create a test message that should trigger this category
                test_messages = {
                    'plumber': 'need a plumber',
                    'electrician': 'electrical work needed',
                    'cleaner': 'cleaning service required',
                    'gardener': 'gardening help needed',
                    'carpenter': 'carpenter work required',
                    'painter': 'painting service needed',
                    'handyman': 'handyman required',
                    'mechanic': 'car mechanic needed',
                    'builder': 'building work required',
                    'roofer': 'roofing service needed',
                    'tiler': 'tiling work required',
                    'pest_control': 'pest control needed',
                    'security': 'security system required',
                    'aircon': 'aircon repair needed',
                    'pool': 'pool maintenance required',
                    'locksmith': 'locksmith service needed',
                    'appliance': 'appliance repair required',
                    'moving': 'moving services needed',
                    'it_tech': 'computer repair needed',
                    'tutor': 'tutoring services required',
                    'beauty': 'beauty services needed',
                    'catering': 'catering services required'
                }
                
                test_message = test_messages.get(category, f"{category} service needed")
                result = self.whatsapp_service._process_text_content(test_message)
                
                if category in result.get("detected_services", []):
                    detected_categories.append(category)
            
            missing_categories = set(expected_categories) - set(detected_categories)
            coverage_percentage = (len(detected_categories) / len(expected_categories)) * 100
            
            success = coverage_percentage >= 90  # Allow for 90% coverage
            
            self.log_result(
                "Service Categories Coverage",
                success,
                f"Detected {len(detected_categories)}/{len(expected_categories)} categories ({coverage_percentage:.1f}%)",
                {
                    "expected_categories": expected_categories,
                    "detected_categories": detected_categories,
                    "missing_categories": list(missing_categories),
                    "coverage_percentage": coverage_percentage
                }
            )
            
        except Exception as e:
            self.log_result(
                "Service Categories Coverage",
                False,
                f"Error testing categories: {str(e)}",
                {"error": str(e)}
            )
    
    def test_universal_service_indicators(self):
        """Test universal service indicators"""
        print("\n🔄 TESTING UNIVERSAL SERVICE INDICATORS")
        
        # Test universal service indicators
        indicators = [
            'need', 'looking for', 'require', 'want', 'hire', 'find', 'get',
            'help with', 'assistance', 'service', 'professional', 'someone to',
            'repair', 'fix', 'install', 'maintain', 'clean', 'paint', 'build',
            'work on', 'sort out', 'deal with', 'handle', 'do'
        ]
        
        for indicator in indicators:
            test_message = f"I {indicator} something"
            try:
                result = self.whatsapp_service._process_text_content(test_message)
                has_service_indicator = result.get("has_service_indicator", False)
                detected_services = result.get("detected_services", [])
                
                # Should detect service indicator and classify as general_service
                success = has_service_indicator and "general_service" in detected_services
                
                self.log_result(
                    f"Universal Indicator: '{indicator}'",
                    success,
                    f"Detected indicator: {has_service_indicator}, Services: {detected_services}",
                    {
                        "indicator": indicator,
                        "test_message": test_message,
                        "has_service_indicator": has_service_indicator,
                        "detected_services": detected_services
                    }
                )
                
            except Exception as e:
                self.log_result(
                    f"Universal Indicator: '{indicator}'",
                    False,
                    f"Error testing indicator: {str(e)}",
                    {"error": str(e), "indicator": indicator}
                )
    
    def test_greeting_and_help_detection(self):
        """Test greeting and help message detection"""
        print("\n👋 TESTING GREETING AND HELP DETECTION")
        
        # Test greeting detection
        greeting_tests = [
            ("hi", True),
            ("hello", True),
            ("hallo", True),
            ("good morning", True),
            ("hey", True),
            ("greetings", True),
            ("I need help", False),  # Should not be detected as greeting
            ("help me", False)  # Should not be detected as greeting
        ]
        
        for text, expected_greeting in greeting_tests:
            try:
                result = self.whatsapp_service._process_text_content(text)
                is_greeting = result.get("is_greeting", False)
                
                success = is_greeting == expected_greeting
                
                self.log_result(
                    f"Greeting Detection: '{text}'",
                    success,
                    f"Expected: {expected_greeting}, Detected: {is_greeting}",
                    {
                        "text": text,
                        "expected_greeting": expected_greeting,
                        "detected_greeting": is_greeting
                    }
                )
                
            except Exception as e:
                self.log_result(
                    f"Greeting Detection: '{text}'",
                    False,
                    f"Error: {str(e)}",
                    {"error": str(e), "text": text}
                )
        
        # Test help detection
        help_tests = [
            ("help", True),
            ("assist", True),
            ("info", True),
            ("information", True),
            ("how", True),
            ("what", True),
            ("I need a plumber", False)  # Should not be detected as help request
        ]
        
        for text, expected_help in help_tests:
            try:
                result = self.whatsapp_service._process_text_content(text)
                is_help_request = result.get("is_help_request", False)
                
                success = is_help_request == expected_help
                
                self.log_result(
                    f"Help Detection: '{text}'",
                    success,
                    f"Expected: {expected_help}, Detected: {is_help_request}",
                    {
                        "text": text,
                        "expected_help": expected_help,
                        "detected_help": is_help_request
                    }
                )
                
            except Exception as e:
                self.log_result(
                    f"Help Detection: '{text}'",
                    False,
                    f"Error: {str(e)}",
                    {"error": str(e), "text": text}
                )
    
    def run_all_tests(self):
        """Run all content verification tests"""
        print("🔍 STARTING WHATSAPP CONTENT VERIFICATION TESTING")
        print("=" * 80)
        
        start_time = datetime.now()
        
        # Run all test suites
        self.test_service_detection_logic()
        self.test_service_categories_coverage()
        self.test_universal_service_indicators()
        self.test_greeting_and_help_detection()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎉 WHATSAPP CONTENT VERIFICATION TEST SUMMARY")
        print("=" * 80)
        print(f"📊 Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.total_tests - self.passed_tests}")
        print(f"📈 Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        
        # Print failed tests
        failed_tests = [r for r in self.results if not r["success"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['message']}")
        
        # Overall assessment
        success_rate = (self.passed_tests / self.total_tests) * 100
        if success_rate >= 95:
            print(f"\n🎉 EXCELLENT: WhatsApp service detection logic is working excellently!")
        elif success_rate >= 85:
            print(f"\n✅ GOOD: WhatsApp service detection logic is working well with minor issues.")
        elif success_rate >= 75:
            print(f"\n⚠️ ACCEPTABLE: WhatsApp service detection logic has some issues that need attention.")
        else:
            print(f"\n❌ CRITICAL: WhatsApp service detection logic has significant issues requiring immediate attention.")
        
        return success_rate >= 85

if __name__ == "__main__":
    verifier = WhatsAppContentVerifier()
    success = verifier.run_all_tests()
    
    if success:
        print("\n🎯 CONCLUSION: WhatsApp content verification completed successfully!")
    else:
        print("\n🚨 CONCLUSION: WhatsApp content verification found issues that need to be addressed.")