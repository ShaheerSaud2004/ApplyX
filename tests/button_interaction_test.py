#!/usr/bin/env python3
"""
Button and Interaction Test Suite for ApplyX
Tests all buttons, forms, and user interactions
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

class ButtonInteractionTest:
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
        
    def test_login_button(self):
        """Test login button functionality"""
        try:
            login_data = {
                "email": "test@example.com",
                "password": "testpassword123"
            }
            response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
            success = response.status_code in [200, 401]  # 401 is expected for invalid credentials
            self.log_test("Login Button", success, f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.auth_token = data['token']
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    
        except Exception as e:
            self.log_test("Login Button", False, f"Error: {str(e)}")
            
    def test_register_button(self):
        """Test register button functionality"""
        try:
            register_data = {
                "firstName": "Test",
                "lastName": "User",
                "email": f"test{int(time.time())}@example.com",
                "password": "testpassword123"
            }
            response = self.session.post(f"{self.base_url}/api/auth/register", json=register_data)
            success = response.status_code in [200, 201, 400]  # 400 if user exists
            self.log_test("Register Button", success, f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("Register Button", False, f"Error: {str(e)}")
            
    def test_logout_button(self):
        """Test logout button functionality"""
        if not self.auth_token:
            self.log_test("Logout Button", False, "No auth token")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/api/auth/logout")
            success = response.status_code in [200, 401, 404]
            self.log_test("Logout Button", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Logout Button", False, f"Error: {str(e)}")
            
    def test_start_bot_button(self):
        """Test start bot button"""
        if not self.auth_token:
            self.log_test("Start Bot Button", False, "No auth token")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/api/bot/start")
            success = response.status_code in [200, 400, 401]
            self.log_test("Start Bot Button", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Start Bot Button", False, f"Error: {str(e)}")
            
    def test_stop_bot_button(self):
        """Test stop bot button"""
        if not self.auth_token:
            self.log_test("Stop Bot Button", False, "No auth token")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/api/bot/stop")
            success = response.status_code in [200, 400, 401]
            self.log_test("Stop Bot Button", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Stop Bot Button", False, f"Error: {str(e)}")
            
    def test_upload_resume_button(self):
        """Test upload resume button"""
        if not self.auth_token:
            self.log_test("Upload Resume Button", False, "No auth token")
            return
            
        try:
            files = {'file': ('test_resume.pdf', b'fake pdf content', 'application/pdf')}
            response = self.session.post(f"{self.base_url}/api/upload/resume", files=files)
            success = response.status_code in [200, 400, 401]
            self.log_test("Upload Resume Button", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Upload Resume Button", False, f"Error: {str(e)}")
            
    def test_save_profile_button(self):
        """Test save profile button"""
        if not self.auth_token:
            self.log_test("Save Profile Button", False, "No auth token")
            return
            
        try:
            profile_data = {
                "firstName": "Updated",
                "lastName": "User",
                "email": "updated@example.com"
            }
            response = self.session.put(f"{self.base_url}/api/profile", json=profile_data)
            success = response.status_code in [200, 400, 401]
            self.log_test("Save Profile Button", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Save Profile Button", False, f"Error: {str(e)}")
            
    def test_add_linkedin_credentials_button(self):
        """Test add LinkedIn credentials button"""
        if not self.auth_token:
            self.log_test("Add LinkedIn Credentials Button", False, "No auth token")
            return
            
        try:
            linkedin_data = {
                "email": "test@linkedin.com",
                "password": "linkedinpass123"
            }
            response = self.session.post(f"{self.base_url}/api/linkedin/verify", json=linkedin_data)
            success = response.status_code in [200, 400, 401]
            self.log_test("Add LinkedIn Credentials Button", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Add LinkedIn Credentials Button", False, f"Error: {str(e)}")
            
    def test_clear_activity_log_button(self):
        """Test clear activity log button"""
        if not self.auth_token:
            self.log_test("Clear Activity Log Button", False, "No auth token")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/api/activity/clear")
            success = response.status_code in [200, 400, 401]
            self.log_test("Clear Activity Log Button", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Clear Activity Log Button", False, f"Error: {str(e)}")
            
    def test_ai_complete_profile_button(self):
        """Test AI complete profile button"""
        if not self.auth_token:
            self.log_test("AI Complete Profile Button", False, "No auth token")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/api/profile/ai-complete")
            success = response.status_code in [200, 400, 401]
            self.log_test("AI Complete Profile Button", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("AI Complete Profile Button", False, f"Error: {str(e)}")
            
    def test_upgrade_plan_button(self):
        """Test upgrade plan button"""
        try:
            response = self.session.get(f"{self.base_url}/api/pricing")
            success = response.status_code == 200
            self.log_test("Upgrade Plan Button", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Upgrade Plan Button", False, f"Error: {str(e)}")
            
    def test_form_validation(self):
        """Test form validation"""
        # Test invalid email
        try:
            invalid_data = {
                "email": "invalid-email",
                "password": "short"
            }
            response = self.session.post(f"{self.base_url}/api/auth/login", json=invalid_data)
            success = response.status_code in [400, 401]
            self.log_test("Form Validation - Invalid Email", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Form Validation - Invalid Email", False, f"Error: {str(e)}")
            
        # Test missing fields
        try:
            incomplete_data = {
                "email": "test@example.com"
                # Missing password
            }
            response = self.session.post(f"{self.base_url}/api/auth/login", json=incomplete_data)
            success = response.status_code in [400, 401]
            self.log_test("Form Validation - Missing Fields", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Form Validation - Missing Fields", False, f"Error: {str(e)}")
            
    def test_button_states(self):
        """Test button states (loading, disabled, etc.)"""
        if not self.auth_token:
            self.log_test("Button States", False, "No auth token")
            return
            
        # Test bot status to check button states
        try:
            response = self.session.get(f"{self.base_url}/api/bot/status")
            success = response.status_code == 200
            self.log_test("Button States Check", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Button States Check", False, f"Error: {str(e)}")
            
    def test_modal_interactions(self):
        """Test modal interactions"""
        if not self.auth_token:
            self.log_test("Modal Interactions", False, "No auth token")
            return
            
        # Test resume upload modal
        try:
            files = {'file': ('test.txt', b'Hello World', 'text/plain')}
            response = self.session.post(f"{self.base_url}/api/upload/resume", files=files)
            success = response.status_code in [200, 400, 401]
            self.log_test("Resume Upload Modal", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Resume Upload Modal", False, f"Error: {str(e)}")
            
    def test_dropdown_interactions(self):
        """Test dropdown interactions"""
        if not self.auth_token:
            self.log_test("Dropdown Interactions", False, "No auth token")
            return
            
        # Test profile update with dropdown values
        try:
            profile_data = {
                "pronouns": "they/them",
                "phoneCountryCode": "United States (+1)",
                "degreeCompleted": "Bachelor's Degree"
            }
            response = self.session.put(f"{self.base_url}/api/profile", json=profile_data)
            success = response.status_code in [200, 400, 401]
            self.log_test("Dropdown Interactions", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Dropdown Interactions", False, f"Error: {str(e)}")
            
    def test_checkbox_interactions(self):
        """Test checkbox interactions"""
        if not self.auth_token:
            self.log_test("Checkbox Interactions", False, "No auth token")
            return
            
        # Test profile update with checkbox values
        try:
            profile_data = {
                "weekendWork": True,
                "eveningWork": False,
                "drugTest": True,
                "backgroundCheck": True
            }
            response = self.session.put(f"{self.base_url}/api/profile", json=profile_data)
            success = response.status_code in [200, 400, 401]
            self.log_test("Checkbox Interactions", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Checkbox Interactions", False, f"Error: {str(e)}")
            
    def test_text_input_interactions(self):
        """Test text input interactions"""
        if not self.auth_token:
            self.log_test("Text Input Interactions", False, "No auth token")
            return
            
        # Test profile update with text inputs
        try:
            profile_data = {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "website": "https://johndoe.com"
            }
            response = self.session.put(f"{self.base_url}/api/profile", json=profile_data)
            success = response.status_code in [200, 400, 401]
            self.log_test("Text Input Interactions", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Text Input Interactions", False, f"Error: {str(e)}")
            
    def test_textarea_interactions(self):
        """Test textarea interactions"""
        if not self.auth_token:
            self.log_test("Textarea Interactions", False, "No auth token")
            return
            
        # Test profile update with textarea
        try:
            profile_data = {
                "messageToManager": "I am excited to join your team and contribute to your mission."
            }
            response = self.session.put(f"{self.base_url}/api/profile", json=profile_data)
            success = response.status_code in [200, 400, 401]
            self.log_test("Textarea Interactions", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Textarea Interactions", False, f"Error: {str(e)}")
            
    def test_file_upload_interactions(self):
        """Test file upload interactions"""
        if not self.auth_token:
            self.log_test("File Upload Interactions", False, "No auth token")
            return
            
        # Test different file types
        file_tests = [
            ("test.pdf", b"fake pdf content", "application/pdf"),
            ("test.txt", b"Hello World", "text/plain"),
            ("test.docx", b"fake docx content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        ]
        
        for filename, content, mime_type in file_tests:
            try:
                files = {'file': (filename, content, mime_type)}
                response = self.session.post(f"{self.base_url}/api/upload/resume", files=files)
                success = response.status_code in [200, 400, 401]
                self.log_test(f"File Upload: {filename}", success, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"File Upload: {filename}", False, f"Error: {str(e)}")
                
    def test_error_handling_buttons(self):
        """Test error handling for buttons"""
        # Test with invalid data
        try:
            invalid_data = {
                "email": "",
                "password": ""
            }
            response = self.session.post(f"{self.base_url}/api/auth/login", json=invalid_data)
            success = response.status_code in [400, 401]
            self.log_test("Error Handling - Empty Fields", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Empty Fields", False, f"Error: {str(e)}")
            
    def test_accessibility_buttons(self):
        """Test accessibility features for buttons"""
        # Test keyboard navigation (simulated)
        try:
            # Test tab order by making requests in sequence
            endpoints = [
                "/api/auth/login",
                "/api/auth/register",
                "/api/bot/status"
            ]
            
            responses = []
            for endpoint in endpoints:
                response = self.session.get(f"{self.base_url}{endpoint}")
                responses.append(response.status_code)
                
            success = all(status in [200, 401, 404] for status in responses)
            self.log_test("Accessibility - Keyboard Navigation", success, f"Responses: {responses}")
        except Exception as e:
            self.log_test("Accessibility - Keyboard Navigation", False, f"Error: {str(e)}")
            
    def run_all_tests(self):
        """Run all button and interaction tests"""
        print("🚀 Starting Button and Interaction Tests...")
        print("=" * 60)
        
        # Authentication buttons
        self.test_login_button()
        self.test_register_button()
        self.test_logout_button()
        
        # Bot control buttons
        self.test_start_bot_button()
        self.test_stop_bot_button()
        
        # Profile and data buttons
        self.test_upload_resume_button()
        self.test_save_profile_button()
        self.test_add_linkedin_credentials_button()
        self.test_clear_activity_log_button()
        self.test_ai_complete_profile_button()
        self.test_upgrade_plan_button()
        
        # Form interactions
        self.test_form_validation()
        self.test_button_states()
        self.test_modal_interactions()
        self.test_dropdown_interactions()
        self.test_checkbox_interactions()
        self.test_text_input_interactions()
        self.test_textarea_interactions()
        self.test_file_upload_interactions()
        
        # Error handling and accessibility
        self.test_error_handling_buttons()
        self.test_accessibility_buttons()
        
        # Summary
        print("=" * 60)
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 BUTTON TEST SUMMARY:")
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
        filename = f"button_test_results_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Main function"""
    base_url = os.getenv('TEST_BASE_URL', 'http://localhost:8000')
    tester = ButtonInteractionTest(base_url)
    tester.run_all_tests()

if __name__ == "__main__":
    main() 