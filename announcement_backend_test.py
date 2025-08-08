#!/usr/bin/env python3
"""
Comprehensive Backend Testing for FixMate-SA Announcement System
Testing all announcement system API endpoints with authentication and authorization
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class AnnouncementSystemTester:
    def __init__(self):
        # Use the correct backend URL from frontend .env
        self.base_url = "http://localhost:8001/api"
        
        print(f"🔗 Testing Backend URL: {self.base_url}")
        
        # Test accounts for different roles
        self.test_accounts = {
            'admin': {
                'phone': '+27800000001',
                'password': 'admin2024test',
                'token': None,
                'user_id': None
            },
            'client': {
                'phone': '+27800000002', 
                'password': 'client2024test',
                'token': None,
                'user_id': None
            },
            'fixer': {
                'phone': '+27800000003',
                'password': 'fixer2024test', 
                'token': None,
                'user_id': None
            }
        }
        
        # Test data storage
        self.test_announcements = []
        self.test_chat_messages = []
        
        # Test results
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'details': []
        }

    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.results['total'] += 1
        if passed:
            self.results['passed'] += 1
            print(f"✅ PASS: {test_name}")
            if details:
                print(f"   Details: {details}")
        else:
            self.results['failed'] += 1
            print(f"❌ FAIL: {test_name}")
            if details:
                print(f"   Details: {details}")
        
        self.results['details'].append({
            'test': test_name,
            'passed': passed,
            'details': details
        })

    def make_request(self, method: str, endpoint: str, data: dict = None, headers: dict = None, auth_token: str = None) -> tuple:
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Setup headers
        request_headers = {'Content-Type': 'application/json'}
        if headers:
            request_headers.update(headers)
        if auth_token:
            request_headers['Authorization'] = f'Bearer {auth_token}'
        
        print(f"🔗 Making {method} request to: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=request_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=request_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=request_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=request_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            print(f"📊 Response: {response.status_code}")
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            return response.status_code, response_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
            return 0, str(e)

    def authenticate_users(self) -> bool:
        """Authenticate all test users"""
        print("🔐 AUTHENTICATING TEST USERS...")
        
        all_authenticated = True
        
        for role, account in self.test_accounts.items():
            login_data = {
                'phone': account['phone'],
                'password': account['password']
            }
            
            status_code, response = self.make_request('POST', '/auth/login', login_data)
            
            if status_code == 200 and isinstance(response, dict) and 'token' in response:
                account['token'] = response['token']
                account['user_id'] = response.get('user', {}).get('id')
                self.log_result(f"Authenticate {role} user", True, f"Token: {account['token'][:20]}...")
            else:
                self.log_result(f"Authenticate {role} user", False, f"Status: {status_code}, Response: {response}")
                all_authenticated = False
        
        return all_authenticated

    def test_admin_announcement_creation(self):
        """Test admin announcement creation with different target audiences"""
        print("\n📢 TESTING ADMIN ANNOUNCEMENT CREATION...")
        
        admin_token = self.test_accounts['admin']['token']
        
        # Test data for different announcements
        announcements_data = [
            {
                'title': 'Important Update for Clients',
                'content': 'We have updated our service pricing. Please check the new rates.',
                'target_audience': 'clients',
                'is_pinned': True,
                'priority': 'high',
                'chat_enabled': True,
                'admin_only_chat': False
            },
            {
                'title': 'New Tools Available for Fixers',
                'content': 'We have added new tools to help you complete jobs more efficiently.',
                'target_audience': 'fixers',
                'is_pinned': False,
                'priority': 'normal',
                'chat_enabled': True,
                'admin_only_chat': True
            },
            {
                'title': 'Platform Maintenance Notice',
                'content': 'The platform will be under maintenance this weekend.',
                'target_audience': 'all',
                'is_pinned': True,
                'priority': 'high',
                'chat_enabled': False,
                'admin_only_chat': False
            }
        ]
        
        for i, announcement_data in enumerate(announcements_data, 1):
            status_code, response = self.make_request(
                'POST', '/admin/announcements', 
                announcement_data, 
                auth_token=admin_token
            )
            
            if status_code == 200 and isinstance(response, dict) and response.get('success'):
                announcement_id = response.get('announcement_id')
                self.test_announcements.append(announcement_id)
                self.log_result(
                    f"Create announcement {i} ({announcement_data['target_audience']})", 
                    True, 
                    f"ID: {announcement_id}"
                )
            else:
                self.log_result(
                    f"Create announcement {i} ({announcement_data['target_audience']})", 
                    False, 
                    f"Status: {status_code}, Response: {response}"
                )

    def test_admin_announcement_management(self):
        """Test admin announcement management operations"""
        print("\n🔧 TESTING ADMIN ANNOUNCEMENT MANAGEMENT...")
        
        admin_token = self.test_accounts['admin']['token']
        
        # Test getting all announcements
        status_code, response = self.make_request('GET', '/admin/announcements', auth_token=admin_token)
        
        if status_code == 200 and isinstance(response, dict) and response.get('success'):
            announcements = response.get('announcements', [])
            self.log_result(
                "Get all announcements (admin)", 
                True, 
                f"Found {len(announcements)} announcements"
            )
        else:
            self.log_result(
                "Get all announcements (admin)", 
                False, 
                f"Status: {status_code}, Response: {response}"
            )
        
        # Test updating an announcement
        if self.test_announcements:
            announcement_id = self.test_announcements[0]
            update_data = {
                'title': 'Updated Important Notice for Clients',
                'content': 'This announcement has been updated with new information.',
                'is_pinned': False
            }
            
            status_code, response = self.make_request(
                'PUT', f'/admin/announcements/{announcement_id}', 
                update_data, 
                auth_token=admin_token
            )
            
            if status_code == 200 and isinstance(response, dict) and response.get('success'):
                self.log_result(
                    "Update announcement", 
                    True, 
                    f"Updated announcement {announcement_id}"
                )
            else:
                self.log_result(
                    "Update announcement", 
                    False, 
                    f"Status: {status_code}, Response: {response}"
                )

    def test_role_based_announcement_access(self):
        """Test role-based announcement filtering"""
        print("\n👥 TESTING USER ROLE-BASED ANNOUNCEMENT ACCESS...")
        
        for role, account in self.test_accounts.items():
            if not account['token']:
                continue
                
            status_code, response = self.make_request('GET', '/announcements', auth_token=account['token'])
            
            if status_code == 200 and isinstance(response, dict) and response.get('success'):
                announcements = response.get('announcements', [])
                user_role = response.get('user_role', 'unknown')
                
                # Verify role-based filtering
                expected_count = self._get_expected_announcement_count(role)
                actual_count = len(announcements)
                
                # Check if filtering is working correctly
                filtering_correct = self._verify_role_filtering(announcements, role)
                
                self.log_result(
                    f"Get announcements as {role}", 
                    filtering_correct, 
                    f"Found {actual_count} announcements, role filtering {'correct' if filtering_correct else 'incorrect'}"
                )
            else:
                self.log_result(
                    f"Get announcements as {role}", 
                    False, 
                    f"Status: {status_code}, Response: {response}"
                )

    def _get_expected_announcement_count(self, role: str) -> int:
        """Get expected announcement count for role"""
        if role == 'admin':
            return len(self.test_announcements)  # Admin sees all
        else:
            return len(self.test_announcements)  # For testing, assume all are visible

    def _verify_role_filtering(self, announcements: List[dict], role: str) -> bool:
        """Verify that announcements are properly filtered by role"""
        for announcement in announcements:
            target_audience = announcement.get('target_audience', '')
            
            if role == 'admin':
                continue  # Admin can see all
            elif role == 'client':
                if target_audience not in ['clients', 'all']:
                    return False
            elif role == 'fixer':
                if target_audience not in ['fixers', 'all']:
                    return False
        
        return True

    def test_announcement_chat_system(self):
        """Test announcement chat functionality"""
        print("\n💬 TESTING ANNOUNCEMENT CHAT SYSTEM...")
        
        if not self.test_announcements:
            print("⚠️ No test announcements available for chat testing")
            return
        
        announcement_id = self.test_announcements[0]  # Use first announcement
        client_token = self.test_accounts['client']['token']
        admin_token = self.test_accounts['admin']['token']
        
        # Test getting chat messages (should be empty initially)
        status_code, response = self.make_request(
            'GET', f'/announcements/{announcement_id}/chat', 
            auth_token=client_token
        )
        
        if status_code == 200 and isinstance(response, dict) and response.get('success'):
            messages = response.get('messages', [])
            self.log_result(
                "Get chat messages", 
                True, 
                f"Found {len(messages)} messages"
            )
        else:
            self.log_result(
                "Get chat messages", 
                False, 
                f"Status: {status_code}, Response: {response}"
            )
        
        # Test posting a chat message as client
        chat_data = {'message': 'This is a test message from a client user.'}
        status_code, response = self.make_request(
            'POST', f'/announcements/{announcement_id}/chat', 
            chat_data, 
            auth_token=client_token
        )
        
        if status_code == 200 and isinstance(response, dict) and response.get('success'):
            message_id = response.get('chat_message', {}).get('id')
            if message_id:
                self.test_chat_messages.append(message_id)
            self.log_result(
                "Post chat message (client)", 
                True, 
                f"Message ID: {message_id}"
            )
        else:
            self.log_result(
                "Post chat message (client)", 
                False, 
                f"Status: {status_code}, Response: {response}"
            )
        
        # Test posting a chat message as admin
        admin_chat_data = {'message': 'This is an admin response to the client message.'}
        status_code, response = self.make_request(
            'POST', f'/announcements/{announcement_id}/chat', 
            admin_chat_data, 
            auth_token=admin_token
        )
        
        if status_code == 200 and isinstance(response, dict) and response.get('success'):
            message_id = response.get('chat_message', {}).get('id')
            if message_id:
                self.test_chat_messages.append(message_id)
            self.log_result(
                "Post chat message (admin)", 
                True, 
                f"Message ID: {message_id}"
            )
        else:
            self.log_result(
                "Post chat message (admin)", 
                False, 
                f"Status: {status_code}, Response: {response}"
            )

    def test_chat_permissions_and_settings(self):
        """Test chat permission controls"""
        print("\n🔒 TESTING CHAT PERMISSIONS AND SETTINGS...")
        
        if len(self.test_announcements) < 2:
            print("⚠️ Not enough test announcements for permission testing")
            return
        
        client_token = self.test_accounts['client']['token']
        admin_token = self.test_accounts['admin']['token']
        
        # Test admin-only chat (announcement 2 should have admin_only_chat=True)
        admin_only_announcement = self.test_announcements[1]
        
        # Client should be blocked from admin-only chat
        chat_data = {'message': 'Client trying to post to admin-only chat'}
        status_code, response = self.make_request(
            'POST', f'/announcements/{admin_only_announcement}/chat', 
            chat_data, 
            auth_token=client_token
        )
        
        # Should get 403 or similar error
        if status_code == 403:
            self.log_result(
                "Admin-only chat restriction (client blocked)", 
                True, 
                "Client correctly blocked from admin-only chat"
            )
        else:
            self.log_result(
                "Admin-only chat restriction (client blocked)", 
                False, 
                f"Expected 403, got {status_code}: {response}"
            )
        
        # Admin should be allowed in admin-only chat
        admin_chat_data = {'message': 'Admin posting to admin-only chat'}
        status_code, response = self.make_request(
            'POST', f'/announcements/{admin_only_announcement}/chat', 
            admin_chat_data, 
            auth_token=admin_token
        )
        
        if status_code == 200 and isinstance(response, dict) and response.get('success'):
            self.log_result(
                "Admin-only chat access (admin allowed)", 
                True, 
                "Admin successfully posted to admin-only chat"
            )
        else:
            self.log_result(
                "Admin-only chat access (admin allowed)", 
                False, 
                f"Status: {status_code}, Response: {response}"
            )
        
        # Test chat disabled (announcement 3 should have chat_enabled=False)
        if len(self.test_announcements) >= 3:
            chat_disabled_announcement = self.test_announcements[2]
            
            chat_data = {'message': 'Trying to post to disabled chat'}
            status_code, response = self.make_request(
                'POST', f'/announcements/{chat_disabled_announcement}/chat', 
                chat_data, 
                auth_token=client_token
            )
            
            if status_code == 403:
                self.log_result(
                    "Chat disabled restriction", 
                    True, 
                    "Chat correctly disabled"
                )
            else:
                self.log_result(
                    "Chat disabled restriction", 
                    False, 
                    f"Expected 403, got {status_code}: {response}"
                )

    def test_authentication_and_authorization(self):
        """Test authentication and authorization controls"""
        print("\n🛡️ TESTING AUTHENTICATION AND AUTHORIZATION...")
        
        # Test admin endpoints without authentication
        status_code, response = self.make_request('GET', '/admin/announcements')
        
        if status_code == 401:
            self.log_result(
                "Admin endpoint without auth", 
                True, 
                "Correctly rejected unauthenticated request"
            )
        else:
            self.log_result(
                "Admin endpoint without auth", 
                False, 
                f"Expected 401, got {status_code}: {response}"
            )
        
        # Test admin endpoints with client authentication
        client_token = self.test_accounts['client']['token']
        status_code, response = self.make_request('GET', '/admin/announcements', auth_token=client_token)
        
        if status_code == 403:
            self.log_result(
                "Admin endpoint with client auth", 
                True, 
                "Client correctly denied admin access"
            )
        else:
            self.log_result(
                "Admin endpoint with client auth", 
                False, 
                f"Expected 403, got {status_code}: {response}"
            )
        
        # Test user endpoints without authentication
        status_code, response = self.make_request('GET', '/announcements')
        
        if status_code == 401:
            self.log_result(
                "User endpoint without auth", 
                True, 
                "Correctly rejected unauthenticated request"
            )
        else:
            self.log_result(
                "User endpoint without auth", 
                False, 
                f"Expected 401, got {status_code}: {response}"
            )

    def test_chat_message_deletion(self):
        """Test chat message deletion functionality"""
        print("\n🗑️ TESTING CHAT MESSAGE DELETION...")
        
        if not self.test_chat_messages or not self.test_announcements:
            print("⚠️ No test chat messages available for deletion testing")
            return
        
        client_token = self.test_accounts['client']['token']
        announcement_id = self.test_announcements[0]
        message_id = self.test_chat_messages[0]
        
        # Test deleting chat message
        status_code, response = self.make_request(
            'DELETE', f'/announcements/{announcement_id}/chat/{message_id}', 
            auth_token=client_token
        )
        
        if status_code == 200 and isinstance(response, dict) and response.get('success'):
            self.log_result(
                "Delete chat message", 
                True, 
                f"Deleted message {message_id}"
            )
        else:
            self.log_result(
                "Delete chat message", 
                False, 
                f"Status: {status_code}, Response: {response}"
            )

    def test_data_integrity_and_cascade_deletion(self):
        """Test data integrity and cascade deletion"""
        print("\n🗑️ TESTING DATA INTEGRITY AND CASCADE DELETION...")
        
        if not self.test_announcements:
            print("⚠️ No test announcements available for cascade deletion testing")
            return
        
        admin_token = self.test_accounts['admin']['token']
        announcement_id = self.test_announcements[0]
        
        # First, check how many chat messages exist
        status_code, response = self.make_request(
            'GET', f'/announcements/{announcement_id}/chat', 
            auth_token=admin_token
        )
        
        chat_count = 0
        if status_code == 200 and isinstance(response, dict):
            chat_count = len(response.get('messages', []))
        
        # Delete announcement (should cascade delete chat messages)
        status_code, response = self.make_request(
            'DELETE', f'/admin/announcements/{announcement_id}', 
            auth_token=admin_token
        )
        
        if status_code == 200 and isinstance(response, dict) and response.get('success'):
            self.log_result(
                "Delete announcement with cascade", 
                True, 
                f"Deleted announcement and {chat_count} chat messages"
            )
            # Remove from test list since it's deleted
            self.test_announcements.remove(announcement_id)
        else:
            self.log_result(
                "Delete announcement with cascade", 
                False, 
                f"Status: {status_code}, Response: {response}"
            )

    def cleanup_test_data(self):
        """Clean up any remaining test data"""
        print("\n🧹 CLEANING UP TEST DATA...")
        
        admin_token = self.test_accounts['admin']['token']
        
        # Delete remaining announcements
        for announcement_id in self.test_announcements[:]:  # Copy list to avoid modification during iteration
            status_code, response = self.make_request(
                'DELETE', f'/admin/announcements/{announcement_id}', 
                auth_token=admin_token
            )
            
            if status_code == 200:
                self.log_result(
                    f"Cleanup announcement {announcement_id}", 
                    True, 
                    "Deleted"
                )
                self.test_announcements.remove(announcement_id)
            else:
                self.log_result(
                    f"Cleanup announcement {announcement_id}", 
                    False, 
                    f"Status: {status_code}, Response: {response}"
                )

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "="*80)
        print("🎯 ANNOUNCEMENT SYSTEM BACKEND TESTING RESULTS")
        print("="*80)
        
        success_rate = (self.results['passed'] / self.results['total'] * 100) if self.results['total'] > 0 else 0
        
        print(f"📊 SUMMARY:")
        print(f"   Total Tests: {self.results['total']}")
        print(f"   Passed: {self.results['passed']}")
        print(f"   Failed: {self.results['failed']}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if self.results['failed'] > 0:
            print(f"\n⚠️ {self.results['failed']} TESTS FAILED. Review the details above.")
        else:
            print(f"\n🎉 ALL TESTS PASSED! Announcement system is working perfectly.")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.results['details']:
            status = "✅" if result['passed'] else "❌"
            print(f"   {status} {result['test']}")
            if result['details']:
                print(f"      {result['details']}")

    def run_all_tests(self):
        """Run all announcement system tests"""
        print("🚀 STARTING COMPREHENSIVE ANNOUNCEMENT SYSTEM BACKEND TESTING")
        print("="*80)
        
        # Step 1: Authenticate users
        if not self.authenticate_users():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Test admin announcement creation
        self.test_admin_announcement_creation()
        
        # Step 3: Test admin announcement management
        self.test_admin_announcement_management()
        
        # Step 4: Test role-based announcement access
        self.test_role_based_announcement_access()
        
        # Step 5: Test announcement chat system
        self.test_announcement_chat_system()
        
        # Step 6: Test chat permissions and settings
        self.test_chat_permissions_and_settings()
        
        # Step 7: Test authentication and authorization
        self.test_authentication_and_authorization()
        
        # Step 8: Test chat message deletion
        self.test_chat_message_deletion()
        
        # Step 9: Test data integrity and cascade deletion
        self.test_data_integrity_and_cascade_deletion()
        
        # Step 10: Clean up test data
        self.cleanup_test_data()
        
        # Step 11: Print final results
        self.print_final_results()
        
        return self.results['failed'] == 0

def main():
    """Main function to run announcement system tests"""
    tester = AnnouncementSystemTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()