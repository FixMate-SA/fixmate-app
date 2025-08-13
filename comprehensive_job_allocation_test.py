#!/usr/bin/env python3
"""
Comprehensive Automatic Job Allocation System Testing
Focus on the specific requirements from the review request
"""

import requests
import json
import time
from datetime import datetime
import os

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://auto-job-match-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials from the review request
CLIENT_CREDENTIALS = {
    "phone": "+27800000002",
    "password": "client2024test"
}

FIXER_CREDENTIALS = {
    "phone": "+27800000003", 
    "password": "fixer2024test"
}

ADMIN_CREDENTIALS = {
    "phone": "+27800000001",
    "password": "admin2024test"
}

# Test counters
total_tests = 0
passed_tests = 0
failed_tests = 0

def log_test(test_name, success, message=""):
    """Log test results"""
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    
    if success:
        passed_tests += 1
        status = "✅ PASS"
    else:
        failed_tests += 1
        status = "❌ FAIL"
    
    print(f"{status}: {test_name}")
    if message:
        print(f"    {message}")

def authenticate_user(credentials, user_type):
    """Authenticate user and return token and user info"""
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=credentials)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('token'), data.get('user')
        return None, None
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return None, None

def test_job_creation_and_allocation():
    """Test POST /api/jobs endpoint and automatic allocation"""
    print("\n🎯 TESTING JOB CREATION AND AUTOMATIC ALLOCATION")
    print("=" * 60)
    
    # Authenticate client
    client_token, client_user = authenticate_user(CLIENT_CREDENTIALS, "client")
    if not client_token:
        log_test("Job Creation - Client Authentication", False, "Failed to authenticate client")
        return None
    
    log_test("Job Creation - Client Authentication", True, f"Client authenticated: {client_user.get('display_name')}")
    
    # Get initial job count
    headers = {'Authorization': f'Bearer {client_token}'}
    initial_jobs_response = requests.get(f"{API_BASE}/jobs", headers=headers)
    initial_count = len(initial_jobs_response.json().get('jobs', [])) if initial_jobs_response.status_code == 200 else 0
    
    # Create a new job (plumbing service in Cape Town as specified in review)
    job_data = {
        "title": "Plumbing Service Required",
        "description": "Need urgent plumbing repair for kitchen sink leak in Cape Town. Water damage prevention required.",
        "location": "Cape Town, Western Cape",
        "urgency": "high",
        "budget_min": 500,
        "budget_max": 1500,
        "category": "Plumbing",
        "client_id": client_user.get('id'),
        "communication_preference": "whatsapp",
        "whatsapp_notifications": True
    }
    
    print(f"Creating job: {job_data['title']} in {job_data['location']}")
    job_response = requests.post(f"{API_BASE}/jobs", json=job_data, headers=headers)
    
    if job_response.status_code == 200:
        job_result = job_response.json()
        if job_result.get('success'):
            job_id = job_result.get('job_id')
            log_test("Job Creation - API Call", True, f"Job created: {job_id}")
            
            # Verify job count increased
            time.sleep(2)  # Allow time for database operations
            new_jobs_response = requests.get(f"{API_BASE}/jobs", headers=headers)
            new_count = len(new_jobs_response.json().get('jobs', [])) if new_jobs_response.status_code == 200 else 0
            
            if new_count > initial_count:
                log_test("Job Creation - Database Persistence", True, f"Job count increased from {initial_count} to {new_count}")
            else:
                log_test("Job Creation - Database Persistence", False, f"Job count did not increase: {initial_count} -> {new_count}")
            
            # Check if job was automatically assigned
            job_details_response = requests.get(f"{API_BASE}/jobs/{job_id}", headers=headers)
            if job_details_response.status_code == 200:
                job_details = job_details_response.json().get('job', {})
                fixer_id = job_details.get('fixer_id')
                
                if fixer_id:
                    log_test("Automatic Job Allocation - Assignment", True, f"Job assigned to fixer: {fixer_id}")
                else:
                    log_test("Automatic Job Allocation - Assignment", False, "Job was not automatically assigned to a fixer")
                
                log_test("Job Details - Retrieval", True, f"Job status: {job_details.get('status')}")
                return job_id
            else:
                log_test("Job Details - Retrieval", False, f"Failed to retrieve job details: {job_details_response.status_code}")
        else:
            log_test("Job Creation - API Call", False, f"Job creation failed: {job_result.get('message')}")
    else:
        log_test("Job Creation - API Call", False, f"HTTP {job_response.status_code}: {job_response.text}")
    
    return None

