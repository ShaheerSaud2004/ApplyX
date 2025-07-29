#!/usr/bin/env python3
"""
Test dashboard APIs to ensure they're reading from the correct database
"""

import requests
import json
import time

def test_dashboard_apis():
    """Test if dashboard APIs return the correct data"""
    print("🧪 Testing Dashboard APIs")
    print("=" * 30)
    
    base_url = "http://localhost:5000"
    
    # First login to get token
    print("🔐 Logging in...")
    login_data = {
        "email": "shaheersaud2004@gmail.com",
        "password": "Capricorn@72"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()['token']
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Test Applications Stats API
    print("\n📊 Testing /api/applications/stats...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/api/applications/stats", headers=headers)
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Stats API working!")
            print(f"   📈 Total Applications: {stats.get('totalApplications', 'N/A')}")
            print(f"   📅 This Week: {stats.get('applicationsThisWeek', 'N/A')}")
            print(f"   🗓️ This Month: {stats.get('applicationsThisMonth', 'N/A')}")
        else:
            print(f"❌ Stats API failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Stats API error: {e}")
    
    # Test Applications List API
    print("\n📋 Testing /api/applications...")
    try:
        response = requests.get(f"{base_url}/api/applications?limit=5", headers=headers)
        
        if response.status_code == 200:
            apps = response.json()
            applications = apps.get('applications', [])
            print(f"✅ Applications API working!")
            print(f"   📝 Found {len(applications)} applications")
            
            if applications:
                print("   📊 Recent applications:")
                for i, app in enumerate(applications[:3], 1):
                    print(f"     {i}. {app.get('company', 'N/A')} - {app.get('jobTitle', 'N/A')}")
            else:
                print("   ⚠️ No applications found - this might be the issue!")
        else:
            print(f"❌ Applications API failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Applications API error: {e}")
    
    # Test Dashboard Stats API
    print("\n🏠 Testing /api/dashboard/stats...")
    try:
        response = requests.get(f"{base_url}/api/dashboard/stats", headers=headers)
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Dashboard Stats API working!")
            print(f"   📊 Data: {json.dumps(stats, indent=2)}")
        else:
            print(f"❌ Dashboard Stats API failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Dashboard Stats API error: {e}")
    
    print("\n🎯 Test complete! If APIs show 0 applications, the database path fix worked.")
    print("Now refresh your dashboard to see the data!")

if __name__ == "__main__":
    # Wait a moment for backend to start
    print("⏳ Waiting for backend to start...")
    time.sleep(3)
    test_dashboard_apis() 