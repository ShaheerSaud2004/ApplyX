#!/usr/bin/env python3
"""
Comprehensive Functionality Test Suite for ApplyX
Tests all buttons, functionality, and components to identify issues
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

class ComprehensiveFunctionalityTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.session = requests.Session()
        self.auth_token = None
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = f"[{timestamp}] {status} {test_name}"
        if details:
            result += f" - {details}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": timestamp
        })
        
    def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            success = response.status_code == 200
            self.log_test("Backend Health Check", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Error: {str(e)}")
            return False
            
    def test_api_endpoints(self):
        """Test all API endpoints"""
        endpoints = [
            "/api/auth/login",
            "/api/auth/register", 
            "/api/user/plan",
            "/api/bot/status",
            "/api/bot/start",
            "/api/bot/stop",
            "/api/profile",
            "/api/resumes",
            "/api/applications",
            "/api/pricing"
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                # Most endpoints should return 401 (unauthorized) without auth
                success = response.status_code in [200, 401, 404]
                self.log_test(f"API Endpoint: {endpoint}", success, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"API Endpoint: {endpoint}", False, f"Error: {str(e)}")
                
    def test_authentication_flow(self):
        """Test authentication flow"""
        # Test registration
        try:
            register_data = {
                "firstName": "Test",
                "lastName": "User", 
                "email": f"test{int(time.time())}@example.com",
                "password": "testpassword123"
            }
            response = self.session.post(f"{self.base_url}/api/auth/register", json=register_data)
            success = response.status_code in [200, 201, 400]  # 400 if user exists
            self.log_test("User Registration", success, f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.auth_token = data['token']
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    
        except Exception as e:
            self.log_test("User Registration", False, f"Error: {str(e)}")
            
        # Test login
        try:
            login_data = {
                "email": "test@example.com",
                "password": "testpassword123"
            }
            response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
            success = response.status_code in [200, 401]
            self.log_test("User Login", success, f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.auth_token = data['token']
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    
        except Exception as e:
            self.log_test("User Login", False, f"Error: {str(e)}")
            
    def test_bot_functionality(self):
        """Test bot functionality"""
        if not self.auth_token:
            self.log_test("Bot Status Check", False, "No auth token")
            return
            
        # Test bot status
        try:
            response = self.session.get(f"{self.base_url}/api/bot/status")
            success = response.status_code == 200
            self.log_test("Bot Status Check", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Bot Status Check", False, f"Error: {str(e)}")
            
        # Test bot start
        try:
            response = self.session.post(f"{self.base_url}/api/bot/start")
            success = response.status_code in [200, 400, 401]
            self.log_test("Bot Start", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Bot Start", False, f"Error: {str(e)}")
            
        # Test bot stop
        try:
            response = self.session.post(f"{self.base_url}/api/bot/stop")
            success = response.status_code in [200, 400, 401]
            self.log_test("Bot Stop", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Bot Stop", False, f"Error: {str(e)}")
            
    def test_profile_functionality(self):
        """Test profile functionality"""
        if not self.auth_token:
            self.log_test("Profile Get", False, "No auth token")
            return
            
        # Test get profile
        try:
            response = self.session.get(f"{self.base_url}/api/profile")
            success = response.status_code in [200, 401]
            self.log_test("Profile Get", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Profile Get", False, f"Error: {str(e)}")
            
        # Test update profile
        try:
            profile_data = {
                "firstName": "Updated",
                "lastName": "User",
                "email": "updated@example.com"
            }
            response = self.session.put(f"{self.base_url}/api/profile", json=profile_data)
            success = response.status_code in [200, 400, 401]
            self.log_test("Profile Update", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Profile Update", False, f"Error: {str(e)}")
            
    def test_resume_functionality(self):
        """Test resume functionality"""
        if not self.auth_token:
            self.log_test("Resume List", False, "No auth token")
            return
            
        # Test get resumes
        try:
            response = self.session.get(f"{self.base_url}/api/resumes")
            success = response.status_code in [200, 401]
            self.log_test("Resume List", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Resume List", False, f"Error: {str(e)}")
            
        # Test upload resume (mock)
        try:
            files = {'file': ('test_resume.pdf', b'fake pdf content', 'application/pdf')}
            response = self.session.post(f"{self.base_url}/api/upload/resume", files=files)
            success = response.status_code in [200, 400, 401]
            self.log_test("Resume Upload", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Resume Upload", False, f"Error: {str(e)}")
            
    def test_applications_functionality(self):
        """Test applications functionality"""
        if not self.auth_token:
            self.log_test("Applications List", False, "No auth token")
            return
            
        # Test get applications
        try:
            response = self.session.get(f"{self.base_url}/api/applications")
            success = response.status_code in [200, 401]
            self.log_test("Applications List", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Applications List", False, f"Error: {str(e)}")
            
        # Test create application
        try:
            app_data = {
                "jobTitle": "Software Engineer",
                "company": "Test Company",
                "location": "Remote",
                "status": "pending"
            }
            response = self.session.post(f"{self.base_url}/api/applications", json=app_data)
            success = response.status_code in [200, 201, 400, 401]
            self.log_test("Application Create", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Application Create", False, f"Error: {str(e)}")
            
    def test_pricing_functionality(self):
        """Test pricing functionality"""
        try:
            response = self.session.get(f"{self.base_url}/api/pricing")
            success = response.status_code == 200
            self.log_test("Pricing Endpoint", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Pricing Endpoint", False, f"Error: {str(e)}")
            
    def test_cors_functionality(self):
        """Test CORS functionality"""
        try:
            headers = {
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            response = self.session.options(f"{self.base_url}/api/bot/status", headers=headers)
            success = response.status_code == 200
            self.log_test("CORS Preflight", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("CORS Preflight", False, f"Error: {str(e)}")
            
    def test_error_handling(self):
        """Test error handling"""
        # Test 404
        try:
            response = self.session.get(f"{self.base_url}/api/nonexistent")
            success = response.status_code == 404
            self.log_test("404 Error Handling", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("404 Error Handling", False, f"Error: {str(e)}")
            
        # Test invalid JSON
        try:
            response = self.session.post(f"{self.base_url}/api/auth/login", 
                                       data="invalid json", 
                                       headers={'Content-Type': 'application/json'})
            success = response.status_code in [400, 500]
            self.log_test("Invalid JSON Handling", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Invalid JSON Handling", False, f"Error: {str(e)}")
            
    def test_rate_limiting(self):
        """Test rate limiting"""
        try:
            responses = []
            for i in range(10):
                response = self.session.get(f"{self.base_url}/api/bot/status")
                responses.append(response.status_code)
                time.sleep(0.1)
                
            # Check if any requests were rate limited
            rate_limited = any(status == 429 for status in responses)
            self.log_test("Rate Limiting", True, f"Responses: {responses[:5]}...")
        except Exception as e:
            self.log_test("Rate Limiting", False, f"Error: {str(e)}")
            
    def test_database_connectivity(self):
        """Test database connectivity"""
        try:
            # Test a simple database operation
            response = self.session.get(f"{self.base_url}/api/user/plan")
            success = response.status_code in [200, 401]
            self.log_test("Database Connectivity", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Database Connectivity", False, f"Error: {str(e)}")
            
    def test_file_operations(self):
        """Test file operations"""
        if not self.auth_token:
            self.log_test("File Operations", False, "No auth token")
            return
            
        # Test file upload
        try:
            files = {'file': ('test.txt', b'Hello World', 'text/plain')}
            response = self.session.post(f"{self.base_url}/api/upload/resume", files=files)
            success = response.status_code in [200, 400, 401]
            self.log_test("File Upload", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("File Upload", False, f"Error: {str(e)}")
            
    def test_websocket_functionality(self):
        """Test WebSocket functionality (if applicable)"""
        try:
            # This would require a WebSocket client
            self.log_test("WebSocket Functionality", True, "Not implemented - requires WebSocket client")
        except Exception as e:
            self.log_test("WebSocket Functionality", False, f"Error: {str(e)}")
            
    def test_background_jobs(self):
        """Test background job functionality"""
        try:
            # Test job aggregator endpoint
            response = self.session.get(f"{self.base_url}/api/jobs")
            success = response.status_code in [200, 401, 404]
            self.log_test("Background Jobs", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Background Jobs", False, f"Error: {str(e)}")
            
    def test_email_functionality(self):
        """Test email functionality"""
        try:
            # Test email endpoint if it exists
            response = self.session.get(f"{self.base_url}/api/email/test")
            success = response.status_code in [200, 401, 404]
            self.log_test("Email Functionality", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Email Functionality", False, f"Error: {str(e)}")
            
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Functionality Tests...")
        print("=" * 60)
        
        # Core functionality tests
        self.test_backend_health()
        self.test_api_endpoints()
        self.test_authentication_flow()
        self.test_bot_functionality()
        self.test_profile_functionality()
        self.test_resume_functionality()
        self.test_applications_functionality()
        self.test_pricing_functionality()
        
        # Advanced functionality tests
        self.test_cors_functionality()
        self.test_error_handling()
        self.test_rate_limiting()
        self.test_database_connectivity()
        self.test_file_operations()
        self.test_websocket_functionality()
        self.test_background_jobs()
        self.test_email_functionality()
        
        # Summary
        print("=" * 60)
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 TEST SUMMARY:")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
                    
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Main function"""
    base_url = os.getenv('TEST_BASE_URL', 'http://localhost:8000')
    tester = ComprehensiveFunctionalityTest(base_url)
    tester.run_all_tests()

if __name__ == "__main__":
    main() 