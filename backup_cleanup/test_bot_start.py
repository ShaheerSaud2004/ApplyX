#!/usr/bin/env python3

"""
Bot Test Script
===============

This script helps test and debug the bot startup process.
Use this to verify that the bot can start and run properly.
"""

import os
import sys
import json
import time
import sqlite3
import subprocess
from datetime import datetime

def test_database_connection():
    """Test database connection and user data"""
    print("🔍 Testing database connection...")
    
    try:
        # Try backend path first
        db_path = 'backend/easyapply.db' if os.path.exists('backend/easyapply.db') else 'easyapply.db'
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get user count
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        print(f"✅ Database connected successfully")
        print(f"📊 Total users: {user_count}")
        
        # Get users with LinkedIn credentials
        cursor.execute('SELECT id, email FROM users WHERE linkedin_email_encrypted IS NOT NULL LIMIT 5')
        users = cursor.fetchall()
        
        print(f"👥 Users with LinkedIn credentials:")
        for user_id, email in users:
            print(f"  - User ID: {user_id}, Email: {email}")
        
        conn.close()
        return users[0][0] if users else None
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def test_chromedriver():
    """Test if chromedriver is available"""
    print("\n🌐 Testing ChromeDriver...")
    
    try:
        # Check if chromedriver exists
        chromedriver_path = os.path.join(os.getcwd(), "chromedriver")
        if os.path.exists(chromedriver_path):
            print(f"✅ ChromeDriver found at: {chromedriver_path}")
        else:
            print(f"⚠️ ChromeDriver not found at: {chromedriver_path}")
            print("   Trying system PATH...")
            
        # Test chromedriver version
        result = subprocess.run(['./chromedriver', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ ChromeDriver version: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ ChromeDriver test failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ ChromeDriver not found in PATH")
        return False
    except Exception as e:
        print(f"❌ ChromeDriver test error: {e}")
        return False

def test_bot_imports():
    """Test if all required modules can be imported"""
    print("\n📦 Testing bot imports...")
    
    try:
        # Test main bot imports
        from linkedineasyapply import LinkedinEasyApply
        print("✅ LinkedinEasyApply imported successfully")
        
        from selenium import webdriver
        print("✅ Selenium imported successfully")
        
        from selenium.webdriver.chrome.options import Options
        print("✅ Chrome options imported successfully")
        
        # Test backend imports
        sys.path.append('backend')
        try:
            from security import decrypt_data
            print("✅ Security module imported successfully")
        except ImportError as e:
            print(f"⚠️ Security module import failed: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config_loading(user_id):
    """Test configuration loading for a user"""
    print(f"\n⚙️ Testing configuration loading for user: {user_id}")
    
    try:
        # Test the enhanced bot configuration
        from main_fast_user import EnhancedUserBot
        
        print("🔧 Creating Enhanced User Bot instance...")
        bot = EnhancedUserBot(user_id)
        
        if bot.config:
            print("✅ Configuration loaded successfully")
            print(f"📧 Email: {bot.config.get('email', 'Not configured')}")
            print(f"🎯 Positions: {bot.config.get('positions', [])}")
            print(f"📍 Locations: {bot.config.get('locations', [])}")
            return True
        else:
            print("❌ Configuration loading failed")
            return False
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_bot_startup(user_id):
    """Test bot startup process"""
    print(f"\n🚀 Testing bot startup for user: {user_id}")
    
    try:
        # Create test configuration
        test_config = {
            'email': 'test@example.com',
            'password': 'test_password',
            'positions': ['Software Engineer'],
            'locations': ['Remote'],
            'easyApplyOnly': True
        }
        
        # Test command construction
        cmd = [
            'python3', 'main_fast_user.py',
            '--user-id', user_id,
            '--config', json.dumps(test_config),
            '--max-applications', '1'
        ]
        
        print(f"🔧 Test command: {' '.join(cmd)}")
        
        # Start process but kill it quickly (just test startup)
        print("🔄 Starting bot process (will terminate after 10 seconds)...")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Wait for 10 seconds and capture output
        try:
            output, _ = process.communicate(timeout=10)
            print("⏰ Process completed within 10 seconds")
            print(f"📝 Output:\n{output}")
        except subprocess.TimeoutExpired:
            print("⏰ Process running for 10+ seconds (good sign!)")
            process.terminate()
            try:
                output, _ = process.communicate(timeout=5)
                print(f"📝 Partial output:\n{output}")
            except subprocess.TimeoutExpired:
                process.kill()
                print("🛑 Process killed after timeout")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot startup test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 80)
    print("🧪 BOT DIAGNOSTIC TEST SUITE")
    print("=" * 80)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Working directory: {os.getcwd()}")
    print()
    
    # Run tests
    test_results = []
    
    # Test 1: Database
    user_id = test_database_connection()
    test_results.append(('Database Connection', user_id is not None))
    
    # Test 2: ChromeDriver
    chromedriver_ok = test_chromedriver()
    test_results.append(('ChromeDriver', chromedriver_ok))
    
    # Test 3: Imports
    imports_ok = test_bot_imports()
    test_results.append(('Bot Imports', imports_ok))
    
    # Test 4: Configuration (only if we have a user)
    config_ok = False
    if user_id:
        config_ok = test_config_loading(user_id)
        test_results.append(('Configuration Loading', config_ok))
        
        # Test 5: Bot Startup (only if previous tests pass)
        if config_ok:
            startup_ok = test_bot_startup(user_id)
            test_results.append(('Bot Startup', startup_ok))
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bot should work correctly.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        
    print("\n💡 To manually test the bot, run:")
    if user_id:
        print(f"   python3 main_fast_user.py --user-id {user_id} --max-applications 1")
    else:
        print("   First ensure you have users with LinkedIn credentials in the database")

if __name__ == "__main__":
    main() 