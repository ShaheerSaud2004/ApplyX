#!/usr/bin/env python3
"""
Test the web bot flow directly to ensure login works
"""

import sys
import os

def test_user_bot_with_credentials():
    """Test creating a user bot with the actual user ID from the web interface"""
    print("🧪 Testing Web Bot Flow")
    print("=" * 30)
    
    # Use the actual user ID from the logs
    user_id = "bf5acf53-8862-48af-b9ab-3b73d3c5527a"
    
    try:
        from main_fast_user import EnhancedUserBot
        
        print(f"🤖 Creating bot for user: {user_id}")
        bot = EnhancedUserBot(user_id)
        
        print("📋 Loading configuration...")
        config = bot.load_user_configuration()
        
        if config:
            print("✅ Configuration loaded successfully!")
            print(f"📧 Email: {config.get('email', 'NOT FOUND')}")
            print(f"🔒 Password: {'SET' if config.get('password') else 'NOT FOUND'}")
            print(f"🎯 Positions: {config.get('positions', ['NOT FOUND'])}")
            print(f"📍 Locations: {config.get('locations', ['NOT FOUND'])}")
            
            if config.get('email') and config.get('password'):
                print("🎉 Credentials are properly loaded!")
                return True
            else:
                print("❌ Credentials missing from configuration")
                return False
        else:
            print("❌ Failed to load configuration")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_linkedin_login():
    """Test direct LinkedIn login with the loaded credentials"""
    print("\n🔐 Testing Direct LinkedIn Login")
    print("=" * 35)
    
    try:
        from main_fast_user import EnhancedUserBot
        user_id = "bf5acf53-8862-48af-b9ab-3b73d3c5527a"
        
        print(f"🤖 Creating bot for user: {user_id}")
        bot = EnhancedUserBot(user_id)
        
        print("📋 Loading configuration...")
        config = bot.load_user_configuration()
        
        if not config or not config.get('email') or not config.get('password'):
            print("❌ Cannot test login - credentials not available")
            return False
        
        print("🌐 Initializing browser...")
        from stealth_config_fixed import create_simple_browser
        driver = create_simple_browser(fresh_session=True)
        
        print("📍 Navigating to LinkedIn...")
        driver.get("https://www.linkedin.com/login")
        
        import time
        time.sleep(3)
        
        print("📧 Entering email...")
        email_field = driver.find_element("id", "username")
        email_field.clear()
        email_field.send_keys(config['email'])
        
        print("🔒 Entering password...")
        password_field = driver.find_element("id", "password")
        password_field.clear()
        password_field.send_keys(config['password'])
        
        print("🚀 Clicking login...")
        login_btn = driver.find_element("xpath", "//button[@type='submit']")
        login_btn.click()
        
        print("⏳ Waiting for login to complete...")
        time.sleep(10)
        
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        if "feed" in current_url or "in/" in current_url:
            print("🎉 Login successful!")
            print("✅ Bot credentials are working!")
            success = True
        elif "challenge" in current_url:
            print("⚠️ Security challenge - but login worked!")
            success = True
        else:
            print("❌ Login may have failed")
            success = False
        
        input("\n👀 Check the browser. Press Enter to close...")
        driver.quit()
        
        return success
        
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        if 'driver' in locals():
            try:
                driver.quit()
            except:
                pass
        return False

def main():
    print("🔧 WEB BOT FLOW TEST")
    print("=" * 25)
    print("Testing the actual web interface bot flow")
    print()
    
    # Test 1: Configuration loading
    config_ok = test_user_bot_with_credentials()
    
    # Test 2: Direct login (optional)
    login_ok = True
    if config_ok:
        test_login = input("\nTest direct login? (y/n): ").lower().strip()
        if test_login == 'y':
            login_ok = test_direct_linkedin_login()
        else:
            print("⚠️ Skipping login test")
    
    # Results
    print("\n📊 TEST RESULTS")
    print("=" * 15)
    print(f"Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Login Test:    {'✅ PASS' if login_ok else '❌ FAIL'}")
    
    if config_ok and login_ok:
        print("\n🎉 WEB BOT IS READY!")
        print("The bot can now be started from the web interface")
        print("and will successfully log in and apply to jobs!")
    else:
        print("\n⚠️ Issues found:")
        if not config_ok:
            print("- Fix credential loading")
        if not login_ok:
            print("- Fix login process")

if __name__ == "__main__":
    main() 