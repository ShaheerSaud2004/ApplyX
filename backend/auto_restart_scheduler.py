"""
Auto Restart Scheduler
Automatically restarts bots at midnight when daily quotas reset
"""

import threading
import schedule
import time
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict

logger = logging.getLogger(__name__)

class AutoRestartScheduler:
    def __init__(self):
        self.running = False
        self.scheduler_thread = None

    def get_users_with_quota_exceeded(self) -> List[Dict]:
        """Get users who have exceeded their quota and might want auto-restart"""
        try:
            conn = sqlite3.connect('easyapply.db')
            cursor = conn.cursor()
            
            # Get users who:
            # 1. Have daily_usage >= daily_quota (quota exceeded)
            # 2. Have auto_restart preference enabled (we'll add this field)
            cursor.execute('''
                SELECT id, email, first_name, daily_usage, daily_quota, subscription_plan
                FROM users 
                WHERE daily_usage >= daily_quota 
                AND auto_restart = 1
            ''')
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'user_id': row[0],
                    'email': row[1],
                    'name': row[2],
                    'daily_usage': row[3],
                    'daily_quota': row[4],
                    'plan': row[5]
                })
            
            conn.close()
            return users
            
        except Exception as e:
            logger.error(f"Error getting users with quota exceeded: {e}")
            return []

    def restart_user_bot(self, user_id: str) -> bool:
        """Restart bot for a specific user"""
        try:
            # Import here to avoid circular imports
            from persistent_bot_manager import persistent_bot_manager
            
            logger.info(f"🔄 Auto-restarting bot for user {user_id} (quota reset)")
            
            # Stop existing bot if running
            stop_result = persistent_bot_manager.stop_persistent_bot(user_id)
            logger.info(f"Stop result for {user_id}: {stop_result}")
            
            # Wait a moment for clean shutdown
            time.sleep(2)
            
            # Start the bot again
            start_result = persistent_bot_manager.start_persistent_bot(user_id)
            
            if 'error' not in start_result:
                logger.info(f"✅ Successfully auto-restarted bot for user {user_id}")
                
                # Log activity
                self.log_auto_restart_activity(user_id, "success")
                return True
            else:
                logger.error(f"❌ Failed to auto-restart bot for user {user_id}: {start_result.get('error')}")
                self.log_auto_restart_activity(user_id, "failed", start_result.get('error'))
                return False
                
        except Exception as e:
            logger.error(f"Error auto-restarting bot for user {user_id}: {e}")
            self.log_auto_restart_activity(user_id, "error", str(e))
            return False

    def log_auto_restart_activity(self, user_id: str, status: str, error_msg: str = None):
        """Log auto-restart activity"""
        try:
            conn = sqlite3.connect('easyapply.db')
            cursor = conn.cursor()
            
            message = f"🔄 Auto-restart at quota reset: {status}"
            if error_msg:
                message += f" - {error_msg}"
            
            cursor.execute('''
                INSERT INTO activity_log (id, user_id, activity_type, message, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                f"auto_restart_{int(time.time())}_{user_id}",
                user_id,
                "Auto-restart",
                message,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging auto-restart activity for user {user_id}: {e}")

    def midnight_auto_restart(self):
        """Run automatic restart at midnight for users who want it"""
        try:
            logger.info("🌙 Running midnight auto-restart check...")
            
            users = self.get_users_with_quota_exceeded()
            logger.info(f"Found {len(users)} users eligible for auto-restart")
            
            if not users:
                logger.info("No users need auto-restart")
                return
            
            restart_count = 0
            for user in users:
                try:
                    logger.info(f"Attempting auto-restart for {user['name']} ({user['email']})")
                    
                    if self.restart_user_bot(user['user_id']):
                        restart_count += 1
                        logger.info(f"✅ Auto-restarted bot for {user['name']}")
                    else:
                        logger.warning(f"⚠️ Failed to auto-restart bot for {user['name']}")
                    
                    # Small delay between restarts to avoid overwhelming the system
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error during auto-restart for user {user['user_id']}: {e}")
            
            logger.info(f"🎉 Midnight auto-restart completed! Successfully restarted {restart_count}/{len(users)} bots")
            
        except Exception as e:
            logger.error(f"Error during midnight auto-restart: {e}")

    def start_scheduler(self):
        """Start the auto-restart scheduler"""
        if self.running:
            logger.info("📅 Auto-restart scheduler already running")
            return
        
        logger.info("🚀 Starting auto-restart scheduler...")
        self.running = True
        
        # Schedule midnight restart (00:01 AM to ensure quota has reset)
        schedule.every().day.at("00:01").do(self.midnight_auto_restart)
        
        # For testing - uncomment this line to test every minute
        # schedule.every().minute.do(self.midnight_auto_restart)
        
        def scheduler_loop():
            while self.running:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
        
        # Run scheduler in background thread
        self.scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("✅ Auto-restart scheduler started! Bots will auto-restart at midnight when quota resets")

    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()
        logger.info("🛑 Auto-restart scheduler stopped")

# Global scheduler instance
auto_restart_scheduler = AutoRestartScheduler()

def start_auto_restart_scheduler():
    """Function to start the auto-restart scheduler"""
    auto_restart_scheduler.start_scheduler()

def stop_auto_restart_scheduler():
    """Function to stop the auto-restart scheduler"""
    auto_restart_scheduler.stop_scheduler()

if __name__ == "__main__":
    # For testing the scheduler
    scheduler = AutoRestartScheduler()
    scheduler.start_scheduler()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping auto-restart scheduler...")
        scheduler.stop_scheduler() 