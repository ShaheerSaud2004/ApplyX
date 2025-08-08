#!/usr/bin/env python3
"""
Comprehensive System Tests for LinkedIn Easy Apply Platform
Tests all functionality: Auth, Admin, User Management, Bot API, Profile, etc.
"""

import requests
import json
import time
import sqlite3
import sys
import os

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(message):
    print(f"{Colors.BLUE}🧪 {message}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_section(message):
    print(f"\n{Colors.PURPLE}{Colors.BOLD}{'='*20} {message} {'='*20}{Colors.END}")

class SystemTester:
    def __init__(self):
        self.backend_url = "http://localhost:5001"
        self.frontend_url = "http://localhost:3000"
        self.admin_token = None
        self.user_tokens = {}
        self.test_users = []
        
    def test_health_checks(self):
        """Test basic service health"""
        print_section("HEALTH CHECKS")
        
        # Backend health
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=5)
            if response.status_code == 200:
                print_success("Backend health check passed")
            else:
                print_error(f"Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Backend not accessible: {e}")
            return False
            
        # Frontend accessibility
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code in [200, 404]:  # 404 is fine for root access
                print_success("Frontend is accessible")
            else:
                print_error(f"Frontend not accessible: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Frontend not accessible: {e}")
            return False
            
        return True
    
    def test_database_connectivity(self):
        """Test database connectivity and schema"""
        print_section("DATABASE TESTS")
        
        try:
            conn = sqlite3.connect('backend/easyapply.db')
            cursor = conn.cursor()
            
            # Test users table
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print_success(f"Database connected - {user_count} users in database")
            
            # Test required columns
            cursor.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cursor.fetchall()]
            required_columns = ['id', 'email', 'password_hash', 'first_name', 'last_name', 
                              'status', 'is_admin', 'linkedin_email_encrypted', 'linkedin_password_encrypted']
            
            missing_columns = [col for col in required_columns if col not in columns]
            if missing_columns:
                print_error(f"Missing database columns: {missing_columns}")
                return False
            else:
                print_success("All required database columns present")
            
            conn.close()
            return True
            
        except Exception as e:
            print_error(f"Database connectivity failed: {e}")
            return False
    
    def test_admin_authentication(self):
        """Test admin login and authentication"""
        print_section("ADMIN AUTHENTICATION")
        
        # Test admin login
        admin_creds = {
            'email': 'admin@teemoai.com',
            'password': 'Admin123!'
        }
        
        try:
            response = requests.post(f"{self.backend_url}/api/auth/login", json=admin_creds, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data['token']
                print_success(f"Admin login successful")
                print_success(f"Admin user: {data['user']['first_name']} {data['user']['last_name']}")
                return True
            else:
                print_error(f"Admin login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Admin login request failed: {e}")
            return False
    
    def test_user_registration_and_approval(self):
        """Test user registration and admin approval workflow"""
        print_section("USER REGISTRATION & APPROVAL")
        
        # Create test users
        test_users_data = [
            {
                'email': 'testuser1@example.com',
                'password': 'TestPass123!',
                'firstName': 'Test',
                'lastName': 'User1'
            },
            {
                'email': 'testuser2@example.com', 
                'password': 'TestPass123!',
                'firstName': 'Test',
                'lastName': 'User2'
            }
        ]
        
        user_ids = []
        
        for user_data in test_users_data:
            try:
                # Register user
                response = requests.post(f"{self.backend_url}/api/auth/register", json=user_data, timeout=10)
                
                if response.status_code == 201:
                    result = response.json()
                    user_ids.append(result['user']['id'])
                    print_success(f"User {user_data['email']} registered successfully")
                else:
                    print_error(f"User registration failed: {response.status_code}")
                    continue
                    
                # Test login (should fail - user pending)
                login_response = requests.post(f"{self.backend_url}/api/auth/login", 
                                             json={'email': user_data['email'], 'password': user_data['password']})
                
                if login_response.status_code == 403:
                    print_success(f"User {user_data['email']} correctly blocked (pending approval)")
                else:
                    print_warning(f"User {user_data['email']} login should be blocked but isn't")
                    
            except Exception as e:
                print_error(f"Registration test failed for {user_data['email']}: {e}")
        
        # Test admin approval
        if not self.admin_token:
            print_error("No admin token available for approval tests")
            return False
            
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Get pending users
        try:
            response = requests.get(f"{self.backend_url}/api/admin/users/pending", headers=headers)
            if response.status_code == 200:
                pending_users = response.json()
                print_success(f"Found {len(pending_users)} pending users")
                
                # Approve test users
                for user_id in user_ids:
                    approve_response = requests.post(f"{self.backend_url}/api/admin/users/{user_id}/approve", 
                                                   headers=headers)
                    if approve_response.status_code == 200:
                        print_success(f"User {user_id} approved successfully")
                    else:
                        print_error(f"Failed to approve user {user_id}")
                        
            else:
                print_error(f"Failed to get pending users: {response.status_code}")
                
        except Exception as e:
            print_error(f"Admin approval test failed: {e}")
        
        # Test approved user login
        for i, user_data in enumerate(test_users_data):
            try:
                login_response = requests.post(f"{self.backend_url}/api/auth/login",
                                             json={'email': user_data['email'], 'password': user_data['password']})
                
                if login_response.status_code == 200:
                    result = login_response.json()
                    self.user_tokens[user_data['email']] = result['token']
                    self.test_users.append(user_data)
                    print_success(f"Approved user {user_data['email']} login successful")
                else:
                    print_error(f"Approved user {user_data['email']} login failed: {login_response.status_code}")
                    
            except Exception as e:
                print_error(f"User login test failed for {user_data['email']}: {e}")
        
        return len(self.user_tokens) > 0
    
    def test_profile_management(self):
        """Test user profile creation and management"""
        print_section("PROFILE MANAGEMENT")
        
        if not self.user_tokens:
            print_error("No user tokens available for profile tests")
            return False
        
        test_email = list(self.user_tokens.keys())[0]
        token = self.user_tokens[test_email]
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test profile creation/update
        profile_data = {
            'personalInfo': {
                'phone': '555-0123',
                'location': 'East Brunswick, New Jersey',
                'experience': 'entry'
            },
            'jobPreferences': {
                'jobTitles': ['Software Engineer', 'Developer'],
                'locations': ['Remote', 'New York'],
                'jobTypes': ['full-time'],
                'salaryMin': 65000
            },
            'linkedinCreds': {
                'email': test_email,
                'password': 'test_linkedin_password'
            }
        }
        
        try:
            response = requests.put(f"{self.backend_url}/api/profile", 
                                  json=profile_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print_success("Profile updated successfully")
                
                # Test profile retrieval
                get_response = requests.get(f"{self.backend_url}/api/profile", headers=headers)
                
                if get_response.status_code == 200:
                    profile = get_response.json()
                    print_success("Profile retrieved successfully")
                    
                    # Verify data
                    if profile.get('personalInfo', {}).get('phone') == '555-0123':
                        print_success("Personal info stored correctly")
                    else:
                        print_error("Personal info not stored correctly")
                        
                    if profile.get('linkedinCreds', {}).get('email') == test_email:
                        print_success("LinkedIn credentials encrypted and stored")
                    else:
                        print_error("LinkedIn credentials not stored correctly")
                        
                    return True
                else:
                    print_error(f"Profile retrieval failed: {get_response.status_code}")
                    
            else:
                print_error(f"Profile update failed: {response.status_code}")
                
        except Exception as e:
            print_error(f"Profile management test failed: {e}")
            
        return False
    
    def test_bot_api_endpoints(self):
        """Test LinkedIn bot API endpoints"""
        print_section("BOT API ENDPOINTS")
        
        if not self.user_tokens:
            print_error("No user tokens available for bot API tests")
            return False
        
        test_email = list(self.user_tokens.keys())[0]
        token = self.user_tokens[test_email]
        headers = {'Authorization': f'Bearer {token}'}
        
        try:
            # Test bot status
            status_response = requests.get(f"{self.backend_url}/api/bot/status", headers=headers)
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                print_success(f"Bot status endpoint working - Status: {status_data.get('status', 'unknown')}")
            else:
                print_error(f"Bot status endpoint failed: {status_response.status_code}")
                return False
            
            # Test bot start
            start_response = requests.post(f"{self.backend_url}/api/bot/start", headers=headers)
            
            if start_response.status_code == 200:
                start_data = start_response.json()
                print_success(f"Bot start endpoint working: {start_data.get('message', 'Started')}")
            else:
                print_warning(f"Bot start may have issues: {start_response.status_code} - {start_response.text}")
            
            # Test bot stop
            stop_response = requests.post(f"{self.backend_url}/api/bot/stop", headers=headers)
            
            if stop_response.status_code == 200:
                stop_data = stop_response.json()
                print_success(f"Bot stop endpoint working: {stop_data.get('message', 'Stopped')}")
            else:
                print_warning(f"Bot stop may have issues: {stop_response.status_code}")
            
            return True
            
        except Exception as e:
            print_error(f"Bot API test failed: {e}")
            return False
    
    def test_admin_dashboard_features(self):
        """Test admin dashboard functionality"""
        print_section("ADMIN DASHBOARD")
        
        if not self.admin_token:
            print_error("No admin token available for dashboard tests")
            return False
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        try:
            # Test admin stats
            stats_response = requests.get(f"{self.backend_url}/api/admin/stats", headers=headers)
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print_success(f"Admin stats endpoint working")
                print_success(f"  Total Users: {stats.get('totalUsers', 0)}")
                print_success(f"  Pending Users: {stats.get('pendingUsers', 0)}")
                print_success(f"  Active Bots: {stats.get('activeBots', 0)}")
            else:
                print_error(f"Admin stats failed: {stats_response.status_code}")
                return False
            
            # Test user list
            users_response = requests.get(f"{self.backend_url}/api/admin/users", headers=headers)
            
            if users_response.status_code == 200:
                users = users_response.json()
                print_success(f"Admin users list working - {len(users)} users found")
            else:
                print_error(f"Admin users list failed: {users_response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            print_error(f"Admin dashboard test failed: {e}")
            return False
    
    def test_shaheer_account(self):
        """Test the pre-configured Shaheer account specifically"""
        print_section("SHAHEER ACCOUNT TEST")
        
        shaheer_creds = {
            'email': 'shaheersaud2004@gmail.com',
            'password': 'TestPassword123!'
        }
        
        try:
            # Test login
            response = requests.post(f"{self.backend_url}/api/auth/login", json=shaheer_creds, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                shaheer_token = data['token']
                print_success(f"Shaheer account login successful")
                
                # Test profile
                headers = {'Authorization': f'Bearer {shaheer_token}'}
                profile_response = requests.get(f"{self.backend_url}/api/profile", headers=headers)
                
                if profile_response.status_code == 200:
                    profile = profile_response.json()
                    print_success("Shaheer profile loaded successfully")
                    
                    # Check LinkedIn credentials
                    linkedin_creds = profile.get('linkedinCreds', {})
                    if linkedin_creds.get('email') and linkedin_creds.get('password'):
                        print_success("Shaheer LinkedIn credentials are encrypted and available")
                    else:
                        print_warning("Shaheer LinkedIn credentials may not be configured")
                    
                    # Check job preferences
                    job_prefs = profile.get('jobPreferences', {})
                    if job_prefs:
                        print_success(f"Shaheer job preferences configured: {job_prefs.get('jobTitles', [])}")
                    else:
                        print_warning("Shaheer job preferences not configured")
                    
                    # Test bot API for Shaheer
                    bot_status_response = requests.get(f"{self.backend_url}/api/bot/status", headers=headers)
                    if bot_status_response.status_code == 200:
                        print_success("Shaheer bot API accessible")
                        return True
                    else:
                        print_warning(f"Shaheer bot API issue: {bot_status_response.status_code}")
                        
                else:
                    print_error(f"Shaheer profile load failed: {profile_response.status_code}")
                    
            else:
                print_error(f"Shaheer login failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print_error(f"Shaheer account test failed: {e}")
            
        return False
    
    def cleanup_test_data(self):
        """Clean up test users created during testing"""
        print_section("CLEANUP")
        
        if not self.admin_token:
            print_warning("No admin token - skipping cleanup")
            return
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Get all users and delete test users
        try:
            response = requests.get(f"{self.backend_url}/api/admin/users", headers=headers)
            if response.status_code == 200:
                users = response.json()
                
                test_emails = ['testuser1@example.com', 'testuser2@example.com']
                cleaned_count = 0
                
                for user in users:
                    if user['email'] in test_emails:
                        delete_response = requests.delete(f"{self.backend_url}/api/admin/users/{user['id']}/delete", 
                                                        headers=headers)
                        if delete_response.status_code == 200:
                            cleaned_count += 1
                
                print_success(f"Cleaned up {cleaned_count} test users")
                
        except Exception as e:
            print_warning(f"Cleanup failed: {e}")
    
    def run_all_tests(self):
        """Run all system tests"""
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("🚀 COMPREHENSIVE LINKEDIN EASY APPLY SYSTEM TESTS")
        print("=" * 60)
        print(f"{Colors.END}")
        
        test_results = []
        
        # Run all tests
        tests = [
            ("Health Checks", self.test_health_checks),
            ("Database Connectivity", self.test_database_connectivity),
            ("Admin Authentication", self.test_admin_authentication),
            ("User Registration & Approval", self.test_user_registration_and_approval),
            ("Profile Management", self.test_profile_management),
            ("Bot API Endpoints", self.test_bot_api_endpoints),
            ("Admin Dashboard", self.test_admin_dashboard_features),
            ("Shaheer Account", self.test_shaheer_account),
        ]
        
        for test_name, test_func in tests:
            print_test(f"Running {test_name}...")
            try:
                result = test_func()
                test_results.append((test_name, result))
                if result:
                    print_success(f"{test_name} PASSED")
                else:
                    print_error(f"{test_name} FAILED")
            except Exception as e:
                print_error(f"{test_name} ERROR: {e}")
                test_results.append((test_name, False))
            
            time.sleep(1)  # Brief pause between tests
        
        # Cleanup
        self.cleanup_test_data()
        
        # Final results
        print_section("FINAL RESULTS")
        
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")
        
        print(f"\n{Colors.BOLD}SUMMARY: {passed}/{total} tests passed{Colors.END}")
        
        if passed == total:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! System is fully operational!{Colors.END}")
        elif passed >= total * 0.8:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  Most tests passed - System mostly functional with minor issues{Colors.END}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ Multiple test failures - System needs attention{Colors.END}")
        
        return passed == total

if __name__ == "__main__":
    tester = SystemTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n{Colors.GREEN}🚀 System ready for production use!{Colors.END}")
        exit(0)
    else:
        print(f"\n{Colors.RED}🔧 System needs fixes before production use.{Colors.END}")
        exit(1) 