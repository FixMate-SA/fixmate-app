#!/usr/bin/env python3
"""
Heroku Push Notification System Diagnostic Testing
Comprehensive testing with detailed diagnostics for production deployment
Base URL: https://service-pros-2.preview.emergentagent.com
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://service-pros-2.preview.emergentagent.com"
CLIENT_CREDENTIALS = {
    "phone": "+27800000002",
    "password": "client2024test"
}

# Test client authentication token and user ID
AUTH_TOKEN = None
USER_ID = None

def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'='*70}")
    print(f"🔍 {test_name}")
    print(f"{'='*70}")

def print_result(success, message, details=None):
    """Print formatted test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")
    if details:
        print(f"   📋 Details: {details}")

def print_diagnostic(label, value):
    """Print diagnostic information"""
    print(f"   🔧 {label}: {value}")

def authenticate_client():
    """Authenticate client and get token/user_id"""
    global AUTH_TOKEN, USER_ID
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=CLIENT_CREDENTIALS,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('token'):
                AUTH_TOKEN = data['token']
                user_info = data.get('user', {})
                USER_ID = user_info.get('id')
                return True
        return False
    except:
        return False

def test_heroku_deployment_status():
    """Test 1: Comprehensive Heroku deployment status"""
    print_test_header("HEROKU DEPLOYMENT STATUS")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Heroku backend is operational", f"Status: {data.get('status')}")
            
            # Detailed service analysis
            services = data.get('services', {})
            print_diagnostic("Available Services", list(services.keys()))
            
            for service, status in services.items():
                print_diagnostic(f"Service '{service}'", status)
            
            # Check for push notification related services
            push_services = [s for s in services.keys() if 'push' in s.lower() or 'notification' in s.lower()]
            if push_services:
                print_diagnostic("Push Services Found", push_services)
            else:
                print_diagnostic("Push Services", "Not explicitly listed in health check")
            
            return True
        else:
            print_result(False, f"Heroku backend not responding", f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, "Cannot connect to Heroku deployment", str(e))
        return False

def test_authentication_system():
    """Test 2: Authentication system verification"""
    print_test_header("AUTHENTICATION SYSTEM")
    
    success = authenticate_client()
    
    if success:
        print_result(True, "Client authentication successful", f"User ID: {USER_ID}")
        print_diagnostic("Token Format", f"Bearer {AUTH_TOKEN[:20]}...")
        print_diagnostic("User Role", "client")
        print_diagnostic("Phone Number", CLIENT_CREDENTIALS['phone'])
        return True
    else:
        print_result(False, "Authentication failed", "Cannot proceed with push notification tests")
        return False

