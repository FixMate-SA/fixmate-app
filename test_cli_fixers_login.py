#!/usr/bin/env python3
"""
Test script to verify that CLI-created fixers can login
"""

import requests
import json
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_fixer_login():
    """Test login for CLI-created fixers"""
    
    # Get CLI-created fixers with passwords from database
    from database import engine
    from sqlalchemy import text
    from sqlalchemy.orm import sessionmaker
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Find users created via CLI that have passwords
    result = db.execute(text("""
        SELECT u.phone, u.first_name, u.last_name, u.password_hash, u.is_password_set, f.name
        FROM users u 
        JOIN fixers f ON u.id = f.user_id 
        WHERE u.password_hash IS NOT NULL 
        AND u.password_hash != '' 
        AND u.phone LIKE '+27%'
        ORDER BY u.created_at DESC
        LIMIT 5
    """))
    
    cli_fixers = result.fetchall()
    db.close()
    
    if not cli_fixers:
        print("❌ No CLI-created fixers with passwords found")
        return
    
    print("🧪 Testing CLI-created fixer logins...")
    print("=" * 50)
    
    # Known passwords for CLI-created fixers (from our test commands)
    test_credentials = {
        '+27824444444': 'test123',
        '+27823333333': 'mike123',
        '+27821111111': 'fixer123',
        '+27822222222': None,  # No password set
    }
    
    success_count = 0
    total_tests = 0
    
    for fixer in cli_fixers:
        phone = fixer[0]
        name = fixer[1] + ' ' + fixer[2] if fixer[2] else fixer[1]
        fixer_name = fixer[5]
        has_password_hash = bool(fixer[3])
        is_password_set = fixer[4]
        
        print(f"\n👤 Testing: {name} ({fixer_name})")
        print(f"   Phone: {phone}")
        print(f"   Has password: {has_password_hash}")
        print(f"   Password set flag: {is_password_set}")
        
        # Skip if no password
        if not has_password_hash or not is_password_set:
            print("   ⏭️  Skipped - No password set")
            continue
        
        # Try to find known password
        password = test_credentials.get(phone)
        if not password:
            print("   ⏭️  Skipped - Unknown password")
            continue
        
        total_tests += 1
        
        # Test login
        try:
            login_data = {'phone': phone, 'password': password}
            response = requests.post('http://localhost:8001/api/auth/login', json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ LOGIN SUCCESS")
                print(f"      Display name: {data['display_name']}")
                print(f"      Role: {data['role_info']['role']}")
                success_count += 1
            else:
                print(f"   ❌ LOGIN FAILED: {response.status_code}")
                if response.content:
                    error_data = response.json()
                    print(f"      Error: {error_data.get('detail', 'Unknown error')}")
                    
        except Exception as e:
            print(f"   ❌ LOGIN ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"🏁 Test Results: {success_count}/{total_tests} successful logins")
    
    if success_count == total_tests and total_tests > 0:
        print("🎉 All CLI-created fixers can login successfully!")
        return True
    elif total_tests == 0:
        print("⚠️  No testable fixers found")
        return True
    else:
        print("❌ Some fixers cannot login - check the errors above")
        return False

if __name__ == "__main__":
    success = test_fixer_login()
    sys.exit(0 if success else 1)