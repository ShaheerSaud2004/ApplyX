#!/usr/bin/env python3

import asyncio
import schedule
import time
import logging
from datetime import datetime
from job_aggregator import JobAggregator
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DailyJobScheduler:
    def __init__(self):
        self.aggregator = JobAggregator()
        self.running = False
        
    async def update_jobs(self):
        """Update all job listings"""
        try:
            logger.info("🌅 Starting daily job update at 8AM...")
            result = await self.aggregator.update_all_jobs()
            logger.info(f"✅ Daily job update completed! Updated {result} jobs")
            return result
        except Exception as e:
            logger.error(f"❌ Error in daily job update: {e}")
            return 0
    
    def run_update(self):
        """Wrapper to run async update in sync context"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.update_jobs())
            loop.close()
            return result
        except Exception as e:
            logger.error(f"❌ Error running job update: {e}")
            return 0
    
    def start_scheduler(self):
        """Start the daily scheduler"""
        if self.running:
            logger.info("📅 Scheduler already running")
            return
            
        logger.info("🚀 Starting daily job scheduler...")
        
        # Schedule daily updates at 8:00 AM
        schedule.every().day.at("08:00").do(self.run_update)
        
        # Also schedule every 6 hours for more frequent updates
        schedule.every(6).hours.do(self.run_update)
        
        # Initial update on startup
        logger.info("🔄 Running initial job update...")
        self.run_update()
        
        self.running = True
        
        def scheduler_loop():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        # Run scheduler in background thread
        scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        scheduler_thread.start()
        
        logger.info("✅ Daily job scheduler started! Updates at 8:00 AM and every 6 hours")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()
        logger.info("🛑 Job scheduler stopped")

# Global scheduler instance
job_scheduler = DailyJobScheduler()

def start_job_scheduler():
    """Function to start the job scheduler"""
    job_scheduler.start_scheduler()

def stop_job_scheduler():
    """Function to stop the job scheduler"""
    job_scheduler.stop_scheduler()

if __name__ == "__main__":
    # For testing the scheduler
    scheduler = DailyJobScheduler()
    scheduler.start_scheduler()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.stop_scheduler() 