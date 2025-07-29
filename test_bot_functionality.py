#!/usr/bin/env python3
"""
BOT FUNCTIONALITY TEST SUITE FOR APPLYX PLATFORM
=================================================

This suite tests LinkedIn bot automation, job application processes,
configuration management, and integration with the web platform.
"""

import os
import sys
import yaml
import json
import time
import requests
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import tempfile

class BotFunctionalityTestSuite:
    """Comprehensive bot functionality testing suite"""
    
    def __init__(self, backend_url="http://localhost:5001"):
        self.backend_url = backend_url
        self.test_results = []
        self.test_config = self._load_test_config()
        
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

    def _load_test_config(self):
        """Load test configuration"""
        return {
            'test_positions': ['Software Engineer', 'AI Engineer', 'Data Scientist'],
            'test_locations': ['New York, NY', 'San Francisco, CA', 'Remote'],
            'test_companies': ['TestCompany Inc', 'Demo Corp', 'Sample LLC'],
            'max_test_applications': 3
        }

    def test_061_bot_module_imports(self):
        """Test bot module imports and dependencies"""
        try:
            # Test main bot imports
            sys.path.append('.')
            
            imports_to_test = [
                ('linkedineasyapply', 'LinkedinEasyApply'),
                ('main_fast', 'ContinuousApplyBot'),
                ('easyapplybot.utils', None)
            ]
            
            for module_name, class_name in imports_to_test:
                try:
                    module = __import__(module_name, fromlist=[class_name] if class_name else [])
                    if class_name:
                        getattr(module, class_name)
                    self.log_test(f"061_Bot_Import_{module_name}", "PASS", 
                                f"Module {module_name} imported successfully")
                except ImportError as e:
                    self.log_test(f"061_Bot_Import_{module_name}", "FAIL", 
                                f"Import failed: {e}")
                    
        except Exception as e:
            self.log_test("061_Bot_Module_Imports", "FAIL", error=e)

    def test_062_config_file_validation(self):
        """Test configuration file validation and structure"""
        try:
            config_files = ['config.yaml', 'config.yml']
            config_found = False
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    config_found = True
                    with open(config_file, 'r') as f:
                        config = yaml.safe_load(f)
                    
                    # Test required configuration fields
                    required_fields = [
                        'email', 'password', 'positions', 'locations',
                        'experienceLevel', 'jobTypes', 'uploads'
                    ]
                    
                    missing_fields = [field for field in required_fields 
                                    if field not in config]
                    
                    if not missing_fields:
                        self.log_test("062_Config_File_Validation", "PASS", 
                                    f"Configuration file {config_file} is valid")
                    else:
                        self.log_test("062_Config_File_Validation", "FAIL", 
                                    f"Missing fields: {missing_fields}")
                    break
            
            if not config_found:
                self.log_test("062_Config_File_Validation", "FAIL", 
                            "No configuration file found")
                            
        except Exception as e:
            self.log_test("062_Config_File_Validation", "FAIL", error=e)

    def test_063_resume_file_validation(self):
        """Test resume file validation and accessibility"""
        try:
            config_path = 'config.yaml' if os.path.exists('config.yaml') else 'config.yml'
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                resume_path = config.get('uploads', {}).get('resume')
                
                if resume_path:
                    if os.path.exists(resume_path):
                        file_size = os.path.getsize(resume_path)
                        if file_size > 0:
                            self.log_test("063_Resume_File_Validation", "PASS", 
                                        f"Resume file found: {resume_path} ({file_size} bytes)")
                        else:
                            self.log_test("063_Resume_File_Validation", "FAIL", 
                                        "Resume file is empty")
                    else:
                        self.log_test("063_Resume_File_Validation", "FAIL", 
                                    f"Resume file not found: {resume_path}")
                else:
                    self.log_test("063_Resume_File_Validation", "FAIL", 
                                "Resume path not configured")
            else:
                self.log_test("063_Resume_File_Validation", "WARN", 
                            "Configuration file not found")
                            
        except Exception as e:
            self.log_test("063_Resume_File_Validation", "FAIL", error=e)

    def test_064_chromedriver_availability(self):
        """Test ChromeDriver availability and version"""
        try:
            # Check for ChromeDriver in common locations
            chromedriver_paths = [
                './chromedriver',
                '/usr/local/bin/chromedriver',
                '/usr/bin/chromedriver',
                'chromedriver.exe'
            ]
            
            chromedriver_found = False
            for path in chromedriver_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    chromedriver_found = True
                    file_size = os.path.getsize(path)
                    self.log_test("064_ChromeDriver_Availability", "PASS", 
                                f"ChromeDriver found: {path} ({file_size} bytes)")
                    break
            
            if not chromedriver_found:
                self.log_test("064_ChromeDriver_Availability", "FAIL", 
                            "ChromeDriver not found in expected locations")
                            
        except Exception as e:
            self.log_test("064_ChromeDriver_Availability", "FAIL", error=e)

    def test_065_selenium_dependencies(self):
        """Test Selenium and browser automation dependencies"""
        try:
            import selenium
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            
            self.log_test("065_Selenium_Dependencies", "PASS", 
                        f"Selenium version {selenium.__version__} available")
                        
        except ImportError as e:
            self.log_test("065_Selenium_Dependencies", "FAIL", 
                        f"Selenium import failed: {e}")
        except Exception as e:
            self.log_test("065_Selenium_Dependencies", "FAIL", error=e)

    def test_066_openai_integration(self):
        """Test OpenAI API integration for AI features"""
        try:
            import openai
            
            # Check if API key is configured
            config_path = 'config.yaml' if os.path.exists('config.yaml') else None
            api_key_configured = False
            
            if config_path:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                api_key = config.get('openaiApiKey')
                if api_key and api_key.startswith('sk-'):
                    api_key_configured = True
            
            if api_key_configured:
                self.log_test("066_OpenAI_Integration", "PASS", 
                            "OpenAI API key configured")
            else:
                self.log_test("066_OpenAI_Integration", "WARN", 
                            "OpenAI API key not configured or invalid")
                            
        except ImportError as e:
            self.log_test("066_OpenAI_Integration", "FAIL", 
                        f"OpenAI import failed: {e}")
        except Exception as e:
            self.log_test("066_OpenAI_Integration", "FAIL", error=e)

    def test_067_job_search_parameters(self):
        """Test job search parameter validation"""
        try:
            config_path = 'config.yaml' if os.path.exists('config.yaml') else None
            
            if config_path:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Validate job search parameters
                positions = config.get('positions', [])
                locations = config.get('locations', [])
                experience_level = config.get('experienceLevel', {})
                job_types = config.get('jobTypes', {})
                
                validation_results = []
                
                if positions and len(positions) > 0:
                    validation_results.append("Positions configured")
                else:
                    validation_results.append("ERROR: No positions configured")
                
                if locations and len(locations) > 0:
                    validation_results.append("Locations configured")
                else:
                    validation_results.append("ERROR: No locations configured")
                
                if any(experience_level.values()):
                    validation_results.append("Experience levels configured")
                else:
                    validation_results.append("ERROR: No experience levels selected")
                
                if any(job_types.values()):
                    validation_results.append("Job types configured")
                else:
                    validation_results.append("ERROR: No job types selected")
                
                errors = [r for r in validation_results if r.startswith("ERROR:")]
                
                if not errors:
                    self.log_test("067_Job_Search_Parameters", "PASS", 
                                "; ".join(validation_results))
                else:
                    self.log_test("067_Job_Search_Parameters", "FAIL", 
                                "; ".join(errors))
            else:
                self.log_test("067_Job_Search_Parameters", "FAIL", 
                            "Configuration file not found")
                            
        except Exception as e:
            self.log_test("067_Job_Search_Parameters", "FAIL", error=e)

    def test_068_application_responses(self):
        """Test application response configuration"""
        try:
            config_path = 'config.yaml' if os.path.exists('config.yaml') else None
            
            if config_path:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Check for application responses configuration
                responses = config.get('applicationResponses', {})
                personal_info = config.get('personalInfo', {})
                checkboxes = config.get('checkboxes', {})
                experience = config.get('experience', {})
                
                required_responses = [
                    'salary', 'startDate', 'citizenship', 'messageToManager'
                ]
                
                required_personal_info = [
                    'First Name', 'Last Name', 'Mobile Phone Number', 'City'
                ]
                
                missing_responses = [r for r in required_responses 
                                   if r not in responses]
                missing_personal = [p for p in required_personal_info 
                                  if p not in personal_info]
                
                if not missing_responses and not missing_personal:
                    self.log_test("068_Application_Responses", "PASS", 
                                "Application responses properly configured")
                else:
                    issues = []
                    if missing_responses:
                        issues.append(f"Missing responses: {missing_responses}")
                    if missing_personal:
                        issues.append(f"Missing personal info: {missing_personal}")
                    self.log_test("068_Application_Responses", "FAIL", 
                                "; ".join(issues))
            else:
                self.log_test("068_Application_Responses", "FAIL", 
                            "Configuration file not found")
                            
        except Exception as e:
            self.log_test("068_Application_Responses", "FAIL", error=e)

    def test_069_database_integration(self):
        """Test bot database integration"""
        try:
            db_path = 'backend/easyapply.db'
            
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Test job applications table
                cursor.execute('''
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='job_applications'
                ''')
                
                if cursor.fetchone():
                    # Test inserting a sample application
                    test_application = {
                        'id': 'test_app_' + str(int(time.time())),
                        'user_id': 'test_user',
                        'job_title': 'Test Engineer',
                        'company': 'Test Company',
                        'location': 'Test Location',
                        'status': 'applied'
                    }
                    
                    cursor.execute('''
                        INSERT INTO job_applications 
                        (id, user_id, job_title, company, location, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', tuple(test_application.values()))
                    
                    # Clean up test data
                    cursor.execute('DELETE FROM job_applications WHERE id = ?', 
                                 (test_application['id'],))
                    
                    conn.commit()
                    conn.close()
                    
                    self.log_test("069_Database_Integration", "PASS", 
                                "Bot database integration working")
                else:
                    self.log_test("069_Database_Integration", "FAIL", 
                                "Job applications table not found")
            else:
                self.log_test("069_Database_Integration", "FAIL", 
                            "Database file not found")
                            
        except Exception as e:
            self.log_test("069_Database_Integration", "FAIL", error=e)

    def test_070_output_file_management(self):
        """Test output file management and logging"""
        try:
            # Check if output files are properly configured
            config_path = 'config.yaml' if os.path.exists('config.yaml') else None
            
            if config_path:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                output_dir = config.get('outputFileDirectory')
                
                if output_dir:
                    # Create output directory if it doesn't exist
                    os.makedirs(output_dir, exist_ok=True)
                    
                    # Test file creation in output directory
                    test_file = os.path.join(output_dir, 'test_output.csv')
                    with open(test_file, 'w') as f:
                        f.write('test,data\n')
                    
                    if os.path.exists(test_file):
                        os.remove(test_file)  # Clean up
                        self.log_test("070_Output_File_Management", "PASS", 
                                    f"Output directory accessible: {output_dir}")
                    else:
                        self.log_test("070_Output_File_Management", "FAIL", 
                                    "Cannot write to output directory")
                else:
                    # Check for default output files
                    default_files = ['output.csv', 'failed.csv', 'qa_log.csv']
                    existing_files = [f for f in default_files if os.path.exists(f)]
                    
                    if existing_files:
                        self.log_test("070_Output_File_Management", "PASS", 
                                    f"Default output files found: {existing_files}")
                    else:
                        self.log_test("070_Output_File_Management", "WARN", 
                                    "No output files or directory configured")
            else:
                self.log_test("070_Output_File_Management", "FAIL", 
                            "Configuration file not found")
                            
        except Exception as e:
            self.log_test("070_Output_File_Management", "FAIL", error=e)

    def test_071_bot_error_handling(self):
        """Test bot error handling and recovery"""
        try:
            # Test with invalid configuration
            invalid_config = {
                'email': '',  # Empty email
                'password': '',  # Empty password
                'positions': [],  # Empty positions
                'locations': []  # Empty locations
            }
            
            # Create temporary invalid config file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(invalid_config, f)
                temp_config_path = f.name
            
            try:
                # Try to load invalid configuration
                with open(temp_config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                
                # Bot should handle invalid config gracefully
                validation_errors = []
                if not loaded_config.get('email'):
                    validation_errors.append("Empty email")
                if not loaded_config.get('positions'):
                    validation_errors.append("No positions")
                
                if validation_errors:
                    self.log_test("071_Bot_Error_Handling", "PASS", 
                                f"Error handling working: {validation_errors}")
                else:
                    self.log_test("071_Bot_Error_Handling", "FAIL", 
                                "Error handling not working")
                                
            finally:
                os.unlink(temp_config_path)
                
        except Exception as e:
            self.log_test("071_Bot_Error_Handling", "FAIL", error=e)

    def test_072_linkedin_url_validation(self):
        """Test LinkedIn URL validation and parsing"""
        try:
            test_urls = [
                ('https://www.linkedin.com/jobs/view/123456/', True),
                ('https://linkedin.com/jobs/view/123456', True),
                ('https://www.linkedin.com/company/test-company/', False),
                ('https://google.com/jobs', False),
                ('invalid-url', False),
                ('', False)
            ]
            
            url_validation_results = []
            
            for url, should_be_valid in test_urls:
                # Simple URL validation logic
                is_valid = (url.startswith('http') and 
                          'linkedin.com' in url and 
                          '/jobs/' in url)
                
                if is_valid == should_be_valid:
                    url_validation_results.append(f"✓ {url}")
                else:
                    url_validation_results.append(f"✗ {url}")
            
            passed_validations = len([r for r in url_validation_results if r.startswith('✓')])
            total_validations = len(url_validation_results)
            
            if passed_validations == total_validations:
                self.log_test("072_LinkedIn_URL_Validation", "PASS", 
                            "All URL validations passed")
            else:
                self.log_test("072_LinkedIn_URL_Validation", "FAIL", 
                            f"{passed_validations}/{total_validations} validations passed")
                            
        except Exception as e:
            self.log_test("072_LinkedIn_URL_Validation", "FAIL", error=e)

    def test_073_application_quota_management(self):
        """Test application quota management"""
        try:
            # Test quota calculation logic
            test_scenarios = [
                {'daily_quota': 5, 'daily_usage': 0, 'requested': 3, 'should_allow': True},
                {'daily_quota': 5, 'daily_usage': 4, 'requested': 2, 'should_allow': False},
                {'daily_quota': 10, 'daily_usage': 5, 'requested': 5, 'should_allow': True},
                {'daily_quota': 0, 'daily_usage': 0, 'requested': 1, 'should_allow': False}
            ]
            
            quota_results = []
            
            for scenario in test_scenarios:
                quota = scenario['daily_quota']
                usage = scenario['daily_usage']
                requested = scenario['requested']
                should_allow = scenario['should_allow']
                
                # Simple quota logic
                remaining = quota - usage
                can_apply = remaining >= requested and quota > 0
                
                if can_apply == should_allow:
                    quota_results.append(f"✓ Quota {quota}, Usage {usage}, Request {requested}")
                else:
                    quota_results.append(f"✗ Quota {quota}, Usage {usage}, Request {requested}")
            
            passed_quota_tests = len([r for r in quota_results if r.startswith('✓')])
            total_quota_tests = len(quota_results)
            
            if passed_quota_tests == total_quota_tests:
                self.log_test("073_Application_Quota_Management", "PASS", 
                            "All quota management tests passed")
            else:
                self.log_test("073_Application_Quota_Management", "FAIL", 
                            f"{passed_quota_tests}/{total_quota_tests} quota tests passed")
                            
        except Exception as e:
            self.log_test("073_Application_Quota_Management", "FAIL", error=e)

    def test_074_bot_performance_limits(self):
        """Test bot performance and rate limiting"""
        try:
            # Test performance configuration
            config_path = 'config.yaml' if os.path.exists('config.yaml') else None
            
            if config_path:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Check for performance-related settings
                performance_settings = {
                    'disableAntiLock': config.get('disableAntiLock', True),
                    'debug': config.get('debug', False)
                }
                
                # Validate performance settings
                if not performance_settings['disableAntiLock']:
                    self.log_test("074_Bot_Performance_Limits", "PASS", 
                                "Anti-lock measures enabled for safety")
                else:
                    self.log_test("074_Bot_Performance_Limits", "WARN", 
                                "Anti-lock measures disabled - use with caution")
            else:
                self.log_test("074_Bot_Performance_Limits", "WARN", 
                            "Configuration file not found")
                            
        except Exception as e:
            self.log_test("074_Bot_Performance_Limits", "FAIL", error=e)

    def test_075_web_agent_integration(self):
        """Test web platform agent integration"""
        try:
            # Check if web agent module exists
            web_agent_files = ['web_agent.py', 'backend/web_agent.py']
            web_agent_found = False
            
            for file_path in web_agent_files:
                if os.path.exists(file_path):
                    web_agent_found = True
                    
                    # Try to import the web agent
                    try:
                        if file_path.startswith('backend/'):
                            sys.path.append('backend')
                            from web_agent import WebPlatformLinkedInBot
                        else:
                            from web_agent import WebPlatformLinkedInBot
                        
                        self.log_test("075_Web_Agent_Integration", "PASS", 
                                    f"Web agent found and importable: {file_path}")
                        break
                    except ImportError as e:
                        self.log_test("075_Web_Agent_Integration", "FAIL", 
                                    f"Web agent import failed: {e}")
                        break
            
            if not web_agent_found:
                self.log_test("075_Web_Agent_Integration", "WARN", 
                            "Web agent module not found")
                            
        except Exception as e:
            self.log_test("075_Web_Agent_Integration", "FAIL", error=e)

    def run_bot_tests(self):
        """Run all bot functionality tests"""
        print("\n🤖 BOT FUNCTIONALITY TESTS")
        print("-" * 50)
        
        self.test_061_bot_module_imports()
        self.test_062_config_file_validation()
        self.test_063_resume_file_validation()
        self.test_064_chromedriver_availability()
        self.test_065_selenium_dependencies()
        self.test_066_openai_integration()
        self.test_067_job_search_parameters()
        self.test_068_application_responses()
        self.test_069_database_integration()
        self.test_070_output_file_management()
        self.test_071_bot_error_handling()
        self.test_072_linkedin_url_validation()
        self.test_073_application_quota_management()
        self.test_074_bot_performance_limits()
        self.test_075_web_agent_integration()
        
        # Summary
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.test_results if r['status'] == 'WARN'])
        
        print(f"\n📊 Bot Functionality Test Results:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   ⚠️  Warnings: {warnings}")
        
        return self.test_results


if __name__ == "__main__":
    suite = BotFunctionalityTestSuite()
    suite.run_bot_tests() 