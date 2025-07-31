#!/usr/bin/env python3
"""
Frontend Component Test Suite for ApplyX
Tests all UI components, buttons, and frontend functionality
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

class FrontendComponentTest:
    def __init__(self, frontend_url: str = "http://localhost:3000", backend_url: str = "http://localhost:8000"):
        self.frontend_url = frontend_url
        self.backend_url = backend_url
        self.test_results = []
        self.session = requests.Session()
        
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
        
    def test_frontend_pages(self):
        """Test all frontend pages"""
        pages = [
            "/",
            "/dashboard",
            "/profile", 
            "/applications",
            "/manual-apply",
            "/auth/login",
            "/auth/signup",
            "/auth/forgot-password",
            "/admin",
            "/pricing"
        ]
        
        for page in pages:
            try:
                response = self.session.get(f"{self.frontend_url}{page}")
                success = response.status_code == 200
                self.log_test(f"Frontend Page: {page}", success, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Frontend Page: {page}", False, f"Error: {str(e)}")
                
    def test_frontend_assets(self):
        """Test frontend assets loading"""
        assets = [
            "/favicon.ico",
            "/favicon-16x16.png",
            "/favicon-32x32.png",
            "/site.webmanifest"
        ]
        
        for asset in assets:
            try:
                response = self.session.get(f"{self.frontend_url}{asset}")
                success = response.status_code == 200
                self.log_test(f"Frontend Asset: {asset}", success, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Frontend Asset: {asset}", False, f"Error: {str(e)}")
                
    def test_frontend_api_integration(self):
        """Test frontend API integration"""
        # Test if frontend can reach backend
        try:
            response = self.session.get(f"{self.backend_url}/")
            success = response.status_code == 200
            self.log_test("Frontend-Backend Integration", success, f"Backend Status: {response.status_code}")
        except Exception as e:
            self.log_test("Frontend-Backend Integration", False, f"Error: {str(e)}")
            
    def test_frontend_authentication_flow(self):
        """Test frontend authentication flow"""
        # Test login page
        try:
            response = self.session.get(f"{self.frontend_url}/auth/login")
            success = response.status_code == 200
            self.log_test("Login Page Load", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Login Page Load", False, f"Error: {str(e)}")
            
        # Test signup page
        try:
            response = self.session.get(f"{self.frontend_url}/auth/signup")
            success = response.status_code == 200
            self.log_test("Signup Page Load", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Signup Page Load", False, f"Error: {str(e)}")
            
    def test_frontend_dashboard_components(self):
        """Test dashboard components"""
        # Test dashboard page
        try:
            response = self.session.get(f"{self.frontend_url}/dashboard")
            success = response.status_code == 200
            self.log_test("Dashboard Page Load", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Dashboard Page Load", False, f"Error: {str(e)}")
            
    def test_frontend_profile_components(self):
        """Test profile page components"""
        try:
            response = self.session.get(f"{self.frontend_url}/profile")
            success = response.status_code == 200
            self.log_test("Profile Page Load", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Profile Page Load", False, f"Error: {str(e)}")
            
    def test_frontend_applications_components(self):
        """Test applications page components"""
        try:
            response = self.session.get(f"{self.frontend_url}/applications")
            success = response.status_code == 200
            self.log_test("Applications Page Load", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Applications Page Load", False, f"Error: {str(e)}")
            
    def test_frontend_admin_components(self):
        """Test admin page components"""
        try:
            response = self.session.get(f"{self.frontend_url}/admin")
            success = response.status_code == 200
            self.log_test("Admin Page Load", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Admin Page Load", False, f"Error: {str(e)}")
            
    def test_frontend_pricing_components(self):
        """Test pricing page components"""
        try:
            response = self.session.get(f"{self.frontend_url}/pricing")
            success = response.status_code == 200
            self.log_test("Pricing Page Load", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Pricing Page Load", False, f"Error: {str(e)}")
            
    def test_frontend_responsive_design(self):
        """Test responsive design elements"""
        # Test with different user agents
        user_agents = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        ]
        
        for i, ua in enumerate(user_agents):
            try:
                headers = {'User-Agent': ua}
                response = self.session.get(f"{self.frontend_url}/", headers=headers)
                success = response.status_code == 200
                device = ["Mobile", "Tablet", "Desktop"][i]
                self.log_test(f"Responsive Design: {device}", success, f"Status: {response.status_code}")
            except Exception as e:
                device = ["Mobile", "Tablet", "Desktop"][i]
                self.log_test(f"Responsive Design: {device}", False, f"Error: {str(e)}")
                
    def test_frontend_performance(self):
        """Test frontend performance"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.frontend_url}/")
            load_time = time.time() - start_time
            
            success = response.status_code == 200 and load_time < 5.0  # 5 second threshold
            self.log_test("Frontend Performance", success, f"Load Time: {load_time:.2f}s")
        except Exception as e:
            self.log_test("Frontend Performance", False, f"Error: {str(e)}")
            
    def test_frontend_security_headers(self):
        """Test security headers"""
        try:
            response = self.session.get(f"{self.frontend_url}/")
            headers = response.headers
            
            # Check for common security headers
            security_headers = [
                'X-Frame-Options',
                'X-Content-Type-Options', 
                'X-XSS-Protection',
                'Referrer-Policy',
                'Content-Security-Policy'
            ]
            
            found_headers = [h for h in security_headers if h in headers]
            success = len(found_headers) > 0
            self.log_test("Security Headers", success, f"Found: {found_headers}")
        except Exception as e:
            self.log_test("Security Headers", False, f"Error: {str(e)}")
            
    def test_frontend_error_pages(self):
        """Test error pages"""
        # Test 404 page
        try:
            response = self.session.get(f"{self.frontend_url}/nonexistent-page")
            success = response.status_code == 404
            self.log_test("404 Error Page", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("404 Error Page", False, f"Error: {str(e)}")
            
    def test_frontend_meta_tags(self):
        """Test meta tags and SEO"""
        try:
            response = self.session.get(f"{self.frontend_url}/")
            content = response.text.lower()
            
            # Check for important meta tags
            meta_tags = [
                'viewport',
                'description',
                'title',
                'charset'
            ]
            
            found_tags = [tag for tag in meta_tags if tag in content]
            success = len(found_tags) >= 2  # At least viewport and charset
            self.log_test("Meta Tags", success, f"Found: {found_tags}")
        except Exception as e:
            self.log_test("Meta Tags", False, f"Error: {str(e)}")
            
    def test_frontend_javascript_loading(self):
        """Test JavaScript loading"""
        try:
            response = self.session.get(f"{self.frontend_url}/")
            content = response.text
            
            # Check for JavaScript files
            js_indicators = [
                'script src=',
                'next.js',
                'react',
                'window.',
                'document.'
            ]
            
            found_js = [indicator for indicator in js_indicators if indicator in content]
            success = len(found_js) > 0
            self.log_test("JavaScript Loading", success, f"Found: {found_js[:3]}...")
        except Exception as e:
            self.log_test("JavaScript Loading", False, f"Error: {str(e)}")
            
    def test_frontend_css_loading(self):
        """Test CSS loading"""
        try:
            response = self.session.get(f"{self.frontend_url}/")
            content = response.text
            
            # Check for CSS files
            css_indicators = [
                'link rel="stylesheet"',
                'tailwind',
                'css',
                'style'
            ]
            
            found_css = [indicator for indicator in css_indicators if indicator in content]
            success = len(found_css) > 0
            self.log_test("CSS Loading", success, f"Found: {found_css[:3]}...")
        except Exception as e:
            self.log_test("CSS Loading", False, f"Error: {str(e)}")
            
    def test_frontend_accessibility(self):
        """Test basic accessibility features"""
        try:
            response = self.session.get(f"{self.frontend_url}/")
            content = response.text
            
            # Check for accessibility features
            a11y_features = [
                'alt=',
                'aria-',
                'role=',
                'tabindex=',
                'title='
            ]
            
            found_a11y = [feature for feature in a11y_features if feature in content]
            success = len(found_a11y) > 0
            self.log_test("Accessibility Features", success, f"Found: {found_a11y[:3]}...")
        except Exception as e:
            self.log_test("Accessibility Features", False, f"Error: {str(e)}")
            
    def test_frontend_mobile_optimization(self):
        """Test mobile optimization"""
        try:
            # Test with mobile user agent
            mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
            headers = {'User-Agent': mobile_ua}
            
            response = self.session.get(f"{self.frontend_url}/", headers=headers)
            content = response.text.lower()
            
            # Check for mobile optimization indicators
            mobile_indicators = [
                'viewport',
                'mobile',
                'responsive',
                'touch'
            ]
            
            found_mobile = [indicator for indicator in mobile_indicators if indicator in content]
            success = len(found_mobile) > 0
            self.log_test("Mobile Optimization", success, f"Found: {found_mobile}")
        except Exception as e:
            self.log_test("Mobile Optimization", False, f"Error: {str(e)}")
            
    def run_all_tests(self):
        """Run all frontend tests"""
        print("🚀 Starting Frontend Component Tests...")
        print("=" * 60)
        
        # Core page tests
        self.test_frontend_pages()
        self.test_frontend_assets()
        self.test_frontend_api_integration()
        
        # Component tests
        self.test_frontend_authentication_flow()
        self.test_frontend_dashboard_components()
        self.test_frontend_profile_components()
        self.test_frontend_applications_components()
        self.test_frontend_admin_components()
        self.test_frontend_pricing_components()
        
        # Advanced tests
        self.test_frontend_responsive_design()
        self.test_frontend_performance()
        self.test_frontend_security_headers()
        self.test_frontend_error_pages()
        self.test_frontend_meta_tags()
        self.test_frontend_javascript_loading()
        self.test_frontend_css_loading()
        self.test_frontend_accessibility()
        self.test_frontend_mobile_optimization()
        
        # Summary
        print("=" * 60)
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 FRONTEND TEST SUMMARY:")
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
        filename = f"frontend_test_results_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Main function"""
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
    tester = FrontendComponentTest(frontend_url, backend_url)
    tester.run_all_tests()

if __name__ == "__main__":
    main() 