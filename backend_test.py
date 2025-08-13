#!/usr/bin/env python3
"""
Comprehensive Backend Testing for FixMate-SA Automatic Job Allocation System
Testing the new job allocation system with notifications and fixer management
"""

import requests
import json
import time
from datetime import datetime
import os
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://7309dccc-5109-4150-b632-8181bb5fde8e.preview.emergentagent.com')
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
    print()

def make_request(method, endpoint, headers=None, data=None, json_data=None):
    """Make HTTP request with error handling"""
    try:
        url = f"{API_BASE}{endpoint}"
        print(f"🔗 Making {method} request to: {url}")
        
        # Set default headers
        if headers is None:
            headers = {}
        headers.setdefault('Content-Type', 'application/json')
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=30, verify=False)
        elif method.upper() == 'POST':
            if json_data:
                response = requests.post(url, headers=headers, json=json_data, timeout=30, verify=False)
            else:
                response = requests.post(url, headers=headers, data=data, timeout=30, verify=False)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=json_data, timeout=30, verify=False)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=30, verify=False)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"📡 Response: HTTP {response.status_code}")
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return None

def authenticate_user(credentials, user_type="client"):
    """Authenticate user and return token"""
    try:
        response = make_request('POST', '/auth/login', json_data=credentials)
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('token'):
                print(f"✅ {user_type.title()} authentication successful")
                return data['token'], data.get('user', {})
            else:
                print(f"❌ {user_type.title()} authentication failed: {data.get('message', 'Unknown error')}")
                return None, None
        else:
            print(f"❌ {user_type.title()} authentication failed: HTTP {response.status_code if response else 'No response'}")
            return None, None
            
    except Exception as e:
        print(f"❌ {user_type.title()} authentication error: {str(e)}")
        return None, None

def test_job_creation_and_allocation():
    """Test 1: Create job and verify automatic allocation"""
    print("🔄 Testing Job Creation and Automatic Allocation...")
    
    # Authenticate client
    client_token, client_user = authenticate_user(CLIENT_CREDENTIALS, "client")
    if not client_token:
        log_test("Job Creation - Client Authentication", False, "Failed to authenticate client")
        return None
    
    log_test("Job Creation - Client Authentication", True, f"Client authenticated: {client_user.get('display_name', 'Unknown')}")
    
    # Get initial job count for verification
    headers = {'Authorization': f'Bearer {client_token}'}
    initial_jobs_response = make_request('GET', '/jobs', headers=headers)
    initial_job_count = 0
    
    if initial_jobs_response and initial_jobs_response.status_code == 200:
        initial_data = initial_jobs_response.json()
        initial_job_count = len(initial_data.get('jobs', []))
        print(f"📊 Initial job count: {initial_job_count}")
    
    # Create test job data as specified in review request
    job_data = {
        "title": "Electrical Repair Needed",
        "description": "Need urgent electrical repair for flickering lights in office building",
        "location": "Cape Town, South Africa",
        "urgency": "high",
        "budget_min": 500,
        "budget_max": 1500,
        "category": "Electrical",
        "client_id": client_user.get('id', 'a89e82ac-dbf3-403e-ab47-4bb340445576')
    }
    
    # Create the job
    create_response = make_request('POST', '/jobs', headers=headers, json_data=job_data)
    
    if not create_response:
        log_test("Job Creation - API Call", False, "No response from job creation endpoint")
        return None
    
    if create_response.status_code != 200:
        log_test("Job Creation - API Call", False, f"HTTP {create_response.status_code}: {create_response.text}")
        return None
    
    try:
        create_data = create_response.json()
    except:
        log_test("Job Creation - API Call", False, "Invalid JSON response")
        return None
    
    if not create_data.get('success'):
        log_test("Job Creation - API Call", False, f"Job creation failed: {create_data.get('message', 'Unknown error')}")
        return None
    
    job_id = create_data.get('job_id')
    if not job_id:
        log_test("Job Creation - API Call", False, "No job_id returned")
        return None
    
    log_test("Job Creation - API Call", True, f"Job created successfully: {job_id}")
    
    # Wait a moment for allocation to process
    time.sleep(2)
    
    # Verify job was created by checking updated job count
    updated_jobs_response = make_request('GET', '/jobs', headers=headers)
    if updated_jobs_response and updated_jobs_response.status_code == 200:
        updated_data = updated_jobs_response.json()
        updated_job_count = len(updated_data.get('jobs', []))
        
        if updated_job_count > initial_job_count:
            log_test("Job Creation - Database Persistence", True, f"Job count increased from {initial_job_count} to {updated_job_count}")
        else:
            log_test("Job Creation - Database Persistence", False, f"Job count did not increase: {initial_job_count} -> {updated_job_count}")
    
    # Get specific job details to check allocation
    job_response = make_request('GET', f'/jobs/{job_id}', headers=headers)
    
    if job_response and job_response.status_code == 200:
        job_details = job_response.json()
        
        if job_details.get('success'):
            job_info = job_details.get('job', {})
            job_status = job_info.get('status')
            fixer_id = job_info.get('fixer_id')
            
            log_test("Job Details - Retrieval", True, f"Job details retrieved successfully")
            
            # Check if job was automatically assigned
            if job_status == 'assigned' and fixer_id:
                log_test("Automatic Job Allocation", True, f"Job automatically assigned to fixer: {fixer_id}")
            elif job_status == 'pending':
                log_test("Automatic Job Allocation", False, f"Job still pending - no automatic assignment occurred")
            else:
                log_test("Automatic Job Allocation", False, f"Unexpected job status: {job_status}, fixer_id: {fixer_id}")
        else:
            log_test("Job Details - Retrieval", False, f"Failed to get job details: {job_details.get('message')}")
    else:
        log_test("Job Details - Retrieval", False, f"HTTP {job_response.status_code if job_response else 'No response'}")
    
    return job_id

