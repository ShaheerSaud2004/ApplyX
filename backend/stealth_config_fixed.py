#!/usr/bin/env python3
"""
Simplified and robust stealth configuration for LinkedIn bot
Focuses on reliability over advanced features
"""

import random
import time
import os
import tempfile
import uuid
import atexit
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class SimpleStealthConfig:
    """Simplified stealth configuration that actually works"""
    
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    ]
    
    @staticmethod
    def create_reliable_options(user_data_dir: str = None) -> Options:
        """Create reliable Chrome options that actually work"""
        options = Options()
        
        # Essential stealth arguments
        user_agent = random.choice(SimpleStealthConfig.USER_AGENTS)
        options.add_argument(f"--user-agent={user_agent}")
        
        # Disable automation indicators
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Basic functionality
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Window sizing (small window by default, configurable)
        try:
            width = int(os.environ.get("WINDOW_WIDTH", "1100"))
            height = int(os.environ.get("WINDOW_HEIGHT", "700"))
        except ValueError:
            width, height = 1100, 700
        options.add_argument(f"--window-size={width},{height}")
        try:
            pos_x = int(os.environ.get("WINDOW_X", "50"))
            pos_y = int(os.environ.get("WINDOW_Y", "50"))
        except ValueError:
            pos_x, pos_y = 50, 50
        options.add_argument(f"--window-position={pos_x},{pos_y}")
        options.add_argument("--disable-extensions")
        
        # User data directory
        if user_data_dir:
            options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # Disable logging to reduce noise
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        
        print(f"🔧 Created browser options with user agent: {user_agent[:50]}...")
        return options
    
    @staticmethod
    def apply_simple_stealth(driver: webdriver.Chrome) -> None:
        """Apply basic stealth measures that won't cause errors"""
        try:
            # Remove webdriver property (most important)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✅ Removed webdriver property")
        except Exception as e:
            print(f"⚠️ Could not remove webdriver property: {e}")
        
        try:
            # Add some basic human-like properties
            driver.execute_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)
            print("✅ Set navigator languages")
        except Exception as e:
            print(f"⚠️ Could not set languages: {e}")

def create_simple_browser(fresh_session: bool = True, user_data_dir: str = None) -> webdriver.Chrome:
    """
    Create a simple, reliable stealth browser
    
    Args:
        fresh_session: If True, creates fresh session (no saved data)
        user_data_dir: Directory for browser data (only used for persistent sessions)
    
    Returns:
        Chrome WebDriver instance that actually works
    """
    print("🔧 Creating simple stealth browser...")
    
    if fresh_session:
        # Create temporary directory for fresh session
        temp_dir = tempfile.mkdtemp(prefix=f"linkedin_simple_{uuid.uuid4().hex[:8]}_")
        print(f"🧹 Fresh session using: {temp_dir}")
        
        # Schedule cleanup
        def cleanup_temp():
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                print(f"🗑️ Cleaned up: {temp_dir}")
            except:
                pass
        atexit.register(cleanup_temp)
        
        options = SimpleStealthConfig.create_reliable_options(temp_dir)
    else:
        if user_data_dir is None:
            user_data_dir = os.path.join(os.getcwd(), "chrome_bot_simple")
        print(f"💾 Persistent session using: {user_data_dir}")
        options = SimpleStealthConfig.create_reliable_options(user_data_dir)
    
    # Create service
    service = Service(os.path.join(os.getcwd(), "chromedriver"))
    
    try:
        print("🚀 Starting Chrome browser...")
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ Chrome started successfully!")
        
        # Wait a moment for startup
        time.sleep(1)
        
        # Apply simple stealth
        print("🥷 Applying stealth measures...")
        SimpleStealthConfig.apply_simple_stealth(driver)
        
        print("🎉 Simple stealth browser ready!")
        return driver
        
    except Exception as e:
        print(f"❌ Failed to create browser: {e}")
        print("💡 Try updating ChromeDriver or Chrome browser")
        raise

def test_simple_browser():
    """Test the simple browser configuration"""
    print("🧪 Testing Simple Browser")
    print("=" * 30)
    
    try:
        # Create browser
        driver = create_simple_browser(fresh_session=True)
        
        print("📍 Testing Google navigation...")
        driver.get("https://www.google.com")
        time.sleep(2)
        
        title = driver.title
        print(f"Google title: {title}")
        
        if "Google" in title:
            print("✅ Google test passed!")
        
        print("📍 Testing LinkedIn navigation...")
        driver.get("https://www.linkedin.com")
        time.sleep(3)
        
        linkedin_title = driver.title
        print(f"LinkedIn title: {linkedin_title}")
        
        if "LinkedIn" in linkedin_title or "Sign In" in linkedin_title:
            print("✅ LinkedIn test passed!")
            print("🎉 Browser is working correctly!")
        else:
            print("⚠️ LinkedIn may have loaded differently")
        
        input("\n👀 Check the browser window. Press Enter to close...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        if 'driver' in locals():
            try:
                driver.quit()
                print("🔚 Browser closed")
            except:
                pass

if __name__ == "__main__":
    test_simple_browser() 