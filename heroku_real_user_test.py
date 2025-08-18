#!/usr/bin/env python3
"""
Heroku Fixer Signup with Real User Testing
==========================================

Test fixer signup with a real existing user to diagnose the "registration failed" issue.
"""

import requests
import json
from datetime import datetime

# Heroku Backend URL
HEROKU_BACKEND_URL = "https://service-pros-2.preview.emergentagent.com"

def test_fixer_signup_with_real_user():
    """Test fixer signup with a real existing user"""
    print("🔧 TESTING FIXER SIGNUP WITH REAL EXISTING USER")
    print("=" * 60)
    
    # First, let's login to get a real user ID
    print("Step 1: Login to get a real user ID...")
    login_data = {
        'phone': '+27800000002',  # Known client user
        'password': 'client2024test'
    }
    
    try:
        login_response = requests.post(
            f"{HEROKU_BACKEND_URL}/api/auth/login",
            json=login_data,
            timeout=30
        )
        
        print(f"Login Response Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print(f"Login Success: {login_result.get('success')}")
            
            if login_result.get('success') and login_result.get('user'):
                user_id = login_result['user']['id']
                print(f"Real User ID: {user_id}")
                
                # Now test fixer application with this real user
                print(f"\nStep 2: Testing fixer application with real user ID: {user_id}")
                
                fixer_data = {
                    'user_id': user_id,
                    'services_offered': 'Plumbing, Electrical, General Maintenance',
                    'experience_years': '5',
                    'why_fixer': 'I have extensive experience in home repairs and want to help people fix their problems quickly and efficiently.',
                    'qualifications': 'Certified Electrician, Plumbing License',
                    'previous_work': 'Worked at ABC Repairs for 3 years, handled 200+ jobs'
                }
                
                fixer_response = requests.post(
                    f"{HEROKU_BACKEND_URL}/api/fixer/apply",
                    data=fixer_data,
                    timeout=30
                )
                
                print(f"Fixer Application Response Status: {fixer_response.status_code}")
                print(f"Response Headers: {dict(fixer_response.headers)}")
                
                try:
                    fixer_result = fixer_response.json()
                    print(f"Fixer Application Response: {json.dumps(fixer_result, indent=2)}")
                    
                    if fixer_response.status_code == 200 and fixer_result.get('success'):
                        print("✅ SUCCESS: Fixer application submitted successfully!")
                        print(f"Fixer ID: {fixer_result.get('fixer_id')}")
                    else:
                        print("❌ FAILED: Fixer application failed")
                        print(f"Error: {fixer_result.get('detail', 'Unknown error')}")
                        
                        # Check if it's because fixer already exists
                        if 'already exists' in str(fixer_result.get('detail', '')):
                            print("🔍 DIAGNOSIS: User already has a fixer application")
                        
                except Exception as e:
                    print(f"❌ FAILED: Could not parse fixer application response")
                    print(f"Response Text: {fixer_response.text}")
                    print(f"Parse Error: {e}")
                    
            else:
                print("❌ FAILED: Login successful but no user data returned")
                print(f"Login Result: {login_result}")
        else:
            print("❌ FAILED: Could not login with test credentials")
            try:
                login_result = login_response.json()
                print(f"Login Error: {login_result}")
            except:
                print(f"Login Response Text: {login_response.text}")
                
    except Exception as e:
        print(f"❌ FAILED: Network or other error")
        print(f"Error: {e}")

def test_database_table_existence():
    """Test if required database tables exist by checking error messages"""
    print("\n🗄️ TESTING DATABASE TABLE EXISTENCE")
    print("=" * 50)
    
    # Test if fixers table exists by trying to get fixers
    try:
        print("Testing if fixers table exists...")
        response = requests.get(f"{HEROKU_BACKEND_URL}/api/fixers", timeout=30)
        
        print(f"Get Fixers Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                fixers_data = response.json()
                print(f"✅ Fixers table exists - found {len(fixers_data.get('fixers', []))} fixers")
            except:
                print(f"Response text: {response.text}")
        else:
            print(f"❌ Fixers table may not exist or have issues")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing fixers table: {e}")

def test_password_reset_table_existence():
    """Test if password_resets table exists"""
    print("\n🔑 TESTING PASSWORD_RESETS TABLE")
    print("=" * 40)
    
    # The issue we found is that some users get dev_code "123456" (hardcoded)
    # while others get real codes. This suggests the password_resets table
    # might not exist for some users or there's a database connection issue
    
    print("Analysis of password reset behavior:")
    print("- Users +27800000001 and +27800000002 get hardcoded dev_code '123456'")
    print("- User +27800000003 gets real generated code")
    print("- This suggests database table creation or user lookup issues")
    
    # Test if the issue is related to user existence
    phones_to_test = ['+27800000001', '+27800000002', '+27800000003']
    
    for phone in phones_to_test:
        try:
            print(f"\nTesting role check for {phone}...")
            response = requests.get(
                f"{HEROKU_BACKEND_URL}/api/auth/role-check/{phone.replace('+', '')}",
                timeout=30
            )
            
            print(f"Role Check Status: {response.status_code}")
            if response.status_code == 200:
                role_data = response.json()
                print(f"User exists: {role_data.get('user_exists')}")
                print(f"Role: {role_data.get('role')}")
                print(f"Database role: {role_data.get('database_role')}")
            else:
                print(f"Role check failed: {response.text}")
                
        except Exception as e:
            print(f"Error checking role for {phone}: {e}")

if __name__ == "__main__":
    print("🚀 HEROKU FIXER SIGNUP AND DATABASE DIAGNOSIS")
    print("=" * 60)
    print(f"Backend URL: {HEROKU_BACKEND_URL}")
    print(f"Test Started: {datetime.now().isoformat()}")
    print("=" * 60)
    
    test_fixer_signup_with_real_user()
    test_database_table_existence()
    test_password_reset_table_existence()
    
    print(f"\n⏰ Test Completed: {datetime.now().isoformat()}")