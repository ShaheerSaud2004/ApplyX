#!/usr/bin/env python3

import asyncio
import schedule
import time
import logging
import sqlite3
import threading
from datetime import datetime, timedelta
from email_service import email_service
import sys
import os

# Add the parent directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main_fast_user import EnhancedUserBot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DailyApplicationScheduler:
    def __init__(self):
        self.running = False
        self.current_jobs = {}  # Track current running jobs
        
    def get_active_users_for_daily_applications(self):
        """Get users who should run daily applications based on their plan"""
        try:
            conn = sqlite3.connect('easyapply.db')
            cursor = conn.cursor()
            
            # Get users who are approved and have valid plans
            cursor.execute('''
                SELECT id, email, first_name, last_name, subscription_plan, daily_quota, daily_usage,
                       linkedin_email_encrypted, linkedin_password_encrypted
                FROM users 
                WHERE is_approved = 1 
                AND subscription_plan IS NOT NULL 
                AND daily_quota > 0
                AND (daily_usage < daily_quota OR daily_usage IS NULL)
            ''')
            
            users = []
            for row in cursor.fetchall():
                user_data = {
                    'id': row[0],
                    'email': row[1], 
                    'first_name': row[2],
                    'last_name': row[3],
                    'subscription_plan': row[4],
                    'daily_quota': row[5] or 5,  # Default to 5 if None
                    'daily_usage': row[6] or 0,  # Default to 0 if None
                    'linkedin_email_encrypted': row[7],
                    'linkedin_password_encrypted': row[8]
                }
                
                # Only add users who have LinkedIn credentials and remaining quota
                if (user_data['linkedin_email_encrypted'] and 
                    user_data['linkedin_password_encrypted'] and
                    user_data['daily_usage'] < user_data['daily_quota']):
                    users.append(user_data)
            
            conn.close()
            return users
            
        except Exception as e:
            logger.error(f"❌ Error getting active users: {e}")
            return []
    
    def send_start_email(self, user_data, applications_to_run):
        """Send email when daily applications start"""
        try:
            subject = f"🚀 Daily Job Applications Started - {applications_to_run} Applications"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center;">
                    <h1 style="margin: 0;">🚀 ApplyX Daily Applications Started!</h1>
                </div>
                
                <div style="padding: 20px; background-color: #f9f9f9;">
                    <h2>Hello {user_data['first_name']}!</h2>
                    
                    <p>Your daily automated job applications have just started! Here's what we're doing for you:</p>
                    
                    <div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0;">
                        <h3 style="color: #667eea; margin-top: 0;">📊 Today's Session Details</h3>
                        <ul style="list-style: none; padding: 0;">
                            <li>🎯 <strong>Applications to Submit:</strong> {applications_to_run}</li>
                            <li>📋 <strong>Plan:</strong> {user_data['subscription_plan'].title()}</li>
                            <li>📈 <strong>Daily Quota:</strong> {user_data['daily_quota']}</li>
                            <li>📊 <strong>Used Today:</strong> {user_data['daily_usage']}</li>
                        </ul>
                    </div>
                    
                    <p>We're now searching LinkedIn for the best job matches based on your profile preferences and will apply to positions that fit your criteria.</p>
                    
                    <p style="color: #666; font-size: 0.9em;">
                        💡 <strong>Tip:</strong> You'll receive another email when the session completes with a summary of all applications submitted.
                    </p>
                </div>
                
                <div style="background-color: #667eea; color: white; padding: 15px; text-align: center;">
                    <p style="margin: 0;">Happy job hunting! 🎉</p>
                    <p style="margin: 5px 0 0 0; font-size: 0.8em;">- The ApplyX Team</p>
                </div>
            </div>
            """
            
            plain_content = f"""
            ApplyX Daily Applications Started!
            
            Hello {user_data['first_name']}!
            
            Your daily automated job applications have just started!
            
            Today's Session Details:
            - Applications to Submit: {applications_to_run}
            - Plan: {user_data['subscription_plan'].title()}
            - Daily Quota: {user_data['daily_quota']}
            - Used Today: {user_data['daily_usage']}
            
            We're now searching LinkedIn for the best job matches and will apply to positions that fit your criteria.
            
            You'll receive another email when the session completes.
            
            Happy job hunting!
            - The ApplyX Team
            """
            
            email_service.send_email(
                to_email=user_data['email'],
                subject=subject,
                html_content=html_content,
                plain_content=plain_content
            )
            
            logger.info(f"✅ Sent start email to {user_data['email']}")
            
        except Exception as e:
            logger.error(f"❌ Error sending start email to {user_data['email']}: {e}")
    
    def send_completion_email(self, user_data, applications_submitted, session_duration_minutes):
        """Send email when daily applications complete"""
        try:
            subject = f"✅ Daily Applications Complete - {applications_submitted} Jobs Applied!"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center;">
                    <h1 style="margin: 0;">✅ Daily Applications Complete!</h1>
                </div>
                
                <div style="padding: 20px; background-color: #f9f9f9;">
                    <h2>Great news, {user_data['first_name']}!</h2>
                    
                    <p>Your daily automated job application session has completed successfully! Here's your summary:</p>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #4CAF50;">
                        <h3 style="color: #4CAF50; margin-top: 0;">🎉 Session Results</h3>
                        <ul style="list-style: none; padding: 0; font-size: 18px;">
                            <li>🎯 <strong>Applications Submitted:</strong> {applications_submitted}</li>
                            <li>⏱️ <strong>Session Duration:</strong> {session_duration_minutes} minutes</li>
                            <li>📅 <strong>Completed:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</li>
                        </ul>
                    </div>
                    
                    <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                        <h4 style="color: #1976d2; margin-top: 0;">📈 What's Next?</h4>
                        <ul>
                            <li>Check your Applications page to see all submitted applications</li>
                            <li>Monitor your email for responses from employers</li>
                            <li>Your next daily session will run tomorrow at the same time</li>
                        </ul>
                    </div>
                    
                    <p style="text-align: center;">
                        <a href="http://localhost:3000/applications" style="background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                            View My Applications 📋
                        </a>
                    </p>
                </div>
                
                <div style="background-color: #4CAF50; color: white; padding: 15px; text-align: center;">
                    <p style="margin: 0;">Keep up the momentum! Success is just around the corner. 🌟</p>
                    <p style="margin: 5px 0 0 0; font-size: 0.8em;">- The ApplyX Team</p>
                </div>
            </div>
            """
            
            plain_content = f"""
            Daily Applications Complete!
            
            Great news, {user_data['first_name']}!
            
            Your daily automated job application session has completed successfully!
            
            Session Results:
            - Applications Submitted: {applications_submitted}
            - Session Duration: {session_duration_minutes} minutes
            - Completed: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            
            What's Next?
            - Check your Applications page to see all submitted applications
            - Monitor your email for responses from employers
            - Your next daily session will run tomorrow at the same time
            
            Keep up the momentum! Success is just around the corner.
            
            - The ApplyX Team
            """
            
            email_service.send_email(
                to_email=user_data['email'],
                subject=subject,
                html_content=html_content,
                plain_content=plain_content
            )
            
            logger.info(f"✅ Sent completion email to {user_data['email']}")
            
        except Exception as e:
            logger.error(f"❌ Error sending completion email to {user_data['email']}: {e}")
    
    async def run_daily_applications_for_user(self, user_data):
        """Run daily applications for a specific user"""
        user_id = user_data['id']
        
        try:
            # Calculate how many applications to run
            remaining_quota = user_data['daily_quota'] - user_data['daily_usage']
            applications_to_run = min(remaining_quota, user_data['daily_quota'])
            
            if applications_to_run <= 0:
                logger.info(f"🚫 User {user_data['email']} has reached daily quota")
                return
            
            logger.info(f"🚀 Starting daily applications for {user_data['email']} - {applications_to_run} applications")
            
            # Send start email
            self.send_start_email(user_data, applications_to_run)
            
            # Record start time
            start_time = datetime.now()
            
            # Initialize and run the bot
            bot = EnhancedUserBot(user_id)
            applications_submitted = 0
            
            try:
                # Run applications (this will use the existing bot logic)
                applications_submitted = await asyncio.to_thread(
                    bot.run_continuous_applications, 
                    max_applications=applications_to_run
                )
                
                logger.info(f"✅ Completed daily applications for {user_data['email']} - {applications_submitted} submitted")
                
            except Exception as bot_error:
                logger.error(f"❌ Error running bot for {user_data['email']}: {bot_error}")
                applications_submitted = 0
            
            # Calculate session duration
            end_time = datetime.now()
            session_duration = end_time - start_time
            session_duration_minutes = int(session_duration.total_seconds() / 60)
            
            # Send completion email
            self.send_completion_email(user_data, applications_submitted, session_duration_minutes)
            
            # Update user's daily usage
            try:
                conn = sqlite3.connect('easyapply.db')
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET daily_usage = daily_usage + ?, 
                        last_daily_run = ?
                    WHERE id = ?
                ''', (applications_submitted, datetime.now().isoformat(), user_id))
                conn.commit()
                conn.close()
                
                logger.info(f"📊 Updated daily usage for {user_data['email']}: +{applications_submitted}")
                
            except Exception as update_error:
                logger.error(f"❌ Error updating daily usage for {user_data['email']}: {update_error}")
            
        except Exception as e:
            logger.error(f"❌ Error in daily applications for {user_data['email']}: {e}")
        
        finally:
            # Remove from current jobs
            if user_id in self.current_jobs:
                del self.current_jobs[user_id]
    
    def run_daily_applications(self):
        """Run daily applications for all eligible users"""
        try:
            logger.info("🌅 Starting daily application runs for all users...")
            
            # Reset daily usage counters (optional - could be done at midnight)
            self.reset_daily_usage_if_new_day()
            
            # Get users who should run applications
            users = self.get_active_users_for_daily_applications()
            
            if not users:
                logger.info("📝 No users found for daily applications")
                return
            
            logger.info(f"👥 Found {len(users)} users for daily applications")
            
            # Run applications for each user concurrently
            async def run_all_users():
                tasks = []
                for user_data in users:
                    if user_data['id'] not in self.current_jobs:
                        self.current_jobs[user_data['id']] = datetime.now()
                        task = self.run_daily_applications_for_user(user_data)
                        tasks.append(task)
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
            
            # Run in async context
            asyncio.run(run_all_users())
            
            logger.info("✅ Daily application runs completed for all users")
            
        except Exception as e:
            logger.error(f"❌ Error in daily application runs: {e}")
    
    def reset_daily_usage_if_new_day(self):
        """Reset daily usage counters if it's a new day"""
        try:
            conn = sqlite3.connect('easyapply.db')
            cursor = conn.cursor()
            
            # Reset usage for users whose last run was yesterday or earlier
            yesterday = (datetime.now() - timedelta(days=1)).date()
            
            cursor.execute('''
                UPDATE users 
                SET daily_usage = 0
                WHERE date(last_daily_run) < date('now') 
                OR last_daily_run IS NULL
            ''')
            
            reset_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if reset_count > 0:
                logger.info(f"🔄 Reset daily usage for {reset_count} users")
                
        except Exception as e:
            logger.error(f"❌ Error resetting daily usage: {e}")
    
    def start_scheduler(self):
        """Start the daily application scheduler"""
        if self.running:
            logger.info("📅 Daily application scheduler already running")
            return
            
        logger.info("🚀 Starting daily application scheduler...")
        
        # Schedule daily application runs at 9:00 AM
        schedule.every().day.at("09:00").do(self.run_daily_applications)
        
        # Optional: Add a test run (uncomment for testing)
        # schedule.every().minute.do(self.run_daily_applications)  # For testing only
        
        self.running = True
        
        def scheduler_loop():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        # Run scheduler in background thread
        scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        scheduler_thread.start()
        
        logger.info("✅ Daily application scheduler started! Applications will run at 9:00 AM daily")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()
        logger.info("🛑 Daily application scheduler stopped")

# Global scheduler instance
daily_app_scheduler = DailyApplicationScheduler()

def start_daily_application_scheduler():
    """Function to start the daily application scheduler"""
    daily_app_scheduler.start_scheduler()

def stop_daily_application_scheduler():
    """Function to stop the daily application scheduler"""
    daily_app_scheduler.stop_scheduler()

if __name__ == "__main__":
    # For testing the scheduler
    scheduler = DailyApplicationScheduler()
    scheduler.start_scheduler()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping daily application scheduler...")
        scheduler.stop_scheduler() 