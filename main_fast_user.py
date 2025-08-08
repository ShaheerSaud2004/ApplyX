#!/usr/bin/env python3

"""
User-Specific LinkedIn Easy Apply Bot - Enhanced Version
=======================================================

This script is designed to work with the web platform and provides:
- Comprehensive logging for debugging
- User-specific configuration and credentials
- Continuous application mode similar to main_fast.py
- Integration with the enhanced bot manager
- Real-time status updates
- Proper database integration for dashboard updates
"""

import os
import time
import random
import yaml
import json
import uuid
import sqlite3
import logging
import argparse
import sys
import traceback
import subprocess
import signal
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
import shutil

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Conditional import for GUI-dependent modules
# Set RUNNING_LOCALLY for local development
os.environ['RUNNING_LOCALLY'] = '1'
os.environ['DISPLAY'] = ':0'  # Set display for local development

LinkedinEasyApply = None
try:
    from linkedineasyapply import LinkedinEasyApply
    print("✅ LinkedinEasyApply module imported successfully")
except ImportError as e:
    print(f"Warning: Could not import LinkedinEasyApply: {e}")
    print("This is expected in headless environments like DigitalOcean")
    # Create a mock class for testing
    class MockLinkedinEasyApply:
        def __init__(self, config, browser):
            self.config = config
            self.browser = browser
            self.write_to_file = None
            print("🤖 Mock LinkedinEasyApply initialized")
        
        def login(self):
            print("🤖 Mock login called")
            return True
        
        def run_continuous_applications(self, max_applications):
            print(f"🤖 Mock run_continuous_applications called with max_applications={max_applications}")
            return 0
        
        def start_applying(self, max_applications=None):
            print(f"🤖 Mock start_applying called with max_applications={max_applications}")
            return 0
    
    LinkedinEasyApply = MockLinkedinEasyApply

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'bot_log_user_{os.getenv("USER_ID", "unknown")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

