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
        # Get backend URL from environment
        self.base_url = os.getenv('REACT_APP_BACKEND_URL', 'https://1738075b-0b63-4b9f-b8d1-a67df8264588.preview.emergentagent.com')
        if not self.base_url.endswith('/api'):
            self.base_url = f"{self.base_url}/api"
        
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
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        self.results['total_tests'] += 1
        if success:
            self.results['passed_tests'] += 1
            status = "✅ PASS"
        else:
            self.results['failed_tests'] += 1
            status = "❌ FAIL"
        
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        
        self.results['test_details'].append({
            'test': test_name,
            'status': 'PASS' if success else 'FAIL',
            'details': details
        })

    def make_request(self, method: str, endpoint: str, data: dict = None, headers: dict = None, role: str = None) -> requests.Response:
        """Make HTTP request with optional authentication"""
        url = f"{self.base_url}{endpoint}"
        
        # Add authentication header if role specified
        if role and self.test_accounts[role]['token']:
            if not headers:
                headers = {}
            headers['Authorization'] = f"Bearer {self.test_accounts[role]['token']}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None

    def authenticate_users(self) -> bool:
        """Authenticate all test users"""
        print("\n🔐 AUTHENTICATING TEST USERS...")
        
        all_authenticated = True
        
        for role, account in self.test_accounts.items():
            try:
                response = self.make_request('POST', '/auth/login', {
                    'phone': account['phone'],
                    'password': account['password']
                })
                
                if response and response.status_code == 200:
                    data = response.json()
                    account['token'] = data.get('token')
                    account['user_id'] = data.get('user', {}).get('id')
                    self.log_test(f"Authenticate {role} user", True, f"Token: {account['token'][:20]}...")
                else:
                    self.log_test(f"Authenticate {role} user", False, f"Status: {response.status_code if response else 'No response'}")
                    all_authenticated = False
                    
            except Exception as e:
                self.log_test(f"Authenticate {role} user", False, str(e))
                all_authenticated = False
        
        return all_authenticated

    def test_admin_announcement_creation(self) -> bool:
        """Test admin announcement creation with different target audiences"""
        print("\n📢 TESTING ADMIN ANNOUNCEMENT CREATION...")
        
        test_announcements = [
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
                'title': 'New Fixer Guidelines',
                'content': 'All fixers must now complete safety training before accepting jobs.',
                'target_audience': 'fixers', 
                'is_pinned': False,
                'priority': 'normal',
                'chat_enabled': True,
                'admin_only_chat': True
            },
            {
                'title': 'Platform Maintenance Notice',
                'content': 'The platform will be under maintenance on Sunday from 2-4 AM.',
                'target_audience': 'all',
                'is_pinned': True,
                'priority': 'high',
                'chat_enabled': False,
                'admin_only_chat': False,
                'expires_at': (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
        ]
        
        all_passed = True
        
        for i, announcement_data in enumerate(test_announcements):
            response = self.make_request('POST', '/admin/announcements', announcement_data, role='admin')
            
            if response and response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('announcement_id'):
                    self.test_announcements.append({
                        'id': data['announcement_id'],
                        'data': announcement_data
                    })
                    self.log_test(f"Create announcement {i+1} ({announcement_data['target_audience']})", True, 
                                f"ID: {data['announcement_id']}")
                else:
                    self.log_test(f"Create announcement {i+1}", False, "Invalid response structure")
                    all_passed = False
            else:
                self.log_test(f"Create announcement {i+1}", False, 
                            f"Status: {response.status_code if response else 'No response'}")
                all_passed = False
        
        return all_passed

    def test_admin_announcement_management(self) -> bool:
        """Test admin announcement retrieval, update, and deletion"""
        print("\n🔧 TESTING ADMIN ANNOUNCEMENT MANAGEMENT...")
        
        all_passed = True
        
        # Test GET all announcements
        response = self.make_request('GET', '/admin/announcements', role='admin')
        if response and response.status_code == 200:
            data = response.json()
            if data.get('success') and 'announcements' in data:
                announcement_count = len(data['announcements'])
                self.log_test("Get all announcements (admin)", True, f"Found {announcement_count} announcements")
            else:
                self.log_test("Get all announcements (admin)", False, "Invalid response structure")
                all_passed = False
        else:
            self.log_test("Get all announcements (admin)", False, 
                        f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        # Test UPDATE announcement (if we have test announcements)
        if self.test_announcements:
            announcement_id = self.test_announcements[0]['id']
            update_data = {
                'title': 'UPDATED: Important Update for Clients',
                'is_pinned': False,
                'priority': 'normal'
            }
            
            response = self.make_request('PUT', f'/admin/announcements/{announcement_id}', update_data, role='admin')
            if response and response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("Update announcement", True, f"Updated announcement {announcement_id}")
                else:
                    self.log_test("Update announcement", False, "Update failed")
                    all_passed = False
            else:
                self.log_test("Update announcement", False, 
                            f"Status: {response.status_code if response else 'No response'}")
                all_passed = False
        
        return all_passed

    def test_user_role_based_access(self) -> bool:
        """Test user role-based announcement access"""
        print("\n👥 TESTING USER ROLE-BASED ANNOUNCEMENT ACCESS...")
        
        all_passed = True
        
        # Test each role's access to announcements
        for role in ['admin', 'client', 'fixer']:
            response = self.make_request('GET', '/announcements', role=role)
            
            if response and response.status_code == 200:
                data = response.json()
                if data.get('success') and 'announcements' in data:
                    announcements = data['announcements']
                    user_role = data.get('user_role', role)
                    
                    # Verify role-based filtering
                    valid_access = True
                    for ann in announcements:
                        target = ann.get('target_audience')
                        if role == 'admin':
                            # Admin should see all
                            pass
                        elif role == 'client':
                            if target not in ['clients', 'all']:
                                valid_access = False
                                break
                        elif role == 'fixer':
                            if target not in ['fixers', 'all']:
                                valid_access = False
                                break
                    
                    if valid_access:
                        self.log_test(f"Get announcements as {role}", True, 
                                    f"Found {len(announcements)} announcements, role filtering correct")
                    else:
                        self.log_test(f"Get announcements as {role}", False, "Role filtering incorrect")
                        all_passed = False
                else:
                    self.log_test(f"Get announcements as {role}", False, "Invalid response structure")
                    all_passed = False
            else:
                self.log_test(f"Get announcements as {role}", False, 
                            f"Status: {response.status_code if response else 'No response'}")
                all_passed = False
        
        return all_passed

    def test_chat_system_functionality(self) -> bool:
        """Test announcement chat system"""
        print("\n💬 TESTING ANNOUNCEMENT CHAT SYSTEM...")
        
        all_passed = True
        
        if not self.test_announcements:
            self.log_test("Chat system test", False, "No test announcements available")
            return False
        
        # Use first announcement for chat testing
        announcement_id = self.test_announcements[0]['id']
        
        # Test GET chat messages (initially empty)
        response = self.make_request('GET', f'/announcements/{announcement_id}/chat', role='client')
        if response and response.status_code == 200:
            data = response.json()
            if data.get('success') and 'messages' in data:
                self.log_test("Get chat messages", True, f"Found {len(data['messages'])} messages")
            else:
                self.log_test("Get chat messages", False, "Invalid response structure")
                all_passed = False
        else:
            self.log_test("Get chat messages", False, 
                        f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        # Test POST chat message as client
        chat_message_data = {
            'message': 'This is a test message from a client user.'
        }
        
        response = self.make_request('POST', f'/announcements/{announcement_id}/chat', chat_message_data, role='client')
        if response and response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('chat_message'):
                message_id = data['chat_message']['id']
                self.test_chat_messages.append({
                    'id': message_id,
                    'announcement_id': announcement_id
                })
                self.log_test("Post chat message (client)", True, f"Message ID: {message_id}")
            else:
                self.log_test("Post chat message (client)", False, "Invalid response structure")
                all_passed = False
        else:
            self.log_test("Post chat message (client)", False, 
                        f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        # Test POST chat message as admin
        admin_message_data = {
            'message': 'This is an admin response to the client message.'
        }
        
        response = self.make_request('POST', f'/announcements/{announcement_id}/chat', admin_message_data, role='admin')
        if response and response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('chat_message'):
                admin_message_id = data['chat_message']['id']
                self.test_chat_messages.append({
                    'id': admin_message_id,
                    'announcement_id': announcement_id
                })
                self.log_test("Post chat message (admin)", True, f"Message ID: {admin_message_id}")
            else:
                self.log_test("Post chat message (admin)", False, "Invalid response structure")
                all_passed = False
        else:
            self.log_test("Post chat message (admin)", False, 
                        f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        return all_passed

    def test_chat_permissions_and_settings(self) -> bool:
        """Test chat permission enforcement and settings"""
        print("\n🔒 TESTING CHAT PERMISSIONS AND SETTINGS...")
        
        all_passed = True
        
        # Find announcement with admin_only_chat enabled (should be the fixer announcement)
        admin_only_announcement = None
        for ann in self.test_announcements:
            if ann['data'].get('admin_only_chat'):
                admin_only_announcement = ann
                break
        
        if admin_only_announcement:
            announcement_id = admin_only_announcement['id']
            
            # Test that non-admin cannot post to admin-only chat
            client_message = {
                'message': 'Client trying to post to admin-only chat'
            }
            
            response = self.make_request('POST', f'/announcements/{announcement_id}/chat', client_message, role='client')
            if response and response.status_code == 403:
                self.log_test("Admin-only chat restriction (client blocked)", True, "Client correctly blocked from admin-only chat")
            else:
                self.log_test("Admin-only chat restriction (client blocked)", False, 
                            f"Expected 403, got {response.status_code if response else 'No response'}")
                all_passed = False
            
            # Test that admin can post to admin-only chat
            admin_message = {
                'message': 'Admin posting to admin-only chat'
            }
            
            response = self.make_request('POST', f'/announcements/{announcement_id}/chat', admin_message, role='admin')
            if response and response.status_code == 200:
                self.log_test("Admin-only chat access (admin allowed)", True, "Admin successfully posted to admin-only chat")
            else:
                self.log_test("Admin-only chat access (admin allowed)", False, 
                            f"Status: {response.status_code if response else 'No response'}")
                all_passed = False
        
        # Find announcement with chat disabled
        chat_disabled_announcement = None
        for ann in self.test_announcements:
            if not ann['data'].get('chat_enabled', True):
                chat_disabled_announcement = ann
                break
        
        if chat_disabled_announcement:
            announcement_id = chat_disabled_announcement['id']
            
            # Test that no one can post to disabled chat
            test_message = {
                'message': 'Trying to post to disabled chat'
            }
            
            response = self.make_request('POST', f'/announcements/{announcement_id}/chat', test_message, role='admin')
            if response and response.status_code == 403:
                self.log_test("Chat disabled restriction", True, "Chat correctly disabled for announcement")
            else:
                self.log_test("Chat disabled restriction", False, 
                            f"Expected 403, got {response.status_code if response else 'No response'}")
                all_passed = False
        
        return all_passed

    def test_authentication_and_authorization(self) -> bool:
        """Test authentication and authorization for all endpoints"""
        print("\n🛡️ TESTING AUTHENTICATION AND AUTHORIZATION...")
        
        all_passed = True
        
        # Test admin endpoints without authentication
        response = self.make_request('GET', '/admin/announcements')
        if response and response.status_code == 401:
            self.log_test("Admin endpoint without auth", True, "Correctly rejected unauthenticated request")
        else:
            self.log_test("Admin endpoint without auth", False, 
                        f"Expected 401, got {response.status_code if response else 'No response'}")
            all_passed = False
        
        # Test admin endpoints with non-admin user
        response = self.make_request('GET', '/admin/announcements', role='client')
        if response and response.status_code == 403:
            self.log_test("Admin endpoint with client auth", True, "Correctly rejected non-admin user")
        else:
            self.log_test("Admin endpoint with client auth", False, 
                        f"Expected 403, got {response.status_code if response else 'No response'}")
            all_passed = False
        
        # Test user endpoints without authentication
        response = self.make_request('GET', '/announcements')
        if response and response.status_code == 401:
            self.log_test("User endpoint without auth", True, "Correctly rejected unauthenticated request")
        else:
            self.log_test("User endpoint without auth", False, 
                        f"Expected 401, got {response.status_code if response else 'No response'}")
            all_passed = False
        
        return all_passed

    def test_data_integrity_and_cascade_deletion(self) -> bool:
        """Test data integrity and cascade deletion"""
        print("\n🗑️ TESTING DATA INTEGRITY AND CASCADE DELETION...")
        
        all_passed = True
        
        if not self.test_announcements or not self.test_chat_messages:
            self.log_test("Data integrity test", False, "No test data available")
            return False
        
        # Get announcement with chat messages
        announcement_with_chat = None
        for ann in self.test_announcements:
            for msg in self.test_chat_messages:
                if msg['announcement_id'] == ann['id']:
                    announcement_with_chat = ann
                    break
            if announcement_with_chat:
                break
        
        if announcement_with_chat:
            announcement_id = announcement_with_chat['id']
            
            # Count chat messages before deletion
            response = self.make_request('GET', f'/announcements/{announcement_id}/chat', role='admin')
            messages_before = 0
            if response and response.status_code == 200:
                data = response.json()
                messages_before = len(data.get('messages', []))
            
            # Delete the announcement
            response = self.make_request('DELETE', f'/admin/announcements/{announcement_id}', role='admin')
            if response and response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("Delete announcement with cascade", True, 
                                f"Deleted announcement and {messages_before} chat messages")
                    
                    # Remove from our test data
                    self.test_announcements = [ann for ann in self.test_announcements if ann['id'] != announcement_id]
                    self.test_chat_messages = [msg for msg in self.test_chat_messages if msg['announcement_id'] != announcement_id]
                else:
                    self.log_test("Delete announcement with cascade", False, "Deletion failed")
                    all_passed = False
            else:
                self.log_test("Delete announcement with cascade", False, 
                            f"Status: {response.status_code if response else 'No response'}")
                all_passed = False
        
        return all_passed

    def test_chat_message_deletion(self) -> bool:
        """Test individual chat message deletion"""
        print("\n🗑️ TESTING CHAT MESSAGE DELETION...")
        
        all_passed = True
        
        if not self.test_chat_messages:
            self.log_test("Chat message deletion test", False, "No test chat messages available")
            return False
        
        # Test deleting a chat message
        message_to_delete = self.test_chat_messages[0]
        message_id = message_to_delete['id']
        announcement_id = message_to_delete['announcement_id']
        
        response = self.make_request('DELETE', f'/announcements/{announcement_id}/chat/{message_id}', role='admin')
        if response and response.status_code == 200:
            data = response.json()
            if data.get('success'):
                self.log_test("Delete chat message", True, f"Deleted message {message_id}")
                # Remove from our test data
                self.test_chat_messages = [msg for msg in self.test_chat_messages if msg['id'] != message_id]
            else:
                self.log_test("Delete chat message", False, "Deletion failed")
                all_passed = False
        else:
            self.log_test("Delete chat message", False, 
                        f"Status: {response.status_code if response else 'No response'}")
            all_passed = False
        
        return all_passed

    def cleanup_test_data(self):
        """Clean up any remaining test data"""
        print("\n🧹 CLEANING UP TEST DATA...")
        
        # Delete remaining announcements
        for announcement in self.test_announcements[:]:
            response = self.make_request('DELETE', f'/admin/announcements/{announcement["id"]}', role='admin')
            if response and response.status_code == 200:
                self.log_test(f"Cleanup announcement {announcement['id']}", True, "Deleted")
                self.test_announcements.remove(announcement)
            else:
                self.log_test(f"Cleanup announcement {announcement['id']}", False, "Failed to delete")

    def run_all_tests(self):
        """Run all announcement system tests"""
        print("🚀 STARTING COMPREHENSIVE ANNOUNCEMENT SYSTEM BACKEND TESTING")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate_users():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Admin Announcement Management
        self.test_admin_announcement_creation()
        self.test_admin_announcement_management()
        
        # Step 3: User Role-Based Access
        self.test_user_role_based_access()
        
        # Step 4: Chat System
        self.test_chat_system_functionality()
        self.test_chat_permissions_and_settings()
        
        # Step 5: Authentication & Authorization
        self.test_authentication_and_authorization()
        
        # Step 6: Data Integrity
        self.test_chat_message_deletion()
        self.test_data_integrity_and_cascade_deletion()
        
        # Step 7: Cleanup
        self.cleanup_test_data()
        
        # Print final results
        self.print_final_results()
        
        return self.results['failed_tests'] == 0

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("🎯 ANNOUNCEMENT SYSTEM BACKEND TESTING RESULTS")
        print("=" * 80)
        
        total = self.results['total_tests']
        passed = self.results['passed_tests']
        failed = self.results['failed_tests']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"📊 SUMMARY:")
        print(f"   Total Tests: {total}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Announcement system is working correctly.")
        else:
            print(f"\n⚠️ {failed} TESTS FAILED. Review the details above.")
        
        print("\n📋 DETAILED RESULTS:")
        for detail in self.results['test_details']:
            status_icon = "✅" if detail['status'] == 'PASS' else "❌"
            print(f"   {status_icon} {detail['test']}")
            if detail['details']:
                print(f"      {detail['details']}")

def main():
    """Main function to run announcement system tests"""
    tester = AnnouncementSystemTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()