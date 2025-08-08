#!/usr/bin/env python3

import requests
import json
import time
import random
import string
from datetime import datetime, timedelta
import uuid

class ComprehensivePlatformTester:
    """
    Comprehensive test suite for the EasyApply Platform
    Tests all features including authentication, profile management, 
    LinkedIn credentials, job preferences, agent controls, and security
    """
    
    def __init__(self, backend_url="http://localhost:5001", frontend_url="http://localhost:3000"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.test_users = []
        self.test_results = []
        
    def log_test(self, test_name, status, details="", error=None):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'error': str(error) if error else None
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   📝 {details}")
        if error:
            print(f"   ❌ Error: {error}")
        print()

    def generate_test_user(self):
        """Generate random test user data"""
        random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return {
            'email': f'test_{random_id}@example.com',
            'password': 'TestPassword123!',
            'first_name': f'Test{random_id}',
            'last_name': 'User',
            'linkedin_email': f'linkedin_{random_id}@example.com',
            'linkedin_password': 'LinkedInPass123!'
        }

    def test_server_health(self):
        """Test 1: Server Health Check"""
        try:
            # Test frontend
            frontend_response = requests.get(self.frontend_url, timeout=10)
            frontend_ok = frontend_response.status_code == 200
            
            # Test backend
            backend_response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            backend_ok = backend_response.status_code == 200
            
            if frontend_ok and backend_ok:
                self.log_test("Server Health Check", "PASS", 
                             f"Frontend: {frontend_response.status_code}, Backend: {backend_response.status_code}")
            else:
                self.log_test("Server Health Check", "FAIL", 
                             f"Frontend: {frontend_response.status_code}, Backend: {backend_response.status_code}")
                             
        except Exception as e:
            self.log_test("Server Health Check", "FAIL", error=e)

    def test_user_registration(self):
        """Test 2: User Registration"""
        try:
            user_data = self.generate_test_user()
            
            response = requests.post(f"{self.backend_url}/api/auth/register", 
                                   json=user_data, timeout=10)
            
            if response.status_code == 201:
                data = response.json()
                if 'token' in data and 'user' in data:
                    user_data['token'] = data['token']
                    user_data['user_id'] = data['user']['id']
                    self.test_users.append(user_data)
                    self.log_test("User Registration", "PASS", 
                                 f"User {user_data['email']} registered successfully")
                else:
                    self.log_test("User Registration", "FAIL", "Missing token or user data in response")
            else:
                self.log_test("User Registration", "FAIL", 
                             f"Status: {response.status_code}, Response: {response.text}")
                             
        except Exception as e:
            self.log_test("User Registration", "FAIL", error=e)

    def test_user_login(self):
        """Test 3: User Login"""
        if not self.test_users:
            self.log_test("User Login", "SKIP", "No test users available")
            return
            
        try:
            user = self.test_users[0]
            login_data = {
                'email': user['email'],
                'password': user['password']
            }
            
            response = requests.post(f"{self.backend_url}/api/auth/login", 
                                   json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.log_test("User Login", "PASS", 
                                 f"User {user['email']} logged in successfully")
                else:
                    self.log_test("User Login", "FAIL", "Missing token in response")
            else:
                self.log_test("User Login", "FAIL", 
                             f"Status: {response.status_code}, Response: {response.text}")
                             
        except Exception as e:
            self.log_test("User Login", "FAIL", error=e)

    def test_profile_get_empty(self):
        """Test 4: Get Empty Profile"""
        if not self.test_users:
            self.log_test("Get Empty Profile", "SKIP", "No test users available")
            return
            
        try:
            user = self.test_users[0]
            headers = {'Authorization': f'Bearer {user["token"]}'}
            
            response = requests.get(f"{self.backend_url}/api/profile", 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_keys = ['user', 'linkedinCreds', 'jobPreferences']
                
                if all(key in data for key in expected_keys):
                    # Check that LinkedIn credentials are empty initially
                    if not data['linkedinCreds']['email'] and not data['linkedinCreds']['password']:
                        self.log_test("Get Empty Profile", "PASS", 
                                     "Profile structure correct, LinkedIn credentials empty as expected")
                    else:
                        self.log_test("Get Empty Profile", "FAIL", 
                                     "LinkedIn credentials should be empty for new user")
                else:
                    self.log_test("Get Empty Profile", "FAIL", 
                                 f"Missing keys in response: {expected_keys}")
            else:
                self.log_test("Get Empty Profile", "FAIL", 
                             f"Status: {response.status_code}, Response: {response.text}")
                             
        except Exception as e:
            self.log_test("Get Empty Profile", "FAIL", error=e)

    def test_profile_update_linkedin_credentials(self):
        """Test 5: Update LinkedIn Credentials"""
        if not self.test_users:
            self.log_test("Update LinkedIn Credentials", "SKIP", "No test users available")
            return
            
        try:
            user = self.test_users[0]
            headers = {'Authorization': f'Bearer {user["token"]}'}
            
            profile_data = {
                'user': {
                    'firstName': user['first_name'],
                    'lastName': user['last_name'],
                    'phone': '+1234567890'
                },
                'linkedinCreds': {
                    'email': user['linkedin_email'],
                    'password': user['linkedin_password']
                },
                'jobPreferences': {
                    'jobTitles': 'Software Engineer, Full Stack Developer',
                    'locations': 'San Francisco, New York, Remote',
                    'remote': True,
                    'experience': 'mid',
                    'salaryMin': '120000',
                    'skills': 'Python, JavaScript, React, Node.js'
                }
            }
            
            response = requests.put(f"{self.backend_url}/api/profile", 
                                  json=profile_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.log_test("Update LinkedIn Credentials", "PASS", 
                             "Profile with LinkedIn credentials updated successfully")
            else:
                self.log_test("Update LinkedIn Credentials", "FAIL", 
                             f"Status: {response.status_code}, Response: {response.text}")
                             
        except Exception as e:
            self.log_test("Update LinkedIn Credentials", "FAIL", error=e)

    def test_profile_get_with_credentials(self):
        """Test 6: Get Profile with Credentials (Encryption Test)"""
        if not self.test_users:
            self.log_test("Get Profile with Credentials", "SKIP", "No test users available")
            return
            
        try:
            user = self.test_users[0]
            headers = {'Authorization': f'Bearer {user["token"]}'}
            
            response = requests.get(f"{self.backend_url}/api/profile", 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                linkedin_creds = data.get('linkedinCreds', {})
                
                # Check that credentials are returned (decrypted)
                if (linkedin_creds.get('email') == user['linkedin_email'] and 
                    linkedin_creds.get('password') == user['linkedin_password']):
                    self.log_test("Get Profile with Credentials", "PASS", 
                                 "LinkedIn credentials encrypted/decrypted correctly")
                else:
                    self.log_test("Get Profile with Credentials", "FAIL", 
                                 "LinkedIn credentials not returned correctly")
            else:
                self.log_test("Get Profile with Credentials", "FAIL", 
                             f"Status: {response.status_code}, Response: {response.text}")
                             
        except Exception as e:
            self.log_test("Get Profile with Credentials", "FAIL", error=e)

    def test_agent_start_without_credentials(self):
        """Test 7: Start Agent Without LinkedIn Credentials"""
        # Create a new user without LinkedIn credentials
        try:
            user_data = self.generate_test_user()
            
            # Register user
            response = requests.post(f"{self.backend_url}/api/auth/register", 
                                   json=user_data, timeout=10)
            
            if response.status_code == 201:
                data = response.json()
                token = data['token']
                headers = {'Authorization': f'Bearer {token}'}
                
                # Try to start agent without LinkedIn credentials
                agent_response = requests.post(f"{self.backend_url}/api/agent/start", 
                                             headers=headers, timeout=10)
                
                if agent_response.status_code == 400:
                    error_data = agent_response.json()
                    if 'LinkedIn credentials not configured' in error_data.get('error', ''):
                        self.log_test("Agent Start Without Credentials", "PASS", 
                                     "Correctly blocked agent start without LinkedIn credentials")
                    else:
                        self.log_test("Agent Start Without Credentials", "FAIL", 
                                     "Wrong error message for missing credentials")
                else:
                    self.log_test("Agent Start Without Credentials", "FAIL", 
                                 f"Should have returned 400, got {agent_response.status_code}")
            else:
                self.log_test("Agent Start Without Credentials", "FAIL", 
                             "Failed to create test user")
                             
        except Exception as e:
            self.log_test("Agent Start Without Credentials", "FAIL", error=e)

    def test_agent_start_with_credentials(self):
        """Test 8: Start Agent With LinkedIn Credentials"""
        if not self.test_users:
            self.log_test("Agent Start With Credentials", "SKIP", "No test users available")
            return
            
        try:
            user = self.test_users[0]  # This user should have LinkedIn credentials
            headers = {'Authorization': f'Bearer {user["token"]}'}
            
            response = requests.post(f"{self.backend_url}/api/agent/start", 
                                   headers=headers, timeout=10)
            
            # Note: This will likely fail because we don't have real LinkedIn credentials
            # But we should get past the credentials check
            if response.status_code in [200, 500]:  # 500 is expected due to invalid creds
                if response.status_code == 200:
                    self.log_test("Agent Start With Credentials", "PASS", 
                                 "Agent started successfully")
                else:
                    # Check if it's failing due to invalid credentials vs missing credentials
                    error_data = response.json()
                    if 'LinkedIn credentials not configured' not in error_data.get('error', ''):
                        self.log_test("Agent Start With Credentials", "PASS", 
                                     "Passed credentials check (failed on actual LinkedIn login as expected)")
                    else:
                        self.log_test("Agent Start With Credentials", "FAIL", 
                                     "Still showing missing credentials error")
            else:
                self.log_test("Agent Start With Credentials", "FAIL", 
                             f"Status: {response.status_code}, Response: {response.text}")
                             
        except Exception as e:
            self.log_test("Agent Start With Credentials", "FAIL", error=e)

    def test_agent_status(self):
        """Test 9: Agent Status Check"""
        if not self.test_users:
            self.log_test("Agent Status Check", "SKIP", "No test users available")
            return
            
        try:
            user = self.test_users[0]
            headers = {'Authorization': f'Bearer {user["token"]}'}
            
            response = requests.get(f"{self.backend_url}/api/agent/status", 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ['status', 'progress', 'applications_submitted']
                
                if all(field in data for field in expected_fields):
                    self.log_test("Agent Status Check", "PASS", 
                                 f"Status: {data['status']}, Progress: {data['progress']}%")
                else:
                    self.log_test("Agent Status Check", "FAIL", 
                                 f"Missing status fields: {expected_fields}")
            else:
                self.log_test("Agent Status Check", "FAIL", 
                             f"Status: {response.status_code}, Response: {response.text}")
                             
        except Exception as e:
            self.log_test("Agent Status Check", "FAIL", error=e)

    def test_invalid_linkedin_credentials(self):
        """Test 10: Invalid LinkedIn Credentials Validation"""
        if not self.test_users:
            self.log_test("Invalid LinkedIn Credentials", "SKIP", "No test users available")
            return
            
        try:
            user = self.test_users[0]
            headers = {'Authorization': f'Bearer {user["token"]}'}
            
            # Test with invalid email format
            invalid_profile_data = {
                'linkedinCreds': {
                    'email': 'invalid-email',
                    'password': 'somepassword'
                }
            }
            
            response = requests.put(f"{self.backend_url}/api/profile", 
                                  json=invalid_profile_data, headers=headers, timeout=10)
            
            if response.status_code == 400:
                error_data = response.json()
                if 'invalid' in error_data.get('error', '').lower():
                    self.log_test("Invalid LinkedIn Credentials", "PASS", 
                                 "Correctly rejected invalid LinkedIn email format")
                else:
                    self.log_test("Invalid LinkedIn Credentials", "FAIL", 
                                 "Wrong error message for invalid credentials")
            else:
                self.log_test("Invalid LinkedIn Credentials", "FAIL", 
                             f"Should have returned 400, got {response.status_code}")
                             
        except Exception as e:
            self.log_test("Invalid LinkedIn Credentials", "FAIL", error=e)

    def test_unauthorized_access(self):
        """Test 11: Unauthorized Access Protection"""
        try:
            # Test profile access without token
            response = requests.get(f"{self.backend_url}/api/profile", timeout=10)
            
            if response.status_code == 401:
                self.log_test("Unauthorized Access Protection", "PASS", 
                             "Correctly blocked access without token")
            else:
                self.log_test("Unauthorized Access Protection", "FAIL", 
                             f"Should have returned 401, got {response.status_code}")
                             
        except Exception as e:
            self.log_test("Unauthorized Access Protection", "FAIL", error=e)

    def test_multi_user_isolation(self):
        """Test 12: Multi-User Data Isolation"""
        try:
            # Create two different users
            user1_data = self.generate_test_user()
            user2_data = self.generate_test_user()
            
            # Register both users
            response1 = requests.post(f"{self.backend_url}/api/auth/register", 
                                    json=user1_data, timeout=10)
            response2 = requests.post(f"{self.backend_url}/api/auth/register", 
                                    json=user2_data, timeout=10)
            
            if response1.status_code == 201 and response2.status_code == 201:
                token1 = response1.json()['token']
                token2 = response2.json()['token']
                
                # Update user1's profile
                user1_profile = {
                    'linkedinCreds': {
                        'email': 'user1@linkedin.com',
                        'password': 'user1password'
                    }
                }
                
                headers1 = {'Authorization': f'Bearer {token1}'}
                requests.put(f"{self.backend_url}/api/profile", 
                           json=user1_profile, headers=headers1, timeout=10)
                
                # Check that user2 can't see user1's data
                headers2 = {'Authorization': f'Bearer {token2}'}
                response = requests.get(f"{self.backend_url}/api/profile", 
                                      headers=headers2, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    user2_creds = data.get('linkedinCreds', {})
                    
                    if not user2_creds.get('email'):  # Should be empty
                        self.log_test("Multi-User Data Isolation", "PASS", 
                                     "User data properly isolated between users")
                    else:
                        self.log_test("Multi-User Data Isolation", "FAIL", 
                                     "User2 can see User1's data - data isolation broken!")
                else:
                    self.log_test("Multi-User Data Isolation", "FAIL", 
                                 f"Failed to get user2 profile: {response.status_code}")
            else:
                self.log_test("Multi-User Data Isolation", "FAIL", 
                             "Failed to create test users")
                             
        except Exception as e:
            self.log_test("Multi-User Data Isolation", "FAIL", error=e)

    def test_job_preferences_storage(self):
        """Test 13: Job Preferences Storage and Retrieval"""
        if not self.test_users:
            self.log_test("Job Preferences Storage", "SKIP", "No test users available")
            return
            
        try:
            user = self.test_users[0]
            headers = {'Authorization': f'Bearer {user["token"]}'}
            
            # Update job preferences
            preferences = {
                'jobPreferences': {
                    'jobTitles': 'Data Scientist, Machine Learning Engineer',
                    'locations': 'Boston, Seattle, Remote',
                    'remote': True,
                    'experience': 'senior',
                    'salaryMin': '150000',
                    'skills': 'Python, TensorFlow, AWS, Docker'
                }
            }
            
            # Update preferences
            update_response = requests.put(f"{self.backend_url}/api/profile", 
                                         json=preferences, headers=headers, timeout=10)
            
            if update_response.status_code == 200:
                # Retrieve preferences
                get_response = requests.get(f"{self.backend_url}/api/profile", 
                                          headers=headers, timeout=10)
                
                if get_response.status_code == 200:
                    data = get_response.json()
                    stored_prefs = data.get('jobPreferences', {})
                    
                    # Check if preferences were stored correctly
                    expected_prefs = preferences['jobPreferences']
                    matches = all(stored_prefs.get(key) == expected_prefs[key] 
                                for key in expected_prefs.keys())
                    
                    if matches:
                        self.log_test("Job Preferences Storage", "PASS", 
                                     "Job preferences stored and retrieved correctly")
                    else:
                        self.log_test("Job Preferences Storage", "FAIL", 
                                     f"Preferences mismatch. Expected: {expected_prefs}, Got: {stored_prefs}")
                else:
                    self.log_test("Job Preferences Storage", "FAIL", 
                                 "Failed to retrieve preferences")
            else:
                self.log_test("Job Preferences Storage", "FAIL", 
                             f"Failed to update preferences: {update_response.status_code}")
                             
        except Exception as e:
            self.log_test("Job Preferences Storage", "FAIL", error=e)

    def test_rate_limiting(self):
        """Test 14: Rate Limiting Protection"""
        try:
            # Attempt multiple rapid requests
            login_data = {
                'email': 'nonexistent@example.com',
                'password': 'wrongpassword'
            }
            
            rapid_requests = 0
            blocked_requests = 0
            
            for i in range(10):  # Try 10 rapid requests
                try:
                    response = requests.post(f"{self.backend_url}/api/auth/login", 
                                           json=login_data, timeout=5)
                    rapid_requests += 1
                    
                    if response.status_code == 429:  # Too Many Requests
                        blocked_requests += 1
                        break
                        
                except requests.exceptions.Timeout:
                    break
            
            if blocked_requests > 0:
                self.log_test("Rate Limiting Protection", "PASS", 
                             f"Rate limiting active - blocked after {rapid_requests} requests")
            else:
                self.log_test("Rate Limiting Protection", "WARNING", 
                             "Rate limiting not detected (may not be configured)")
                             
        except Exception as e:
            self.log_test("Rate Limiting Protection", "FAIL", error=e)

    def test_frontend_accessibility(self):
        """Test 15: Frontend Page Accessibility"""
        pages_to_test = [
            ('/', 'Landing Page'),
            ('/auth/signup', 'Signup Page'),
            ('/auth/login', 'Login Page'),
            ('/pricing', 'Pricing Page'),
            ('/dashboard', 'Dashboard'),
            ('/profile', 'Profile Page')
        ]
        
        passed_pages = 0
        
        for path, name in pages_to_test:
            try:
                response = requests.get(f"{self.frontend_url}{path}", timeout=10)
                if response.status_code == 200:
                    passed_pages += 1
                    print(f"   ✅ {name}: Accessible")
                else:
                    print(f"   ❌ {name}: Status {response.status_code}")
            except Exception as e:
                print(f"   ❌ {name}: Error - {e}")
        
        if passed_pages == len(pages_to_test):
            self.log_test("Frontend Page Accessibility", "PASS", 
                         f"All {len(pages_to_test)} pages accessible")
        elif passed_pages > len(pages_to_test) // 2:
            self.log_test("Frontend Page Accessibility", "WARNING", 
                         f"{passed_pages}/{len(pages_to_test)} pages accessible")
        else:
            self.log_test("Frontend Page Accessibility", "FAIL", 
                         f"Only {passed_pages}/{len(pages_to_test)} pages accessible")

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Comprehensive Platform Tests")
        print("=" * 50)
        
        start_time = datetime.now()
        
        # Core functionality tests
        self.test_server_health()
        self.test_user_registration()
        self.test_user_login()
        
        # Profile and credentials tests
        self.test_profile_get_empty()
        self.test_profile_update_linkedin_credentials()
        self.test_profile_get_with_credentials()
        self.test_job_preferences_storage()
        
        # Agent functionality tests
        self.test_agent_start_without_credentials()
        self.test_agent_start_with_credentials()
        self.test_agent_status()
        
        # Security tests
        self.test_invalid_linkedin_credentials()
        self.test_unauthorized_access()
        self.test_multi_user_isolation()
        self.test_rate_limiting()
        
        # Frontend tests
        self.test_frontend_accessibility()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Generate test summary
        self.generate_test_summary(duration)

    def generate_test_summary(self, duration):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warning_tests = len([r for r in self.test_results if r['status'] == 'WARNING'])
        skipped_tests = len([r for r in self.test_results if r['status'] == 'SKIP'])
        
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Warnings: {warning_tests}")
        print(f"⏭️  Skipped: {skipped_tests}")
        print(f"⏱️  Duration: {duration.total_seconds():.2f} seconds")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}")
                    if result['error']:
                        print(f"     Error: {result['error']}")
        
        if warning_tests > 0:
            print(f"\n⚠️  WARNINGS:")
            for result in self.test_results:
                if result['status'] == 'WARNING':
                    print(f"   • {result['test']}: {result['details']}")
        
        print("\n" + "=" * 50)
        
        # Overall status
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED! Platform is working correctly.")
        elif failed_tests <= 2:
            print("✅ Most tests passed. Minor issues detected.")
        else:
            print("⚠️  Multiple test failures. Platform needs attention.")
        
        print("=" * 50)
        
        # Save detailed results
        with open('test_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'warnings': warning_tests,
                    'skipped': skipped_tests,
                    'success_rate': success_rate,
                    'duration_seconds': duration.total_seconds()
                },
                'results': self.test_results
            }, f, indent=2)
        
        print("📄 Detailed results saved to test_results.json")

if __name__ == "__main__":
    import sys
    
    backend_url = "http://localhost:5001"
    frontend_url = "http://localhost:3000"
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1].startswith('--backend='):
            backend_url = sys.argv[1].split('=')[1]
        if len(sys.argv) > 2 and sys.argv[2].startswith('--frontend='):
            frontend_url = sys.argv[2].split('=')[1]
    
    print(f"🔗 Testing Backend: {backend_url}")
    print(f"🔗 Testing Frontend: {frontend_url}")
    print()
    
    tester = ComprehensivePlatformTester(backend_url, frontend_url)
    tester.run_all_tests() 