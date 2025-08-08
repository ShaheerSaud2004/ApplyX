#!/usr/bin/env python3
"""
Ultra-Fresh LinkedIn Bot Session Demo
Creates completely fresh browser sessions with no saved data
"""

import time
from stealth_config import StealthLinkedInSession, AdvancedStealthConfig
from user_easy_apply_bot import UserEasyApplyBot

def test_ultra_fresh_session():
    """Test the ultra-fresh session capability"""
    print("🧹 ULTRA-FRESH SESSION TEST")
    print("=" * 50)
    
    # Create fresh session
    session = StealthLinkedInSession("dummy_dir", fresh_session=True)
    
    try:
        print("🚀 Starting ultra-fresh browser...")
        driver = session.start_session()
        
        print("✅ Fresh browser started successfully!")
        print("📋 Session characteristics:")
        print("   - No saved cookies or login data")
        print("   - Fresh browser fingerprint")
        print("   - Temporary user data directory")
        print("   - Will require login each time")
        print("   - Auto-cleanup on exit")
        
        # Navigate to LinkedIn to test
        print("\n🔗 Navigating to LinkedIn...")
        driver.get("https://www.linkedin.com")
        
        print("✅ Successfully loaded LinkedIn")
        print("🔐 You should see the login page (no auto-login)")
        
        # Wait a bit to see the fresh login page
        input("\n👀 Check the browser - you should see a fresh login page. Press Enter to continue...")
        
        print("🧹 Session will auto-cleanup when script ends")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()
            print("🔚 Browser closed - temporary data will be cleaned up")

def run_fresh_session_bot():
    """Run the bot with ultra-fresh sessions"""
    print("🧹 LINKEDIN BOT WITH ULTRA-FRESH SESSIONS")
    print("=" * 50)
    print("⚠️  WARNING: You will need to login EVERY time!")
    print("✅ BENEFIT: Maximum stealth - no persistent tracking data")
    
    proceed = input("\nProceed with fresh session bot? (y/n): ").lower().strip()
    
    if proceed != 'y':
        print("👋 Cancelled")
        return
    
    # Your bot configuration
    config = {
        'email': input("LinkedIn Email: ").strip(),
        'password': input("LinkedIn Password: ").strip(),
        'positions': ['Software Engineer', 'Developer'],  # Modify as needed
        'locations': ['Remote', 'East Brunswick, New Jersey'],
        'disableAntiLock': False,
        'outputFileDirectory': './logs',
        'uploads': {
            'resume': './resume.pdf'  # Make sure this file exists
        },
        'universityGpa': '3.5',
        'salaryMinimum': 80000,
        'noticePeriod': 30,
        'personalInfo': {
            'first_name': 'Your',
            'last_name': 'Name',
            'location': 'East Brunswick, New Jersey',
            'phone': '555-123-4567'
        },
        'experience': {
            'Python': 5,
            'JavaScript': 3,
            'React': 2
        }
    }
    
    print("\n🧹 Starting bot with ULTRA-FRESH sessions...")
    print("📝 Each run will:")
    print("   ✅ Create completely fresh browser")
    print("   ✅ Require fresh login")
    print("   ✅ Use randomized fingerprint")
    print("   ✅ Leave no persistent data")
    print("   ✅ Auto-cleanup after each session")
    
    user_id = f"fresh_user_{int(time.time())}"
    bot = UserEasyApplyBot(user_id, config)
    
    try:
        print(f"\n🚀 Starting fresh session bot for user: {user_id}")
        bot.run_continuous_applications()
    except KeyboardInterrupt:
        print("\n🛑 Fresh session bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if hasattr(bot, 'browser') and bot.browser:
            bot.browser.quit()
        print("🧹 Fresh session completed - all data cleaned up!")

def compare_session_types():
    """Compare different session types"""
    print("🔄 SESSION TYPE COMPARISON")
    print("=" * 40)
    print("""
    💾 PERSISTENT SESSIONS (Old way):
    ❌ Saves cookies and login state
    ❌ Reuses browser fingerprint
    ❌ Builds up browsing history
    ❌ LinkedIn can track patterns
    ✅ No need to login each time
    
    🧹 FRESH SESSIONS (New way):
    ✅ No saved cookies or login state
    ✅ Fresh browser fingerprint each time
    ✅ No browsing history accumulation
    ✅ Much harder for LinkedIn to detect
    ✅ Maximum stealth and anonymity
    ❌ Must login each time (actually good for stealth!)
    
    🎯 RECOMMENDATION: Use Fresh Sessions for maximum stealth
    """)

if __name__ == "__main__":
    print("🧹 LinkedIn Bot - Ultra-Fresh Session Mode")
    print("Choose an option:")
    print("1. Test ultra-fresh session")
    print("2. Run bot with fresh sessions")
    print("3. Compare session types")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        test_ultra_fresh_session()
    elif choice == "2":
        run_fresh_session_bot()
    elif choice == "3":
        compare_session_types()
    else:
        print("Running comparison by default...")
        compare_session_types() 