def test_fixer_notifications(job_id=None):
    """Test 2: Verify fixer notification system"""
    print("🔄 Testing Fixer Notification System...")
    
    # Authenticate fixer
    fixer_token, fixer_user = authenticate_user(FIXER_CREDENTIALS, "fixer")
    if not fixer_token:
        log_test("Fixer Notifications - Authentication", False, "Failed to authenticate fixer")
        return
    
    log_test("Fixer Notifications - Authentication", True, f"Fixer authenticated: {fixer_user.get('display_name', 'Unknown')}")
    
    # Get fixer notifications
    headers = {'Authorization': f'Bearer {fixer_token}'}
    notifications_response = make_request('GET', '/fixer/notifications', headers=headers)
    
    if not notifications_response:
        log_test("Fixer Notifications - API Call", False, "No response from notifications endpoint")
        return
    
    if notifications_response.status_code != 200:
        log_test("Fixer Notifications - API Call", False, f"HTTP {notifications_response.status_code}: {notifications_response.text}")
        return
    
    try:
        notifications_data = notifications_response.json()
    except:
        log_test("Fixer Notifications - API Call", False, "Invalid JSON response")
        return
    
    if not notifications_data.get('success'):
        log_test("Fixer Notifications - API Call", False, f"Failed to get notifications: {notifications_data.get('message')}")
        return
    
    notifications = notifications_data.get('notifications', [])
    unread_count = notifications_data.get('unread_count', 0)
    
    log_test("Fixer Notifications - API Call", True, f"Retrieved {len(notifications)} notifications ({unread_count} unread)")
    
    # Check notification content
    if notifications:
        # Check for job assignment notifications
        assignment_notifications = [n for n in notifications if n.get('notification_type') == 'job_assigned']
        available_notifications = [n for n in notifications if n.get('notification_type') == 'job_available']
        
        if assignment_notifications:
            log_test("Fixer Notifications - Job Assignment", True, f"Found {len(assignment_notifications)} job assignment notifications")
            
            # Check notification details
            sample_notification = assignment_notifications[0]
            if sample_notification.get('job_details'):
                log_test("Fixer Notifications - Job Details", True, "Notification includes job details")
            else:
                log_test("Fixer Notifications - Job Details", False, "Notification missing job details")
        else:
            log_test("Fixer Notifications - Job Assignment", False, "No job assignment notifications found")
        
        if available_notifications:
            log_test("Fixer Notifications - Available Jobs", True, f"Found {len(available_notifications)} available job notifications")
        else:
            log_test("Fixer Notifications - Available Jobs", False, "No available job notifications found")
    else:
        log_test("Fixer Notifications - Content", False, "No notifications found")
    
    return notifications

