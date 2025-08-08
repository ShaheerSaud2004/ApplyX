#!/usr/bin/env python3
"""
Test script to verify LinkedIn bot fixes
"""

import sys
import os

def test_stealth_import():
    """Test if stealth module imports correctly"""
    print("🧪 Testing stealth module import...")
    try:
        from stealth_config_fixed import create_simple_browser, SimpleStealthConfig
        print("✅ Stealth module imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import stealth module: {e}")
        return False

def test_simple_browser():
    """Test creating a simple browser"""
    print("\n🧪 Testing simple browser creation...")
    try:
        from stealth_config_fixed import create_simple_browser
        
        # Create browser
        driver = create_simple_browser(fresh_session=True)
        
        # Test basic navigation
        print("📍 Testing LinkedIn navigation...")
        driver.get("https://www.linkedin.com")
        
        # Wait for page load
        import time
        time.sleep(3)
        
        title = driver.title
        print(f"Page title: {title}")
        
        if "LinkedIn" in title or "Sign In" in title:
            print("✅ LinkedIn navigation successful!")
            success = True
        else:
            print("⚠️ LinkedIn page may not have loaded correctly")
            success = False
        
        # Close browser
        driver.quit()
        print("🔚 Browser closed")
        
        return success
        
    except Exception as e:
        print(f"❌ Browser test failed: {e}")
        if 'driver' in locals():
            try:
                driver.quit()
            except:
                pass
        return False

def test_bot_import():
    """Test if bot modules import correctly"""
    print("\n🧪 Testing bot module imports...")
    try:
        # Test main bot imports
        from main_fast_user import EasyApplyLinkedIn
        print("✅ main_fast_user imported successfully")
        
        from user_easy_apply_bot import EasyApplyLinkedIn as UserBot
        print("✅ user_easy_apply_bot imported successfully")
        
        from main_fast import EasyApplyLinkedIn as FastBot
        print("✅ main_fast imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot import failed: {e}")
        return False

def main():
    print("🔧 LINKEDIN BOT FIX VERIFICATION")
    print("=" * 40)
    
    # Test 1: Import stealth module
    import_ok = test_stealth_import()
    
    # Test 2: Import bot modules
    bot_import_ok = test_bot_import()
    
    # Test 3: Create browser (most important)
    if import_ok:
        browser_ok = test_simple_browser()
    else:
        browser_ok = False
    
    # Summary
    print("\n📊 TEST RESULTS")
    print("=" * 20)
    print(f"Stealth Import: {'✅ PASS' if import_ok else '❌ FAIL'}")
    print(f"Bot Import:     {'✅ PASS' if bot_import_ok else '❌ FAIL'}")
    print(f"Browser Test:   {'✅ PASS' if browser_ok else '❌ FAIL'}")
    
    if import_ok and bot_import_ok and browser_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("Your LinkedIn bot is now fixed and ready to use!")
        print("\nYou can now:")
        print("1. Start your bot from the web interface")
        print("2. Or run: python3 main_fast_user.py")
        print("3. The bot will use fresh sessions (no saved cookies)")
        print("4. Each session requires login for maximum stealth")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        if not import_ok:
            print("- Fix stealth module import issues")
        if not bot_import_ok:
            print("- Check bot module dependencies")
        if not browser_ok:
            print("- Verify ChromeDriver is working")
            print("- Try updating Chrome browser")
    
    return import_ok and bot_import_ok and browser_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 