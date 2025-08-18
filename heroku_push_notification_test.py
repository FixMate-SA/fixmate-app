#!/usr/bin/env python3
"""
Heroku Push Notification System Testing
Test the production deployment of push notification endpoints on Heroku
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

# Test client authentication token (will be obtained during login)
AUTH_TOKEN = None

def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")

def print_result(success, message, details=None):
    """Print formatted test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")
    if details:
        print(f"   Details: {details}")

def test_health_check():
    """Test 1: Basic health check to verify backend is running"""
    print_test_header("HEALTH CHECK - Backend Availability")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Backend is running on Heroku", f"Status: {data.get('status', 'unknown')}")
            
            # Check services status
            services = data.get('services', {})
            for service, status in services.items():
                print(f"   📊 {service}: {status}")
            
            return True
        else:
            print_result(False, f"Health check failed", f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, "Cannot connect to Heroku backend", str(e))
        return False

def test_client_authentication():
    """Test 2: Client authentication and token generation"""
    print_test_header("CLIENT AUTHENTICATION")
    global AUTH_TOKEN
    
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
                print_result(True, "Client authentication successful", 
                           f"Role: {user_info.get('role')}, ID: {user_info.get('id')}")
                return True
            else:
                print_result(False, "Authentication failed", data.get('message', 'Unknown error'))
                return False
        else:
            print_result(False, f"Authentication request failed", f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, "Authentication request error", str(e))
        return False

