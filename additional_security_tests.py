#!/usr/bin/env python3
"""
Additional Security Tests for Specific Review Request Scenarios
"""

import requests
import json
import os

def test_specific_scenarios():
    backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://service-pros-2.preview.emergentagent.com')
    api_base = f"{backend_url}/api"
    
    print("🔒 TESTING SPECIFIC SECURITY SCENARIOS FROM REVIEW REQUEST")
    print("=" * 80)
    
    # Get tokens for User1 and User2
    user1_response = requests.post(f"{api_base}/auth/login", json={"phone": "+27800000002", "password": "client2024test"})
    user2_response = requests.post(f"{api_base}/auth/login", json={"phone": "+27800000003", "password": "fixer2024test"})
    
    user1_data = user1_response.json()
    user2_data = user2_response.json()
    
    user1_token = user1_data["token"]
    user1_id = user1_data["user"]["id"]
    user2_token = user2_data["token"]
    user2_id = user2_data["user"]["id"]
    
    print(f"👤 User1: {user1_data['user']['phone']} (ID: {user1_id})")
    print(f"👤 User2: {user2_data['user']['phone']} (ID: {user2_id})")
    print()
    
    # Test 1: Jobs endpoint WITHOUT token - should return 401
    print("📋 TEST 1: GET /api/jobs WITHOUT token")
    response = requests.get(f"{api_base}/jobs")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print(f"   ✅ PASS: Unauthorized access blocked" if response.status_code >= 400 else f"   ❌ FAIL: Should block unauthorized access")
    print()
    
    # Test 2: Jobs endpoint with INVALID token - should return 401
    print("📋 TEST 2: GET /api/jobs with INVALID token")
    response = requests.get(f"{api_base}/jobs", headers={"Authorization": "Bearer invalid_token"})
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print(f"   ✅ PASS: Invalid token blocked" if response.status_code >= 400 else f"   ❌ FAIL: Should block invalid token")
    print()
    
    # Test 3: Jobs endpoint with User1 token - should return only User1's jobs
    print("📋 TEST 3: GET /api/jobs with User1 token")
    response = requests.get(f"{api_base}/jobs", headers={"Authorization": f"Bearer {user1_token}"})
    if response.status_code == 200:
        data = response.json()
        jobs = data.get("jobs", [])
        user1_jobs = [job for job in jobs if job.get("client_id") == user1_id]
        other_jobs = [job for job in jobs if job.get("client_id") != user1_id]
        
        print(f"   Status: {response.status_code}")
        print(f"   Total jobs returned: {len(jobs)}")
        print(f"   User1's jobs: {len(user1_jobs)}")
        print(f"   Other users' jobs: {len(other_jobs)}")
        print(f"   ✅ PASS: User isolation working" if len(other_jobs) == 0 else f"   ❌ FAIL: User can see other users' jobs")
    else:
        print(f"   Status: {response.status_code}")
        print(f"   ❌ FAIL: Valid token should work")
    print()
    
    # Test 4: Jobs endpoint with User2 token - should return only User2's jobs
    print("📋 TEST 4: GET /api/jobs with User2 token")
    response = requests.get(f"{api_base}/jobs", headers={"Authorization": f"Bearer {user2_token}"})
    if response.status_code == 200:
        data = response.json()
        jobs = data.get("jobs", [])
        user2_jobs = [job for job in jobs if job.get("client_id") == user2_id]
        other_jobs = [job for job in jobs if job.get("client_id") != user2_id]
        
        print(f"   Status: {response.status_code}")
        print(f"   Total jobs returned: {len(jobs)}")
        print(f"   User2's jobs: {len(user2_jobs)}")
        print(f"   Other users' jobs: {len(other_jobs)}")
        print(f"   ✅ PASS: User isolation working" if len(other_jobs) == 0 else f"   ❌ FAIL: User can see other users' jobs")
    else:
        print(f"   Status: {response.status_code}")
        print(f"   ❌ FAIL: Valid token should work")
    print()
    
    # Test 5: Dashboard endpoint WITHOUT token - should return 401
    print("📋 TEST 5: GET /api/dashboard/{user1_id} WITHOUT token")
    response = requests.get(f"{api_base}/dashboard/{user1_id}")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print(f"   ✅ PASS: Unauthorized access blocked" if response.status_code >= 400 else f"   ❌ FAIL: Should block unauthorized access")
    print()
    
    # Test 6: Dashboard endpoint with INVALID token - should return 401
    print("📋 TEST 6: GET /api/dashboard/{user1_id} with INVALID token")
    response = requests.get(f"{api_base}/dashboard/{user1_id}", headers={"Authorization": "Bearer invalid_token"})
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print(f"   ✅ PASS: Invalid token blocked" if response.status_code >= 400 else f"   ❌ FAIL: Should block invalid token")
    print()
    
    # Test 7: Dashboard endpoint with User1 token accessing User1's dashboard - should work
    print("📋 TEST 7: GET /api/dashboard/{user1_id} with User1 token")
    response = requests.get(f"{api_base}/dashboard/{user1_id}", headers={"Authorization": f"Bearer {user1_token}"})
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   User ID in response: {data.get('user_id')}")
        print(f"   ✅ PASS: User can access own dashboard" if data.get('user_id') == user1_id else f"   ❌ FAIL: Wrong user data returned")
    else:
        print(f"   Response: {response.json()}")
        print(f"   ❌ FAIL: User should access own dashboard")
    print()
    
    # Test 8: Dashboard endpoint with User2 token accessing User1's dashboard - should return 403
    print("📋 TEST 8: GET /api/dashboard/{user1_id} with User2 token (cross-user access)")
    response = requests.get(f"{api_base}/dashboard/{user1_id}", headers={"Authorization": f"Bearer {user2_token}"})
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print(f"   ✅ PASS: Cross-user access blocked" if response.status_code == 403 else f"   ❌ FAIL: Should block cross-user access")
    print()
    
    # Test 9: Dashboard endpoint with User2 token accessing User2's dashboard - should work
    print("📋 TEST 9: GET /api/dashboard/{user2_id} with User2 token")
    response = requests.get(f"{api_base}/dashboard/{user2_id}", headers={"Authorization": f"Bearer {user2_token}"})
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   User ID in response: {data.get('user_id')}")
        print(f"   ✅ PASS: User can access own dashboard" if data.get('user_id') == user2_id else f"   ❌ FAIL: Wrong user data returned")
    else:
        print(f"   Response: {response.json()}")
        print(f"   ❌ FAIL: User should access own dashboard")
    print()
    
    # Test 10: Malformed tokens
    print("📋 TEST 10: Testing malformed tokens")
    malformed_tokens = [
        "Bearer ",
        "Bearer token_invalid",
        "InvalidFormat token_123",
        "Bearer token_nonexistent_user",
        ""
    ]
    
    for i, token in enumerate(malformed_tokens, 1):
        print(f"   Test 10.{i}: Token '{token[:20]}...'")
        headers = {"Authorization": token} if token else {}
        response = requests.get(f"{api_base}/jobs", headers=headers)
        print(f"      Status: {response.status_code}")
        print(f"      ✅ PASS: Malformed token blocked" if response.status_code >= 400 else f"      ❌ FAIL: Should block malformed token")
    print()
    
    print("🎉 SECURITY TESTING COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    test_specific_scenarios()
