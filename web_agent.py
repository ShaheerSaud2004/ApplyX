#!/usr/bin/env python3

import os
import time
import random
import yaml
import sqlite3
import json
import uuid
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import SessionNotCreatedException

# Conditional import for GUI-dependent modules
LinkedinEasyApply = None
if os.environ.get('DISPLAY') or os.environ.get('RUNNING_LOCALLY'):
    try:
        from linkedineasyapply import LinkedinEasyApply
    except ImportError as e:
        print(f"Warning: Could not import LinkedinEasyApply: {e}")
        print("This is expected in headless environments like DigitalOcean")

def safe_split_to_list(value, delimiter=','):
    """Safely convert string or list to a list of trimmed strings"""
    if not value:
        return []
    
    # If it's already a list, return it cleaned
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    
    # If it's a string, split it
    if isinstance(value, str):
        return [item.strip() for item in value.split(delimiter) if item.strip()]
    
    # Fallback for other types
    return [str(value).strip()] if str(value).strip() else []

class WebPlatformLinkedInBot:
    """Enhanced LinkedIn bot that integrates with the web platform"""
    
    def __init__(self, user_id, config_override=None):
        self.user_id = user_id or os.getenv('USER_ID')
        self.session_id = os.getenv('SESSION_ID', f"{self.user_id}_{int(time.time())}")
        self.daily_quota = int(os.getenv('DAILY_QUOTA', '5'))
        
        self.config = self.load_config(config_override)
        self.applications_today = 0
        self.session_count = 0
        self.start_time = datetime.now()
        self.stop_requested = False
        self.fast_mode = False
        self.status_callback = None
        self.db_path = 'backend/easyapply.db'
        
        # Timeout tracking for auto-restart
        self.last_application_time = datetime.now()
        self.timeout_minutes = 4  # Restart if no application in 4 minutes
        self.restart_count = 0
        self.max_restarts = 5  # Maximum number of auto-restarts
        
        # Enhanced bot manager integration
        self.application_callback = None
        self.activity_logger = None
        
        # Get enhanced bot manager instance
        try:
            from backend.enhanced_bot_manager import get_enhanced_bot_manager
            self.enhanced_manager = get_enhanced_bot_manager()
            # Set up callbacks
            self.application_callback = self.enhanced_manager.log_application
            self.activity_logger = self.enhanced_manager.log_activity
        except ImportError:
            self.enhanced_manager = None
            
        if config_override and isinstance(config_override, dict):
            # Override with provided callbacks
            if 'application_callback' in config_override:
                self.application_callback = config_override['application_callback']
            if 'activity_logger' in config_override:
                self.activity_logger = config_override['activity_logger']
        else:
            self.application_callback = None
            self.activity_logger = None
        
    def load_config(self, config_override=None):
        """Load configuration from file or use provided override"""
        if config_override:
            return config_override
        
        # Get user-specific configuration from database
        user_config = self.get_user_config()
        if user_config:
            return user_config
            
        try:
            with open('config.yaml', 'r') as stream:
                return yaml.safe_load(stream)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()
    
    def get_user_config(self):
        """Get user-specific configuration from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user's encrypted LinkedIn credentials
            cursor.execute('''
                SELECT linkedin_email_encrypted, linkedin_password_encrypted
                FROM users WHERE id = ?
            ''', (self.user_id,))
            
            user_data = cursor.fetchone()
            if not user_data or not user_data[0] or not user_data[1]:
                conn.close()
                return None
            
            # Decrypt LinkedIn credentials
            try:
                from backend.security import decrypt_data
                email = decrypt_data(user_data[0])
                password = decrypt_data(user_data[1])
                
                if not email or not password:
                    conn.close()
                    return None
                    
            except Exception as e:
                print(f"Failed to decrypt LinkedIn credentials: {e}")
                conn.close()
                return None
            
            # Get user preferences
            cursor.execute('''
                SELECT job_titles, locations, remote, experience, salary_min, skills
                FROM user_preferences WHERE user_id = ?
            ''', (self.user_id,))
            
            prefs = cursor.fetchone()
            conn.close()
            
            # Build configuration
            config = {
                'email': email,
                'password': password,
                'openaiApiKey': os.environ.get('OPENAI_API_KEY', ''),
                'positions': safe_split_to_list(prefs[0]) if prefs and prefs[0] else ['Software Engineer'],
                'locations': safe_split_to_list(prefs[1]) if prefs and prefs[1] else ['Any'],
                'remote': bool(prefs[2]) if prefs else True,
                'experienceLevel': {prefs[3]: True} if prefs and prefs[3] else {'entry': True, 'associate': False},
                'skills': safe_split_to_list(prefs[5]) if prefs and prefs[5] else [],
            }
            
            # Add other default settings
            default_settings = {
                'uploads': {'resume': '', 'cover_letter': ''},
                'outputFileDirectory': os.getcwd(),
                'checkJobUrls': [],
                'date_range': '1',
                'salary': '',
                'distance': '25',
                'experienceExclude': [],
                'preferredCompanies': [],
                'blacklistCompanies': [],
                'appliedJobUrl': []
            }
            config.update(default_settings)
            return config
            
        except Exception as e:
            print(f"Error loading user config: {e}")
            return None

    def get_default_config(self):
        """Return default configuration"""
        return {
            'email': os.environ.get('LINKEDIN_EMAIL', ''),
            'password': os.environ.get('LINKEDIN_PASSWORD', ''),
            'openaiApiKey': os.environ.get('OPENAI_API_KEY', ''),
            'positions': ['Software Engineer', 'AI Engineer'],
            'locations': ['Any'],
            'remote': True,
            'experienceLevel': {'entry': True, 'associate': False},
            'jobTypes': {'full-time': True, 'contract': True},
            'salaryMinimum': 65000
        }
    
    def set_status_callback(self, callback):
        """Set callback function for status updates"""
        self.status_callback = callback
    
    def update_status(self, status, progress=None, current_task=None, applications_submitted=None):
        """Update status in database and call callback if set"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update or insert agent status
            cursor.execute('''
                INSERT OR REPLACE INTO agent_status 
                (user_id, status, progress, current_task, applications_submitted, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                self.user_id, status, progress or 0, 
                current_task or '', applications_submitted or 0,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            if self.status_callback:
                self.status_callback({
                    'status': status,
                    'progress': progress,
                    'current_task': current_task,
                    'applications_submitted': applications_submitted
                })
                
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def init_browser_with_retry(self):
        """Initialize browser with comprehensive error handling and broken pipe prevention"""
        print("🌐 BROWSER INIT: Starting browser initialization with enhanced error handling...")
        
        def _launch(user_data_dir):
            """Launch Chrome with enhanced error handling and broken pipe prevention"""
            print(f"🚀 BROWSER INIT: Launching Chrome with user directory: {user_data_dir}")
            
            options = Options()
            # Enhanced Chrome options for stability
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")  # Faster loading
            options.add_argument("--disable-javascript")  # Sometimes helps with stability
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-default-apps")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-translate")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-features=TranslateUI")
            options.add_argument("--disable-ipc-flooding-protection")
            options.add_argument(f"--user-data-dir={user_data_dir}")
            
            # Process management arguments to prevent broken pipes
            options.add_argument("--no-zygote")
            options.add_argument("--disable-background-networking")
            options.add_argument("--disable-sync")
            options.add_argument("--metrics-recording-only")
            options.add_argument("--safebrowsing-disable-auto-update")
            
            # Set window size and position for visibility
            options.add_argument("--window-size=1400,900")
            options.add_argument("--window-position=100,100")
            
            print("🔧 BROWSER INIT: Chrome options configured for maximum stability")
            
            try:
                print("🚀 BROWSER INIT: Creating WebDriver instance...")
                service = Service()
                driver = webdriver.Chrome(service=service, options=options)
                
                # Test connection immediately to catch broken pipe early
                print("🔍 BROWSER INIT: Testing browser connection...")
                driver.get("about:blank")
                print("✅ BROWSER INIT: Browser connection test successful")
                
                # Enhanced process monitoring
                print("🔧 BROWSER INIT: Setting up process monitoring...")
                driver.set_page_load_timeout(30)
                driver.implicitly_wait(10)
                
                print("🔧 BROWSER INIT: Configuring browser for LinkedIn automation...")
                
            except SessionNotCreatedException as e:
                print(f"❌ BROWSER INIT: Session creation failed: {e}")
                if "chrome not reachable" in str(e).lower():
                    print("🔄 BROWSER INIT: Chrome process issue detected - will retry")
                raise e
            except Exception as e:
                print(f"❌ BROWSER INIT: Browser launch failed: {e}")
                print(f"🚨 BROWSER INIT: Error type: {type(e).__name__}")
                raise e
            
            # macOS-specific visibility handling with error protection
            if os.name == 'posix' and 'darwin' in os.uname().sysname.lower():
                print("🍎 BROWSER INIT: Detected macOS - applying visibility enhancements...")
                try:
                    import subprocess
                    import time
                    
                    # Wait for Chrome to fully initialize
                    time.sleep(2)
                    
                    print("🖥️ BROWSER INIT: Making Chrome visible and active...")
                    
                    # Enhanced visibility with error handling
                    try:
                        subprocess.run(['osascript', '-e', 'tell application "Google Chrome" to activate'], 
                                      capture_output=True, timeout=10)
                        print("✅ BROWSER INIT: Chrome activation successful")
                    except subprocess.TimeoutExpired:
                        print("⚠️ BROWSER INIT: Chrome activation timeout - continuing anyway")
                    except Exception as vis_error:
                        print(f"⚠️ BROWSER INIT: Chrome activation error: {vis_error}")
                    
                    # Set window bounds with error handling
                    try:
                        subprocess.run(['osascript', '-e', '''
                            tell application "Google Chrome"
                                activate
                                if (count of windows) > 0 then
                                    set bounds of window 1 to {100, 100, 1400, 900}
                                    set frontmost to true
                                end if
                            end tell
                        '''], capture_output=True, timeout=10)
                        print("✅ BROWSER INIT: Chrome window positioning successful")
                    except Exception as bound_error:
                        print(f"⚠️ BROWSER INIT: Chrome window positioning error: {bound_error}")
                    
                    print("🎉 BROWSER INIT: macOS visibility enhancements completed")
                    
                except Exception as mac_error:
                    print(f"⚠️ BROWSER INIT: macOS-specific setup failed: {mac_error}")
                    print("🔄 BROWSER INIT: Continuing with standard setup...")
                
            return driver

        # Try the default directory first with enhanced error handling
        default_dir = os.path.join(os.getcwd(), f"chrome_bot_user_{self.user_id}")
        print(f"🔧 BROWSER INIT: Attempting to use Chrome directory: {default_dir}")
        
        max_attempts = 5  # Increased retry attempts
        last_error = None
        
        for attempt in range(max_attempts):
            print(f"🔄 BROWSER INIT: Attempt {attempt + 1}/{max_attempts}")
            
            try:
                if attempt == 0:
                    # First attempt: Use default directory
                    os.makedirs(default_dir, exist_ok=True)
                    chrome_dir = default_dir
                    print(f"🔧 BROWSER INIT: Using default Chrome directory: {chrome_dir}")
                else:
                    # Subsequent attempts: Use temporary directories
                    import uuid
                    temp_suffix = f"_{uuid.uuid4().hex[:6]}"
                    chrome_dir = f"{default_dir}{temp_suffix}"
                    os.makedirs(chrome_dir, exist_ok=True)
                    print(f"🔧 BROWSER INIT: Using temporary Chrome directory: {chrome_dir}")
                
                # Clean up any leftover Chrome processes before retry
                if attempt > 0:
                    print("🧹 BROWSER INIT: Cleaning up Chrome processes...")
                    try:
                        import subprocess
                        subprocess.run(['pkill', '-f', 'chrome'], capture_output=True, timeout=10)
                        time.sleep(2)  # Wait for cleanup
                    except Exception as cleanup_error:
                        print(f"⚠️ BROWSER INIT: Chrome cleanup warning: {cleanup_error}")
                
                # Launch browser with current directory
                driver = _launch(chrome_dir)
                
                # Additional connection validation
                print("🔍 BROWSER INIT: Performing extended connection validation...")
                try:
                    driver.get("https://www.google.com")
                    print("✅ BROWSER INIT: Google connectivity test passed")
                    
                    # Test LinkedIn access
                    driver.get("https://www.linkedin.com")
                    print("✅ BROWSER INIT: LinkedIn connectivity test passed")
                    
                    print(f"🎉 BROWSER INIT: Browser launched successfully on attempt {attempt + 1}")
                    print(f"🌐 BROWSER INIT: Chrome directory: {chrome_dir}")
                    print(f"🔗 BROWSER INIT: Browser session ID: {driver.session_id}")
                    return driver
                    
                except Exception as validation_error:
                    print(f"❌ BROWSER INIT: Connection validation failed: {validation_error}")
                    try:
                        driver.quit()
                    except:
                        pass
                    raise validation_error
                
            except SessionNotCreatedException as session_error:
                last_error = session_error
                print(f"❌ BROWSER INIT: Session creation failed on attempt {attempt + 1}: {session_error}")
                
                if "chrome not reachable" in str(session_error).lower():
                    print("🔄 BROWSER INIT: Chrome process issue - will retry with clean slate")
                elif "port" in str(session_error).lower():
                    print("🔄 BROWSER INIT: Port conflict detected - will retry")
                else:
                    print(f"🔄 BROWSER INIT: Unspecified session error - will retry")
                
                # Wait before retry
                wait_time = (attempt + 1) * 2
                print(f"⏱️ BROWSER INIT: Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                
            except Exception as general_error:
                last_error = general_error
                print(f"❌ BROWSER INIT: General error on attempt {attempt + 1}: {general_error}")
                print(f"🚨 BROWSER INIT: Error type: {type(general_error).__name__}")
                
                # Wait before retry
                wait_time = (attempt + 1) * 2
                print(f"⏱️ BROWSER INIT: Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        # All attempts failed
        print(f"❌ BROWSER INIT: CRITICAL FAILURE - All {max_attempts} attempts failed")
        print(f"🚨 BROWSER INIT: Last error: {last_error}")
        print(f"🚨 BROWSER INIT: Last error type: {type(last_error).__name__}")
        
        # Try one final fallback with minimal options
        print("🆘 BROWSER INIT: Attempting emergency fallback launch...")
        try:
            fallback_dir = os.path.join(os.getcwd(), f"chrome_emergency_{int(time.time())}")
            os.makedirs(fallback_dir, exist_ok=True)
            
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument(f"--user-data-dir={fallback_dir}")
            options.add_argument("--window-size=1400,900")
            
            service = Service()
            driver = webdriver.Chrome(service=service, options=options)
            driver.get("about:blank")
            
            print("🎉 BROWSER INIT: Emergency fallback successful!")
            return driver
            
        except Exception as fallback_error:
            print(f"❌ BROWSER INIT: Emergency fallback also failed: {fallback_error}")
            
        raise Exception(f"Browser initialization failed after {max_attempts} attempts. Last error: {last_error}")

    def init_browser(self):
        """Initialize browser - compatibility wrapper"""
        return self.init_browser_with_retry()
    
    def save_application_to_db(self, job_title, company, location, job_url, status='applied'):
        """Save application to database and use quota - Enhanced version"""
        try:
            application_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            print(f"🔄 STARTING DATABASE SAVE: {job_title} at {company}")
            print(f"🔄 ===============================================")
            print(f"🔄 📊 DATABASE OPERATION DETAILS:")
            print(f"🔄    👤 User ID: {self.user_id}")
            print(f"🔄    🆔 Application ID: {application_id}")
            print(f"🔄    📂 Database path: {self.db_path}")
            print(f"🔄    💼 Job Title: {job_title}")
            print(f"🔄    🏢 Company: {company}")
            print(f"🔄    📍 Location: {location}")
            print(f"🔄    🔗 Job URL: {job_url}")
            print(f"🔄    📊 Status: {status}")
            print(f"🔄    🕐 Timestamp: {timestamp}")
            print(f"🔄 ===============================================")
            
            # Check if database file exists
            if not os.path.exists(self.db_path):
                print(f"🔄 ⚠️ WARNING: Database file doesn't exist at {self.db_path}")
                print(f"🔄 📁 Creating database directory if needed...")
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            else:
                print(f"🔄 ✅ Database file exists at {self.db_path}")
            
            # ALWAYS save to the main job_applications table that the dashboard reads from
            print(f"🔄 🔌 Opening database connection...")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            print(f"🔄 ✅ Database connection established")
            
            # First check if table exists and has correct structure
            print(f"🔄 🔍 Checking if job_applications table exists...")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='job_applications'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                print("🔄 ⚠️ WARNING: job_applications table doesn't exist, creating it...")
                cursor.execute('''
                    CREATE TABLE job_applications (
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
                print("🔄 ✅ Created job_applications table successfully")
            else:
                print("🔄 ✅ job_applications table exists")
            
            # Show table structure
            print(f"🔄 📋 Checking table structure...")
            cursor.execute("PRAGMA table_info(job_applications)")
            columns = cursor.fetchall()
            print(f"🔄 📋 Table columns: {[col[1] for col in columns]}")
            
            print(f"🔄 💾 Inserting into job_applications table...")
            insert_query = '''
                INSERT INTO job_applications 
                (id, user_id, job_title, company, location, job_url, status, applied_at, ai_generated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            insert_data = (
                application_id, self.user_id, job_title, company, location,
                job_url, status, timestamp, True
            )
            
            print(f"🔄 📝 SQL Query: {insert_query}")
            print(f"🔄 📊 Insert Data: {insert_data}")
            
            cursor.execute(insert_query, insert_data)
            print(f"🔄 ✅ INSERT statement executed successfully")
            
            # Verify insertion
            print(f"🔄 🔍 Verifying record insertion...")
            cursor.execute('SELECT COUNT(*) FROM job_applications WHERE id = ?', (application_id,))
            count = cursor.fetchone()[0]
            
            if count == 1:
                print(f"🔄 ✅ DATABASE VERIFICATION: Record inserted successfully")
                print(f"🔄 🎯 Verification count: {count}")
            else:
                print(f"🔄 ❌ DATABASE ERROR: Record not found after insertion")
                print(f"🔄 🚨 Verification count: {count} (should be 1)")
                return None
            
            print(f"🔄 💾 Committing transaction...")
            conn.commit()
            print(f"🔄 ✅ DATABASE COMMIT: Transaction committed successfully")
            
            # Check total applications for this user
            print(f"🔄 📊 Checking total applications for user...")
            cursor.execute('SELECT COUNT(*) FROM job_applications WHERE user_id = ?', (self.user_id,))
            total_apps = cursor.fetchone()[0]
            print(f"🔄 📊 TOTAL APPLICATIONS: User {self.user_id} now has {total_apps} applications")
            
            # Get recent applications for verification
            print(f"🔄 📋 Getting recent applications for verification...")
            cursor.execute('''
                SELECT job_title, company, applied_at 
                FROM job_applications 
                WHERE user_id = ? 
                ORDER BY applied_at DESC 
                LIMIT 5
            ''', (self.user_id,))
            recent_apps = cursor.fetchall()
            print(f"🔄 📋 Recent applications:")
            for i, app in enumerate(recent_apps, 1):
                print(f"🔄    {i}. {app[1]} - {app[0]} ({app[2]})")
            
            print(f"🔄 🔌 Closing database connection...")
            conn.close()
            print(f"🔄 ✅ Database connection closed")
            
            print(f"🔄 ===============================================")
            print(f"🔄 🎉 DATABASE SAVE COMPLETED SUCCESSFULLY!")
            print(f"🔄 📊 Application ID: {application_id}")
            print(f"🔄 📈 Total user applications: {total_apps}")
            print(f"🔄 ===============================================")
            
            return application_id
            
        except Exception as e:
            print(f"🔄 ❌ CRITICAL DATABASE ERROR: {e}")
            print(f"🔄 🚨 Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            print(f"🔄 ===============================================")
            return None
    
    def log_activity(self, action, details, status='info', metadata=None):
        """Log activity to database for live updates - Enhanced version"""
        try:
            # Use enhanced activity logger if available
            if hasattr(self, 'activity_logger') and callable(self.activity_logger):
                # Format activity for enhanced manager: log_activity(user_id, activity, metadata)
                activity_text = f"{action}: {details}"
                enhanced_metadata = metadata or {}
                enhanced_metadata.update({
                    'status': status,
                    'action': action,
                    'details': details,
                    'session_id': getattr(self, 'session_id', None),
                    'timestamp': datetime.now().isoformat()
                })
                self.activity_logger(self.user_id, activity_text, enhanced_metadata)
            else:
                # Fallback to legacy method
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO activity_log (user_id, action, details, status, metadata)
                    VALUES (?, ?, ?, ?, ?)
                ''', (self.user_id, action, details, status, json.dumps(metadata or {})))
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Failed to log activity: {e}")

    def check_quota_remaining(self):
        """Check if we can still apply to more jobs today"""
        if hasattr(self, 'daily_quota') and self.applications_today >= self.daily_quota:
            self.log_activity("Quota Reached", f"Daily quota of {self.daily_quota} applications reached", "warning")
            return False
        return True

    def check_timeout_and_restart(self):
        """Check if bot has been inactive for too long and restart if needed"""
        time_since_last_application = datetime.now() - self.last_application_time
        timeout_seconds = self.timeout_minutes * 60
        
        if time_since_last_application.total_seconds() > timeout_seconds:
            if self.restart_count < self.max_restarts:
                print(f"⏰ TIMEOUT DETECTED: No application in {self.timeout_minutes} minutes")
                print(f"🔄 Auto-restarting bot (attempt {self.restart_count + 1}/{self.max_restarts})")
                self.log_activity("Timeout", f"Auto-restarting bot after {self.timeout_minutes} minutes of inactivity", "warning")
                
                # Increment restart count
                self.restart_count += 1
                
                # Reset timeout timer
                self.last_application_time = datetime.now()
                
                print(f"✅ Bot restart initiated (attempt {self.restart_count})")
                return True
            else:
                print(f"❌ MAX RESTARTS REACHED: {self.max_restarts} restarts attempted")
                self.log_activity("Fatal", f"Bot stopped after {self.max_restarts} auto-restarts", "error")
                self.stop_requested = True
                return False
        return False

    def run_applications(self, max_applications=10, continuous=False):
        """Run job applications with web platform integration"""
        self.update_status('running', 0, 'Initializing browser and LinkedIn session...')
        self.log_activity("Bot Starting", "🚀 Initializing LinkedIn Easy Apply bot session", "info", {
            'max_applications': max_applications,
            'continuous_mode': continuous
        })
        
        browser = None
        bot = None
        
        try:
            # Initialize browser
            browser = self.init_browser()
            self.update_status('running', 10, 'Browser initialized, logging into LinkedIn...')
            self.log_activity("Browser", "🌐 Chrome browser initialized with stealth settings", "success")
            
            # Initialize bot
            if LinkedinEasyApply is None:
                raise Exception("LinkedIn bot functionality is not available in this environment. Please run locally for full bot features.")
            
            bot = LinkedinEasyApply(self.config, browser)
            bot.fast_mode = False
            bot.continuous_mode = continuous
            
            # Set up bot activity logging
            bot.activity_logger = self.log_activity
            
            # Login
            self.update_status('running', 20, 'Logging into LinkedIn...')
            self.log_activity("LinkedIn Login", f"🔐 Connecting to LinkedIn with email: {self.config.get('email', 'unknown')}", "info")
            
            bot.login()
            bot.security_check()
            
            self.update_status('running', 30, 'LinkedIn login successful, starting job search...')
            self.log_activity("Login Success", "✅ Successfully logged into LinkedIn and passed security checks", "success")
            
            if continuous:
                return self._run_continuous_applications(bot, max_applications)
            else:
                return self._run_batch_applications(bot, max_applications)
                
        except Exception as e:
            self.update_status('error', 0, f'Error: {str(e)}')
            raise e
        finally:
            if browser:
                try:
                    browser.quit()
                except:
                    pass
    
    def _run_batch_applications(self, bot, max_applications):
        """Run a batch of applications"""
        applications_made = 0
        
        try:
            self.log_activity("Job Search", f"🎯 Starting job search for {max_applications} applications", "info", {
                'target_applications': max_applications,
                'positions': self.config.get('positions', []),
                'locations': self.config.get('locations', [])
            })
            
            # Override the bot's write_to_file method to use our database
            original_write_to_file = bot.write_to_file
            print(f"🔧 HOOKING INTO BOT'S write_to_file METHOD")
            
            def enhanced_write_to_file(company, job_title, link, location, search_location):
                print(f"🎯 ENHANCED_WRITE_TO_FILE CALLED!")
                print(f"🎯 ===============================================")
                print(f"🎯 📊 APPLICATION DETAILS:")
                print(f"🎯    🏢 Company: {company}")
                print(f"🎯    💼 Job Title: {job_title}")
                print(f"🎯    📍 Location: {location}")
                print(f"🎯    🔗 URL: {link}")
                print(f"🎯    🎯 Search Location: {search_location}")
                print(f"🎯    👤 User ID: {self.user_id}")
                print(f"🎯    🕐 Timestamp: {datetime.now()}")
                print(f"🎯 ===============================================")
                
                # Update last application time for timeout tracking
                self.last_application_time = datetime.now()
                print(f"⏰ Updated last application time: {self.last_application_time}")
                
                # Check quota before processing application
                print(f"🎯 🔍 CHECKING DAILY QUOTA...")
                if not self.check_quota_remaining():
                    print(f"🎯 ❌ QUOTA EXCEEDED - Cannot process application")
                    print(f"🎯 ⚠️ Daily limit reached: {self.daily_quota} applications")
                    self.log_activity("Quota Exceeded", f"❌ Cannot apply to {job_title} at {company} - daily quota reached", "warning")
                    return
                
                print(f"🎯 ✅ QUOTA CHECK PASSED - Processing application...")
                print(f"🎯 📈 Applications today: {self.applications_today}/{self.daily_quota}")
                
                # Log application attempt
                print(f"🎯 📝 LOGGING APPLICATION ACTIVITY...")
                self.log_activity("Application Submit", f"📝 Applied to {job_title} at {company}", "success", {
                    'job_title': job_title,
                    'company': company,
                    'location': location,
                    'job_url': link,
                    'search_location': search_location,
                    'user_id': self.user_id,
                    'session_id': self.session_id
                })
                print(f"🎯 ✅ Activity logged successfully")
                
                # Save to our database
                print(f"🎯 💾 CALLING save_application_to_db...")
                print(f"🎯 📊 Database parameters:")
                print(f"🎯    - Job Title: {job_title}")
                print(f"🎯    - Company: {company}")
                print(f"🎯    - Location: {location}")
                print(f"🎯    - Job URL: {link}")
                print(f"🎯    - User ID: {self.user_id}")
                
                try:
                    application_id = self.save_application_to_db(job_title, company, location, link)
                    if application_id:
                        nonlocal applications_made
                        applications_made += 1
                        print(f"🎯 🎉 APPLICATION SAVED SUCCESSFULLY!")
                        print(f"🎯 📊 Application ID: {application_id}")
                        print(f"🎯 📈 Total applications in this session: {applications_made}")
                        print(f"🎯 🎯 SUCCESS RATE: 100% for this application!")
                        
                        # Update session counters
                        self.session_count += 1
                        self.applications_today += 1
                        
                        print(f"🎯 📊 UPDATED COUNTERS:")
                        print(f"🎯    - Session count: {self.session_count}")
                        print(f"🎯    - Applications today: {self.applications_today}")
                        print(f"🎯    - Total in this batch: {applications_made}")
                        
                        # Also call original method for CSV backup
                        print(f"🎯 📄 Calling original write_to_file for CSV backup...")
                        try:
                            original_write_to_file(company, job_title, link, location, search_location)
                            print(f"🎯 ✅ CSV backup completed successfully")
                        except Exception as csv_error:
                            print(f"🎯 ⚠️ CSV backup failed: {csv_error}")
                            # Don't fail the whole process for CSV issues
                    else:
                        print(f"🎯 ❌ APPLICATION SAVE FAILED - No application ID returned")
                        print(f"🎯 🚨 This is a critical database issue!")
                        self.log_activity("Application Failed", f"❌ Failed to save application to {job_title} at {company}", "error")
                except Exception as save_error:
                    print(f"🎯 ❌ CRITICAL ERROR in save_application_to_db: {save_error}")
                    print(f"🎯 🚨 Database connection or query failed!")
                    import traceback
                    traceback.print_exc()
                    self.log_activity("Application Failed", f"❌ Database error saving {job_title} at {company}: {save_error}", "error")
                    
                print(f"🎯 ===============================================")
                print(f"🎯 🎉 ENHANCED_WRITE_TO_FILE COMPLETED!")
                print(f"🎯 ===============================================")
            
            bot.write_to_file = enhanced_write_to_file
            print(f"✅ BOT WRITE_TO_FILE METHOD SUCCESSFULLY OVERRIDDEN")
            
            # Override bot's print statements to log activities
            original_print = print
            def log_print(*args, **kwargs):
                message = ' '.join(str(arg) for arg in args)
                # Log interesting bot messages
                if any(keyword in message.lower() for keyword in ['starting the search', 'going to job page', 'application sent', 'failed to apply']):
                    if 'starting the search' in message.lower():
                        self.log_activity("Search Starting", f"🔍 {message}", "info")
                    elif 'going to job page' in message.lower():
                        self.log_activity("Page Navigation", f"📄 {message}", "info")
                    elif 'application sent' in message.lower():
                        self.log_activity("Application Success", f"✅ {message}", "success")
                    elif 'failed to apply' in message.lower():
                        self.log_activity("Application Error", f"❌ {message}", "error")
                # Still call original print
                original_print(*args, **kwargs)
            
            # Temporarily replace print for bot logging
            import builtins
            builtins.print = log_print
            
            try:
                # Start applying
                applications_made = bot.start_applying(max_applications=max_applications)
            finally:
                # Restore original print
                builtins.print = original_print
            
            self.log_activity("Session Complete", f"🎉 Batch completed successfully! Applied to {applications_made} jobs", "success", {
                'applications_made': applications_made,
                'success_rate': (applications_made / max_applications * 100) if max_applications > 0 else 0
            })
            
            self.update_status(
                'completed', 100, 
                f'Batch completed successfully. Applied to {applications_made} jobs.',
                applications_made
            )
            
            return applications_made
            
        except Exception as e:
            error_msg = str(e)
            self.log_activity("Batch Error", f"❌ Error during batch applications: {error_msg}", "error", {
                'error_details': error_msg,
                'applications_completed': applications_made
            })
            self.update_status('error', 0, f'Error during batch applications: {error_msg}')
            raise e
    
    def _run_continuous_applications(self, bot, max_applications):
        """Run continuous applications"""
        applications_made = 0
        
        try:
            # Initialize timeout tracking
            self.last_application_time = datetime.now()
            print(f"⏰ Timeout tracking initialized - will restart if no application in {self.timeout_minutes} minutes")
            
            while not self.stop_requested and applications_made < max_applications:
                # Check for timeout and restart if needed
                if self.check_timeout_and_restart():
                    print("🔄 Bot restarted due to timeout, continuing...")
                    continue
                
                # Apply to one job at a time
                batch_applications = bot.start_applying(max_applications=1)
                
                if batch_applications > 0:
                    applications_made += batch_applications
                    progress = int((applications_made / max_applications) * 100)
                    
                    self.update_status(
                        'running', progress,
                        f'Applied to {applications_made} jobs. Waiting before next application...',
                        applications_made
                    )
                    
                    # Delay between applications
                    delay_minutes = random.uniform(1, 3)
                    delay_seconds = delay_minutes * 60
                    
                    # Sleep in chunks to allow for interruption
                    sleep_chunks = int(delay_seconds / 10)
                    for i in range(sleep_chunks):
                        if self.stop_requested:
                            break
                        time.sleep(10)
                        
                        # Update status with countdown
                        remaining = delay_seconds - ((i + 1) * 10)
                        self.update_status(
                            'running', progress,
                            f'Waiting {remaining:.0f} seconds before next application...',
                            applications_made
                        )
                else:
                    # No applications made, short delay before trying again
                    self.update_status(
                        'running', 
                        int((applications_made / max_applications) * 100),
                        'No suitable jobs found, searching for more...',
                        applications_made
                    )
                    time.sleep(30)
            
            if self.stop_requested:
                self.update_status(
                    'stopped', 
                    int((applications_made / max_applications) * 100),
                    f'Agent stopped by user. Applied to {applications_made} jobs.',
                    applications_made
                )
            else:
                self.update_status(
                    'completed', 100,
                    f'Continuous application completed. Applied to {applications_made} jobs.',
                    applications_made
                )
            
            return applications_made
            
        except Exception as e:
            self.update_status('error', 0, f'Error during continuous applications: {str(e)}')
            raise e
    
    def stop_applications(self):
        """Stop the application process"""
        self.stop_requested = True
        self.update_status('stopping', None, 'Stop requested, finishing current application...')
    
    def get_status(self):
        """Get current status from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT status, progress, current_task, applications_submitted, updated_at
                FROM agent_status 
                WHERE user_id = ?
                ORDER BY updated_at DESC 
                LIMIT 1
            ''', (self.user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'status': row[0],
                    'progress': row[1],
                    'current_task': row[2],
                    'applications_submitted': row[3],
                    'updated_at': row[4]
                }
            else:
                return {
                    'status': 'idle',
                    'progress': 0,
                    'current_task': 'Agent not running',
                    'applications_submitted': 0
                }
                
        except Exception as e:
            print(f"Error getting status: {e}")
            return {
                'status': 'error',
                'progress': 0,
                'current_task': f'Error: {str(e)}',
                'applications_submitted': 0
            }

def create_agent_status_table():
    """Create agent_status table if it doesn't exist"""
    try:
        conn = sqlite3.connect('backend/easyapply.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_status (
                user_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                progress INTEGER DEFAULT 0,
                current_task TEXT,
                applications_submitted INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error creating agent_status table: {e}")

if __name__ == "__main__":
    import sys
    import argparse
    
    # Create the agent_status table
    create_agent_status_table()
    
    # Parse command line arguments for enhanced bot manager integration
    parser = argparse.ArgumentParser(description='LinkedIn Easy Apply Bot')
    parser.add_argument('--config', type=str, help='JSON configuration string')
    parser.add_argument('--user-id', type=str, help='User ID')
    parser.add_argument('--daily-quota', type=int, default=5, help='Daily application quota')
    
    args = parser.parse_args()
    
    # Get user ID from args or environment
    user_id = args.user_id or os.getenv('USER_ID')
    if not user_id:
        print("❌ No user ID provided via --user-id argument or USER_ID environment variable")
        sys.exit(1)
    
    # Parse configuration if provided
    config_override = None
    if args.config:
        try:
            config_override = json.loads(args.config)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON configuration: {e}")
            sys.exit(1)
    
    # Set daily quota
    daily_quota = args.daily_quota or int(os.getenv('DAILY_QUOTA', '5'))
    
    print(f"🚀 Starting Enhanced LinkedIn Bot for user: {user_id}")
    print(f"📊 Daily quota: {daily_quota}")
    
    try:
        # Create and run the bot
        bot = WebPlatformLinkedInBot(user_id, config_override)
        
        # Run applications continuously until quota is reached
        while bot.applications_today < daily_quota:
            remaining = daily_quota - bot.applications_today
            batch_size = min(5, remaining)  # Apply to max 5 jobs per batch
            
            print(f"🎯 Running batch: {batch_size} applications (remaining quota: {remaining})")
            result = bot.run_applications(max_applications=batch_size, continuous=False)
            
            if result == 0:
                print("⏸️ No suitable jobs found, waiting before next attempt...")
                time.sleep(300)  # Wait 5 minutes before trying again
            
            # Check if quota reached
            if bot.applications_today >= daily_quota:
                print(f"🎉 Daily quota of {daily_quota} applications reached!")
                break
        
        print("✅ Bot session completed successfully")
        
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        sys.exit(1) 