def test_available_jobs():
    """Test 3: Verify available jobs for fixers"""
    print("🔄 Testing Available Jobs for Fixers...")
    
    # Authenticate fixer
    fixer_token, fixer_user = authenticate_user(FIXER_CREDENTIALS, "fixer")
    if not fixer_token:
        log_test("Available Jobs - Authentication", False, "Failed to authenticate fixer")
        return []
    
    # Get available jobs
    headers = {'Authorization': f'Bearer {fixer_token}'}
    jobs_response = make_request('GET', '/fixer/available-jobs', headers=headers)
    
    if not jobs_response:
        log_test("Available Jobs - API Call", False, "No response from available jobs endpoint")
        return []
    
    if jobs_response.status_code != 200:
        log_test("Available Jobs - API Call", False, f"HTTP {jobs_response.status_code}: {jobs_response.text}")
        return []
    
    try:
        jobs_data = jobs_response.json()
    except:
        log_test("Available Jobs - API Call", False, "Invalid JSON response")
        return []
    
    if not jobs_data.get('success'):
        log_test("Available Jobs - API Call", False, f"Failed to get available jobs: {jobs_data.get('message')}")
        return []
    
    available_jobs = jobs_data.get('available_jobs', [])
    log_test("Available Jobs - API Call", True, f"Retrieved {len(available_jobs)} available jobs")
    
    # Check job details completeness
    if available_jobs:
        sample_job = available_jobs[0]
        required_fields = ['id', 'service', 'description', 'location', 'estimated_price']
        missing_fields = [field for field in required_fields if field not in sample_job or sample_job[field] is None]
        
        if not missing_fields:
            log_test("Available Jobs - Job Details Complete", True, "All required job fields present")
        else:
            log_test("Available Jobs - Job Details Complete", False, f"Missing fields: {missing_fields}")
    else:
        log_test("Available Jobs - Job Details Complete", False, "No jobs available to check")
    
    return available_jobs

def test_job_application(available_jobs):
    """Test 4: Test job application process"""
    print("🔄 Testing Job Application Process...")
    
    if not available_jobs:
        log_test("Job Application - Prerequisites", False, "No available jobs to apply for")
        return
    
    # Authenticate fixer
    fixer_token, fixer_user = authenticate_user(FIXER_CREDENTIALS, "fixer")
    if not fixer_token:
        log_test("Job Application - Authentication", False, "Failed to authenticate fixer")
        return
    
    # Select first available job
    target_job = available_jobs[0]
    job_id = target_job['id']
    
    log_test("Job Application - Target Selection", True, f"Selected job: {job_id} ({target_job.get('service', 'Unknown service')})")
    
    # Apply for the job
    headers = {'Authorization': f'Bearer {fixer_token}'}
    apply_response = make_request('POST', f'/fixer/apply-job/{job_id}', headers=headers)
    
    if not apply_response:
        log_test("Job Application - API Call", False, "No response from job application endpoint")
        return
    
    if apply_response.status_code != 200:
        log_test("Job Application - API Call", False, f"HTTP {apply_response.status_code}: {apply_response.text}")
        return
    
    try:
        apply_data = apply_response.json()
    except:
        log_test("Job Application - API Call", False, "Invalid JSON response")
        return
    
    if apply_data.get('success'):
        log_test("Job Application - API Call", True, f"Successfully applied for job: {apply_data.get('message')}")
        
        # Verify job status changed to 'assigned'
        time.sleep(1)  # Brief wait for database update
        
        # We need client credentials to check job status
        client_token, client_user = authenticate_user(CLIENT_CREDENTIALS, "client")
        if client_token:
            client_headers = {'Authorization': f'Bearer {client_token}'}
            job_check_response = make_request('GET', f'/jobs/{job_id}', headers=client_headers)
            
            if job_check_response and job_check_response.status_code == 200:
                job_check_data = job_check_response.json()
                if job_check_data.get('success'):
                    job_info = job_check_data.get('job', {})
                    if job_info.get('status') == 'assigned':
                        log_test("Job Application - Status Update", True, "Job status updated to 'assigned'")
                    else:
                        log_test("Job Application - Status Update", False, f"Job status is '{job_info.get('status')}', expected 'assigned'")
                else:
                    log_test("Job Application - Status Update", False, "Failed to retrieve job details for verification")
            else:
                log_test("Job Application - Status Update", False, "Failed to check job status after application")
        else:
            log_test("Job Application - Status Update", False, "Could not authenticate client to verify job status")
    else:
        log_test("Job Application - API Call", False, f"Job application failed: {apply_data.get('message')}")

