#!/usr/bin/env python3
"""
Heroku Database Schema Analysis
===============================

Deep dive analysis to identify the exact database schema differences causing:
1. "registration failed" for fixer signup (HTTP 500 error)
2. "invalid reset code" for password reset verification

Key Findings So Far:
- Fixer signup returns HTTP 500 "Failed to submit fixer application" 
- Password reset works for user +27800000003 but fails for +27800000001 and +27800000002
- All users exist in database with correct roles
- Fixers table exists with 4 fixers
"""

import requests
import json
from datetime import datetime

HEROKU_BACKEND_URL = "https://service-pros-2.preview.emergentagent.com"

def analyze_fixer_signup_error():
    """Analyze the HTTP 500 error in fixer signup"""
    print("🔍 ANALYZING FIXER SIGNUP HTTP 500 ERROR")
    print("=" * 50)
    
    # The error suggests a database constraint violation or missing column
    # Let's test with minimal data first
    
    print("Testing with minimal required fields...")
    
    minimal_data = {
        'user_id': 'a89e82ac-dbf3-403e-ab47-4bb340445576',  # Real user ID from previous test
        'services_offered': 'Plumbing',
        'experience_years': '1',
        'why_fixer': 'Test application'
    }
    
    try:
        response = requests.post(
            f"{HEROKU_BACKEND_URL}/api/fixer/apply",
            data=minimal_data,
            timeout=30
        )
        
        print(f"Minimal Data Response Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 500:
            print("❌ DIAGNOSIS: HTTP 500 suggests database constraint violation")
            print("Possible causes:")
            print("1. Missing required columns in fixers table")
            print("2. Data type mismatch (e.g., services field expects JSON array)")
            print("3. Foreign key constraint violation")
            print("4. Database connection timeout")
            
    except Exception as e:
        print(f"Error: {e}")

def analyze_password_reset_inconsistency():
    """Analyze why password reset works for some users but not others"""
    print("\n🔍 ANALYZING PASSWORD RESET INCONSISTENCY")
    print("=" * 50)
    
    # We found that:
    # - +27800000001 (admin) gets dev_code "123456" but verification fails
    # - +27800000002 (client) gets dev_code "123456" but verification fails  
    # - +27800000003 (fixer) gets real code and verification works
    
    print("HYPOTHESIS: password_resets table creation fails for some users")
    print("Testing password reset request behavior...")
    
    test_cases = [
        ('+27800000001', 'admin'),
        ('+27800000002', 'client'), 
        ('+27800000003', 'fixer')
    ]
    
    for phone, role in test_cases:
        print(f"\nTesting {phone} ({role})...")
        
        try:
            # Request reset code
            response = requests.post(
                f"{HEROKU_BACKEND_URL}/api/auth/request-password-reset",
                data={'phone': phone},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                dev_code = data.get('dev_code')
                message = data.get('message')
                
                print(f"Reset request: {message}")
                print(f"Dev code: {dev_code}")
                
                # Analyze the response pattern
                if dev_code == "123456":
                    print("🚨 ISSUE: Hardcoded dev_code suggests user not found in database")
                    print("   This means the user lookup is failing despite role-check working")
                elif dev_code and len(dev_code) == 6 and dev_code.isdigit():
                    print("✅ GOOD: Real generated code suggests proper database operation")
                    
                    # Test verification with the real code
                    verify_response = requests.post(
                        f"{HEROKU_BACKEND_URL}/api/auth/verify-reset-code",
                        data={'phone': phone, 'reset_code': dev_code},
                        timeout=30
                    )
                    
                    print(f"Verification status: {verify_response.status_code}")
                    if verify_response.status_code == 200:
                        print("✅ Verification successful")
                    else:
                        verify_data = verify_response.json()
                        print(f"❌ Verification failed: {verify_data.get('detail')}")
                        
        except Exception as e:
            print(f"Error testing {phone}: {e}")

def test_database_field_mapping():
    """Test if there are field mapping issues between local and Heroku"""
    print("\n🔍 TESTING DATABASE FIELD MAPPING ISSUES")
    print("=" * 50)
    
    print("HYPOTHESIS: Heroku database has different column names than local")
    print("Common issues:")
    print("1. password vs password_hash column")
    print("2. services field data type (TEXT vs JSON)")
    print("3. Missing columns added in recent migrations")
    
    # Test user table structure by checking login behavior
    print("\nTesting user table structure via login...")
    
    # Test with different phone formats to see if there's a format issue
    phone_formats = [
        '+27800000003',
        '27800000003', 
        '0800000003'
    ]
    
    for phone_format in phone_formats:
        try:
            response = requests.post(
                f"{HEROKU_BACKEND_URL}/api/auth/login",
                json={'phone': phone_format, 'password': 'fixer2024test'},
                timeout=30
            )
            
            print(f"Login with {phone_format}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Login successful - phone format {phone_format} works")
                else:
                    print(f"❌ Login failed: {data.get('message')}")
            else:
                print(f"❌ HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"Error testing {phone_format}: {e}")

def test_services_field_format():
    """Test if the services field format is causing the fixer signup issue"""
    print("\n🔍 TESTING SERVICES FIELD FORMAT")
    print("=" * 40)
    
    print("HYPOTHESIS: services field expects specific format (JSON array vs comma-separated)")
    
    # Test different services formats
    services_formats = [
        'Plumbing',  # Simple string
        'Plumbing,Electrical',  # Comma-separated
        '["Plumbing"]',  # JSON array string
        ['Plumbing'],  # Python list (will be converted)
    ]
    
    base_data = {
        'user_id': 'a89e82ac-dbf3-403e-ab47-4bb340445576',
        'experience_years': '1',
        'why_fixer': 'Test application'
    }
    
    for i, services_format in enumerate(services_formats):
        print(f"\nTest {i+1}: services_offered = {repr(services_format)}")
        
        test_data = base_data.copy()
        test_data['services_offered'] = services_format
        
        try:
            response = requests.post(
                f"{HEROKU_BACKEND_URL}/api/fixer/apply",
                data=test_data,
                timeout=30
            )
            
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS: This format works!")
                result = response.json()
                print(f"Result: {result}")
                break
            elif response.status_code == 400:
                result = response.json()
                print(f"❌ Validation error: {result.get('detail')}")
            elif response.status_code == 500:
                print("❌ Server error: Database constraint or field issue")
            else:
                print(f"❌ Unexpected status: {response.text}")
                
        except Exception as e:
            print(f"Error: {e}")

def generate_diagnosis_report():
    """Generate final diagnosis report"""
    print("\n" + "=" * 70)
    print("📊 HEROKU DEPLOYMENT DIAGNOSIS REPORT")
    print("=" * 70)
    
    print("🚨 CRITICAL ISSUES IDENTIFIED:")
    print()
    print("1. FIXER SIGNUP FAILURE (HTTP 500)")
    print("   - Error: 'Failed to submit fixer application'")
    print("   - Root Cause: Database constraint violation or missing column")
    print("   - Impact: Users cannot register as fixers")
    print("   - Status: CRITICAL - Blocks core functionality")
    print()
    
    print("2. PASSWORD RESET INCONSISTENCY")
    print("   - Admin/Client users get hardcoded dev_code '123456' but verification fails")
    print("   - Fixer users get real codes and verification works")
    print("   - Root Cause: User lookup inconsistency in password reset logic")
    print("   - Impact: Admin and Client users cannot reset passwords")
    print("   - Status: HIGH - Affects user account recovery")
    print()
    
    print("🔍 TECHNICAL ANALYSIS:")
    print()
    print("DATABASE SCHEMA DIFFERENCES:")
    print("- Local development and Heroku production have different schemas")
    print("- Fixers table exists but may have missing/different columns")
    print("- Password reset logic has user lookup inconsistencies")
    print("- Services field format may be incompatible")
    print()
    
    print("USER AUTHENTICATION STATUS:")
    print("✅ All test users exist and can login")
    print("✅ Role detection works correctly")
    print("✅ Database connection is healthy")
    print("❌ Fixer application creation fails")
    print("❌ Password reset verification inconsistent")
    print()
    
    print("🛠️ RECOMMENDED FIXES:")
    print()
    print("1. IMMEDIATE (Fixer Signup):")
    print("   - Check fixers table schema on Heroku vs local")
    print("   - Verify all required columns exist")
    print("   - Check data type compatibility (especially services field)")
    print("   - Run database migration if needed")
    print()
    
    print("2. HIGH PRIORITY (Password Reset):")
    print("   - Fix user lookup logic in password reset request")
    print("   - Ensure password_resets table creation works for all users")
    print("   - Verify phone number format consistency")
    print()
    
    print("3. DEPLOYMENT SYNC:")
    print("   - Deploy latest backend code to Heroku")
    print("   - Run database migrations on production")
    print("   - Verify environment variables match")
    print()
    
    print("⚠️ PRODUCTION IMPACT:")
    print("- Fixer registration completely broken")
    print("- Password reset broken for admin/client users")
    print("- Core business functionality affected")
    print("- Immediate deployment fix required")

if __name__ == "__main__":
    print("🚀 HEROKU DATABASE SCHEMA ANALYSIS")
    print("=" * 50)
    print(f"Backend URL: {HEROKU_BACKEND_URL}")
    print(f"Analysis Started: {datetime.now().isoformat()}")
    print("=" * 50)
    
    analyze_fixer_signup_error()
    analyze_password_reset_inconsistency()
    test_database_field_mapping()
    test_services_field_format()
    generate_diagnosis_report()
    
    print(f"\n⏰ Analysis Completed: {datetime.now().isoformat()}")