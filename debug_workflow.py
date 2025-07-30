#!/usr/bin/env python3
"""
Debug specific workflow endpoints
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('/app/frontend/.env')
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

def test_workflow_creation():
    # First create a user
    user_data = {
        "phone": "+27821234999",
        "first_name": "Test",
        "last_name": "User",
        "id_number": "8001015009999",
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
    
    # Accept terms
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

if __name__ == "__main__":
    test_workflow_creation()