#!/usr/bin/env python3
"""
Comprehensive Backend Testing for FixMate-SA Announcement System
Testing all announcement system API endpoints with authentication and authorization
"""

import requests
import json
import time
from datetime import datetime

class AnnouncementTester:
    def __init__(self):
        self.base_url = "http://localhost:8001/api"
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Test accounts
        self.accounts = {
            'admin': {'phone': '+27800000001', 'password': 'admin2024test', 'token': None},
            'client': {'phone': '+27800000002', 'password': 'client2024test', 'token': None},
            'fixer': {'phone': '+27800000003', 'password': 'fixer2024test', 'token': None}
        }
        
        self.test_announcements = []
        self.test_messages = []
        self.results = {'total': 0, 'passed': 0, 'failed': 0}

    def log_test(self, name, success, details=""):
        self.results['total'] += 1
        if success:
            self.results['passed'] += 1
            print(f"✅ {name}")
        else:
            self.results['failed'] += 1
            print(f"❌ {name}")
        if details:
            print(f"   {details}")

    def authenticate_all(self):
        print("🔐 AUTHENTICATING USERS...")
        for role, account in self.accounts.items():
            try:
                response = self.session.post(f"{self.base_url}/auth/login", 
                                           json={'phone': account['phone'], 'password': account['password']})
                if response.status_code == 200:
                    data = response.json()
                    account['token'] = data.get('token')
                    self.log_test(f"Authenticate {role}", True, f"Token: {account['token'][:20]}...")
                else:
                    self.log_test(f"Authenticate {role}", False, f"Status: {response.status_code}")
                    return False
            except Exception as e:
                self.log_test(f"Authenticate {role}", False, f"Error: {e}")
                return False
        return True

    def test_admin_announcement_crud(self):
        print("\n📢 TESTING ADMIN ANNOUNCEMENT CRUD...")
        admin_token = self.accounts['admin']['token']
        headers = {'Authorization': f'Bearer {admin_token}'}
        
        # Test 1: Create announcements for different audiences
        announcements = [
            {'title': 'Client Update', 'content': 'Important update for clients', 'target_audience': 'clients', 'chat_enabled': True, 'admin_only_chat': False},
            {'title': 'Fixer Tools', 'content': 'New tools for fixers', 'target_audience': 'fixers', 'chat_enabled': True, 'admin_only_chat': True},
            {'title': 'Platform Maintenance', 'content': 'System maintenance notice', 'target_audience': 'all', 'chat_enabled': False}
        ]
        
        for i, ann_data in enumerate(announcements, 1):
            try:
                response = self.session.post(f"{self.base_url}/admin/announcements", json=ann_data, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    ann_id = data.get('announcement_id')
                    self.test_announcements.append(ann_id)
                    self.log_test(f"Create announcement {i} ({ann_data['target_audience']})", True, f"ID: {ann_id}")
                else:
                    self.log_test(f"Create announcement {i}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Create announcement {i}", False, f"Error: {e}")
        
        # Test 2: Get all announcements (admin)
        try:
            response = self.session.get(f"{self.base_url}/admin/announcements", headers=headers)
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('announcements', []))
                self.log_test("Get all announcements (admin)", True, f"Found {count} announcements")
            else:
                self.log_test("Get all announcements (admin)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get all announcements (admin)", False, f"Error: {e}")
        
        # Test 3: Update announcement
        if self.test_announcements:
            update_data = {'title': 'Updated Client Notice', 'is_pinned': True}
            try:
                response = self.session.put(f"{self.base_url}/admin/announcements/{self.test_announcements[0]}", 
                                          json=update_data, headers=headers)
                if response.status_code == 200:
                    self.log_test("Update announcement", True, "Successfully updated")
                else:
                    self.log_test("Update announcement", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Update announcement", False, f"Error: {e}")

    def test_role_based_access(self):
        print("\n👥 TESTING ROLE-BASED ACCESS...")
        
        for role, account in self.accounts.items():
            if not account['token']:
                continue
                
            headers = {'Authorization': f'Bearer {account["token"]}'}
            try:
                response = self.session.get(f"{self.base_url}/announcements", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    announcements = data.get('announcements', [])
                    user_role = data.get('user_role', 'unknown')
                    
                    # Verify role-based filtering
                    valid_filtering = True
                    for ann in announcements:
                        target = ann.get('target_audience', '')
                        if role == 'client' and target not in ['clients', 'all']:
                            valid_filtering = False
                        elif role == 'fixer' and target not in ['fixers', 'all']:
                            valid_filtering = False
                    
                    self.log_test(f"Get announcements as {role}", valid_filtering, 
                                f"Found {len(announcements)} announcements, filtering {'correct' if valid_filtering else 'incorrect'}")
                else:
                    self.log_test(f"Get announcements as {role}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Get announcements as {role}", False, f"Error: {e}")

    def test_chat_system(self):
        print("\n💬 TESTING CHAT SYSTEM...")
        
        if not self.test_announcements:
            print("⚠️ No announcements available for chat testing")
            return
        
        client_token = self.accounts['client']['token']
        admin_token = self.accounts['admin']['token']
        ann_id = self.test_announcements[0]  # Use first announcement (clients/all)
        
        # Test 1: Get initial chat messages
        try:
            response = self.session.get(f"{self.base_url}/announcements/{ann_id}/chat", 
                                      headers={'Authorization': f'Bearer {client_token}'})
            if response.status_code == 200:
                data = response.json()
                msg_count = len(data.get('messages', []))
                self.log_test("Get chat messages", True, f"Found {msg_count} messages")
            else:
                self.log_test("Get chat messages", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get chat messages", False, f"Error: {e}")
        
        # Test 2: Post message as client
        try:
            response = self.session.post(f"{self.base_url}/announcements/{ann_id}/chat", 
                                       json={'message': 'Test message from client'},
                                       headers={'Authorization': f'Bearer {client_token}'})
            if response.status_code == 200:
                data = response.json()
                msg_id = data.get('chat_message', {}).get('id')
                if msg_id:
                    self.test_messages.append(msg_id)
                self.log_test("Post chat message (client)", True, f"Message ID: {msg_id}")
            else:
                self.log_test("Post chat message (client)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Post chat message (client)", False, f"Error: {e}")
        
        # Test 3: Post message as admin
        try:
            response = self.session.post(f"{self.base_url}/announcements/{ann_id}/chat", 
                                       json={'message': 'Admin response to client'},
                                       headers={'Authorization': f'Bearer {admin_token}'})
            if response.status_code == 200:
                data = response.json()
                msg_id = data.get('chat_message', {}).get('id')
                if msg_id:
                    self.test_messages.append(msg_id)
                self.log_test("Post chat message (admin)", True, f"Message ID: {msg_id}")
            else:
                self.log_test("Post chat message (admin)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Post chat message (admin)", False, f"Error: {e}")

    def test_chat_permissions(self):
        print("\n🔒 TESTING CHAT PERMISSIONS...")
        
        if len(self.test_announcements) < 2:
            print("⚠️ Not enough announcements for permission testing")
            return
        
        client_token = self.accounts['client']['token']
        admin_token = self.accounts['admin']['token']
        
        # Test admin-only chat (second announcement should be for fixers with admin_only_chat=True)
        admin_only_ann = self.test_announcements[1]
        
        # Client should be blocked from fixer announcement
        try:
            response = self.session.post(f"{self.base_url}/announcements/{admin_only_ann}/chat", 
                                       json={'message': 'Client trying to access fixer announcement'},
                                       headers={'Authorization': f'Bearer {client_token}'})
            if response.status_code == 403:
                self.log_test("Client blocked from fixer announcement", True, "Access correctly denied")
            else:
                self.log_test("Client blocked from fixer announcement", False, f"Expected 403, got {response.status_code}")
        except Exception as e:
            self.log_test("Client blocked from fixer announcement", False, f"Error: {e}")
        
        # Admin should access admin-only chat
        try:
            response = self.session.post(f"{self.base_url}/announcements/{admin_only_ann}/chat", 
                                       json={'message': 'Admin posting to admin-only chat'},
                                       headers={'Authorization': f'Bearer {admin_token}'})
            if response.status_code == 200:
                self.log_test("Admin access to admin-only chat", True, "Admin successfully posted")
            else:
                self.log_test("Admin access to admin-only chat", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Admin access to admin-only chat", False, f"Error: {e}")
        
        # Test chat disabled (third announcement should have chat_enabled=False)
        if len(self.test_announcements) >= 3:
            disabled_chat_ann = self.test_announcements[2]
            try:
                response = self.session.post(f"{self.base_url}/announcements/{disabled_chat_ann}/chat", 
                                           json={'message': 'Trying to post to disabled chat'},
                                           headers={'Authorization': f'Bearer {client_token}'})
                if response.status_code == 403:
                    self.log_test("Chat disabled restriction", True, "Chat correctly disabled")
                else:
                    self.log_test("Chat disabled restriction", False, f"Expected 403, got {response.status_code}")
            except Exception as e:
                self.log_test("Chat disabled restriction", False, f"Error: {e}")

    def test_authentication_authorization(self):
        print("\n🛡️ TESTING AUTHENTICATION & AUTHORIZATION...")
        
        # Test admin endpoint without auth
        try:
            response = self.session.get(f"{self.base_url}/admin/announcements")
            if response.status_code == 401:
                self.log_test("Admin endpoint without auth", True, "Correctly rejected")
            else:
                self.log_test("Admin endpoint without auth", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_test("Admin endpoint without auth", False, f"Error: {e}")
        
        # Test admin endpoint with client auth
        client_token = self.accounts['client']['token']
        try:
            response = self.session.get(f"{self.base_url}/admin/announcements", 
                                      headers={'Authorization': f'Bearer {client_token}'})
            if response.status_code == 403:
                self.log_test("Admin endpoint with client auth", True, "Client correctly denied")
            else:
                self.log_test("Admin endpoint with client auth", False, f"Expected 403, got {response.status_code}")
        except Exception as e:
            self.log_test("Admin endpoint with client auth", False, f"Error: {e}")

    def test_message_deletion(self):
        print("\n🗑️ TESTING MESSAGE DELETION...")
        
        if not self.test_messages or not self.test_announcements:
            print("⚠️ No messages available for deletion testing")
            return
        
        client_token = self.accounts['client']['token']
        ann_id = self.test_announcements[0]
        msg_id = self.test_messages[0]
        
        try:
            response = self.session.delete(f"{self.base_url}/announcements/{ann_id}/chat/{msg_id}", 
                                         headers={'Authorization': f'Bearer {client_token}'})
            if response.status_code == 200:
                self.log_test("Delete chat message", True, f"Deleted message {msg_id}")
            else:
                self.log_test("Delete chat message", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Delete chat message", False, f"Error: {e}")

    def test_cascade_deletion(self):
        print("\n🗑️ TESTING CASCADE DELETION...")
        
        if not self.test_announcements:
            print("⚠️ No announcements available for cascade testing")
            return
        
        admin_token = self.accounts['admin']['token']
        ann_id = self.test_announcements[0]
        
        # Get chat count first
        try:
            response = self.session.get(f"{self.base_url}/announcements/{ann_id}/chat", 
                                      headers={'Authorization': f'Bearer {admin_token}'})
            chat_count = 0
            if response.status_code == 200:
                data = response.json()
                chat_count = len(data.get('messages', []))
        except:
            chat_count = 0
        
        # Delete announcement
        try:
            response = self.session.delete(f"{self.base_url}/admin/announcements/{ann_id}", 
                                         headers={'Authorization': f'Bearer {admin_token}'})
            if response.status_code == 200:
                self.log_test("Delete announcement with cascade", True, f"Deleted announcement and {chat_count} messages")
                self.test_announcements.remove(ann_id)
            else:
                self.log_test("Delete announcement with cascade", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Delete announcement with cascade", False, f"Error: {e}")

    def cleanup(self):
        print("\n🧹 CLEANING UP...")
        admin_token = self.accounts['admin']['token']
        
        for ann_id in self.test_announcements[:]:
            try:
                response = self.session.delete(f"{self.base_url}/admin/announcements/{ann_id}", 
                                             headers={'Authorization': f'Bearer {admin_token}'})
                if response.status_code == 200:
                    self.log_test(f"Cleanup announcement {ann_id}", True, "Deleted")
                    self.test_announcements.remove(ann_id)
                else:
                    self.log_test(f"Cleanup announcement {ann_id}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Cleanup announcement {ann_id}", False, f"Error: {e}")

    def print_results(self):
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
        else:
            print(f"\n⚠️ {failed} TESTS FAILED. Review the details above.")

    def run_all_tests(self):
        print("🚀 STARTING COMPREHENSIVE ANNOUNCEMENT SYSTEM BACKEND TESTING")
        print("="*80)
        
        if not self.authenticate_all():
            print("❌ Authentication failed. Cannot proceed.")
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

if __name__ == "__main__":
    tester = AnnouncementTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)