#!/usr/bin/env python3

import os
import time
import random
import yaml
import argparse
import requests
import sqlite3
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Add the main directory to path to import linkedineasyapply
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from linkedineasyapply import LinkedinEasyApply
except ImportError:
    print("❌ Error: linkedineasyapply module not found")
    print("   Make sure the linkedineasyapply.py file is in the same directory")
    sys.exit(1)

class UserEasyApplyBot:
    def __init__(self, user_id, config_path):
        self.user_id = user_id
        self.config_path = config_path
        self.config = self.load_config()
        self.applications_today = 0
        self.session_count = 0
        self.start_time = datetime.now()
        self.stop_requested = False
        
    def load_config(self):
        with open(self.config_path, 'r') as stream:
            return yaml.safe_load(stream)
    
    def log_application(self, job_title, company, status):
        """Log application to the database"""
        try:
            # Add applications to the database
            conn = sqlite3.connect('backend/easyapply.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO job_applications 
                (user_id, job_title, company, status, applied_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.user_id, job_title, company, status, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            print(f"📝 Logged application: {job_title} at {company} - {status}")
        except Exception as e:
            print(f"⚠️ Failed to log application: {str(e)}")
    
    def init_browser(self):
        """Initialize Chrome browser with advanced stealth features"""
        from selenium.common.exceptions import SessionNotCreatedException
        import uuid, shutil

        def _launch(chrome_user_dir: str):
            # Use simple, reliable stealth configuration
            from stealth_config_fixed import create_simple_browser
            return create_simple_browser(fresh_session=True, user_data_dir=chrome_user_dir)

        # Create user-specific chrome directory
        chrome_user_dir = os.path.join(os.getcwd(), f"chrome_bot_user_{self.user_id}")
        
        try:
            return _launch(chrome_user_dir)
        
        except SessionNotCreatedException as e:
            print(f"⚠️ Failed to create browser session: {e}")
            # Retry with temporary directory
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix=f"chrome_bot_temp_{self.user_id}_")
            print(f"🔄 Retrying with temp directory: {temp_dir}")
            return _launch(temp_dir)
    
    def should_continue(self):
        """Check if we should continue applying"""
        return not self.stop_requested
    
    def run_continuous_applications(self):
        """Run continuous applications with delays"""
        print(f"\n🔄 EASY APPLY BOT STARTED FOR USER: {self.user_id}")
        print(f"⏰ Started at: {datetime.now().strftime('%I:%M %p')}")
        print(f"👤 LinkedIn Email: {self.config.get('email')}")
        print(f"🎯 Positions: {', '.join(self.config.get('positions', []))}")
        print(f"📍 Locations: {', '.join(self.config.get('locations', []))}")
        
        browser = None
        bot = None
        
        try:
            # Initialize browser
            print("🔧 Initializing browser...")
            browser = self.init_browser()
            
            # Initialize bot
            bot = LinkedinEasyApply(self.config, browser)
            bot.fast_mode = False
            bot.continuous_mode = True
            
            # Login
            print("🔐 Logging in to LinkedIn...")
            try:
                bot.login()
                print("✅ Successfully logged into LinkedIn")
                
                print("🔒 Performing security check...")
                bot.security_check()
                print("✅ Security check completed")
                
                # Verify we're actually logged in by checking the current URL
                current_url = bot.browser.current_url
                if "feed" in current_url or "search" in current_url:
                    print("✅ Login verification successful - ready to start job search")
                else:
                    print(f"⚠️ Login verification uncertain - current URL: {current_url}")
                    
            except Exception as e:
                print(f"❌ Login failed: {str(e)}")
                print("🔧 This could be due to:")
                print("   - Incorrect LinkedIn credentials")
                print("   - LinkedIn requiring additional verification")
                print("   - Network connectivity issues")
                print("   - LinkedIn blocking automated access")
                raise e
            
            print("🎯 Starting continuous job applications...")
            
            while self.should_continue():
                try:
                    # Apply to jobs
                    applications_made = bot.start_applying(max_applications=1)
                    
                    if applications_made > 0:
                        self.applications_today += applications_made
                        print(f"✅ Application #{self.applications_today} completed at {datetime.now().strftime('%I:%M %p')}")
                        
                        # Log to database (this would need to be implemented in the bot)
                        self.log_application("Job Title", "Company", "applied")
                        
                        # 1-3 minute delay between applications
                        delay_minutes = random.uniform(1, 3)
                        delay_seconds = delay_minutes * 60
                        print(f"⏱️  Waiting {delay_minutes:.1f} minutes before next application...")
                        
                        # Sleep in chunks to allow for interruption
                        sleep_chunks = int(delay_seconds / 10)
                        for i in range(sleep_chunks):
                            if not self.should_continue():
                                break
                            time.sleep(10)
                        
                        # Sleep any remaining time
                        remaining_sleep = delay_seconds - (sleep_chunks * 10)
                        if remaining_sleep > 0 and self.should_continue():
                            time.sleep(remaining_sleep)
                    else:
                        print("⏭️  No applications made this round, waiting...")
                        time.sleep(60)  # Wait 1 minute before trying again
                        
                except KeyboardInterrupt:
                    print("\n🛑 Stopping applications...")
                    self.stop_requested = True
                    break
                except Exception as e:
                    print(f"❌ Application error: {str(e)}")
                    print("⏸️  Waiting 2 minutes before retrying...")
                    time.sleep(120)
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping applications...")
            self.stop_requested = True
        except Exception as e:
            print(f"❌ Fatal error: {str(e)}")
        finally:
            # Clean up
            if browser:
                try:
                    browser.quit()
                    print("🔧 Browser closed")
                except:
                    pass
            
            # Clean up temporary user data directory
            try:
                import shutil
                user_dirs = [
                    f'chrome_bot_user_{self.user_id}',
                    f'chrome_bot_tmp_user_{self.user_id}_*'
                ]
                for pattern in user_dirs:
                    for temp_dir in os.listdir('.'):
                        if temp_dir.startswith(pattern.replace('*', '')):
                            shutil.rmtree(temp_dir, ignore_errors=True)
                print("🧹 Temporary files cleaned up")
            except:
                pass
            
            print(f"\n📊 Session Summary for User {self.user_id}:")
            print(f"   Total applications: {self.applications_today}")
            print(f"   Duration: {datetime.now() - self.start_time}")
            print(f"   Ended at: {datetime.now().strftime('%I:%M %p')}")
    
    def stop_applications(self):
        """Stop continuous applications"""
        self.stop_requested = True
        print("🛑 Stop requested - applications will finish current job and stop...")

def main():
    parser = argparse.ArgumentParser(description='User-specific LinkedIn Easy Apply Bot')
    parser.add_argument('--user-id', required=True, help='User ID for the bot')
    parser.add_argument('--config', required=True, help='Path to user config file')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.config):
        print(f"❌ Config file not found: {args.config}")
        sys.exit(1)
    
    print("=" * 60)
    print(f"🚀 LINKEDIN EASY APPLY BOT - USER {args.user_id}")
    print("=" * 60)
    print("🛡️  Full safety features enabled")
    print("⏰ 1-3 minute delays between applications")
    print("🔄 Continuous application mode")
    print("=" * 60)
    
    bot = UserEasyApplyBot(args.user_id, args.config)
    
    try:
        bot.run_continuous_applications()
    except KeyboardInterrupt:
        print("\n🛑 Stopping applications...")
        bot.stop_applications()
    except Exception as e:
        print(f"❌ Bot error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 