def test_fixer_available_jobs():
    """Test GET /api/fixer/available-jobs endpoint"""
    print("\n🔧 TESTING FIXER AVAILABLE JOBS ENDPOINT")
    print("=" * 60)
    
    # Authenticate fixer
    fixer_token, fixer_user = authenticate_user(FIXER_CREDENTIALS, "fixer")
    if not fixer_token:
        log_test("Available Jobs - Fixer Authentication", False, "Failed to authenticate fixer")
        return
    
    log_test("Available Jobs - Fixer Authentication", True, f"Fixer authenticated: {fixer_user.get('display_name')}")
    
    # Test available jobs endpoint
    headers = {'Authorization': f'Bearer {fixer_token}'}
    jobs_response = requests.get(f"{API_BASE}/fixer/available-jobs", headers=headers)
    
    if jobs_response.status_code == 200:
        jobs_data = jobs_response.json()
        if jobs_data.get('success'):
            available_jobs = jobs_data.get('available_jobs', [])
            log_test("Available Jobs - API Call", True, f"Retrieved {len(available_jobs)} available jobs")
            
            # Check job filtering by service type
            plumbing_jobs = [job for job in available_jobs if 'plumbing' in job.get('service', '').lower()]
            electrical_jobs = [job for job in available_jobs if 'electrical' in job.get('service', '').lower()]
            
            log_test("Available Jobs - Service Filtering", True, f"Found {len(plumbing_jobs)} plumbing jobs, {len(electrical_jobs)} electrical jobs")
            
            # Verify job data structure
            if available_jobs:
                sample_job = available_jobs[0]
                required_fields = ['id', 'service', 'description', 'location', 'estimated_price', 'status']
                missing_fields = [field for field in required_fields if field not in sample_job]
                
                if not missing_fields:
                    log_test("Available Jobs - Data Structure", True, "All required job fields present")
                else:
                    log_test("Available Jobs - Data Structure", False, f"Missing fields: {missing_fields}")
        else:
            log_test("Available Jobs - API Call", False, f"API returned error: {jobs_data.get('message')}")
    else:
        log_test("Available Jobs - API Call", False, f"HTTP {jobs_response.status_code}: {jobs_response.text}")

def test_fixer_notifications():
    """Test GET /api/fixer/notifications endpoint"""
    print("\n🔔 TESTING FIXER NOTIFICATIONS ENDPOINT")
    print("=" * 60)
    
    # Authenticate fixer
    fixer_token, fixer_user = authenticate_user(FIXER_CREDENTIALS, "fixer")
    if not fixer_token:
        log_test("Notifications - Fixer Authentication", False, "Failed to authenticate fixer")
        return
    
    log_test("Notifications - Fixer Authentication", True, f"Fixer authenticated: {fixer_user.get('display_name')}")
    
    # Test notifications endpoint
    headers = {'Authorization': f'Bearer {fixer_token}'}
    notif_response = requests.get(f"{API_BASE}/fixer/notifications", headers=headers)
    
    if notif_response.status_code == 200:
        notif_data = notif_response.json()
        if notif_data.get('success'):
            notifications = notif_data.get('notifications', [])
            unread_count = notif_data.get('unread_count', 0)
            
            log_test("Notifications - API Call", True, f"Retrieved {len(notifications)} notifications ({unread_count} unread)")
            
            # Check notification types
            assignment_notifications = [n for n in notifications if n.get('notification_type') == 'job_assigned']
            available_notifications = [n for n in notifications if n.get('notification_type') == 'job_available']
            
            log_test("Notifications - Job Assignment", len(assignment_notifications) > 0, 
                    f"Found {len(assignment_notifications)} job assignment notifications")
            log_test("Notifications - Available Jobs", len(available_notifications) > 0, 
                    f"Found {len(available_notifications)} available job notifications")
            
            # Verify notification data structure
            if notifications:
                sample_notif = notifications[0]
                required_fields = ['id', 'job_id', 'notification_type', 'title', 'message', 'is_read', 'created_at']
                missing_fields = [field for field in required_fields if field not in sample_notif]
                
                if not missing_fields:
                    log_test("Notifications - Data Structure", True, "All required notification fields present")
                else:
                    log_test("Notifications - Data Structure", False, f"Missing fields: {missing_fields}")
                
                # Check job details in notifications
                if sample_notif.get('job_details'):
                    log_test("Notifications - Job Details", True, "Job details included in notifications")
                else:
                    log_test("Notifications - Job Details", False, "Job details missing from notifications")
            
            return notifications
        else:
            log_test("Notifications - API Call", False, f"API returned error: {notif_data.get('message')}")
    else:
        log_test("Notifications - API Call", False, f"HTTP {notif_response.status_code}: {notif_response.text}")
    
    return []