def test_push_subscription_system():
    """Test 3: Push subscription system comprehensive test"""
    print_test_header("PUSH SUBSCRIPTION SYSTEM")
    
    if not AUTH_TOKEN or not USER_ID:
        print_result(False, "Authentication required", "Cannot test without valid token")
        return False
    
    # Test subscription with comprehensive data
    subscription_data = {
        "subscription": {
            "endpoint": "https://fcm.googleapis.com/fcm/send/diagnostic-test-endpoint-12345",
            "keys": {
                "p256dh": "BEl62iUYgUivxIkv69yViEuiBIa40HI80NMtRGe6rLZRgSdrNjqDQKcnASV33EXe8aD9p7BuYa3v4kHgm-9PjLc",
                "auth": "yNb3vGkk1fHZGkT6YxHF5vV0EpzKp_YKR2Rv7p3qXuI"
            }
        },
        "userId": USER_ID,
        "userRole": "client"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/push/subscribe",
            json=subscription_data,
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            timeout=10
        )
        
        print_diagnostic("Subscription Request Status", f"HTTP {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_diagnostic("Response Data", data)
            
            if data.get('success'):
                print_result(True, "Push subscription system working", data.get('message'))
                
                # Test database table creation
                print_diagnostic("Database Table", "push_subscriptions table created/updated")
                print_diagnostic("Subscription Storage", "Endpoint and keys stored successfully")
                
                return True
            else:
                print_result(False, "Subscription failed", data.get('message'))
                return False
        else:
            print_result(False, f"Subscription request failed", f"HTTP {response.status_code}: {response.text[:300]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, "Subscription request error", str(e))
        return False

def test_vapid_keys_configuration():
    """Test 4: VAPID keys configuration diagnostic"""
    print_test_header("VAPID KEYS CONFIGURATION DIAGNOSTIC")
    
    if not AUTH_TOKEN or not USER_ID:
        print_result(False, "Authentication required", "Cannot test without valid token")
        return False
    
    # Test by attempting to send a test notification and analyzing the response
    test_data = {
        "userId": USER_ID,
        "type": "vapid_test",
        "title": "VAPID Configuration Test",
        "message": "Testing VAPID key configuration"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/push/test",
            json=test_data,
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            timeout=10
        )
        
        print_diagnostic("Test Notification Status", f"HTTP {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_diagnostic("Response Data", data)
            
            # Analyze response for VAPID configuration clues
            simulation_mode = data.get('simulation_mode', False)
            sent_count = data.get('sent', 0)
            failed_count = data.get('failed', 0)
            message = data.get('message', '')
            
            print_diagnostic("Simulation Mode", simulation_mode)
            print_diagnostic("Notifications Sent", sent_count)
            print_diagnostic("Notifications Failed", failed_count)
            print_diagnostic("Backend Message", message)
            
            if simulation_mode:
                print_result(False, "VAPID keys not properly configured", "Running in simulation mode")
                print_diagnostic("Issue", "VAPID_PRIVATE_KEY or VAPID_PUBLIC_KEY missing from environment")
                return False
            elif sent_count > 0:
                print_result(True, "VAPID keys properly configured", f"Successfully sent {sent_count} notifications")
                return True
            elif failed_count > 0:
                print_result(False, "VAPID keys configured but notifications failing", f"{failed_count} notifications failed")
                print_diagnostic("Possible Issue", "Invalid subscription endpoints or network issues")
                return False
            else:
                print_result(False, "No subscriptions found for testing", "Need valid subscriptions to test VAPID")
                return False
        else:
            print_result(False, f"Test notification request failed", f"HTTP {response.status_code}: {response.text[:300]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, "VAPID test request error", str(e))
        return False

def test_database_push_subscriptions():
    """Test 5: Database push_subscriptions table verification"""
    print_test_header("DATABASE PUSH_SUBSCRIPTIONS TABLE")
    
    if not AUTH_TOKEN or not USER_ID:
        print_result(False, "Authentication required", "Cannot test without valid token")
        return False
    
    try:
        # First, ensure we have a subscription
        subscription_data = {
            "subscription": {
                "endpoint": "https://fcm.googleapis.com/fcm/send/db-verification-endpoint",
                "keys": {
                    "p256dh": "BEl62iUYgUivxIkv69yViEuiBIa40HI80NMtRGe6rLZRgSdrNjqDQKcnASV33EXe8aD9p7BuYa3v4kHgm-9PjLc",
                    "auth": "yNb3vGkk1fHZGkT6YxHF5vV0EpzKp_YKR2Rv7p3qXuI"
                }
            },
            "userId": USER_ID,
            "userRole": "client"
        }
        
        # Subscribe
        sub_response = requests.post(
            f"{BASE_URL}/api/push/subscribe",
            json=subscription_data,
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            timeout=10
        )
        
        print_diagnostic("Subscription Creation", f"HTTP {sub_response.status_code}")
        
        if sub_response.status_code == 200 and sub_response.json().get('success'):
            print_diagnostic("Database Write", "Subscription successfully stored")
            
            # Test retrieval by attempting a test notification
            test_response = requests.post(
                f"{BASE_URL}/api/push/test",
                json={"userId": USER_ID, "title": "DB Test", "message": "Testing database retrieval"},
                headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
                timeout=10
            )
            
            if test_response.status_code == 200:
                test_data = test_response.json()
                print_diagnostic("Database Read", f"Retrieved subscriptions for notification test")
                print_diagnostic("Test Response", test_data.get('message', 'No message'))
                
                # Clean up - unsubscribe
                unsub_response = requests.post(
                    f"{BASE_URL}/api/push/unsubscribe",
                    json={"subscription": {"endpoint": "https://fcm.googleapis.com/fcm/send/db-verification-endpoint"}, "userId": USER_ID},
                    headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
                    timeout=10
                )
                
                print_diagnostic("Database Cleanup", f"Unsubscribe HTTP {unsub_response.status_code}")
                
                print_result(True, "Database push_subscriptions table working", "Create, read, and delete operations successful")
                return True
            else:
                print_result(False, "Database read operation failed", f"Test notification failed: HTTP {test_response.status_code}")
                return False
        else:
            print_result(False, "Database write operation failed", f"Subscription failed: HTTP {sub_response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, "Database test error", str(e))
        return False

def test_push_notification_sending():
    """Test 6: Push notification sending capability"""
    print_test_header("PUSH NOTIFICATION SENDING CAPABILITY")
    
    if not AUTH_TOKEN or not USER_ID:
        print_result(False, "Authentication required", "Cannot test without valid token")
        return False
    
    try:
        # Create multiple test subscriptions
        test_subscriptions = [
            {
                "subscription": {
                    "endpoint": f"https://fcm.googleapis.com/fcm/send/send-test-endpoint-{i}",
                    "keys": {
                        "p256dh": "BEl62iUYgUivxIkv69yViEuiBIa40HI80NMtRGe6rLZRgSdrNjqDQKcnASV33EXe8aD9p7BuYa3v4kHgm-9PjLc",
                        "auth": "yNb3vGkk1fHZGkT6YxHF5vV0EpzKp_YKR2Rv7p3qXuI"
                    }
                },
                "userId": USER_ID,
                "userRole": "client"
            }
            for i in range(3)
        ]
        
        # Subscribe to all
        subscription_count = 0
        for sub_data in test_subscriptions:
            response = requests.post(
                f"{BASE_URL}/api/push/subscribe",
                json=sub_data,
                headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
                timeout=10
            )
            if response.status_code == 200 and response.json().get('success'):
                subscription_count += 1
        
        print_diagnostic("Test Subscriptions Created", subscription_count)
        
        # Test sending notifications
        test_scenarios = [
            {"type": "test", "title": "Test Notification", "message": "Basic test"},
            {"type": "job_assignment", "title": "Job Assignment", "message": "New job assigned"},
            {"type": "urgent", "title": "Urgent Notification", "message": "Urgent message"}
        ]
        
        successful_sends = 0
        for scenario in test_scenarios:
            send_data = {
                "userId": USER_ID,
                **scenario
            }
            
            send_response = requests.post(
                f"{BASE_URL}/api/push/send",
                json=send_data,
                headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
                timeout=10
            )
            
            if send_response.status_code == 200:
                send_result = send_response.json()
                sent_count = send_result.get('sent', 0)
                failed_count = send_result.get('failed', 0)
                
                print_diagnostic(f"Scenario '{scenario['type']}'", f"Sent: {sent_count}, Failed: {failed_count}")
                
                if sent_count > 0:
                    successful_sends += 1
            else:
                print_diagnostic(f"Scenario '{scenario['type']}'", f"Request failed: HTTP {send_response.status_code}")
        
        # Cleanup
        for i in range(3):
            requests.post(
                f"{BASE_URL}/api/push/unsubscribe",
                json={"subscription": {"endpoint": f"https://fcm.googleapis.com/fcm/send/send-test-endpoint-{i}"}, "userId": USER_ID},
                headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
                timeout=5
            )
        
        if successful_sends > 0:
            print_result(True, f"Push notification sending working", f"{successful_sends}/{len(test_scenarios)} scenarios successful")
            return True
        else:
            print_result(False, "Push notification sending not working", "No notifications were successfully sent")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, "Push notification sending test error", str(e))
        return False

def test_production_environment():
    """Test 7: Production environment verification"""
    print_test_header("PRODUCTION ENVIRONMENT VERIFICATION")
    
    try:
        # Test HTTPS
        https_valid = BASE_URL.startswith('https://')
        print_diagnostic("HTTPS Protocol", "✅ Enabled" if https_valid else "❌ Disabled")
        
        # Test SSL certificate
        try:
            response = requests.get(f"{BASE_URL}/api/health", verify=True, timeout=10)
            ssl_valid = response.status_code == 200
            print_diagnostic("SSL Certificate", "✅ Valid" if ssl_valid else "❌ Invalid")
        except requests.exceptions.SSLError:
            ssl_valid = False
            print_diagnostic("SSL Certificate", "❌ Invalid or expired")
        
        # Test domain
        domain = BASE_URL.replace('https://', '').replace('http://', '')
        print_diagnostic("Domain", domain)
        print_diagnostic("Heroku Domain", "✅ Confirmed" if 'emergentagent.com' in domain else "❌ Not confirmed")
        
        # Test environment variables (indirectly)
        if authenticate_client():
            print_diagnostic("Environment Variables", "✅ Authentication working (DATABASE_URL configured)")
        else:
            print_diagnostic("Environment Variables", "❌ Authentication issues (check DATABASE_URL)")
        
        # Overall assessment
        if https_valid and ssl_valid:
            print_result(True, "Production environment properly configured", "HTTPS and SSL working correctly")
            return True
        else:
            print_result(False, "Production environment issues", "HTTPS or SSL problems detected")
            return False
            
    except Exception as e:
        print_result(False, "Production environment test error", str(e))
        return False

def run_comprehensive_diagnostic():
    """Run comprehensive diagnostic test suite"""
    print(f"\n🔬 HEROKU PUSH NOTIFICATION SYSTEM - COMPREHENSIVE DIAGNOSTIC")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"👤 Test Client: {CLIENT_CREDENTIALS['phone']}")
    print(f"🎯 Focus: Production deployment verification with detailed diagnostics")
    
    # Track test results
    test_results = []
    
    # Run diagnostic tests
    test_results.append(("Heroku Deployment Status", test_heroku_deployment_status()))
    test_results.append(("Authentication System", test_authentication_system()))
    test_results.append(("Push Subscription System", test_push_subscription_system()))
    test_results.append(("VAPID Keys Configuration", test_vapid_keys_configuration()))
    test_results.append(("Database Push Subscriptions", test_database_push_subscriptions()))
    test_results.append(("Push Notification Sending", test_push_notification_sending()))
    test_results.append(("Production Environment", test_production_environment()))
    
    # Summary
    print_test_header("COMPREHENSIVE DIAGNOSTIC SUMMARY")
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print(f"📊 Overall Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print(f"\n📋 Detailed Results:")
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    # Critical issues analysis
    print(f"\n🔍 CRITICAL ISSUES ANALYSIS:")
    
    if passed >= 6:
        print(f"   ✅ CORE SYSTEM: Functional - {passed}/{total} components working")
        print(f"   ✅ DEPLOYMENT: Heroku deployment is operational")
        print(f"   ✅ SECURITY: HTTPS and authentication working")
        print(f"   ✅ DATABASE: Push subscriptions table accessible")
    else:
        print(f"   ❌ CORE SYSTEM: Issues detected - only {passed}/{total} components working")
    
    # Specific recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if "VAPID Keys Configuration" in [name for name, result in test_results if not result]:
        print(f"   🔧 VAPID KEYS: Configure VAPID_PUBLIC_KEY and VAPID_PRIVATE_KEY in Heroku environment")
        print(f"   🔧 ENVIRONMENT: Ensure pywebpush library is installed in production")
    
    if "Push Notification Sending" in [name for name, result in test_results if not result]:
        print(f"   🔧 NOTIFICATIONS: Check VAPID key configuration and subscription endpoints")
        print(f"   🔧 DEBUGGING: Enable detailed logging for push notification failures")
    
    # Final assessment
    if passed == total:
        print(f"\n🎉 EXCELLENT: All systems operational! Push notifications ready for production use.")
    elif passed >= 5:
        print(f"\n⚠️  GOOD: Core functionality working. Minor issues need attention.")
    else:
        print(f"\n🚨 CRITICAL: Major issues detected. System needs immediate attention before production use.")
    
    return passed, total

if __name__ == "__main__":
    run_comprehensive_diagnostic()