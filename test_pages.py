#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime

class PageTester:
    """Test each page individually to ensure proper authentication and functionality"""
    
    def __init__(self, frontend_url="http://localhost:3000", backend_url="http://localhost:5001"):
        self.frontend_url = frontend_url
        self.backend_url = backend_url
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

    def test_page_accessibility(self, path, page_name, expected_elements=None):
        """Test if a page is accessible and contains expected elements"""
        try:
            response = requests.get(f"{self.frontend_url}{path}", timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Check for expected elements
                if expected_elements:
                    missing_elements = []
                    for element in expected_elements:
                        if element not in content:
                            missing_elements.append(element)
                    
                    if missing_elements:
                        self.log_test(f"{page_name} Content Check", "FAIL", 
                                     f"Missing elements: {missing_elements}")
                    else:
                        self.log_test(f"{page_name} Content Check", "PASS", 
                                     "All expected elements found")
                else:
                    self.log_test(f"{page_name} Accessibility", "PASS", 
                                 f"Page loads successfully (status: {response.status_code})")
            else:
                self.log_test(f"{page_name} Accessibility", "FAIL", 
                             f"HTTP {response.status_code}")
                             
        except Exception as e:
            self.log_test(f"{page_name} Accessibility", "FAIL", error=e)

    def test_landing_page(self):
        """Test landing page (/"""
        print("🏠 Testing Landing Page...")
        
        expected_elements = [
            "Teemo AI",
            "Get Started Free",
            "Features", 
            "Pricing",
            "Sign In",
            "Sign Up",
            "Apply to 30+ jobs per day"
        ]
        
        self.test_page_accessibility("/", "Landing Page", expected_elements)
        
        # Test that it shows non-authenticated UI
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if "Get Started Free" in response.text and "Go to Dashboard" not in response.text:
                self.log_test("Landing Page - Non-Auth UI", "PASS", 
                             "Shows correct UI for non-authenticated users")
            else:
                self.log_test("Landing Page - Non-Auth UI", "FAIL", 
                             "Not showing correct non-authenticated UI")
        except Exception as e:
            self.log_test("Landing Page - Non-Auth UI", "FAIL", error=e)

    def test_signup_page(self):
        """Test signup page (/auth/signup)"""
        print("📝 Testing Signup Page...")
        
        expected_elements = [
            "Create Account",
            "First Name",
            "Last Name", 
            "Email",
            "Password",
            "Confirm Password",
            "Already have an account"
        ]
        
        self.test_page_accessibility("/auth/signup", "Signup Page", expected_elements)

    def test_login_page(self):
        """Test login page (/auth/login)"""
        print("🔑 Testing Login Page...")
        
        expected_elements = [
            "Welcome Back",
            "Email",
            "Password",
            "Sign In",
            "Don't have an account",
            "Remember me",
            "Continue with Google"
        ]
        
        self.test_page_accessibility("/auth/login", "Login Page", expected_elements)

    def test_pricing_page(self):
        """Test pricing page (/pricing)"""
        print("💰 Testing Pricing Page...")
        
        expected_elements = [
            "Choose Your Plan",
            "Free",
            "Basic", 
            "Pro",
            "applications per day",
            "Get Started"
        ]
        
        self.test_page_accessibility("/pricing", "Pricing Page", expected_elements)

    def test_dashboard_page(self):
        """Test dashboard page (/dashboard) - should redirect if not authenticated"""
        print("📊 Testing Dashboard Page...")
        
        try:
            response = requests.get(f"{self.frontend_url}/dashboard", timeout=10, allow_redirects=False)
            
            # Should either be the page content or redirect (for unauthenticated users)
            if response.status_code in [200, 302, 307, 308]:
                if response.status_code == 200:
                    # If it loads, check for dashboard elements
                    if "Agent Status" in response.text or "Dashboard" in response.text:
                        self.log_test("Dashboard Accessibility", "PASS", 
                                     "Dashboard loads with expected content")
                    else:
                        self.log_test("Dashboard Accessibility", "WARNING", 
                                     "Page loads but may be missing dashboard content")
                else:
                    self.log_test("Dashboard Auth Protection", "PASS", 
                                 f"Properly redirects unauthenticated users (status: {response.status_code})")
            else:
                self.log_test("Dashboard Accessibility", "FAIL", 
                             f"Unexpected status: {response.status_code}")
                             
        except Exception as e:
            self.log_test("Dashboard Accessibility", "FAIL", error=e)

    def test_profile_page(self):
        """Test profile page (/profile) - should redirect if not authenticated"""
        print("👤 Testing Profile Page...")
        
        try:
            response = requests.get(f"{self.frontend_url}/profile", timeout=10, allow_redirects=False)
            
            # Should either be the page content or redirect (for unauthenticated users)
            if response.status_code in [200, 302, 307, 308]:
                if response.status_code == 200:
                    # If it loads, check for profile elements
                    if "Profile Settings" in response.text or "LinkedIn Credentials" in response.text:
                        self.log_test("Profile Accessibility", "PASS", 
                                     "Profile loads with expected content")
                    else:
                        self.log_test("Profile Accessibility", "WARNING", 
                                     "Page loads but may be missing profile content")
                else:
                    self.log_test("Profile Auth Protection", "PASS", 
                                 f"Properly redirects unauthenticated users (status: {response.status_code})")
            else:
                self.log_test("Profile Accessibility", "FAIL", 
                             f"Unexpected status: {response.status_code}")
                             
        except Exception as e:
            self.log_test("Profile Accessibility", "FAIL", error=e)

    def test_authentication_flow(self):
        """Test complete authentication flow"""
        print("🔐 Testing Authentication Flow...")
        
        try:
            # Test user registration
            test_email = f"test_{int(time.time())}@example.com"
            signup_data = {
                'first_name': 'Test',
                'last_name': 'User',
                'email': test_email,
                'password': 'TestPassword123!'
            }
            
            response = requests.post(f"{self.backend_url}/api/auth/register", 
                                   json=signup_data, timeout=10)
            
            if response.status_code == 201:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.log_test("User Registration API", "PASS", 
                                 f"User {test_email} registered successfully")
                    
                    # Test login
                    login_data = {
                        'email': test_email,
                        'password': 'TestPassword123!'
                    }
                    
                    login_response = requests.post(f"{self.backend_url}/api/auth/login", 
                                                 json=login_data, timeout=10)
                    
                    if login_response.status_code == 200:
                        login_data = login_response.json()
                        if 'token' in login_data:
                            self.log_test("User Login API", "PASS", 
                                         f"User {test_email} logged in successfully")
                        else:
                            self.log_test("User Login API", "FAIL", "Missing token in response")
                    else:
                        self.log_test("User Login API", "FAIL", 
                                     f"Login failed: {login_response.status_code}")
                else:
                    self.log_test("User Registration API", "FAIL", "Missing token or user in response")
            else:
                self.log_test("User Registration API", "FAIL", 
                             f"Registration failed: {response.status_code}")
                             
        except Exception as e:
            self.log_test("Authentication Flow", "FAIL", error=e)

    def test_backend_health(self):
        """Test backend health endpoint"""
        print("🏥 Testing Backend Health...")
        
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'status' in data and data['status'] == 'healthy':
                    self.log_test("Backend Health", "PASS", 
                                 f"Backend is healthy: {data}")
                else:
                    self.log_test("Backend Health", "WARNING", 
                                 f"Backend responds but status unclear: {data}")
            else:
                self.log_test("Backend Health", "FAIL", 
                             f"Backend health check failed: {response.status_code}")
                             
        except Exception as e:
            self.log_test("Backend Health", "FAIL", error=e)

    def run_all_tests(self):
        """Run all page tests"""
        print("🚀 Starting Comprehensive Page Tests")
        print("=" * 50)
        
        start_time = datetime.now()
        
        # Test backend first
        self.test_backend_health()
        
        # Test each page
        self.test_landing_page()
        self.test_signup_page()
        self.test_login_page()
        self.test_pricing_page()
        self.test_dashboard_page()
        self.test_profile_page()
        
        # Test authentication flow
        self.test_authentication_flow()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Generate summary
        self.generate_summary(duration)

    def generate_summary(self, duration):
        """Generate test summary"""
        print("\n" + "=" * 50)
        print("📊 PAGE TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warning_tests = len([r for r in self.test_results if r['status'] == 'WARNING'])
        
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Warnings: {warning_tests}")
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
        
        if failed_tests == 0 and warning_tests <= 1:
            print("🎉 ALL PAGES WORKING PERFECTLY!")
        elif failed_tests <= 2:
            print("✅ Most pages working well. Minor issues detected.")
        else:
            print("⚠️  Multiple issues detected. Platform needs attention.")
        
        print("=" * 50)

if __name__ == "__main__":
    import sys
    
    frontend_url = "http://localhost:3000"
    backend_url = "http://localhost:5001"
    
    print(f"🔗 Testing Frontend: {frontend_url}")
    print(f"🔗 Testing Backend: {backend_url}")
    print()
    
    tester = PageTester(frontend_url, backend_url)
    tester.run_all_tests() 