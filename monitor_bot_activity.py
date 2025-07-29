#!/usr/bin/env python3

"""
Real-Time Bot Activity Monitor
==============================

This script monitors bot activity and database changes in real-time
to help debug application saving issues.
"""

import sqlite3
import time
import os
from datetime import datetime

def get_db_path():
    """Get the correct database path"""
    if os.path.exists('backend/easyapply.db'):
        return 'backend/easyapply.db'
    elif os.path.exists('easyapply.db'):
        return 'easyapply.db'
    else:
        print("❌ Database not found!")
        return None

def monitor_applications():
    """Monitor job applications table for changes"""
    
    db_path = get_db_path()
    if not db_path:
        return
    
    print("🔍 STARTING APPLICATION MONITOR...")
    print(f"📊 Database: {db_path}")
    print("=" * 60)
    
    # Get initial count
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM job_applications")
    initial_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT user_id, job_title, company, applied_at 
        FROM job_applications 
        ORDER BY applied_at DESC 
        LIMIT 3
    """)
    latest_apps = cursor.fetchall()
    
    conn.close()
    
    print(f"📈 Initial application count: {initial_count}")
    if latest_apps:
        print(f"🕐 Latest applications:")
        for app in latest_apps:
            print(f"   {app[1]} at {app[2]} (User: {app[0][:8]}...) - {app[3]}")
    
    print(f"\n🔄 Monitoring for new applications... (Press Ctrl+C to stop)")
    print("=" * 60)
    
    last_count = initial_count
    last_check_time = datetime.now()
    
    try:
        while True:
            time.sleep(5)  # Check every 5 seconds
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check current count
            cursor.execute("SELECT COUNT(*) FROM job_applications")
            current_count = cursor.fetchone()[0]
            
            if current_count > last_count:
                new_applications = current_count - last_count
                now = datetime.now()
                
                print(f"\n🎉 NEW APPLICATION(S) DETECTED!")
                print(f"   Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   New applications: {new_applications}")
                print(f"   Total applications: {current_count}")
                
                # Get the new applications
                cursor.execute("""
                    SELECT user_id, job_title, company, applied_at, job_url
                    FROM job_applications 
                    ORDER BY applied_at DESC 
                    LIMIT ?
                """, (new_applications,))
                
                new_apps = cursor.fetchall()
                
                print(f"📝 New application details:")
                for app in new_apps:
                    print(f"   📋 {app[1]} at {app[2]}")
                    print(f"      User: {app[0]}")
                    print(f"      Applied: {app[3]}")
                    print(f"      URL: {app[4] or 'N/A'}")
                    print()
                
                last_count = current_count
            
            # Show periodic status
            now = datetime.now()
            if (now - last_check_time).seconds >= 30:  # Every 30 seconds
                print(f"⏰ {now.strftime('%H:%M:%S')} - Still monitoring... (Total: {current_count} applications)")
                last_check_time = now
            
            conn.close()
            
    except KeyboardInterrupt:
        print(f"\n🛑 Monitoring stopped by user")
        print(f"📊 Final application count: {current_count}")

def show_recent_activity():
    """Show recent bot activity from activity log"""
    
    db_path = get_db_path()
    if not db_path:
        return
    
    print("🔍 RECENT BOT ACTIVITY:")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, action, details, status, timestamp
            FROM activity_log 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        
        activities = cursor.fetchall()
        
        if activities:
            for activity in activities:
                status_emoji = {
                    'success': '✅',
                    'error': '❌', 
                    'warning': '⚠️',
                    'info': 'ℹ️'
                }.get(activity[3], '📝')
                
                print(f"{status_emoji} {activity[1]}: {activity[2]}")
                print(f"   User: {activity[0][:8]}... | Time: {activity[4]}")
                print()
        else:
            print("No recent activity found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading activity log: {e}")

if __name__ == "__main__":
    print("🤖 BOT ACTIVITY MONITOR")
    print("=" * 60)
    
    # Show recent activity first
    show_recent_activity()
    
    print()
    
    # Start monitoring
    monitor_applications() 