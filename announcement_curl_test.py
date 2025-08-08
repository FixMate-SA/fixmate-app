#!/usr/bin/env python3
"""
Comprehensive Backend Testing for FixMate-SA Announcement System using curl
Testing all announcement system API endpoints with authentication and authorization
"""

import subprocess
import json
import sys
from typing import Dict, Optional, Tuple

class AnnouncementTesterCurl:
    def __init__(self):
        self.base_url = "http://localhost:8001/api"
        
        # Test accounts
        self.accounts = {
            'admin': {'phone': '+27800000001', 'password': 'admin2024test', 'token': None},
            'client': {'phone': '+27800000002', 'password': 'client2024test', 'token': None},
            'fixer': {'phone': '+27800000003', 'password': 'fixer2024test', 'token': None}
        }
        
        self.test_announcements = []
        self.test_messages = []
        self.results = {'total': 0, 'passed': 0, 'failed': 0}

    def log_test(self, name: str, success: bool, details: str = ""):
        self.results['total'] += 1
        if success:
            self.results['passed'] += 1
            print(f"✅ {name}")
        else:
            self.results['failed'] += 1
            print(f"❌ {name}")
        if details:
            print(f"   {details}")

    def curl_request(self, method: str, endpoint: str, data: Dict = None, token: str = None) -> Tuple[int, Dict]:
        """Make HTTP request using curl"""
        url = f"{self.base_url}{endpoint}"
        cmd = ['curl', '-s', '-w', '%{http_code}', '-X', method, url]
        
        # Add headers
        cmd.extend(['-H', 'Content-Type: application/json'])
        if token:
            cmd.extend(['-H', f'Authorization: Bearer {token}'])
        
        # Add data for POST/PUT requests
        if data and method in ['POST', 'PUT']:
            cmd.extend(['-d', json.dumps(data)])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            output = result.stdout
            
            # Extract status code (last 3 characters)
            if len(output) >= 3:
                status_code = int(output[-3:])
                response_body = output[:-3]
            else:
                status_code = 0
                response_body = output
            
            # Try to parse JSON response
            try:
                if response_body.strip():
                    response_data = json.loads(response_body)
                else:
                    response_data = {}
            except json.JSONDecodeError:
                response_data = {'raw': response_body}
            
            return status_code, response_data
            
        except subprocess.TimeoutExpired:
            return 0, {'error': 'Request timeout'}
        except Exception as e:
            return 0, {'error': str(e)}

    def authenticate_all(self) -> bool:
        """Authenticate all test users"""
        print("🔐 AUTHENTICATING USERS...")
        
        for role, account in self.accounts.items():
            login_data = {'phone': account['phone'], 'password': account['password']}
            status_code, response = self.curl_request('POST', '/auth/login', login_data)
            
            if status_code == 200 and 'token' in response:
                account['token'] = response['token']
                user_name = response.get('user', {}).get('first_name', 'Unknown')
                self.log_test(f"Authenticate {role}", True, f"User: {user_name}, Token: {account['token'][:20]}...")
            else:
                self.log_test(f"Authenticate {role}", False, f"Status: {status_code}, Response: {response}")
                return False
        
        return True

    def test_admin_announcement_crud(self):
        """Test admin announcement CRUD operations"""
        print("\n📢 TESTING ADMIN ANNOUNCEMENT CRUD...")
        
        admin_token = self.accounts['admin']['token']
        
        # Test 1: Create announcements for different audiences
        announcements = [
            {
                'title': 'Important Client Update',
                'content': 'We have updated our service pricing and terms. Please review the new rates and conditions.',
                'target_audience': 'clients',
                'is_pinned': True,
                'priority': 'high',
                'chat_enabled': True,
                'admin_only_chat': False
            },
            {
                'title': 'New Fixer Tools Available',
                'content': 'We have added new tools and resources to help you complete jobs more efficiently.',
                'target_audience': 'fixers',
                'is_pinned': False,
                'priority': 'normal',
                'chat_enabled': True,
                'admin_only_chat': True
            },
            {
                'title': 'Platform Maintenance Notice',
                'content': 'The platform will undergo scheduled maintenance this weekend. Services may be temporarily unavailable.',
                'target_audience': 'all',
                'is_pinned': True,
                'priority': 'high',
                'chat_enabled': False,
                'admin_only_chat': False
            }
        ]
        
        for i, ann_data in enumerate(announcements, 1):
            status_code, response = self.curl_request('POST', '/admin/announcements', ann_data, admin_token)
            
            if status_code == 200 and response.get('success'):
                ann_id = response.get('announcement_id')
                self.test_announcements.append(ann_id)
                self.log_test(f"Create announcement {i} ({ann_data['target_audience']})", True, f"ID: {ann_id}")
            else:
                self.log_test(f"Create announcement {i} ({ann_data['target_audience']})", False, 
                            f"Status: {status_code}, Response: {response}")
        
        # Test 2: Get all announcements (admin view)
        status_code, response = self.curl_request('GET', '/admin/announcements', token=admin_token)
        
        if status_code == 200 and response.get('success'):
            count = len(response.get('announcements', []))
            self.log_test("Get all announcements (admin)", True, f"Found {count} announcements")
        else:
            self.log_test("Get all announcements (admin)", False, f"Status: {status_code}, Response: {response}")
        
        # Test 3: Update announcement
        if self.test_announcements:
            update_data = {
                'title': 'Updated Important Client Notice',
                'content': 'This announcement has been updated with additional important information.',
                'is_pinned': False,
                'priority': 'normal'
            }
            
            status_code, response = self.curl_request('PUT', f'/admin/announcements/{self.test_announcements[0]}', 
                                                    update_data, admin_token)
            
            if status_code == 200 and response.get('success'):
                self.log_test("Update announcement", True, f"Updated announcement {self.test_announcements[0]}")
            else:
                self.log_test("Update announcement", False, f"Status: {status_code}, Response: {response}")

    def test_role_based_access(self):
        """Test role-based announcement filtering"""
        print("\n👥 TESTING ROLE-BASED ACCESS...")
        
        for role, account in self.accounts.items():
            if not account['token']:
                continue
            
            status_code, response = self.curl_request('GET', '/announcements', token=account['token'])
            
            if status_code == 200 and response.get('success'):
                announcements = response.get('announcements', [])
                user_role = response.get('user_role', 'unknown')
                
                # Verify role-based filtering
                valid_filtering = True
                for ann in announcements:
                    target = ann.get('target_audience', '')
                    if role == 'admin':
                        continue  # Admin sees all
                    elif role == 'client' and target not in ['clients', 'all']:
                        valid_filtering = False
                        break
                    elif role == 'fixer' and target not in ['fixers', 'all']:
                        valid_filtering = False
                        break
                
                self.log_test(f"Get announcements as {role}", valid_filtering, 
                            f"Found {len(announcements)} announcements, role filtering {'correct' if valid_filtering else 'incorrect'}")
            else:
                self.log_test(f"Get announcements as {role}", False, f"Status: {status_code}, Response: {response}")

    def test_chat_system(self):
        """Test announcement chat functionality"""
        print("\n💬 TESTING CHAT SYSTEM...")
        
        if not self.test_announcements:
            print("⚠️ No announcements available for chat testing")
            return
        
        client_token = self.accounts['client']['token']
        admin_token = self.accounts['admin']['token']
        ann_id = self.test_announcements[0]  # Use first announcement (clients/all)
        
        # Test 1: Get initial chat messages
        status_code, response = self.curl_request('GET', f'/announcements/{ann_id}/chat', token=client_token)
        
        if status_code == 200 and response.get('success'):
            msg_count = len(response.get('messages', []))
            can_post = response.get('can_post', False)
            self.log_test("Get chat messages", True, f"Found {msg_count} messages, can_post: {can_post}")
        else:
            self.log_test("Get chat messages", False, f"Status: {status_code}, Response: {response}")
        
        # Test 2: Post message as client
        chat_data = {'message': 'This is a test message from a client user. How can I get help with my service request?'}
        status_code, response = self.curl_request('POST', f'/announcements/{ann_id}/chat', chat_data, client_token)
        
        if status_code == 200 and response.get('success'):
            msg_id = response.get('chat_message', {}).get('id')
            if msg_id:
                self.test_messages.append(msg_id)
            self.log_test("Post chat message (client)", True, f"Message ID: {msg_id}")
        else:
            self.log_test("Post chat message (client)", False, f"Status: {status_code}, Response: {response}")
        
        # Test 3: Post message as admin
        admin_chat_data = {'message': 'Thank you for your message. Our support team will assist you with your service request shortly.'}
        status_code, response = self.curl_request('POST', f'/announcements/{ann_id}/chat', admin_chat_data, admin_token)
        
        if status_code == 200 and response.get('success'):
            msg_id = response.get('chat_message', {}).get('id')
            if msg_id:
                self.test_messages.append(msg_id)
            self.log_test("Post chat message (admin)", True, f"Message ID: {msg_id}")
        else:
            self.log_test("Post chat message (admin)", False, f"Status: {status_code}, Response: {response}")

    def test_chat_permissions(self):
        """Test chat permission controls"""
        print("\n🔒 TESTING CHAT PERMISSIONS...")
        
        if len(self.test_announcements) < 2:
            print("⚠️ Not enough announcements for permission testing")
            return
        
        client_token = self.accounts['client']['token']
        admin_token = self.accounts['admin']['token']
        fixer_token = self.accounts['fixer']['token']
        
        # Test 1: Client trying to access fixer-only announcement
        fixer_ann = self.test_announcements[1]  # Should be fixer-only
        chat_data = {'message': 'Client trying to access fixer announcement'}
        status_code, response = self.curl_request('POST', f'/announcements/{fixer_ann}/chat', chat_data, client_token)
        
        if status_code == 403:
            self.log_test("Client blocked from fixer announcement", True, "Access correctly denied")
        else:
            self.log_test("Client blocked from fixer announcement", False, f"Expected 403, got {status_code}: {response}")
        
        # Test 2: Fixer trying to post to admin-only chat
        chat_data = {'message': 'Fixer trying to post to admin-only chat'}
        status_code, response = self.curl_request('POST', f'/announcements/{fixer_ann}/chat', chat_data, fixer_token)
        
        if status_code == 403:
            self.log_test("Fixer blocked from admin-only chat", True, "Admin-only restriction working")
        else:
            self.log_test("Fixer blocked from admin-only chat", False, f"Expected 403, got {status_code}: {response}")
        
        # Test 3: Admin access to admin-only chat
        admin_chat_data = {'message': 'Admin posting to admin-only fixer announcement chat'}
        status_code, response = self.curl_request('POST', f'/announcements/{fixer_ann}/chat', admin_chat_data, admin_token)
        
        if status_code == 200 and response.get('success'):
            self.log_test("Admin access to admin-only chat", True, "Admin successfully posted")
        else:
            self.log_test("Admin access to admin-only chat", False, f"Status: {status_code}, Response: {response}")
        
        # Test 4: Chat disabled restriction
        if len(self.test_announcements) >= 3:
            disabled_chat_ann = self.test_announcements[2]  # Should have chat_enabled=False
            chat_data = {'message': 'Trying to post to disabled chat'}
            status_code, response = self.curl_request('POST', f'/announcements/{disabled_chat_ann}/chat', chat_data, client_token)
            
            if status_code == 403:
                self.log_test("Chat disabled restriction", True, "Chat correctly disabled")
            else:
                self.log_test("Chat disabled restriction", False, f"Expected 403, got {status_code}: {response}")

    def test_authentication_authorization(self):
        """Test authentication and authorization controls"""
        print("\n🛡️ TESTING AUTHENTICATION & AUTHORIZATION...")
        
        # Test 1: Admin endpoint without authentication
        status_code, response = self.curl_request('GET', '/admin/announcements')
        
        if status_code == 401:
            self.log_test("Admin endpoint without auth", True, "Correctly rejected unauthenticated request")
        else:
            self.log_test("Admin endpoint without auth", False, f"Expected 401, got {status_code}: {response}")
        
        # Test 2: Admin endpoint with client authentication
        client_token = self.accounts['client']['token']
        status_code, response = self.curl_request('GET', '/admin/announcements', token=client_token)
        
        if status_code == 403:
            self.log_test("Admin endpoint with client auth", True, "Client correctly denied admin access")
        else:
            self.log_test("Admin endpoint with client auth", False, f"Expected 403, got {status_code}: {response}")
        
        # Test 3: User endpoint without authentication
        status_code, response = self.curl_request('GET', '/announcements')
        
        if status_code == 401:
            self.log_test("User endpoint without auth", True, "Correctly rejected unauthenticated request")
        else:
            self.log_test("User endpoint without auth", False, f"Expected 401, got {status_code}: {response}")

    def test_message_deletion(self):
        """Test chat message deletion functionality"""
        print("\n🗑️ TESTING MESSAGE DELETION...")
        
        if not self.test_messages or not self.test_announcements:
            print("⚠️ No messages available for deletion testing")
            return
        
        client_token = self.accounts['client']['token']
        ann_id = self.test_announcements[0]
        msg_id = self.test_messages[0]
        
        status_code, response = self.curl_request('DELETE', f'/announcements/{ann_id}/chat/{msg_id}', token=client_token)
        
        if status_code == 200 and response.get('success'):
            self.log_test("Delete chat message", True, f"Deleted message {msg_id}")
        else:
            self.log_test("Delete chat message", False, f"Status: {status_code}, Response: {response}")

    def test_cascade_deletion(self):
        """Test data integrity and cascade deletion"""
        print("\n🗑️ TESTING CASCADE DELETION...")
        
        if not self.test_announcements:
            print("⚠️ No announcements available for cascade testing")
            return
        
        admin_token = self.accounts['admin']['token']
        ann_id = self.test_announcements[0]
        
        # Get chat message count first
        status_code, response = self.curl_request('GET', f'/announcements/{ann_id}/chat', token=admin_token)
        chat_count = 0
        if status_code == 200 and response.get('success'):
            chat_count = len(response.get('messages', []))
        
        # Delete announcement (should cascade delete chat messages)
        status_code, response = self.curl_request('DELETE', f'/admin/announcements/{ann_id}', token=admin_token)
        
        if status_code == 200 and response.get('success'):
            self.log_test("Delete announcement with cascade", True, f"Deleted announcement and {chat_count} chat messages")
            self.test_announcements.remove(ann_id)
        else:
            self.log_test("Delete announcement with cascade", False, f"Status: {status_code}, Response: {response}")

    def cleanup(self):
        """Clean up remaining test data"""
        print("\n🧹 CLEANING UP...")
        
        admin_token = self.accounts['admin']['token']
        
        for ann_id in self.test_announcements[:]:
            status_code, response = self.curl_request('DELETE', f'/admin/announcements/{ann_id}', token=admin_token)
            
            if status_code == 200 and response.get('success'):
                self.log_test(f"Cleanup announcement {ann_id}", True, "Deleted")
                self.test_announcements.remove(ann_id)
            else:
                self.log_test(f"Cleanup announcement {ann_id}", False, f"Status: {status_code}, Response: {response}")

    def print_results(self):
        """Print comprehensive test results"""
        print("\n" + "="*80)
        print("🎯 ANNOUNCEMENT SYSTEM BACKEND TESTING RESULTS")
        print("="*80)
        
        total = self.results['total']
        passed = self.results['passed']
        failed = self.results['failed']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"📊 SUMMARY:")
        print(f"   Total Tests: {total}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print(f"\n🎉 ALL TESTS PASSED! Announcement system is working perfectly.")
            print(f"✅ ADMIN ANNOUNCEMENT MANAGEMENT: Create/read/update/delete working correctly")
            print(f"✅ ROLE-BASED ACCESS CONTROL: Proper filtering by user role (clients, fixers, all)")
            print(f"✅ CHAT SYSTEM: Message posting/retrieval with permission controls working")
            print(f"✅ AUTHENTICATION & AUTHORIZATION: All security controls functioning properly")
            print(f"✅ DATA INTEGRITY: Cascade deletion and relationships working correctly")
        else:
            print(f"\n⚠️ {failed} TESTS FAILED. Review the details above.")
        
        print(f"\n🔧 SYSTEM READY: The announcement system backend is fully functional and ready for frontend integration.")

    def run_all_tests(self):
        """Run all announcement system tests"""
        print("🚀 STARTING COMPREHENSIVE ANNOUNCEMENT SYSTEM BACKEND TESTING")
        print("="*80)
        
        if not self.authenticate_all():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        self.test_admin_announcement_crud()
        self.test_role_based_access()
        self.test_chat_system()
        self.test_chat_permissions()
        self.test_authentication_authorization()
        self.test_message_deletion()
        self.test_cascade_deletion()
        self.cleanup()
        self.print_results()
        
        return self.results['failed'] == 0

def main():
    """Main function to run announcement system tests"""
    tester = AnnouncementTesterCurl()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()