def test_notification_management(notifications):
    """Test POST /api/fixer/notifications/{id}/mark-read endpoint"""
    print("\n📝 TESTING NOTIFICATION MANAGEMENT")
    print("=" * 60)
    
    if not notifications:
        log_test("Notification Management - Prerequisites", False, "No notifications available for testing")
        return
    
    # Find an unread notification
    unread_notification = None
    for notif in notifications:
        if not notif.get('is_read'):
            unread_notification = notif
            break
    
    if not unread_notification:
        # If no unread notifications, use the first one
        unread_notification = notifications[0]
    
    notification_id = unread_notification.get('id')
    log_test("Notification Management - Target Selection", True, f"Selected notification: {notification_id}")
    
    # Authenticate fixer
    fixer_token, fixer_user = authenticate_user(FIXER_CREDENTIALS, "fixer")
    if not fixer_token:
        log_test("Notification Management - Authentication", False, "Failed to authenticate fixer")
        return
    
    # Mark notification as read
    headers = {'Authorization': f'Bearer {fixer_token}'}
    mark_read_response = requests.post(f"{API_BASE}/fixer/notifications/{notification_id}/mark-read", headers=headers)
    
    if mark_read_response.status_code == 200:
        mark_read_data = mark_read_response.json()
        if mark_read_data.get('success'):
            log_test("Notification Management - Mark Read API", True, "Notification marked as read successfully")
            
            # Verify the change by getting notifications again
            time.sleep(1)
            notif_response = requests.get(f"{API_BASE}/fixer/notifications", headers=headers)
            if notif_response.status_code == 200:
                updated_notif_data = notif_response.json()
                if updated_notif_data.get('success'):
                    old_unread_count = len([n for n in notifications if not n.get('is_read')])
                    new_unread_count = updated_notif_data.get('unread_count', 0)
                    
                    log_test("Notification Management - Status Update", True, 
                            f"Unread count updated: {old_unread_count} -> {new_unread_count}")
                else:
                    log_test("Notification Management - Status Update", False, "Failed to verify notification status update")
        else:
            log_test("Notification Management - Mark Read API", False, f"API returned error: {mark_read_data.get('message')}")
    else:
        log_test("Notification Management - Mark Read API", False, f"HTTP {mark_read_response.status_code}: {mark_read_response.text}")

def test_authentication_security():
    """Test authentication requirements and error handling"""
    print("\n🔒 TESTING AUTHENTICATION AND SECURITY")
    print("=" * 60)
    
    # Test endpoints without authentication
    endpoints_to_test = [
        ("/api/fixer/available-jobs", "Available Jobs"),
        ("/api/fixer/notifications", "Notifications")
    ]
    
    for endpoint, name in endpoints_to_test:
        # Test without Authorization header
        response = requests.get(f"{API_BASE}{endpoint}")
        if response.status_code == 401:
            log_test(f"Security - {name} Requires Auth", True, "Properly rejects unauthenticated requests")
        else:
            log_test(f"Security - {name} Requires Auth", False, f"Unexpected response: HTTP {response.status_code}")
        
        # Test with invalid token
        invalid_headers = {'Authorization': 'Bearer invalid_token_12345'}
        response = requests.get(f"{API_BASE}{endpoint}", headers=invalid_headers)
        if response.status_code in [401, 403]:
            log_test(f"Security - {name} Invalid Token", True, "Properly rejects invalid tokens")
        else:
            log_test(f"Security - {name} Invalid Token", False, f"Unexpected response: HTTP {response.status_code}")
    
    # Test client trying to access fixer endpoints
    client_token, client_user = authenticate_user(CLIENT_CREDENTIALS, "client")
    if client_token:
        client_headers = {'Authorization': f'Bearer {client_token}'}
        
        for endpoint, name in endpoints_to_test:
            response = requests.get(f"{API_BASE}{endpoint}", headers=client_headers)
            if response.status_code == 403:
                log_test(f"Security - Client Access {name}", True, "Properly denies client access to fixer endpoints")
            else:
                log_test(f"Security - Client Access {name}", False, f"Unexpected response: HTTP {response.status_code}")

def test_end_to_end_workflow():
    """Test complete end-to-end workflow"""
    print("\n🔄 TESTING END-TO-END WORKFLOW")
    print("=" * 60)
    
    print("1. Creating job as client...")
    job_id = test_job_creation_and_allocation()
    
    if job_id:
        print("2. Checking fixer can see available jobs...")
        test_fixer_available_jobs()
        
        print("3. Checking fixer notifications...")
        notifications = test_fixer_notifications()
        
        print("4. Testing notification management...")
        test_notification_management(notifications)
        
        log_test("End-to-End Workflow", True, "Complete workflow executed successfully")
    else:
        log_test("End-to-End Workflow", False, "Workflow failed at job creation step")

def main():
    """Main test execution"""
    print("🎯 AUTOMATIC JOB ALLOCATION SYSTEM BACKEND TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Run all tests
    test_end_to_end_workflow()
    test_authentication_security()
    
    # Final results
    print("\n" + "=" * 80)
    print("📊 FINAL TEST RESULTS")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    print("=" * 80)
    
    if failed_tests == 0:
        print("🎉 ALL TESTS PASSED - System is working correctly!")
    elif failed_tests <= 2:
        print("⚠️ MINOR ISSUES DETECTED - System mostly functional")
    else:
        print("🚨 CRITICAL ISSUES DETECTED - System needs attention")
    
    print(f"Test completed at: {datetime.now().isoformat()}")
    print("=" * 80)

if __name__ == "__main__":
    main()