def test_push_subscribe_endpoint():
    """Test 3: Push notification subscription endpoint"""
    print_test_header("PUSH NOTIFICATION SUBSCRIPTION")
    
    if not AUTH_TOKEN:
        print_result(False, "No authentication token available", "Cannot test without login")
        return False
    
    # Simulate a valid push subscription object
    test_subscription = {
        "endpoint": "https://fcm.googleapis.com/fcm/send/test-endpoint-123",
        "keys": {
            "p256dh": "BEl62iUYgUivxIkv69yViEuiBIa40HI80NMtRGe6rLZRgSdrNjqDQKcnASV33EXe8aD9p7BuYa3v4kHgm-9PjLc",
            "auth": "yNb3vGkk1fHZGkT6YxHF5vV0EpzKp_YKR2Rv7p3qXuI"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/push/subscribe",
            json={"subscription": test_subscription},
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_result(True, "Push subscription endpoint working", 
                           f"Message: {data.get('message')}")
                return True
            else:
                print_result(False, "Push subscription failed", data.get('message', 'Unknown error'))
                return False
        elif response.status_code == 401:
            print_result(False, "Authentication failed for push subscription", 
                        "Token may be invalid or endpoint requires different auth")
            return False
        else:
            print_result(False, f"Push subscription request failed", 
                        f"HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, "Push subscription request error", str(e))
        return False

def test_push_test_endpoint():
    """Test 4: Push notification test sending capability"""
    print_test_header("PUSH NOTIFICATION TEST SENDING")
    
    if not AUTH_TOKEN:
        print_result(False, "No authentication token available", "Cannot test without login")
        return False
    
    test_notification = {
        "title": "Test Notification",
        "body": "Testing push notification system on Heroku",
        "icon": "/icon-192x192.png"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/push/test",
            json=test_notification,
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_result(True, "Push test endpoint working", 
                           f"Message: {data.get('message')}")
                return True
            else:
                print_result(False, "Push test failed", data.get('message', 'Unknown error'))
                return False
        elif response.status_code == 401:
            print_result(False, "Authentication failed for push test", 
                        "Token may be invalid or endpoint requires different auth")
            return False
        else:
            print_result(False, f"Push test request failed", 
                        f"HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, "Push test request error", str(e))
        return False

def test_push_unsubscribe_endpoint():
    """Test 5: Push notification unsubscription functionality"""
    print_test_header("PUSH NOTIFICATION UNSUBSCRIPTION")
    
    if not AUTH_TOKEN:
        print_result(False, "No authentication token available", "Cannot test without login")
        return False
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/push/unsubscribe",
            json={"endpoint": "https://fcm.googleapis.com/fcm/send/test-endpoint-123"},
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_result(True, "Push unsubscribe endpoint working", 
                           f"Message: {data.get('message')}")
                return True
            else:
                print_result(False, "Push unsubscribe failed", data.get('message', 'Unknown error'))
                return False
        elif response.status_code == 401:
            print_result(False, "Authentication failed for push unsubscribe", 
                        "Token may be invalid or endpoint requires different auth")
            return False
        else:
            print_result(False, f"Push unsubscribe request failed", 
                        f"HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, "Push unsubscribe request error", str(e))
        return False

def test_push_send_endpoint():
    """Test 6: Targeted push notification sending"""
    print_test_header("TARGETED PUSH NOTIFICATION SENDING")
    
    if not AUTH_TOKEN:
        print_result(False, "No authentication token available", "Cannot test without login")
        return False
    
    test_message = {
        "title": "Job Assignment",
        "body": "You have been assigned a new plumbing job in Cape Town",
        "data": {
            "job_id": "job_test_123",
            "type": "job_assignment"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/push/send",
            json=test_message,
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_result(True, "Push send endpoint working", 
                           f"Message: {data.get('message')}")
                return True
            else:
                print_result(False, "Push send failed", data.get('message', 'Unknown error'))
                return False
        elif response.status_code == 401:
            print_result(False, "Authentication failed for push send", 
                        "Token may be invalid or endpoint requires different auth")
            return False
        else:
            print_result(False, f"Push send request failed", 
                        f"HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, "Push send request error", str(e))
        return False

def test_vapid_configuration():
    """Test 7: VAPID keys configuration verification"""
    print_test_header("VAPID KEYS CONFIGURATION")
    
    try:
        # Test if VAPID public key is accessible through health endpoint
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if push notification service is mentioned
            services = data.get('services', {})
            if 'push_notifications' in services or any('push' in service.lower() for service in services.keys()):
                print_result(True, "Push notification service detected in health check", 
                           f"Services: {list(services.keys())}")
            else:
                print_result(False, "Push notification service not found in health check", 
                           f"Available services: {list(services.keys())}")
            
            # Try to get VAPID public key from a dedicated endpoint if it exists
            try:
                vapid_response = requests.get(f"{BASE_URL}/api/push/vapid-public-key", timeout=5)
                if vapid_response.status_code == 200:
                    vapid_data = vapid_response.json()
                    if vapid_data.get('publicKey'):
                        print_result(True, "VAPID public key accessible", 
                                   f"Key length: {len(vapid_data['publicKey'])}")
                        return True
                    else:
                        print_result(False, "VAPID public key endpoint exists but no key returned", 
                                   str(vapid_data))
                        return False
                else:
                    print_result(False, "VAPID public key endpoint not accessible", 
                               f"HTTP {vapid_response.status_code}")
                    return False
            except:
                print_result(False, "VAPID public key endpoint not available", 
                           "Endpoint may not be implemented")
                return False
                
        else:
            print_result(False, "Cannot verify VAPID configuration", 
                        f"Health check failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, "VAPID configuration check error", str(e))
        return False

def test_database_connectivity():
    """Test 8: Database connectivity and push_subscriptions table"""
    print_test_header("DATABASE CONNECTIVITY & PUSH SUBSCRIPTIONS TABLE")
    
    if not AUTH_TOKEN:
        print_result(False, "No authentication token available", "Cannot test without login")
        return False
    
    try:
        # Test database connectivity through a simple API call that requires DB
        response = requests.get(
            f"{BASE_URL}/api/dashboard/{CLIENT_CREDENTIALS['phone'].replace('+', '').replace('27800000002', 'a89e82ac-dbf3-403e-ab47-4bb340445576')}",
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            timeout=10
        )
        
        if response.status_code == 200:
            print_result(True, "Database connectivity confirmed", 
                        "Dashboard API successfully accessed database")
            
            # Try to test push subscription storage by attempting a subscription
            test_subscription = {
                "endpoint": "https://fcm.googleapis.com/fcm/send/db-test-endpoint",
                "keys": {
                    "p256dh": "BEl62iUYgUivxIkv69yViEuiBIa40HI80NMtRGe6rLZRgSdrNjqDQKcnASV33EXe8aD9p7BuYa3v4kHgm-9PjLc",
                    "auth": "yNb3vGkk1fHZGkT6YxHF5vV0EpzKp_YKR2Rv7p3qXuI"
                }
            }
            
            sub_response = requests.post(
                f"{BASE_URL}/api/push/subscribe",
                json={"subscription": test_subscription},
                headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
                timeout=10
            )
            
            if sub_response.status_code == 200:
                sub_data = sub_response.json()
                if sub_data.get('success'):
                    print_result(True, "Push subscriptions table accessible", 
                               "Successfully stored test subscription")
                    return True
                else:
                    print_result(False, "Push subscriptions table issue", 
                               sub_data.get('message', 'Unknown error'))
                    return False
            else:
                print_result(False, "Cannot verify push subscriptions table", 
                           f"Subscription test failed: HTTP {sub_response.status_code}")
                return False
                
        else:
            print_result(False, "Database connectivity issue", 
                        f"Dashboard API failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_result(False, "Database connectivity test error", str(e))
        return False

def test_https_secure_context():
    """Test 9: HTTPS secure context verification"""
    print_test_header("HTTPS SECURE CONTEXT VERIFICATION")
    
    try:
        if BASE_URL.startswith('https://'):
            print_result(True, "HTTPS secure context confirmed", 
                        f"Base URL: {BASE_URL}")
            
            # Test SSL certificate validity
            response = requests.get(f"{BASE_URL}/api/health", timeout=10, verify=True)
            if response.status_code == 200:
                print_result(True, "SSL certificate valid", 
                            "HTTPS connection established successfully")
                return True
            else:
                print_result(False, "SSL certificate issue", 
                            f"HTTPS request failed: HTTP {response.status_code}")
                return False
        else:
            print_result(False, "Not using HTTPS", 
                        f"Base URL: {BASE_URL} - Push notifications require HTTPS")
            return False
            
    except requests.exceptions.SSLError as e:
        print_result(False, "SSL certificate error", str(e))
        return False
    except requests.exceptions.RequestException as e:
        print_result(False, "HTTPS verification error", str(e))
        return False

def run_comprehensive_heroku_test():
    """Run comprehensive Heroku push notification system test"""
    print(f"\n🚀 HEROKU PUSH NOTIFICATION SYSTEM TESTING")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"👤 Test Client: {CLIENT_CREDENTIALS['phone']}")
    
    # Track test results
    test_results = []
    
    # Run all tests
    test_results.append(("Health Check", test_health_check()))
    test_results.append(("Client Authentication", test_client_authentication()))
    test_results.append(("Push Subscribe Endpoint", test_push_subscribe_endpoint()))
    test_results.append(("Push Test Endpoint", test_push_test_endpoint()))
    test_results.append(("Push Unsubscribe Endpoint", test_push_unsubscribe_endpoint()))
    test_results.append(("Push Send Endpoint", test_push_send_endpoint()))
    test_results.append(("VAPID Configuration", test_vapid_configuration()))
    test_results.append(("Database Connectivity", test_database_connectivity()))
    test_results.append(("HTTPS Secure Context", test_https_secure_context()))
    
    # Summary
    print_test_header("TEST SUMMARY")
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print(f"📊 Overall Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print(f"\n📋 Detailed Results:")
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    # Final assessment
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! Heroku push notification system is fully functional.")
    elif passed >= total * 0.8:
        print(f"\n⚠️  MOSTLY WORKING: {total-passed} issues found but core functionality appears operational.")
    else:
        print(f"\n🚨 CRITICAL ISSUES: {total-passed} major problems detected. System needs attention.")
    
    return passed, total

if __name__ == "__main__":
    run_comprehensive_heroku_test()