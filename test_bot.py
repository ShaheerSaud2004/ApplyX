#!/usr/bin/env python3

import sys
import os
import traceback
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main_fast_user import EnhancedUserBot
    print("✅ EnhancedUserBot imported successfully")
    
    # Test configuration
    config = {
        'email': 'shaheersaud2004@gmail.com',
        'password': 'Capricorn@72',
        'positions': ['Software Engineer', 'Developer'],
        'locations': ['Remote', 'United States'],
        'experience_level': ['Associate', 'Mid-Senior level'],
        'job_types': ['Full-time'],
        'date_posted': 'Past 24 hours',
        'easy_apply_only': True,
        'max_applications': 2  # Small number for testing
    }
    
    print("🔧 Creating bot instance...")
    bot = EnhancedUserBot(user_id="test_user_123", config_data=config)
    
    print("🚀 Starting bot...")
    applications_count = bot.run_continuous_applications(max_applications=2)
    
    print(f"✅ Bot completed! Applied to {applications_count} jobs")
    
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc() 