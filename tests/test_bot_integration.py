#!/usr/bin/env python3
"""
LinkedIn Bot Integration Test
Tests the core bot functionality and file dependencies
"""

import os
import sys
import yaml
import requests
import time

def test_bot_files():
    """Test if all required bot files exist"""
    print("🔍 Testing Bot File Dependencies...")
    
    required_files = [
        'linkedineasyapply.py',
        'config.yaml',
        'user_easy_apply_bot.py',
        'backend/app.py',
        'Shaheer_Saud_Resume.pdf'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path} exists")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required bot files present")
    return True

def test_config_file():
    """Test config.yaml structure"""
    print("\n🔍 Testing Config File...")
    
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        required_fields = ['email', 'password', 'linkedinEmail', 'linkedinPassword']
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            print(f"❌ Missing config fields: {missing_fields}")
            return False
        
        print(f"✅ Config file valid")
        print(f"  Email: {config.get('email', 'Not set')}")
        print(f"  LinkedIn Email: {config.get('linkedinEmail', 'Not set')}")
        return True
        
    except Exception as e:
        print(f"❌ Config file error: {e}")
        return False

def test_shaheer_bot_readiness():
    """Test if Shaheer's account is ready for bot usage"""
    print("\n🔍 Testing Shaheer's Bot Readiness...")
    
    backend_url = "http://localhost:5001"
    
    # Login as Shaheer
    shaheer_creds = {
        'email': 'shaheersaud2004@gmail.com',
        'password': 'TestPassword123!'
    }
    
    try:
        # Test login
        login_response = requests.post(f"{backend_url}/api/auth/login", json=shaheer_creds, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Shaheer login failed: {login_response.status_code}")
            return False
        
        token = login_response.json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test profile
        profile_response = requests.get(f"{backend_url}/api/profile", headers=headers)
        
        if profile_response.status_code != 200:
            print(f"❌ Profile load failed: {profile_response.status_code}")
            return False
        
        profile = profile_response.json()
        
        # Check LinkedIn credentials
        linkedin_creds = profile.get('linkedinCreds', {})
        if not (linkedin_creds.get('email') and linkedin_creds.get('password')):
            print("❌ LinkedIn credentials not configured")
            return False
        
        # Check job preferences
        job_prefs = profile.get('jobPreferences', {})
        if not job_prefs.get('jobTitles'):
            print("❌ Job preferences not configured")
            return False
        
        # Check personal info
        personal_info = profile.get('personalInfo', {})
        if not personal_info.get('location'):
            print("❌ Personal info not configured")
            return False
        
        print("✅ Shaheer account fully configured for bot")
        print(f"  LinkedIn Email: {linkedin_creds.get('email', 'Not set')}")
        print(f"  Job Titles: {job_prefs.get('jobTitles', [])}")
        print(f"  Location: {personal_info.get('location', 'Not set')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot readiness test failed: {e}")
        return False

def test_bot_api_complete():
    """Test complete bot API workflow"""
    print("\n🔍 Testing Complete Bot API Workflow...")
    
    backend_url = "http://localhost:5001"
    
    # Login as Shaheer
    shaheer_creds = {
        'email': 'shaheersaud2004@gmail.com',
        'password': 'TestPassword123!'
    }
    
    try:
        # Login
        login_response = requests.post(f"{backend_url}/api/auth/login", json=shaheer_creds)
        token = login_response.json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test status
        status_response = requests.get(f"{backend_url}/api/bot/status", headers=headers)
        if status_response.status_code != 200:
            print(f"❌ Bot status API failed: {status_response.status_code}")
            return False
        
        status_data = status_response.json()
        print(f"✅ Bot status: {status_data.get('status', 'unknown')}")
        
        # Test start (but don't actually run the bot for long)
        print("🔄 Testing bot start...")
        start_response = requests.post(f"{backend_url}/api/bot/start", headers=headers)
        
        if start_response.status_code == 200:
            print("✅ Bot start API working")
            
            # Wait a moment then stop
            time.sleep(2)
            
            # Test stop
            stop_response = requests.post(f"{backend_url}/api/bot/stop", headers=headers)
            if stop_response.status_code == 200:
                print("✅ Bot stop API working")
                return True
            else:
                print(f"⚠️  Bot stop API issue: {stop_response.status_code}")
                return False
        else:
            print(f"❌ Bot start API failed: {start_response.status_code}")
            print(f"Response: {start_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Bot API workflow test failed: {e}")
        return False

def main():
    """Run all bot integration tests"""
    print("🤖 LINKEDIN BOT INTEGRATION TESTS")
    print("=" * 50)
    
    tests = [
        ("Bot Files", test_bot_files),
        ("Config File", test_config_file),
        ("Shaheer Bot Readiness", test_shaheer_bot_readiness),
        ("Bot API Workflow", test_bot_api_complete)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 BOT INTEGRATION TEST RESULTS")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nSUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All bot integration tests passed! Bot is ready to use!")
        return True
    else:
        print("🔧 Some bot tests failed. Please fix issues before using the bot.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 