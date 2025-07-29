#!/usr/bin/env python3

import os
import time
import random
import yaml
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from linkedineasyapply import LinkedinEasyApply

class ContinuousApplyBot:
    def __init__(self):
        self.config = self.load_config()
        self.applications_today = 0
        self.session_count = 0
        self.start_time = datetime.now()
        self.stop_requested = False  # Flag to stop continuous application
        self.fast_mode = False  # Use all safety features
        
    def load_config(self):
        with open('config.yaml', 'r') as stream:
            return yaml.safe_load(stream)
    
    def init_browser(self):
        """Initialize Chrome browser with simple stealth features and retry if user-data-dir is locked"""
        from selenium.common.exceptions import SessionNotCreatedException
        import uuid, shutil

        def _launch(chrome_user_dir: str):
            # Use simple, reliable stealth configuration
            from stealth_config_fixed import create_simple_browser
            return create_simple_browser(fresh_session=True, user_data_dir=chrome_user_dir)

        # First try the shared chrome_bot directory
        default_dir = os.path.join(os.getcwd(), "chrome_bot")
        try:
            return _launch(default_dir)
        except SessionNotCreatedException:
            print("⚠️ Default user-data-dir locked, launching with a temporary profile…")
            tmp_dir = os.path.join(os.getcwd(), f"chrome_bot_tmp_{uuid.uuid4().hex[:6]}")
            driver = _launch(tmp_dir)
            # Schedule temp dir cleanup on driver quit
            def _cleanup(path):
                try:
                    shutil.rmtree(path, ignore_errors=True)
                except Exception:
                    pass
            import atexit
            atexit.register(_cleanup, tmp_dir)
            return driver
    
    def should_continue(self):
        """Check if we should continue applying"""
        return not self.stop_requested
    
    def run_continuous_applications(self):
        """Run continuous applications with 1-2 minute delays"""
        print(f"\n🔄 CONTINUOUS APPLICATION MODE")
        print(f"⏰ Started at: {datetime.now().strftime('%I:%M %p')}")
        print(f"🛑 Press Ctrl+C to stop")
        
        browser = None
        bot = None
        
        try:
            # Initialize browser once
            print("🔧 Initializing browser with stealth features...")
            browser = self.init_browser()
            
            # Initialize bot with continuous mode settings
            bot = LinkedinEasyApply(self.config, browser)
            bot.fast_mode = False  # Keep stealth features but not session breaks
            bot.continuous_mode = True  # Custom flag for continuous mode
            
            # Login
            print("🔐 Logging in...")
            bot.login()
            bot.security_check()
            
            print("🎯 Starting continuous job applications...")
            print("💡 Each application will have 1-2 minute delay with safety features enabled")
            
            while self.should_continue():
                try:
                    # Apply to one job at a time
                    applications_made = bot.start_applying(max_applications=1)
                    
                    if applications_made > 0:
                        self.applications_today += applications_made
                        print(f"✅ Application #{self.applications_today} completed at {datetime.now().strftime('%I:%M %p')}")
                        
                        # 1-2 minute delay between applications
                        delay_minutes = random.uniform(1, 2)
                        delay_seconds = delay_minutes * 60
                        print(f"⏱️  Waiting {delay_minutes:.1f} minutes before next application...")
                        
                        # Sleep in small chunks to allow for interruption
                        sleep_chunks = int(delay_seconds / 10)  # 10-second chunks
                        for i in range(sleep_chunks):
                            if not self.should_continue():
                                break
                            time.sleep(10)
                            # Show countdown every 30 seconds
                            if (i + 1) % 3 == 0:
                                remaining = delay_seconds - ((i + 1) * 10)
                                print(f"   ⏳ {remaining:.0f} seconds remaining...")
                        
                        # Sleep any remaining time
                        remaining_sleep = delay_seconds - (sleep_chunks * 10)
                        if remaining_sleep > 0 and self.should_continue():
                            time.sleep(remaining_sleep)
                    else:
                        print("⏭️  No applications made this round, continuing search...")
                        time.sleep(30)  # Short delay before trying again
                        
                except KeyboardInterrupt:
                    print("\n🛑 Stopping continuous applications...")
                    self.stop_requested = True
                    break
                except Exception as e:
                    print(f"❌ Application error: {str(e)}")
                    print("⏸️  Waiting 2 minutes before retrying...")
                    time.sleep(120)
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping continuous applications...")
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
                temp_dirs = [d for d in os.listdir('.') if d.startswith('chrome_bot_continuous_')]
                for temp_dir in temp_dirs:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                print("🧹 Temporary files cleaned up")
            except:
                pass
            
            print(f"\n📊 Session Summary:")
            print(f"   Total applications: {self.applications_today}")
            print(f"   Duration: {datetime.now() - self.start_time}")
            print(f"   Ended at: {datetime.now().strftime('%I:%M %p')}")
    
    def stop_applications(self):
        """Stop continuous applications"""
        self.stop_requested = True
        print("🛑 Stop requested - applications will finish current job and stop...")

def main():
    print("=" * 60)
    print("🚀 LINKEDIN EASY APPLY BOT - CONTINUOUS MODE")
    print("=" * 60)
    print("🛡️  Full safety features enabled (stealth, human behavior)")
    print("⏰ 1-2 minute delays between applications")
    print("🔄 Continuous application until you stop")
    print("🛑 Press Ctrl+C anytime to stop safely")
    print("=" * 60)
    
    bot = ContinuousApplyBot()
    
    print("\nSelect mode:")
    print("1. Start continuous applications (safe mode with delays)")
    print("2. Exit")
    
    choice = input("\nEnter choice (1-2): ").strip()
    
    if choice == "1":
        try:
            bot.run_continuous_applications()
        except KeyboardInterrupt:
            print("\n🛑 Stopping applications...")
            bot.stop_applications()
    elif choice == "2":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 