class EnhancedUserBot:
    """Enhanced user-specific bot with comprehensive logging and error handling"""
    
    def __init__(self, user_id, config_data=None):
        self.user_id = user_id
        self.session_id = f"{user_id}_{int(time.time())}"
        self.start_time = datetime.now()
        self.applications_today = 0
        self.stop_requested = False
        self.browser = None
        self.bot = None
        self.db_path = 'backend/easyapply.db' if os.path.exists('backend/easyapply.db') else 'easyapply.db'
        
        logger.info(f"🚀 Initializing Enhanced User Bot for user: {user_id}")
        logger.info(f"📝 Session ID: {self.session_id}")
        logger.info(f"💾 Database path: {self.db_path}")
        
        # Initialize database and tables
        self.init_database()
        
        # Load configuration
        self.config = self.load_user_config(config_data)
        if not self.config:
            raise Exception("Failed to load user configuration")
            
        logger.info(f"✅ Configuration loaded successfully")
        logger.info(f"👤 LinkedIn Email: {self.config.get('email', 'Not configured')}")
        logger.info(f"🎯 Target Positions: {', '.join(self.config.get('positions', []))}")
        logger.info(f"📍 Target Locations: {', '.join(self.config.get('locations', []))}")

    def init_database(self):
        """Initialize database and ensure job_applications table exists"""
        try:
            logger.info("🗄️ Initializing database for application tracking...")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create job_applications table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_applications (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    job_title TEXT,
                    company TEXT,
                    location TEXT,
                    job_url TEXT,
                    status TEXT DEFAULT 'applied',
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ai_generated BOOLEAN DEFAULT FALSE
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise

    def save_discovered_job_to_manual_apply(self, job_title, company, location, job_url):
        """Save discovered job to manual apply database for other users"""
        try:
            import hashlib
            import requests
            
            # Generate unique job ID
            job_id = hashlib.md5(f"{job_title}_{company}_{job_url}".encode()).hexdigest()
            
            # Connect to job listings database
            job_db_path = os.path.join(os.path.dirname(__file__), 'backend', 'job_listings.db')
            
            conn = sqlite3.connect(job_db_path)
            cursor = conn.cursor()
            
            # Check if job already exists
            cursor.execute('SELECT id FROM job_listings WHERE id = ?', (job_id,))
            if cursor.fetchone():
                conn.close()
                return  # Job already exists
            
            # Categorize and determine details
            category = self.categorize_job(job_title, company)
            experience_level = self.determine_experience_level(job_title)
            is_remote = 1 if 'remote' in location.lower() or 'remote' in job_title.lower() else 0
            
            logger.info(f"🔍 SAVING DISCOVERED JOB TO MANUAL APPLY DATABASE:")
            logger.info(f"🔍    🏢 Company: {company}")
            logger.info(f"🔍    💼 Job Title: {job_title}")
            logger.info(f"🔍    📍 Location: {location}")
            logger.info(f"🔍    🆔 Job ID: {job_id}")
            logger.info(f"🔍    📂 Category: {category}")
            
            # Insert the job
            cursor.execute('''
                INSERT INTO job_listings 
                (id, title, company, location, posted_date, url, category, 
                 is_remote, experience_level, source, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_id, job_title, company, location, datetime.now().isoformat(),
                job_url, category, is_remote, experience_level,
                f'Bot Discovery - User {self.user_id}', '[]',
                datetime.now().isoformat(), datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Job saved to manual apply database!")
            
        except Exception as e:
            logger.error(f"❌ Error saving discovered job to manual apply: {e}")

    def categorize_job(self, title, company):
        """Categorize a job based on title and company"""
        title_lower = title.lower()
        
        if any(keyword in title_lower for keyword in ['software', 'engineer', 'developer', 'programming', 'coding', 'frontend', 'backend', 'fullstack', 'react', 'python', 'javascript']):
            return 'software'
        elif any(keyword in title_lower for keyword in ['data', 'analytics', 'scientist', 'machine learning', 'ai', 'ml']):
            return 'data'
        elif any(keyword in title_lower for keyword in ['security', 'cybersecurity', 'infosec']):
            return 'cybersecurity'
        elif any(keyword in title_lower for keyword in ['devops', 'infrastructure', 'cloud', 'aws', 'sysadmin']):
            return 'it'
        elif any(keyword in title_lower for keyword in ['product', 'pm', 'product manager']):
            return 'product'
        elif any(keyword in title_lower for keyword in ['design', 'ui', 'ux', 'designer']):
            return 'design'
        else:
            return 'other'

    def determine_experience_level(self, title):
        """Determine experience level from job title"""
        title_lower = title.lower()
        
        if any(keyword in title_lower for keyword in ['intern', 'internship', 'entry', 'graduate', 'junior', 'new grad']):
            return 'entry'
        elif any(keyword in title_lower for keyword in ['senior', 'lead', 'principal', 'staff', 'architect']):
            return 'senior'
        else:
            return 'mid'

    def save_application_to_db(self, job_title, company, location, job_url, status='applied'):
        """Save application to database for dashboard updates"""
        try:
            # First, save the discovered job to manual apply database
            self.save_discovered_job_to_manual_apply(job_title, company, location, job_url)
            
            application_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            logger.info(f"💾 SAVING APPLICATION TO DATABASE:")
            logger.info(f"💾    🏢 Company: {company}")
            logger.info(f"💾    💼 Job Title: {job_title}")
            logger.info(f"💾    📍 Location: {location}")
            logger.info(f"💾    🔗 URL: {job_url}")
            logger.info(f"💾    👤 User ID: {self.user_id}")
            logger.info(f"💾    🆔 Application ID: {application_id}")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO job_applications 
                (id, user_id, job_title, company, location, job_url, status, applied_at, ai_generated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                application_id, self.user_id, job_title, company, location,
                job_url, status, timestamp, True
            ))
            
            conn.commit()
            
            # Verify insertion
            cursor.execute('SELECT COUNT(*) FROM job_applications WHERE id = ?', (application_id,))
            count = cursor.fetchone()[0]
            
            if count == 1:
                logger.info(f"✅ APPLICATION SAVED TO DATABASE SUCCESSFULLY!")
                logger.info(f"✅ Application ID: {application_id}")
                
                # Get total applications for user
                cursor.execute('SELECT COUNT(*) FROM job_applications WHERE user_id = ?', (self.user_id,))
                total_apps = cursor.fetchone()[0]
                logger.info(f"📊 Total applications for user: {total_apps}")
                
                conn.close()
                return application_id
            else:
                logger.error(f"❌ Database verification failed - record not found")
                conn.close()
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to save application to database: {e}")
            traceback.print_exc()
            return None

    def kill_existing_chrome_processes(self):
        """Kill any existing Chrome processes to prevent conflicts"""
        try:
            logger.info("🧹 Cleaning up existing Chrome processes...")
            
            # Kill Chrome processes on macOS/Linux
            try:
                subprocess.run(['pkill', '-f', 'chrome'], capture_output=True)
                subprocess.run(['pkill', '-f', 'chromedriver'], capture_output=True)
                time.sleep(2)
                logger.info("✅ Chrome processes cleaned up")
            except Exception as e:
                logger.warning(f"⚠️ Chrome cleanup warning: {e}")
                
        except Exception as e:
            logger.warning(f"⚠️ Process cleanup failed: {e}")
    
    def load_user_config(self, config_data=None):
        """Load user configuration from various sources with comprehensive logging"""
        logger.info("📋 Loading user configuration...")
        
        # If config data is provided directly (from enhanced bot manager)
        if config_data:
            logger.info("✅ Using provided configuration data")
            # Merge provided config with required defaults
            return self._merge_with_defaults(config_data)
            
        # Try to get from database
        try:
            db_config = self.get_config_from_database()
            if db_config:
                logger.info("✅ Configuration loaded from database")
                return db_config
        except Exception as e:
            logger.error(f"❌ Failed to load config from database: {e}")
            
        # Fallback to default config.yaml
        try:
            with open('config.yaml', 'r') as f:
                fallback_config = yaml.safe_load(f)
                logger.warning("⚠️ Using fallback config.yaml file")
                
                # Ensure email and password are properly set from config.yaml
                if 'email' in fallback_config and fallback_config['email']:
                    logger.info(f"📧 Found email in config.yaml: {fallback_config['email']}")
                else:
                    logger.error("❌ No email found in config.yaml")
                
                if 'password' in fallback_config and fallback_config['password']:
                    logger.info("🔒 Found password in config.yaml")
                else:
                    logger.error("❌ No password found in config.yaml")
                
                return fallback_config
        except Exception as e:
            logger.error(f"❌ Failed to load fallback config: {e}")
            return None
    
    def _parse_list_field(self, field_value):
        """Parse a field that could be a string, list, or comma-separated values"""
        if not field_value:
            return []
        if isinstance(field_value, list):
            return [str(item).strip() for item in field_value if str(item).strip()]
        if isinstance(field_value, str):
            return [item.strip() for item in field_value.split(',') if item.strip()]
        return [str(field_value).strip()] if str(field_value).strip() else []

    def get_config_from_database(self):
        """Get user configuration from database"""
        logger.info("📊 Querying database for user configuration...")
        
        try:
            # Determine database path
            db_path = 'backend/easyapply.db' if os.path.exists('backend/easyapply.db') else 'easyapply.db'
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get user's LinkedIn credentials
            cursor.execute('''
                SELECT linkedin_email_encrypted, linkedin_password_encrypted, 
                       personal_info, job_preferences, subscription_plan
                FROM users WHERE id = ?
            ''', (self.user_id,))
            
            user_data = cursor.fetchone()
            if not user_data or not user_data[0] or not user_data[1]:
                logger.error("❌ User not found or missing LinkedIn credentials")
                conn.close()
                return None
            
            # Decrypt credentials
            try:
                from backend.security import decrypt_data
                email = decrypt_data(user_data[0])
                password = decrypt_data(user_data[1])
                
                if not email or not password:
                    logger.error(f"❌ Decryption returned empty credentials")
                    conn.close()
                    return None
                
                logger.info(f"✅ Successfully decrypted credentials for: {email}")
            except ImportError as e:
                logger.error(f"❌ Failed to import security module: {e}")
                logger.error("⚠️ Trying alternative import path...")
                try:
                    from backend.security import decrypt_data
                    email = decrypt_data(user_data[0])
                    password = decrypt_data(user_data[1])
                    logger.info(f"✅ Successfully decrypted credentials with alternative import for: {email}")
                except Exception as e2:
                    logger.error(f"❌ Alternative import also failed: {e2}")
                    conn.close()
                    return None
            except Exception as e:
                logger.error(f"❌ Failed to decrypt credentials: {e}")
                logger.error(f"❌ Error type: {type(e).__name__}")
                conn.close()
                return None
            
            # Parse user preferences
            personal_info = json.loads(user_data[2]) if user_data[2] else {}
            job_preferences = json.loads(user_data[3]) if user_data[3] else {}
            subscription_plan = user_data[4] or 'free'
            
            logger.info(f"📋 LOADED JOB PREFERENCES FROM WEBSITE:")
            logger.info(f"    📝 Job Titles: {job_preferences.get('jobTitles', 'Not found')}")
            logger.info(f"    📍 Locations: {job_preferences.get('locations', 'Not found')}")
            logger.info(f"    💰 Salary Min: {job_preferences.get('salaryMin', 'Not found')}")
            logger.info(f"    📊 Experience: {job_preferences.get('experience', 'Not found')}")
            
            # Get user preferences for job search
            cursor.execute('''
                SELECT job_titles, locations, remote, experience, salary_min, skills
                FROM user_preferences WHERE user_id = ?
            ''', (self.user_id,))
            
            prefs_data = cursor.fetchone()
            conn.close()
            
            # Build configuration with all required LinkedinEasyApply keys
            config = {
                # Basic credentials
                'email': email,
                'password': password,
                'user_id': self.user_id,
                'subscription_plan': subscription_plan,
                'openaiApiKey': '',
                
                # Required LinkedinEasyApply settings
                'disableAntiLock': False,
                'remote': prefs_data[2] if prefs_data else True,
                'lessthanTenApplicants': False,
                'newestPostingsFirst': False,
                'residentStatus': False,
                'distance': 100,
                'outputFileDirectory': os.getcwd(),
                'debug': False,
                'evaluateJobFit': True,
                'textResume': '',
                'noticePeriod': 2,
                'universityGpa': 3.7,
                'salaryMinimum': 65000,
                
                # Job search preferences - USE WEBSITE PROFILE DATA FIRST
                'positions': self._parse_list_field(job_preferences.get('jobTitles') or job_preferences.get('job_titles') or (prefs_data[0] if prefs_data and prefs_data[0] else 'Software Engineer')),
                'locations': self._parse_list_field(job_preferences.get('locations') or (prefs_data[1] if prefs_data and prefs_data[1] else 'East Brunswick, New Jersey')),
                'companyBlacklist': job_preferences.get('company_blacklist', []),
                'titleBlacklist': job_preferences.get('title_blacklist', []),
                'posterBlacklist': [],
                
                # Experience level (LinkedIn format)
                'experienceLevel': {
                    'internship': False,
                    'entry': True,
                    'associate': True,
                    'mid-senior level': True,
                    'director': False,
                    'executive': False
                },
                
                # Job types (LinkedIn format)
                'jobTypes': {
                    'full-time': True,
                    'contract': True,
                    'part-time': False,
                    'temporary': False,
                    'internship': False,
                    'other': False,
                    'volunteer': False
                },
                
                # Date filter (LinkedIn format)
                'date': {
                    'all time': True,
                    'month': False,
                    'week': False,
                    '24 hours': False
                },
                
                # File uploads
                'uploads': {
                    'resume': 'uploads/resume.pdf',
                    'coverLetter': ''
                },
                
                # Personal information
                'personalInfo': {
                    'First Name': personal_info.get('first_name', 'John'),
                    'Last Name': personal_info.get('last_name', 'Doe'),
                    'Phone': personal_info.get('phone', '555-0123'),
                    'Email': email,
                    **personal_info
                },
                
                # Languages
                'languages': {
                    'english': 'Native or bilingual'
                },
                
                # Experience
                'experience': {
                    'Python': 4,
                    'JavaScript': 3,
                    'SQL': 3,
                    'default': 2
                },
                
                # EEO information
                'eeo': {
                    'gender': 'Prefer not to say',
                    'race': 'Prefer not to say',
                    'veteran': False,
                    'disability': False,
                    'citizenship': True
                },
                
                # Checkboxes for application questions
                'checkboxes': {
                    'driversLicence': True,
                    'requireVisa': False,
                    'legallyAuthorized': True,
                    'certifiedProfessional': False,
                    'urgentFill': True,
                    'commute': True,
                    'remote': True,
                    'drugTest': True,
                    'assessment': True,
                    'securityClearance': False,
                    'degreeCompleted': ['Bachelor\'s Degree'],
                    'backgroundCheck': True
                },
                
                # Additional settings for compatibility
                'easyApplyOnly': True
            }
            
            logger.info(f"✅ Database configuration built successfully")
            logger.info(f"🎯 FINAL BOT SEARCH CONFIG:")
            logger.info(f"    📝 Will search for: {config['positions']}")
            logger.info(f"    📍 In locations: {config['locations']}")
            logger.info(f"    🎯 Total job titles to search: {len(config['positions'])}")
            return config
            
        except Exception as e:
            logger.error(f"❌ Database query failed: {e}")
            return None
    
    def _merge_with_defaults(self, provided_config):
        """Merge provided configuration with required LinkedinEasyApply defaults"""
        logger.info("🔧 Merging provided config with required defaults...")
        
        # Get defaults configuration
        defaults = {
            # Required LinkedinEasyApply settings
            'disableAntiLock': False,
            'remote': True,
            'lessthanTenApplicants': False,
            'newestPostingsFirst': False,
            'residentStatus': False,
            'distance': 100,
            'outputFileDirectory': os.getcwd(),
            'debug': False,
            'evaluateJobFit': True,
            'textResume': '',
            'noticePeriod': 2,
            'universityGpa': 3.7,
            'salaryMinimum': 65000,
            'openaiApiKey': '',
            
            # Blacklists
            'companyBlacklist': [],
            'titleBlacklist': [],
            'posterBlacklist': [],
            
            # Experience level (LinkedIn format)
            'experienceLevel': {
                'internship': False,
                'entry': True,
                'associate': True,
                'mid-senior level': True,
                'director': False,
                'executive': False
            },
            
            # Job types (LinkedIn format)
            'jobTypes': {
                'full-time': True,
                'contract': True,
                'part-time': False,
                'temporary': False,
                'internship': False,
                'other': False,
                'volunteer': False
            },
            
            # Date filter (LinkedIn format)
            'date': {
                'all time': True,
                'month': False,
                'week': False,
                '24 hours': False
            },
            
            # File uploads
            'uploads': {
                'resume': 'uploads/resume.pdf',
                'coverLetter': ''
            },
            
            # Personal information
            'personalInfo': {
                'First Name': 'John',
                'Last Name': 'Doe',
                'Phone': '555-0123',
                'Email': provided_config.get('email', 'test@example.com')
            },
            
            # Languages
            'languages': {
                'english': 'Native or bilingual'
            },
            
            # Experience
            'experience': {
                'Python': 4,
                'JavaScript': 3,
                'SQL': 3,
                'default': 2
            },
            
            # EEO information
            'eeo': {
                'gender': 'Prefer not to say',
                'race': 'Prefer not to say',
                'veteran': False,
                'disability': False,
                'citizenship': True
            },
            
            # Checkboxes for application questions
            'checkboxes': {
                'driversLicence': True,
                'requireVisa': False,
                'legallyAuthorized': True,
                'certifiedProfessional': False,
                'urgentFill': True,
                'commute': True,
                'remote': True,
                'drugTest': True,
                'assessment': True,
                'securityClearance': False,
                'degreeCompleted': ['Bachelor\'s Degree'],
                'backgroundCheck': True
            }
        }
        
        # Merge provided config over defaults
        merged_config = {**defaults, **provided_config}
        
        # Ensure positions and locations are lists
        if 'positions' in merged_config and isinstance(merged_config['positions'], str):
            merged_config['positions'] = [merged_config['positions']]
        if 'locations' in merged_config and isinstance(merged_config['locations'], str):
            merged_config['locations'] = [merged_config['locations']]
        
        # Set default positions and locations if not provided
        if 'positions' not in merged_config or not merged_config['positions']:
            merged_config['positions'] = ['Software Engineer']
        if 'locations' not in merged_config or not merged_config['locations']:
            merged_config['locations'] = ['Remote']
        
        logger.info("✅ Configuration merged successfully with defaults")
        return merged_config
    
    def init_browser_with_retry(self):
        """Initialize Chrome browser with stealth features and retry if user-data-dir is locked"""
        from selenium.common.exceptions import SessionNotCreatedException
        import uuid, shutil

        def _launch(chrome_user_dir: str):
            # Use simple, reliable stealth configuration
            from stealth_config_fixed import create_simple_browser
            return create_simple_browser(fresh_session=True, user_data_dir=chrome_user_dir)

        # First try the user-specific directory
        user_dir = os.path.join(os.getcwd(), f"chrome_bot_user_{self.user_id}")
        try:
            logger.info(f"🌐 Attempting to launch browser with user directory: {user_dir}")
            return _launch(user_dir)
        except SessionNotCreatedException:
            logger.warning("⚠️ User-specific directory locked, trying with temporary profile...")
            tmp_dir = os.path.join(os.getcwd(), f"chrome_bot_tmp_user_{self.user_id}_{uuid.uuid4().hex[:6]}")
            driver = _launch(tmp_dir)
            # Schedule temp dir cleanup on driver quit
            def _cleanup(path):
                try:
                    shutil.rmtree(path, ignore_errors=True)
                except Exception:
                    pass
            import atexit
            atexit.register(_cleanup, tmp_dir)
            logger.info(f"✅ Browser launched with temporary directory: {tmp_dir}")
            return driver

    def clear_previous_logs(self):
        """Clear previous activity logs when starting a new session"""
        try:
            logger.info("🧹 Clearing previous activity logs...")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear old activity logs for this user
            cursor.execute('DELETE FROM activity_log WHERE user_id = ?', (self.user_id,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Cleared {deleted_count} previous activity log entries")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to clear previous logs: {e}")

    def run_continuous_applications(self, max_applications=None):
        """Run continuous job applications with enhanced tracking and restart functionality"""
        self.start_time = datetime.now()
        self.stop_requested = False
        
        # Initialize restart tracking
        consecutive_failures = 0
        max_consecutive_failures = 2  # Restart after 2 consecutive failures
        
        try:
            # Initialize browser and bot
            logger.info("🌐 Initializing browser...")
            self.browser = self.init_browser_with_retry()
            if not self.browser:
                raise Exception("Failed to initialize browser")
            
            logger.info("🤖 Initializing LinkedIn bot...")
            if LinkedinEasyApply is None:
                raise Exception("LinkedinEasyApply module not available")
            
            self.bot = LinkedinEasyApply(self.config, self.browser)
            logger.info("✅ Bot initialized successfully")
            
            # Store the original write_to_file function
            original_write_to_file = self.bot.write_to_file
            
            # Enhanced write_to_file function for better tracking
            def enhanced_write_to_file(company, job_title, link, location, search_location):
                """Enhanced application tracking with database integration"""
                try:
                    logger.info("🎯 ===============================================")
                    logger.info("🎯 🎉 SUCCESSFUL APPLICATION DETECTED!")
                    logger.info(f"🎯 🏢 Company: {company}")
                    logger.info(f"🎯 💼 Job Title: {job_title}")
                    logger.info(f"🎯 📍 Location: {location}")
                    logger.info(f"🎯 🔗 URL: {link}")
                    logger.info(f"🎯 🎯 Search Location: {search_location}")
                    logger.info(f"🎯 👤 User ID: {self.user_id}")
                    logger.info(f"🎯 🕐 Timestamp: {datetime.now()}")
                    logger.info("🎯 ===============================================")
                    
                    # Save to database for dashboard updates
                    print("🎯 💾 STARTING DATABASE SAVE...")
                    print("🎯 💾 STARTING DATABASE SAVE...")
                    print("🎯 💾 STARTING DATABASE SAVE...")
                    logger.info("🎯 💾 SAVING TO DATABASE FOR DASHBOARD...")
                    try:
                        print(f"🎯 📞 CALLING save_application_to_db with: {job_title}, {company}, {location}, {link}")
                        application_id = self.save_application_to_db(job_title, company, location, link)
                        print(f"🎯 📋 SAVE RESULT: {application_id}")
                        if application_id:
                            self.applications_today += 1
                            print(f"🎯 🎉 SUCCESS! APPLICATION SAVED!")
                            print(f"🎯 🎉 APPLICATION ID: {application_id}")
                            print(f"🎯 📈 APPLICATIONS TODAY: {self.applications_today}")
                            logger.info(f"🎯 🎉 APPLICATION SAVED TO DATABASE SUCCESSFULLY!")
                            logger.info(f"🎯 📊 Application ID: {application_id}")
                            logger.info(f"🎯 📈 Total applications today: {self.applications_today}")
                            logger.info(f"🎯 ✅ DASHBOARD WILL BE UPDATED WITH THIS APPLICATION!")
                            
                            # Reset consecutive failures on successful application
                            consecutive_failures = 0
                            
                            # Notify enhanced bot manager about the application
                            try:
                                # Create job data for notification
                                job_data = {
                                    'job_title': job_title,
                                    'company': company,
                                    'location': location,
                                    'job_url': link,
                                    'applied_at': datetime.now().isoformat(),
                                    'application_id': application_id
                                }
                                
                                # Try to notify the enhanced bot manager
                                self.notify_bot_manager(job_data)
                                
                            except Exception as notify_error:
                                logger.warning(f"🎯 ⚠️ Could not notify bot manager: {notify_error}")
                            
                        else:
                            print(f"🎯 ❌ DATABASE SAVE FAILED!")
                            logger.error(f"🎯 ❌ Failed to save application to database")
                    except Exception as db_error:
                        print(f"🎯 🚨 DATABASE ERROR: {db_error}")
                        logger.error(f"🎯 ❌ Database save error: {db_error}")
                        traceback.print_exc()
                    
                    # Also save to CSV file (original functionality)
                    logger.info("🎯 📄 SAVING TO CSV FILE (BACKUP)...")
                    try:
                        original_write_to_file(company, job_title, link, location, search_location)
                        logger.info("🎯 ✅ CSV backup completed successfully")
                    except Exception as csv_error:
                        logger.error(f"🎯 ⚠️ CSV backup failed: {csv_error}")
                    
                    logger.info("🎯 🎉 APPLICATION PROCESSING COMPLETED!")
                    logger.info("🎯 ===============================================")
                        
                except Exception as e:
                    logger.error(f"🎯 ❌ Error in enhanced_write_to_file: {e}")
                    traceback.print_exc()
            
            # Override the bot's write_to_file method
            self.bot.write_to_file = enhanced_write_to_file
            logger.info("✅ Database integration enabled for application tracking")
            
            # Login process with detailed logging
            logger.info("🔐 Starting LinkedIn login process...")
            self.log_activity("Login", "Starting LinkedIn authentication")
            
            try:
                self.bot.login()
                logger.info("✅ LinkedIn login successful")
                self.log_activity("Login", "Successfully logged into LinkedIn")
            except Exception as e:
                error_message = str(e).lower()
                logger.error(f"❌ LinkedIn login failed: {e}")
                
                # Check for specific credential-related errors
                if any(keyword in error_message for keyword in ['invalid', 'incorrect', 'wrong', 'failed', 'error', 'unauthorized', '401', '403']):
                    if 'email' in error_message or 'username' in error_message:
                        error_msg = "❌ Invalid email address. Please check your LinkedIn email and try again."
                        self.log_activity("Login", "Invalid email address provided", "error")
                    elif 'password' in error_message:
                        error_msg = "❌ Invalid password. Please check your LinkedIn password and try again."
                        self.log_activity("Login", "Invalid password provided", "error")
                    else:
                        error_msg = "❌ Invalid credentials. Please check your LinkedIn email and password."
                        self.log_activity("Login", "Invalid credentials provided", "error")
                elif 'captcha' in error_message or 'verification' in error_message:
                    error_msg = "❌ LinkedIn security check required. Please complete the verification manually and try again."
                    self.log_activity("Login", "LinkedIn security verification required", "error")
                elif 'network' in error_message or 'connection' in error_message:
                    error_msg = "❌ Network connection error. Please check your internet connection and try again."
                    self.log_activity("Login", "Network connection error", "error")
                elif 'timeout' in error_message:
                    error_msg = "❌ Login timeout. Please try again."
                    self.log_activity("Login", "Login timeout error", "error")
                else:
                    error_msg = f"❌ Login failed: {e}"
                self.log_activity("Login", f"Login failed: {str(e)}", "error")
                
                # Notify the enhanced bot manager about the login failure
                try:
                    self.notify_bot_manager({
                        'error_type': 'login_failure',
                        'error_message': error_msg,
                        'timestamp': datetime.now().isoformat()
                    })
                except Exception as notify_error:
                    logger.warning(f"⚠️ Could not notify bot manager about login failure: {notify_error}")
                
                # Log the detailed error for debugging
                logger.error(f"🔍 Login error details: {error_msg}")
                logger.error(f"🔍 Original error: {e}")
                
                raise Exception(error_msg)
            
            # Security check
            logger.info("🛡️ Performing security check...")
            try:
                self.bot.security_check()
                logger.info("✅ Security check passed")
                self.log_activity("Security", "Security check completed successfully")
            except Exception as e:
                error_message = str(e).lower()
                logger.error(f"❌ Security check failed: {e}")
                
                # Check for specific security-related errors
                if any(keyword in error_message for keyword in ['invalid', 'incorrect', 'wrong', 'failed', 'unauthorized', '401', '403']):
                    if 'email' in error_message or 'username' in error_message:
                        error_msg = "❌ Invalid email address detected during security check. Please verify your LinkedIn credentials."
                        self.log_activity("Security", "Invalid email detected during security check", "error")
                    elif 'password' in error_message:
                        error_msg = "❌ Invalid password detected during security check. Please verify your LinkedIn credentials."
                        self.log_activity("Security", "Invalid password detected during security check", "error")
                    else:
                        error_msg = "❌ Invalid credentials detected during security check. Please verify your LinkedIn email and password."
                        self.log_activity("Security", "Invalid credentials detected during security check", "error")
                elif 'captcha' in error_message or 'verification' in error_message:
                    error_msg = "❌ LinkedIn security verification required. Please complete the verification manually and try again."
                    self.log_activity("Security", "LinkedIn security verification required", "error")
                elif 'network' in error_message or 'connection' in error_message:
                    error_msg = "❌ Network connection error during security check. Please check your internet connection."
                    self.log_activity("Security", "Network connection error during security check", "error")
                elif 'timeout' in error_message:
                    error_msg = "❌ Security check timeout. Please try again."
                    self.log_activity("Security", "Security check timeout", "error")
                else:
                    error_msg = f"❌ Security check failed: {e}"
                self.log_activity("Security", f"Security check failed: {str(e)}", "error")
                
                # Notify the enhanced bot manager about the security check failure
                try:
                    self.notify_bot_manager({
                        'error_type': 'security_check_failure',
                        'error_message': error_msg,
                        'timestamp': datetime.now().isoformat()
                    })
                except Exception as notify_error:
                    logger.warning(f"⚠️ Could not notify bot manager about security check failure: {notify_error}")
                
                # Log the detailed error for debugging
                logger.error(f"🔍 Security check error details: {error_msg}")
                logger.error(f"🔍 Original error: {e}")
                
                raise Exception(error_msg)
            
            # Start application process with restart functionality
            logger.info("🎯 Starting job application process...")
            self.log_activity("Application", "Starting continuous job application process")
            
            application_count = 0
            
            while not self.stop_requested:
                try:
                    if max_applications and application_count >= max_applications:
                        logger.info(f"🎉 Reached maximum applications limit: {max_applications}")
                        break
                    
                    # Check current quota status from database
                    current_usage, daily_quota = self.check_current_quota()
                    if current_usage >= daily_quota:
                        logger.info(f"🚫 Daily quota reached: {current_usage}/{daily_quota} applications used")
                        self.log_activity("Quota Limit", f"Daily quota of {daily_quota} applications reached", "warning")
                        
                        # Send quota completion email
                        try:
                            self.send_quota_completion_email()
                        except Exception as email_error:
                            logger.error(f"❌ Failed to send quota completion email: {email_error}")
                        
                        break
                    
                    remaining_quota = daily_quota - current_usage
                    logger.info(f"📊 Current quota status: {current_usage}/{daily_quota} used, {remaining_quota} remaining")
                    
                    logger.info(f"🔍 Looking for job opportunities (attempt {application_count + 1})...")
                    self.log_activity("Search", f"Searching for jobs (application {application_count + 1}) - {remaining_quota} applications remaining")
                    
                    # Apply to jobs using the OLD WORKING method
                    result = self.bot.start_applying()
                    
                    if result and result > 0:
                        application_count += result
                        consecutive_failures = 0  # Reset failure counter on success
                        logger.info(f"✅ Successfully applied to {result} job(s) - Total: {application_count}")
                        self.log_activity("Application", f"Successfully applied to {result} job(s) - Total: {application_count}", "success")
                        
                        # Delay like the old working code
                        delay_minutes = random.uniform(1, 2)
                        delay_seconds = delay_minutes * 60
                        logger.info(f"⏱️ Waiting {delay_minutes:.1f} minutes before next application...")
                        time.sleep(delay_seconds)
                        
                    else:
                        consecutive_failures += 1
                        logger.info(f"⏸️ No suitable jobs found in this cycle (failure {consecutive_failures}/{max_consecutive_failures})")
                        self.log_activity("Search", f"No suitable jobs found in current search cycle - failure {consecutive_failures}/{max_consecutive_failures}")
                        
                        # Check if we need to restart due to consecutive failures
                        if consecutive_failures >= max_consecutive_failures:
                            logger.warning(f"🔄 Restarting bot after {consecutive_failures} consecutive failures")
                            self.log_activity("Restart", f"Restarting bot after {consecutive_failures} consecutive failures", "warning")
                            
                            # Restart the browser and login
                            try:
                                self.cleanup()
                                time.sleep(5)  # Wait before restart
                                self.init_browser_with_retry()
                                self.bot.login()
                                consecutive_failures = 0  # Reset counter
                                logger.info("✅ Bot restarted successfully")
                                self.log_activity("Restart", "Bot restarted successfully", "success")
                            except Exception as restart_error:
                                logger.error(f"❌ Failed to restart bot: {restart_error}")
                                self.log_activity("Restart", f"Failed to restart bot: {str(restart_error)}", "error")
                                break
                        else:
                            logger.info("⏭️ Continuing search...")
                            time.sleep(30)  # Short delay before trying again
                    
                except KeyboardInterrupt:
                    logger.info("🛑 Received stop signal from user")
                    self.stop_requested = True
                    break
                    
                except Exception as e:
                    consecutive_failures += 1
                    logger.error(f"❌ Error in application cycle: {e}")
                    traceback.print_exc()
                    self.log_activity("Error", f"Application cycle error: {str(e)}", "error")
                    
                    # Check if we need to restart due to consecutive failures
                    if consecutive_failures >= max_consecutive_failures:
                        logger.warning(f"🔄 Restarting bot after {consecutive_failures} consecutive failures")
                        self.log_activity("Restart", f"Restarting bot after {consecutive_failures} consecutive failures", "warning")
                        
                        try:
                            self.cleanup()
                            time.sleep(5)  # Wait before restart
                            self.init_browser_with_retry()
                            self.bot.login()
                            consecutive_failures = 0  # Reset counter
                            logger.info("✅ Bot restarted successfully")
                            self.log_activity("Restart", "Bot restarted successfully", "success")
                        except Exception as restart_error:
                            logger.error(f"❌ Failed to restart bot: {restart_error}")
                            self.log_activity("Restart", f"Failed to restart bot: {str(restart_error)}", "error")
                            break
                    else:
                        logger.info("⏸️ Waiting 2 minutes before retrying...")
                        time.sleep(120)
            
            # Session summary
            runtime = datetime.now() - self.start_time
            logger.info("=" * 80)
            logger.info("📊 SESSION COMPLETE - SUMMARY")
            logger.info("=" * 80)
            logger.info(f"⏰ Total Runtime: {runtime}")
            logger.info(f"📝 Applications Submitted: {application_count}")
            logger.info(f"📊 Applications Today: {self.applications_today}")
            logger.info(f"📧 User: {self.config.get('email')}")
            logger.info(f"🎯 Session ID: {self.session_id}")
            logger.info(f"💾 Database: {self.db_path}")
            
            self.log_activity("Complete", f"Session completed with {application_count} applications", "success", {
                'total_applications': application_count,
                'applications_today': self.applications_today,
                'runtime_seconds': runtime.total_seconds()
            })
            
            return application_count
            
        except Exception as e:
            logger.error(f"❌ FATAL ERROR in continuous applications: {e}")
            traceback.print_exc()
            self.log_activity("Fatal Error", f"Session failed: {str(e)}", "error")
            raise
            
        finally:
            self.cleanup()

    def check_current_quota(self):
        """Check current quota usage from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get today's applications count
            cursor.execute('''
                SELECT COUNT(*) FROM job_applications 
                WHERE user_id = ? AND DATE(applied_at) = DATE('now')
            ''', (self.user_id,))
            
            current_usage = cursor.fetchone()[0]
            
            # Get user's daily quota from config
            daily_quota = self.config.get('daily_quota', 10)
            
            conn.close()
            
            logger.info(f"📊 Quota check: {current_usage}/{daily_quota} applications used today")
            return current_usage, daily_quota
            
        except Exception as e:
            logger.error(f"❌ Error checking quota: {e}")
            return 0, 10  # Default fallback
    
    def notify_bot_manager(self, job_data):
        """Notify the enhanced bot manager about a successful application"""
        try:
            # Try to send notification to the enhanced bot manager using internal endpoint
            import requests
            response = requests.post(
                'http://localhost:5001/api/bot/application/internal',
                json={
                    'user_id': self.user_id,
                    'job_data': job_data
                },
                timeout=5
            )
            if response.status_code == 200:
                logger.info("✅ Successfully notified enhanced bot manager")
                response_data = response.json()
                logger.info(f"📊 Current usage: {response_data.get('current_usage', 'unknown')}/{response_data.get('daily_quota', 'unknown')}")
            else:
                logger.warning(f"⚠️ Bot manager notification failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.warning(f"⚠️ Could not notify bot manager: {e}")

    def send_quota_completion_email(self):
        """Send email when daily quota is reached"""
        try:
            # Get today's applications for the summary
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT job_title, company, location, applied_at 
                FROM job_applications 
                WHERE user_id = ? AND DATE(applied_at) = DATE('now')
                ORDER BY applied_at DESC
            ''', (self.user_id,))
            
            applications = cursor.fetchall()
            conn.close()
            
            if not applications:
                logger.warning("⚠️ No applications found for quota completion email")
                return
            
            # Create applications summary
            applications_summary = []
            for job_title, company, location, applied_at in applications:
                applications_summary.append({
                    'title': job_title,
                    'company': company,
                    'location': location,
                    'applied_at': applied_at
                })
            
            # Try to send email via the enhanced bot manager
            try:
                import requests
                response = requests.post(
                    'http://localhost:5001/api/bot/quota-completion',
                    json={
                        'user_id': self.user_id,
                        'user_email': self.config.get('email'),
                        'user_name': self.config.get('name', 'User'),
                        'applications_summary': applications_summary
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    logger.info("✅ Quota completion email sent successfully")
                else:
                    logger.warning(f"⚠️ Quota completion email failed: {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ Could not send quota completion email: {e}")
                
        except Exception as e:
            logger.error(f"❌ Error in send_quota_completion_email: {e}")
            traceback.print_exc()

    def cleanup(self):
        """Clean up resources"""
        logger.info("🧹 Cleaning up resources...")
        
        try:
            if self.browser:
                logger.info("🌐 Closing browser...")
                self.browser.quit()
                logger.info("✅ Browser closed successfully")
        except Exception as e:
            logger.warning(f"⚠️ Browser cleanup warning: {e}")
        
        try:
            # Kill any remaining Chrome processes
            self.kill_existing_chrome_processes()
        except Exception as e:
            logger.warning(f"⚠️ Process cleanup warning: {e}")
        
        logger.info("✅ Cleanup completed")

    def log_activity(self, action, details, status='info', metadata=None):
        """Log activity to database for web platform integration"""
        try:
            db_path = 'backend/easyapply.db' if os.path.exists('backend/easyapply.db') else 'easyapply.db'
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Use the existing activity_log table structure
            # Insert activity without specifying id (let it auto-increment)
            cursor.execute('''
                INSERT INTO activity_log 
                (user_id, action, details, status, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                self.user_id, action, details, status,
                json.dumps(metadata) if metadata else None, datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to log activity: {e}")

def main():
    """Main entry point for the enhanced user bot"""
    parser = argparse.ArgumentParser(description='Enhanced LinkedIn Easy Apply Bot')
    parser.add_argument('--user-id', required=True, help='User ID for the bot session')
    parser.add_argument('--max-applications', type=int, help='Maximum number of applications to submit')
    parser.add_argument('--config', help='Path to configuration file')
    
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("🚀 ENHANCED LINKEDIN EASY APPLY BOT STARTING")
    logger.info("=" * 80)
    logger.info(f"👤 User ID: {args.user_id}")
    logger.info(f"🎯 Max Applications: {args.max_applications if args.max_applications else 'Unlimited'}")
    
    try:
        # Load config data if provided
        config_data = None
        if args.config:
            # Check if it's a JSON string (starts with {)
            if args.config.strip().startswith('{'):
                try:
                    import json
                    config_data = json.loads(args.config)
                    logger.info("✅ Loaded configuration from JSON string")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Invalid JSON in config: {e}")
                    return -1
            # Check if it's a file path
            elif os.path.exists(args.config):
                with open(args.config, 'r') as f:
                    config_data = yaml.safe_load(f)
                    logger.info(f"✅ Loaded configuration from: {args.config}")
            else:
                logger.error(f"❌ Config file not found: {args.config}")
                return -1
        
        # Initialize and run bot
        bot = EnhancedUserBot(args.user_id, config_data)
        applications_count = bot.run_continuous_applications(args.max_applications)
        
        logger.info("=" * 80)
        logger.info("🎉 BOT EXECUTION COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"📝 Total Applications: {applications_count}")
        logger.info(f"⏰ Session Duration: {datetime.now() - bot.start_time}")
        
        return applications_count
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Bot execution failed: {e}")
        traceback.print_exc()
        return -1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(0 if exit_code >= 0 else 1) 