def test_notification_management(notifications):
    """Test 5: Test notification management"""
    print("🔄 Testing Notification Management...")
    
    if not notifications:
        log_test("Notification Management - Prerequisites", False, "No notifications to manage")
        return
    
    # Authenticate fixer
    fixer_token, fixer_user = authenticate_user(FIXER_CREDENTIALS, "fixer")
    if not fixer_token:
        log_test("Notification Management - Authentication", False, "Failed to authenticate fixer")
        return
    
    # Find an unread notification
    unread_notifications = [n for n in notifications if not n.get('is_read', True)]
    
    if not unread_notifications:
        log_test("Notification Management - Unread Notifications", False, "No unread notifications found")
        return
    
    target_notification = unread_notifications[0]
    notification_id = target_notification['id']
    
    log_test("Notification Management - Target Selection", True, f"Selected notification: {notification_id}")
    
    # Mark notification as read
    headers = {'Authorization': f'Bearer {fixer_token}'}
    mark_read_response = make_request('POST', f'/fixer/notifications/{notification_id}/mark-read', headers=headers)
    
    if not mark_read_response:
        log_test("Notification Management - Mark Read API", False, "No response from mark read endpoint")
        return
    
    if mark_read_response.status_code != 200:
        log_test("Notification Management - Mark Read API", False, f"HTTP {mark_read_response.status_code}: {mark_read_response.text}")
        return
    
    try:
        mark_read_data = mark_read_response.json()
    except:
        log_test("Notification Management - Mark Read API", False, "Invalid JSON response")
        return
    
    if mark_read_data.get('success'):
        log_test("Notification Management - Mark Read API", True, "Notification marked as read successfully")
        
        # Verify unread count decreased
        time.sleep(1)  # Brief wait for database update
        
        updated_notifications_response = make_request('GET', '/fixer/notifications', headers=headers)
        if updated_notifications_response and updated_notifications_response.status_code == 200:
            updated_data = updated_notifications_response.json()
            if updated_data.get('success'):
                original_unread = len(unread_notifications)
                new_unread_count = updated_data.get('unread_count', 0)
                
                if new_unread_count < original_unread:
                    log_test("Notification Management - Unread Count Update", True, f"Unread count decreased from {original_unread} to {new_unread_count}")
                else:
                    log_test("Notification Management - Unread Count Update", False, f"Unread count did not decrease: {original_unread} -> {new_unread_count}")
            else:
                log_test("Notification Management - Unread Count Update", False, "Failed to retrieve updated notifications")
        else:
            log_test("Notification Management - Unread Count Update", False, "Failed to check updated notification count")
    else:
        log_test("Notification Management - Mark Read API", False, f"Failed to mark notification as read: {mark_read_data.get('message')}")

def test_user_isolation():
    """Test 6: Verify user isolation"""
    print("🔄 Testing User Isolation...")
    
    # Test that client cannot access fixer endpoints
    client_token, client_user = authenticate_user(CLIENT_CREDENTIALS, "client")
    if not client_token:
        log_test("User Isolation - Client Authentication", False, "Failed to authenticate client")
        return
    
    client_headers = {'Authorization': f'Bearer {client_token}'}
    
    # Try to access fixer notifications with client token
    client_notifications_response = make_request('GET', '/fixer/notifications', headers=client_headers)
    
    if client_notifications_response and client_notifications_response.status_code == 403:
        log_test("User Isolation - Client Access Denied", True, "Client correctly denied access to fixer notifications")
    elif client_notifications_response and client_notifications_response.status_code == 200:
        log_test("User Isolation - Client Access Denied", False, "Client incorrectly allowed access to fixer notifications")
    else:
        log_test("User Isolation - Client Access Denied", False, f"Unexpected response: HTTP {client_notifications_response.status_code if client_notifications_response else 'No response'}")
    
    # Try to access available jobs with client token
    client_jobs_response = make_request('GET', '/fixer/available-jobs', headers=client_headers)
    
    if client_jobs_response and client_jobs_response.status_code == 403:
        log_test("User Isolation - Client Job Access Denied", True, "Client correctly denied access to fixer available jobs")
    elif client_jobs_response and client_jobs_response.status_code == 200:
        log_test("User Isolation - Client Job Access Denied", False, "Client incorrectly allowed access to fixer available jobs")
    else:
        log_test("User Isolation - Client Job Access Denied", False, f"Unexpected response: HTTP {client_jobs_response.status_code if client_jobs_response else 'No response'}")

