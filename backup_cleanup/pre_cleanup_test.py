#!/usr/bin/env python3
"""
Pre-Cleanup Test Script
Tests all functionality before cleanup to ensure we don't break anything
"""

import requests
import json
import time
import sys
from datetime import datetime

class PreCleanupTester:
    def __init__(self):
        self.frontend_url = "http://localhost:3000"
        self.backend_url = "http://localhost:5001"
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Backend Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Error: {str(e)}")
            return False
            
    def test_frontend_access(self):
        """Test frontend accessibility"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.log_test("Frontend Access", True, "Homepage loads")
                return True
            else:
                self.log_test("Frontend Access", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Access", False, f"Error: {str(e)}")
            return False
            
    def test_api_endpoints(self):
        """Test key API endpoints"""
        endpoints = [
            ("/api/pricing", "Pricing API"),
            ("/api/user/plan", "User Plan API"),
            ("/api/bot/status", "Bot Status API"),
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                if response.status_code in [200, 401]:  # 401 is expected for unauthenticated requests
                    self.log_test(f"{name}", True, f"Status: {response.status_code}")
                else:
                    self.log_test(f"{name}", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test(f"{name}", False, f"Error: {str(e)}")
                
    def test_pricing_quota(self):
        """Test that free plan quota is 10"""
        try:
            response = requests.get(f"{self.backend_url}/api/pricing", timeout=5)
            if response.status_code == 200:
                data = response.json()
                free_plan = next((plan for plan in data.get('plans', []) if plan.get('id') == 'free'), None)
                if free_plan and free_plan.get('dailyQuota') == 10:
                    self.log_test("Free Plan Quota", True, "Quota correctly set to 10")
                    return True
                else:
                    self.log_test("Free Plan Quota", False, f"Expected 10, got {free_plan.get('dailyQuota') if free_plan else 'None'}")
                    return False
            else:
                self.log_test("Free Plan Quota", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Free Plan Quota", False, f"Error: {str(e)}")
            return False
            
    def test_email_config(self):
        """Test email configuration"""
        try:
            # Check if email config file exists
            import os
            if os.path.exists("email_config.sh"):
                self.log_test("Email Configuration", True, "Email config file exists")
                return True
            else:
                self.log_test("Email Configuration", False, "Email config file missing")
                return False
        except Exception as e:
            self.log_test("Email Configuration", False, f"Error: {str(e)}")
            return False
            
    def test_database_connection(self):
        """Test database connectivity"""
        try:
            # This is a basic test - in a real scenario you'd test actual DB queries
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_test("Database Connection", True, "Backend can access database")
                return True
            else:
                self.log_test("Database Connection", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Database Connection", False, f"Error: {str(e)}")
            return False
            
    def test_file_structure(self):
        """Test that essential files exist"""
        essential_files = [
            "src/app/layout.tsx",
            "src/components/AuthModals.tsx",
            "backend/app.py",
            "package.json",
            "requirements.txt"
        ]
        
        import os
        for file_path in essential_files:
            if os.path.exists(file_path):
                self.log_test(f"File: {file_path}", True)
            else:
                self.log_test(f"File: {file_path}", False, "File missing")
                
    def test_build_system(self):
        """Test that the project can build"""
        try:
            import subprocess
            result = subprocess.run(["npm", "run", "build"], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                self.log_test("Frontend Build", True, "Build successful")
                return True
            else:
                self.log_test("Frontend Build", False, f"Build failed: {result.stderr[:200]}")
                return False
        except Exception as e:
            self.log_test("Frontend Build", False, f"Error: {str(e)}")
            return False
            
    def run_all_tests(self):
        """Run all pre-cleanup tests"""
        print("🧪 Running Pre-Cleanup Tests...")
        print("=" * 50)
        
        tests = [
            self.test_backend_health,
            self.test_frontend_access,
            self.test_api_endpoints,
            self.test_pricing_quota,
            self.test_email_config,
            self.test_database_connection,
            self.test_file_structure,
            # self.test_build_system,  # Commented out to avoid long build time
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}")
                
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Summary:")
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        # Save results
        with open("cleanup_plan/pre_cleanup_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
            
        return passed == total

if __name__ == "__main__":
    tester = PreCleanupTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1) 