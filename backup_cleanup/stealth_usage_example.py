#!/usr/bin/env python3
"""
Example usage of advanced stealth features for LinkedIn bot
"""

import time
from stealth_config import StealthLinkedInSession, AdvancedHumanBehavior, AdvancedStealthConfig
from user_easy_apply_bot import UserEasyApplyBot

def run_stealth_bot_example():
    """Example of running the bot with maximum stealth"""
    
    # Example configuration
    config = {
        'email': 'your-email@example.com',
        'password': 'your-password',
        'positions': ['Software Engineer', 'Developer'],
        'locations': ['Remote', 'San Francisco'],
        'openaiApiKey': 'your-openai-key',  # Optional for AI responses
        
        # Stealth settings
        'disableAntiLock': False,  # Keep some safety features
        'outputFileDirectory': './logs',
        'uploads': {
            'resume': './resume.pdf'
        },
        'universityGpa': '3.5',
        'salaryMinimum': 80000,
        'noticePeriod': 30,
        'personalInfo': {
            'first_name': 'John',
            'last_name': 'Doe',
            'location': 'East Brunswick, New Jersey',  # Using user's preferred location
            'phone': '555-123-4567'
        },
        'experience': {
            'Python': 5,
            'JavaScript': 3,
            'React': 2
        }
    }
    
    print("🥷 Starting LinkedIn Bot with Advanced Stealth Features")
    print("=" * 60)
    
    # Create bot instance
    user_id = "stealth_user_example"
    bot = UserEasyApplyBot(user_id, config)
    
    try:
        # The bot will automatically use stealth features from the updated init_browser method
        bot.run_continuous_applications()
        
    except KeyboardInterrupt:
        print("\n🛑 Stealth bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if hasattr(bot, 'browser') and bot.browser:
            bot.browser.quit()

def test_stealth_features():
    """Test individual stealth features"""
    print("🧪 Testing Advanced Stealth Features")
    print("=" * 40)
    
    # Test timing patterns
    timing = AdvancedHumanBehavior.advanced_timing_patterns()
    print(f"📊 Current timing profile: {timing}")
    
    # Test browser configuration
    user_data_dir = "/tmp/test_stealth"
    options = AdvancedStealthConfig.create_stealth_options(user_data_dir)
    print(f"🛠️ Stealth browser options configured")
    print(f"   - User agent randomized: ✅")
    print(f"   - Screen size randomized: ✅") 
    print(f"   - Language preferences set: ✅")
    print(f"   - Automation markers removed: ✅")
    print(f"   - Fingerprint protection: ✅")
    
    print("\n🎯 Stealth Features Summary:")
    print("   ✅ Advanced user agent rotation")
    print("   ✅ Browser fingerprint randomization") 
    print("   ✅ Realistic screen sizes and resolutions")
    print("   ✅ Professional timezone spoofing")
    print("   ✅ Human-like mouse movements")
    print("   ✅ Realistic typing patterns with typos")
    print("   ✅ Professional reading simulation")
    print("   ✅ Time-based behavior adjustment")
    print("   ✅ Automated session breaks")
    print("   ✅ WebRTC leak protection")
    print("   ✅ Canvas fingerprinting protection")

def stealth_configuration_tips():
    """Provide tips for optimal stealth configuration"""
    print("\n🎯 STEALTH CONFIGURATION TIPS")
    print("=" * 40)
    print("""
    1. 🕐 TIMING IS EVERYTHING:
       - Bot automatically adjusts behavior based on time of day
       - Morning: Faster, more productive patterns
       - Evening: Slower, more casual browsing
    
    2. 🎭 RANDOMIZATION:
       - User agents rotate between real professional browsers
       - Screen sizes match common business monitors
       - Timezones limited to professional regions
    
    3. 🤖 HUMAN BEHAVIOR:
       - Mouse movements follow curved, realistic paths
       - Typing includes occasional typos and corrections
       - Reading patterns simulate professional scanning
    
    4. 🛡️ DETECTION EVASION:
       - Browser fingerprints are randomized per session
       - WebDriver properties are hidden/modified
       - Request headers appear natural
    
    5. ⏱️ SESSION MANAGEMENT:
       - Automatic breaks after realistic usage periods
       - Background activity during breaks
       - Gradual session wind-down patterns
    
    6. 📍 PROFESSIONAL TARGETING:
       - User location set to: East Brunswick, New Jersey
       - Languages optimized for business usage
       - Browser preferences match professional users
    """)

if __name__ == "__main__":
    print("🥷 LinkedIn Bot - Advanced Stealth Mode")
    print("Choose an option:")
    print("1. Run stealth bot example")
    print("2. Test stealth features")
    print("3. Show configuration tips")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        run_stealth_bot_example()
    elif choice == "2":
        test_stealth_features()
    elif choice == "3":
        stealth_configuration_tips()
    else:
        print("Running configuration tips by default...")
        stealth_configuration_tips() 