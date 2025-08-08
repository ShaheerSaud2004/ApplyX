#!/usr/bin/env python3
"""
MASTER TEST SUITE FOR APPLYX PLATFORM - PRODUCTION READY
=========================================================

This master suite combines all test modules and provides comprehensive
testing for production readiness including 100+ tests covering:

- Backend API functionality (50+ tests)
- Frontend components (15+ tests) 
- Bot functionality (15+ tests)
- Security & penetration testing (10+ tests)
- Performance & load testing (10+ tests)
- Database integrity (5+ tests)
- Integration & E2E workflows (10+ tests)

Total: 115+ comprehensive tests for production readiness
"""

import os
import sys
import json
import time
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path

# Import test suites
try:
    from test_production_ready import ProductionReadyTester
    from test_frontend_components import FrontendTestSuite
    from test_bot_functionality import BotFunctionalityTestSuite
except ImportError as e:
    print(f"⚠️  Import warning: {e}")
    print("Some test modules may not be available. Continuing with available tests...")

class MasterTestSuite:
    """Master test suite orchestrator"""
    
    def __init__(self, backend_url="http://localhost:5001", frontend_url="http://localhost:3000"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.all_results = []
        self.start_time = None
        self.backend_process = None
        self.frontend_process = None
        
    def log_suite_result(self, suite_name, results):
        """Log results from a test suite"""
        suite_result = {
            'suite': suite_name,
            'results': results,
            'timestamp': datetime.now().isoformat(),
            'passed': len([r for r in results if r.get('status') == 'PASS']),
            'failed': len([r for r in results if r.get('status') == 'FAIL']),
            'warnings': len([r for r in results if r.get('status') == 'WARN']),
            'total': len(results)
        }
        self.all_results.append(suite_result)
        
        print(f"\n📊 {suite_name} Summary:")
        print(f"   ✅ Passed: {suite_result['passed']}")
        print(f"   ❌ Failed: {suite_result['failed']}")
        print(f"   ⚠️  Warnings: {suite_result['warnings']}")
        print(f"   📈 Total: {suite_result['total']}")

    def check_prerequisites(self):
        """Check system prerequisites before running tests"""
        print("🔍 CHECKING SYSTEM PREREQUISITES")
        print("-" * 50)
        
        prerequisites = {
            'Python': self._check_python(),
            'Node.js': self._check_nodejs(),
            'Backend Server': self._check_backend(),
            'Frontend Server': self._check_frontend(),
            'Database': self._check_database(),
            'ChromeDriver': self._check_chromedriver()
        }
        
        all_good = True
        for prereq, status in prerequisites.items():
            status_emoji = "✅" if status else "❌"
            print(f"{status_emoji} {prereq}: {'Available' if status else 'Missing/Failed'}")
            if not status:
                all_good = False
        
        print()
        if all_good:
            print("✅ All prerequisites met!")
        else:
            print("⚠️  Some prerequisites missing - tests may fail")
        
        return all_good

    def _check_python(self):
        """Check Python availability"""
        try:
            version = sys.version_info
            return version.major >= 3 and version.minor >= 9
        except:
            return False

    def _check_nodejs(self):
        """Check Node.js availability"""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def _check_backend(self):
        """Check if backend server is running"""
        try:
            import requests
            response = requests.get(f"{self.backend_url}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _check_frontend(self):
        """Check if frontend server is running"""
        try:
            import requests
            response = requests.get(self.frontend_url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def _check_database(self):
        """Check database availability"""
        try:
            db_path = 'backend/easyapply.db'
            return os.path.exists(db_path)
        except:
            return False

    def _check_chromedriver(self):
        """Check ChromeDriver availability"""
        try:
            chromedriver_paths = ['./chromedriver', 'chromedriver', 'chromedriver.exe']
            return any(os.path.exists(path) for path in chromedriver_paths)
        except:
            return False

    def start_servers(self):
        """Start backend and frontend servers if not running"""
        print("🚀 STARTING SERVERS")
        print("-" * 30)
        
        # Check if servers are already running
        backend_running = self._check_backend()
        frontend_running = self._check_frontend()
        
        if backend_running:
            print("✅ Backend server already running")
        else:
            print("🔄 Starting backend server...")
            try:
                self.backend_process = subprocess.Popen(
                    ['python3', 'backend/app.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                time.sleep(5)  # Give server time to start
                if self._check_backend():
                    print("✅ Backend server started successfully")
                else:
                    print("❌ Backend server failed to start")
            except Exception as e:
                print(f"❌ Failed to start backend: {e}")
        
        if frontend_running:
            print("✅ Frontend server already running")
        else:
            print("🔄 Starting frontend server...")
            try:
                self.frontend_process = subprocess.Popen(
                    ['npm', 'run', 'dev'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                time.sleep(10)  # Give frontend time to start
                if self._check_frontend():
                    print("✅ Frontend server started successfully")
                else:
                    print("❌ Frontend server failed to start")
            except Exception as e:
                print(f"❌ Failed to start frontend: {e}")
        
        print()

    def stop_servers(self):
        """Stop servers if we started them"""
        if self.backend_process:
            print("🛑 Stopping backend server...")
            self.backend_process.terminate()
        
        if self.frontend_process:
            print("🛑 Stopping frontend server...")
            self.frontend_process.terminate()

    def run_backend_tests(self):
        """Run comprehensive backend tests"""
        print("\n" + "=" * 80)
        print("🔧 RUNNING BACKEND API TESTS")
        print("=" * 80)
        
        try:
            backend_tester = ProductionReadyTester(self.backend_url, self.frontend_url)
            backend_tester.run_comprehensive_tests()
            self.log_suite_result("Backend API Tests", backend_tester.test_results)
        except Exception as e:
            print(f"❌ Backend tests failed: {e}")
            self.log_suite_result("Backend API Tests", [
                {'test': 'Backend Test Suite', 'status': 'FAIL', 'error': str(e)}
            ])

    def run_frontend_tests(self):
        """Run frontend component tests"""
        print("\n" + "=" * 80)
        print("🌐 RUNNING FRONTEND COMPONENT TESTS")
        print("=" * 80)
        
        try:
            frontend_tester = FrontendTestSuite()
            results = frontend_tester.run_frontend_tests()
            self.log_suite_result("Frontend Component Tests", results)
        except Exception as e:
            print(f"❌ Frontend tests failed: {e}")
            self.log_suite_result("Frontend Component Tests", [
                {'test': 'Frontend Test Suite', 'status': 'FAIL', 'error': str(e)}
            ])

    def run_bot_tests(self):
        """Run bot functionality tests"""
        print("\n" + "=" * 80)
        print("🤖 RUNNING BOT FUNCTIONALITY TESTS")
        print("=" * 80)
        
        try:
            bot_tester = BotFunctionalityTestSuite(self.backend_url)
            results = bot_tester.run_bot_tests()
            self.log_suite_result("Bot Functionality Tests", results)
        except Exception as e:
            print(f"❌ Bot tests failed: {e}")
            self.log_suite_result("Bot Functionality Tests", [
                {'test': 'Bot Test Suite', 'status': 'FAIL', 'error': str(e)}
            ])

    def run_integration_tests(self):
        """Run additional integration tests"""
        print("\n" + "=" * 80)
        print("🔗 RUNNING INTEGRATION TESTS")
        print("=" * 80)
        
        integration_results = []
        
        # Test 076: Full user registration to agent setup workflow
        try:
            import requests
            session = requests.Session()
            
            # Register user
            user_data = {
                'email': f'integration_test_{int(time.time())}@test.com',
                'password': 'IntegrationTest123!',
                'first_name': 'Integration',
                'last_name': 'Test'
            }
            
            register_response = session.post(f"{self.backend_url}/api/auth/register", json=user_data)
            
            if register_response.status_code == 201:
                token = register_response.json()['token']
                headers = {'Authorization': f'Bearer {token}'}
                
                # Update profile with LinkedIn credentials
                profile_data = {
                    'linkedinCreds': {
                        'email': 'test@linkedin.com',
                        'password': 'testpass123'
                    }
                }
                
                profile_response = session.put(f"{self.backend_url}/api/profile", 
                                             json=profile_data, headers=headers)
                
                if profile_response.status_code == 200:
                    # Try to start agent
                    agent_response = session.post(f"{self.backend_url}/api/agent/start",
                                                json={'max_applications': 1}, headers=headers)
                    
                    integration_results.append({
                        'test': '076_Full_Integration_Workflow',
                        'status': 'PASS' if agent_response.status_code in [200, 400] else 'FAIL',
                        'details': 'Complete user workflow tested'
                    })
                else:
                    integration_results.append({
                        'test': '076_Full_Integration_Workflow',
                        'status': 'FAIL',
                        'details': 'Profile update failed'
                    })
            else:
                integration_results.append({
                    'test': '076_Full_Integration_Workflow',
                    'status': 'FAIL',
                    'details': 'User registration failed'
                })
                
        except Exception as e:
            integration_results.append({
                'test': '076_Full_Integration_Workflow',
                'status': 'FAIL',
                'error': str(e)
            })
        
        # Test 077: Database consistency
        try:
            import sqlite3
            db_path = 'backend/easyapply.db'
            
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check foreign key constraints
                cursor.execute('PRAGMA foreign_key_check')
                fk_violations = cursor.fetchall()
                
                # Check table integrity
                cursor.execute('PRAGMA integrity_check')
                integrity_result = cursor.fetchone()
                
                conn.close()
                
                if not fk_violations and integrity_result[0] == 'ok':
                    integration_results.append({
                        'test': '077_Database_Consistency',
                        'status': 'PASS',
                        'details': 'Database integrity verified'
                    })
                else:
                    integration_results.append({
                        'test': '077_Database_Consistency',
                        'status': 'FAIL',
                        'details': f'Integrity issues: {fk_violations}'
                    })
            else:
                integration_results.append({
                    'test': '077_Database_Consistency',
                    'status': 'FAIL',
                    'details': 'Database file not found'
                })
                
        except Exception as e:
            integration_results.append({
                'test': '077_Database_Consistency',
                'status': 'FAIL',
                'error': str(e)
            })
        
        # Test 078: Configuration validation
        try:
            config_files = ['config.yaml', 'package.json', '.env.example']
            config_status = []
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    config_status.append(f"{config_file}: ✓")
                else:
                    config_status.append(f"{config_file}: ✗")
            
            missing_configs = [s for s in config_status if '✗' in s]
            
            integration_results.append({
                'test': '078_Configuration_Validation',
                'status': 'PASS' if not missing_configs else 'WARN',
                'details': '; '.join(config_status)
            })
            
        except Exception as e:
            integration_results.append({
                'test': '078_Configuration_Validation',
                'status': 'FAIL',
                'error': str(e)
            })
        
        self.log_suite_result("Integration Tests", integration_results)

    def generate_final_report(self):
        """Generate comprehensive final report"""
        print("\n" + "=" * 100)
        print("🎉 MASTER TEST SUITE - FINAL COMPREHENSIVE REPORT")
        print("=" * 100)
        
        # Calculate overall statistics
        total_tests = sum(suite['total'] for suite in self.all_results)
        total_passed = sum(suite['passed'] for suite in self.all_results)
        total_failed = sum(suite['failed'] for suite in self.all_results)
        total_warnings = sum(suite['warnings'] for suite in self.all_results)
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        duration = datetime.now() - self.start_time if self.start_time else timedelta(0)
        
        print(f"📊 **OVERALL TEST STATISTICS**")
        print(f"   🎯 Total Tests Run: {total_tests}")
        print(f"   ✅ Tests Passed: {total_passed}")
        print(f"   ❌ Tests Failed: {total_failed}")
        print(f"   ⚠️  Warnings: {total_warnings}")
        print(f"   📈 Success Rate: {overall_success_rate:.1f}%")
        print(f"   ⏱️  Total Duration: {duration}")
        print()
        
        # Suite breakdown
        print(f"📋 **TEST SUITE BREAKDOWN**")
        for suite in self.all_results:
            suite_success_rate = (suite['passed'] / suite['total'] * 100) if suite['total'] > 0 else 0
            print(f"   {suite['suite']}:")
            print(f"      ✅ {suite['passed']}/{suite['total']} passed ({suite_success_rate:.1f}%)")
            if suite['failed'] > 0:
                print(f"      ❌ {suite['failed']} failed")
            if suite['warnings'] > 0:
                print(f"      ⚠️  {suite['warnings']} warnings")
        print()
        
        # Production readiness assessment
        print(f"🏭 **PRODUCTION READINESS ASSESSMENT**")
        
        critical_failures = 0
        for suite in self.all_results:
            for result in suite.get('results', []):
                if (result.get('status') == 'FAIL' and 
                    any(keyword in result.get('test', '').lower() for keyword in 
                        ['security', 'auth', 'sql', 'xss', 'csrf', 'database'])):
                    critical_failures += 1
        
        if overall_success_rate >= 95 and critical_failures == 0:
            readiness_status = "✅ READY FOR PRODUCTION"
            readiness_detail = "Platform passes comprehensive testing with excellent success rate"
        elif overall_success_rate >= 85 and critical_failures == 0:
            readiness_status = "⚠️  MOSTLY READY FOR PRODUCTION"
            readiness_detail = "Platform is mostly ready but consider addressing warnings"
        elif overall_success_rate >= 70 and critical_failures <= 2:
            readiness_status = "🔄 NEEDS IMPROVEMENT BEFORE PRODUCTION"
            readiness_detail = "Several issues need to be resolved before deployment"
        else:
            readiness_status = "❌ NOT READY FOR PRODUCTION"
            readiness_detail = "Critical issues must be resolved before deployment"
        
        print(f"   Status: {readiness_status}")
        print(f"   Details: {readiness_detail}")
        if critical_failures > 0:
            print(f"   🚨 Critical Security Issues: {critical_failures}")
        print()
        
        # Top recommendations
        print(f"💡 **TOP RECOMMENDATIONS**")
        recommendations = self._generate_recommendations()
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        print()
        
        # Save detailed report
        self._save_master_report(total_tests, overall_success_rate, duration)
        
        print("=" * 100)
        print(f"🎯 TESTING COMPLETE - {total_tests} tests run with {overall_success_rate:.1f}% success rate")
        print("=" * 100)

    def _generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Analyze failures across all suites
        all_failures = []
        for suite in self.all_results:
            for result in suite.get('results', []):
                if result.get('status') == 'FAIL':
                    all_failures.append(result.get('test', '').lower())
        
        # Generate specific recommendations
        if any('auth' in failure for failure in all_failures):
            recommendations.append("Fix authentication issues - critical for security")
        
        if any('database' in failure for failure in all_failures):
            recommendations.append("Resolve database connectivity and integrity issues")
        
        if any('frontend' in failure for failure in all_failures):
            recommendations.append("Address frontend compilation and component issues")
        
        if any('bot' in failure for failure in all_failures):
            recommendations.append("Fix bot configuration and functionality issues")
        
        if len(all_failures) > 10:
            recommendations.append("High number of failures - conduct thorough review")
        
        # Performance recommendations
        performance_issues = any('performance' in failure or 'timeout' in failure 
                               for failure in all_failures)
        if performance_issues:
            recommendations.append("Optimize API response times and performance")
        
        # Security recommendations
        security_issues = any(keyword in failure for failure in all_failures 
                            for keyword in ['security', 'xss', 'csrf', 'injection'])
        if security_issues:
            recommendations.append("Address security vulnerabilities before production")
        
        if not recommendations:
            recommendations = [
                "Platform looks excellent! Consider setting up monitoring and logging",
                "Implement automated testing in CI/CD pipeline",
                "Set up production environment configuration",
                "Plan for scalability and performance monitoring"
            ]
        
        return recommendations[:5]  # Top 5 recommendations

    def _save_master_report(self, total_tests, success_rate, duration):
        """Save master test report to file"""
        try:
            report_data = {
                'master_summary': {
                    'timestamp': datetime.now().isoformat(),
                    'total_tests': total_tests,
                    'success_rate': success_rate,
                    'duration': str(duration),
                    'backend_url': self.backend_url,
                    'frontend_url': self.frontend_url
                },
                'suite_results': self.all_results
            }
            
            report_filename = f"master_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_filename, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            print(f"📄 Master test report saved to: {report_filename}")
            
        except Exception as e:
            print(f"⚠️  Could not save master report: {e}")

    def run_all_tests(self):
        """Run all test suites comprehensively"""
        self.start_time = datetime.now()
        
        print("🚀 APPLYX PLATFORM - MASTER TEST SUITE")
        print("=" * 100)
        print("Running comprehensive production-ready tests...")
        print(f"Started at: {self.start_time}")
        print("=" * 100)
        
        # Check prerequisites
        prereqs_ok = self.check_prerequisites()
        
        if not prereqs_ok:
            print("⚠️  Some prerequisites missing, but continuing with available tests...")
        
        # Start servers if needed
        self.start_servers()
        
        try:
            # Run all test suites
            self.run_backend_tests()
            self.run_frontend_tests()
            self.run_bot_tests()
            self.run_integration_tests()
            
            # Generate final report
            self.generate_final_report()
            
        finally:
            # Clean up
            self.stop_servers()


def main():
    """Main function to run master test suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ApplyX Platform Master Test Suite')
    parser.add_argument('--backend-url', default='http://localhost:5001',
                       help='Backend server URL')
    parser.add_argument('--frontend-url', default='http://localhost:3000',
                       help='Frontend server URL')
    parser.add_argument('--start-servers', action='store_true',
                       help='Automatically start backend and frontend servers')
    
    args = parser.parse_args()
    
    # Initialize master test suite
    master_suite = MasterTestSuite(args.backend_url, args.frontend_url)
    
    # Run all tests
    master_suite.run_all_tests()


if __name__ == "__main__":
    main() 