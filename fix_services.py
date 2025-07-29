#!/usr/bin/env python3
"""
Fix services field format for existing fixers
Convert comma-separated services to JSON format
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

def fix_services_format():
    """Fix services field format for existing fixers"""
    session = requests.Session()
    
    print("Fetching existing fixers...")
    response = session.get(f"{API_BASE}/fixers")
    if response.status_code != 200:
        print(f"Failed to fetch fixers: {response.status_code}")
        return
    
    fixers = response.json()
    print(f"Found {len(fixers)} fixers")
    
    fixed_count = 0
    for fixer in fixers:
        services = fixer.get('services', '')
        
        # Check if services is already JSON format
        try:
            parsed_services = json.loads(services)
            if isinstance(parsed_services, list):
                print(f"✅ Fixer {fixer['name']}: Services already in JSON format")
                continue
        except json.JSONDecodeError:
            pass
        
        # Convert comma-separated to JSON array
        if ',' in services and not services.startswith('['):
            services_list = [s.strip() for s in services.split(',') if s.strip()]
            json_services = json.dumps(services_list)
            
            print(f"🔧 Fixing {fixer['name']}: '{services}' -> {json_services}")
            
            # Update fixer via direct database access since we don't have PUT endpoint
            # For now, we'll create a new fixer with correct format
            # This is a limitation of the current API design
            print(f"   Note: Services format needs to be fixed in database directly")
            fixed_count += 1
    
    print(f"\nFound {fixed_count} fixers that need services format fixing")
    print("Note: These need to be fixed directly in the database or via admin interface")

if __name__ == "__main__":
    fix_services_format()