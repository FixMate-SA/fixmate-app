#!/usr/bin/env python3
"""
Setup proper test data for workflow system
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('/app/frontend/.env')
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

def setup_workflow_test_data():
    # Create user
    user_data = {
        "phone": "+27821234888",
        "first_name": "Test",
        "last_name": "User",
        "id_number": "8001015009888",
        "town": "Cape Town",
        "email": "test@example.com",
        "address": "123 Test St"
    }
    
    response = requests.post(f"{API_BASE}/users", json=user_data)
    if response.status_code != 200:
        print(f"Failed to create user: {response.status_code} - {response.text}")
        return
    
    user = response.json()
    user_id = user['id']
    print(f"Created user: {user_id}")
    
    # Create fixer user
    fixer_user_data = {
        "phone": "+27821234777",
        "first_name": "Test",
        "last_name": "Fixer",
        "id_number": "8001015009777",
        "town": "Cape Town",
        "email": "fixer@example.com",
        "address": "456 Fixer St"
    }
    
    response = requests.post(f"{API_BASE}/users", json=fixer_user_data)
    if response.status_code != 200:
        print(f"Failed to create fixer user: {response.status_code} - {response.text}")
        return
    
    fixer_user = response.json()
    
    # Create fixer
    fixer_data = {
        "user_id": fixer_user['id'],
        "phone": "+27821234777",
        "name": "Test Fixer",
        "email": "fixer@example.com",
        "services": '["plumbing", "electrical"]',
        "location": "Cape Town",
        "is_approved": True  # Make sure fixer is approved
    }
    
    response = requests.post(f"{API_BASE}/fixers", json=fixer_data)
    if response.status_code != 200:
        print(f"Failed to create fixer: {response.status_code} - {response.text}")
        return
    
    fixer = response.json()
    fixer_id = fixer['id']
    print(f"Created fixer: {fixer_id}")
    
    # Accept terms for user
    terms_data = {
        'user_id': user_id,
        'ip_address': '192.168.1.1',
        'user_agent': 'Test Client',
        'method': 'web'
    }
    
    response = requests.post(f"{API_BASE}/terms/accept", json=terms_data)
    if response.status_code != 200:
        print(f"Failed to accept terms: {response.status_code} - {response.text}")
        return
    
    print("Terms accepted successfully")
    
    # Now try to create job with workflow
    job_data = {
        'user_id': user_id,
        'service': 'plumbing',
        'description': 'Emergency pipe burst in kitchen',
        'location': 'Cape Town CBD',
        'estimated_price': 450.0
    }
    
    response = requests.post(f"{API_BASE}/jobs/workflow", json=job_data)
    print(f"Job workflow creation: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        job_result = response.json()
        if job_result.get('success') and 'job_id' in job_result:
            job_id = job_result['job_id']
            print(f"Job created successfully: {job_id}")
            
            # Test other workflow endpoints
            print("\nTesting other workflow endpoints...")
            
            # Test fixer eligible jobs
            response = requests.get(f"{API_BASE}/fixer/{fixer_id}/eligible-jobs")
            print(f"Fixer eligible jobs: {response.status_code} - {response.json()}")
            
            # Test job workflow status
            response = requests.get(f"{API_BASE}/jobs/{job_id}/workflow-status")
            print(f"Job workflow status: {response.status_code} - {response.json()}")
            
            # Test fixer location update
            location_data = {'latitude': -33.9249, 'longitude': 18.4241}
            response = requests.post(f"{API_BASE}/fixer/{fixer_id}/location", json=location_data)
            print(f"Fixer location update: {response.status_code} - {response.text}")

if __name__ == "__main__":
    setup_workflow_test_data()