#!/usr/bin/env python3
"""
FRONTEND COMPONENT TEST SUITE FOR APPLYX PLATFORM
==================================================

This suite tests frontend components and user interface functionality
including authentication modals, dashboard components, and user flows.
"""

import subprocess
import json
import os
import time
from datetime import datetime

class FrontendTestSuite:
    """Comprehensive frontend testing suite"""
    
    def __init__(self):
        self.test_results = []
        self.frontend_running = False
        
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

    def test_051_react_component_compilation(self):
        """Test React component compilation"""
        try:
            # Check if Next.js can compile without errors
            result = subprocess.run(['npm', 'run', 'build'], 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.log_test("051_React_Component_Compilation", "PASS", 
                            "React components compile successfully")
            else:
                self.log_test("051_React_Component_Compilation", "FAIL", 
                            f"Compilation errors: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.log_test("051_React_Component_Compilation", "FAIL", 
                        "Build timeout")
        except Exception as e:
            self.log_test("051_React_Component_Compilation", "FAIL", error=e)

    def test_052_typescript_validation(self):
        """Test TypeScript type checking"""
        try:
            result = subprocess.run(['npx', 'tsc', '--noEmit'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_test("052_TypeScript_Validation", "PASS", 
                            "TypeScript validation passed")
            else:
                self.log_test("052_TypeScript_Validation", "FAIL", 
                            f"TypeScript errors: {result.stderr}")
        except Exception as e:
            self.log_test("052_TypeScript_Validation", "FAIL", error=e)

    def test_053_eslint_code_quality(self):
        """Test ESLint code quality"""
        try:
            result = subprocess.run(['npx', 'eslint', 'src/', '--format', 'json'], 
                                  capture_output=True, text=True)
            
            if result.stdout:
                eslint_results = json.loads(result.stdout)
                total_errors = sum(len(file['messages']) for file in eslint_results 
                                 if file['messages'])
                
                if total_errors == 0:
                    self.log_test("053_ESLint_Code_Quality", "PASS", 
                                "No ESLint errors found")
                else:
                    self.log_test("053_ESLint_Code_Quality", "WARN", 
                                f"{total_errors} ESLint issues found")
            else:
                self.log_test("053_ESLint_Code_Quality", "PASS", 
                            "ESLint completed")
        except Exception as e:
            self.log_test("053_ESLint_Code_Quality", "FAIL", error=e)

    def test_054_dependency_vulnerabilities(self):
        """Test for dependency vulnerabilities"""
        try:
            result = subprocess.run(['npm', 'audit', '--json'], 
                                  capture_output=True, text=True)
            
            if result.stdout:
                audit_data = json.loads(result.stdout)
                vulnerabilities = audit_data.get('metadata', {}).get('vulnerabilities', {})
                
                critical = vulnerabilities.get('critical', 0)
                high = vulnerabilities.get('high', 0)
                
                if critical == 0 and high == 0:
                    self.log_test("054_Dependency_Vulnerabilities", "PASS", 
                                "No critical/high vulnerabilities")
                else:
                    self.log_test("054_Dependency_Vulnerabilities", "WARN", 
                                f"Vulnerabilities: {critical} critical, {high} high")
        except Exception as e:
            self.log_test("054_Dependency_Vulnerabilities", "FAIL", error=e)

    def test_055_component_imports(self):
        """Test critical component imports"""
        try:
            components_to_check = [
                'src/components/AuthModals.tsx',
                'src/components/LoginModal.tsx',
                'src/components/SignupModal.tsx',
                'src/app/page.tsx',
                'src/app/dashboard/page.tsx'
            ]
            
            missing_components = []
            for component in components_to_check:
                if not os.path.exists(component):
                    missing_components.append(component)
            
            if not missing_components:
                self.log_test("055_Component_Imports", "PASS", 
                            "All critical components found")
            else:
                self.log_test("055_Component_Imports", "FAIL", 
                            f"Missing components: {missing_components}")
        except Exception as e:
            self.log_test("055_Component_Imports", "FAIL", error=e)

    def test_056_package_json_integrity(self):
        """Test package.json integrity"""
        try:
            with open('package.json', 'r') as f:
                package_data = json.load(f)
            
            required_scripts = ['dev', 'build', 'start']
            required_deps = ['next', 'react', 'react-dom']
            
            missing_scripts = [script for script in required_scripts 
                             if script not in package_data.get('scripts', {})]
            missing_deps = [dep for dep in required_deps 
                          if dep not in package_data.get('dependencies', {})]
            
            if not missing_scripts and not missing_deps:
                self.log_test("056_Package_JSON_Integrity", "PASS", 
                            "Package.json is properly configured")
            else:
                issues = []
                if missing_scripts:
                    issues.append(f"Missing scripts: {missing_scripts}")
                if missing_deps:
                    issues.append(f"Missing dependencies: {missing_deps}")
                self.log_test("056_Package_JSON_Integrity", "FAIL", 
                            "; ".join(issues))
        except Exception as e:
            self.log_test("056_Package_JSON_Integrity", "FAIL", error=e)

    def test_057_environment_config(self):
        """Test frontend environment configuration"""
        try:
            env_files = ['.env.local', '.env', '.env.example']
            found_env = False
            
            for env_file in env_files:
                if os.path.exists(env_file):
                    found_env = True
                    with open(env_file, 'r') as f:
                        env_content = f.read()
                    
                    required_vars = ['NEXT_PUBLIC_API_URL']
                    missing_vars = [var for var in required_vars if var not in env_content]
                    
                    if not missing_vars:
                        self.log_test("057_Environment_Config", "PASS", 
                                    f"Environment config found in {env_file}")
                        return
                    
            if not found_env:
                self.log_test("057_Environment_Config", "WARN", 
                            "No environment config file found")
        except Exception as e:
            self.log_test("057_Environment_Config", "FAIL", error=e)

    def test_058_tailwind_config(self):
        """Test Tailwind CSS configuration"""
        try:
            tailwind_files = ['tailwind.config.js', 'tailwind.config.ts']
            found_config = False
            
            for config_file in tailwind_files:
                if os.path.exists(config_file):
                    found_config = True
                    self.log_test("058_Tailwind_Config", "PASS", 
                                f"Tailwind config found: {config_file}")
                    break
            
            if not found_config:
                self.log_test("058_Tailwind_Config", "FAIL", 
                            "Tailwind config not found")
        except Exception as e:
            self.log_test("058_Tailwind_Config", "FAIL", error=e)

    def test_059_next_config(self):
        """Test Next.js configuration"""
        try:
            next_config_files = ['next.config.js', 'next.config.ts', 'next.config.mjs']
            
            for config_file in next_config_files:
                if os.path.exists(config_file):
                    self.log_test("059_Next_Config", "PASS", 
                                f"Next.js config found: {config_file}")
                    return
            
            # Next.js can work without explicit config
            self.log_test("059_Next_Config", "PASS", 
                        "Using default Next.js configuration")
        except Exception as e:
            self.log_test("059_Next_Config", "FAIL", error=e)

    def test_060_static_assets(self):
        """Test static assets availability"""
        try:
            asset_paths = [
                'public/',
                'src/app/favicon.ico',
                'src/app/globals.css'
            ]
            
            missing_assets = []
            for asset_path in asset_paths:
                if not os.path.exists(asset_path):
                    missing_assets.append(asset_path)
            
            if not missing_assets:
                self.log_test("060_Static_Assets", "PASS", "All static assets found")
            else:
                self.log_test("060_Static_Assets", "WARN", 
                            f"Missing assets: {missing_assets}")
        except Exception as e:
            self.log_test("060_Static_Assets", "FAIL", error=e)

    def run_frontend_tests(self):
        """Run all frontend tests"""
        print("\n🌐 FRONTEND COMPONENT TESTS")
        print("-" * 50)
        
        self.test_051_react_component_compilation()
        self.test_052_typescript_validation()
        self.test_053_eslint_code_quality()
        self.test_054_dependency_vulnerabilities()
        self.test_055_component_imports()
        self.test_056_package_json_integrity()
        self.test_057_environment_config()
        self.test_058_tailwind_config()
        self.test_059_next_config()
        self.test_060_static_assets()
        
        # Summary
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.test_results if r['status'] == 'WARN'])
        
        print(f"\n📊 Frontend Test Results:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   ⚠️  Warnings: {warnings}")
        
        return self.test_results


if __name__ == "__main__":
    suite = FrontendTestSuite()
    suite.run_frontend_tests() 