def test_database_operations():
    """Test 7: Verify database operations"""
    print("🔄 Testing Database Operations...")
    
    # Authenticate fixer to trigger table creation
    fixer_token, fixer_user = authenticate_user(FIXER_CREDENTIALS, "fixer")
    if not fixer_token:
        log_test("Database Operations - Authentication", False, "Failed to authenticate fixer")
        return
    
    # Access notifications endpoint to ensure table exists
    headers = {'Authorization': f'Bearer {fixer_token}'}
    notifications_response = make_request('GET', '/fixer/notifications', headers=headers)
    
    if notifications_response and notifications_response.status_code == 200:
        log_test("Database Operations - Table Access", True, "fixer_notifications table accessible")
        
        try:
            notifications_data = notifications_response.json()
            if notifications_data.get('success'):
                notifications = notifications_data.get('notifications', [])
                
                # Check data persistence by verifying notification structure
                if notifications:
                    sample_notification = notifications[0]
                    required_fields = ['id', 'job_id', 'notification_type', 'title', 'message', 'is_read', 'created_at']
                    missing_fields = [field for field in required_fields if field not in sample_notification]
                    
                    if not missing_fields:
                        log_test("Database Operations - Data Structure", True, "Notification data structure complete")
                    else:
                        log_test("Database Operations - Data Structure", False, f"Missing fields in notification: {missing_fields}")
                    
                    # Check foreign key relationships
                    if sample_notification.get('job_details'):
                        log_test("Database Operations - Foreign Key Relationships", True, "Job details linked correctly to notifications")
                    else:
                        log_test("Database Operations - Foreign Key Relationships", False, "Job details not linked to notifications")
                else:
                    log_test("Database Operations - Data Persistence", True, "No notifications found (expected for new system)")
            else:
                log_test("Database Operations - Table Access", False, f"Failed to access notifications: {notifications_data.get('message')}")
        except Exception as e:
            log_test("Database Operations - Data Structure", False, f"Error parsing notification data: {str(e)}")
    else:
        log_test("Database Operations - Table Access", False, f"Failed to access fixer_notifications table: HTTP {notifications_response.status_code if notifications_response else 'No response'}")

def main():
    """Main test execution"""
    print("=" * 80)
    print("🚀 FIXMATE-SA AUTOMATIC JOB ALLOCATION SYSTEM TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    print("=" * 80)
    print()
    
    # Test 1: Job Creation and Automatic Allocation
    job_id = test_job_creation_and_allocation()
    
    # Test 2: Fixer Notification System
    notifications = test_fixer_notifications(job_id)
    
    # Test 3: Available Jobs for Fixers
    available_jobs = test_available_jobs()
    
    # Test 4: Job Application Process
    test_job_application(available_jobs)
    
    # Test 5: Notification Management
    test_notification_management(notifications)
    
    # Test 6: User Isolation
    test_user_isolation()
    
    # Test 7: Database Operations
    test_database_operations()
    
    # Final Results
    print("=" * 80)
    print("📊 FINAL TEST RESULTS")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
    print("=" * 80)
    
    if failed_tests == 0:
        print("🎉 ALL TESTS PASSED! Automatic Job Allocation System is working correctly!")
    elif failed_tests <= 2:
        print("⚠️  MOSTLY WORKING with minor issues that need attention")
    else:
        print("🚨 CRITICAL ISSUES DETECTED - System needs immediate attention")
    
    print(f"Test completed at: {datetime.now().isoformat()}")
    print("=" * 80)

if __name__ == "__main__":
    main()