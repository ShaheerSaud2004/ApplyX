#!/usr/bin/env python3
"""
ENHANCED BOT STATUS SYSTEM
=========================

Provides detailed real-time status updates for LinkedIn Easy Apply bot including:
- Live activity logs
- Progress tracking with ETAs
- Error reporting with solutions
- Performance metrics
- Real-time notifications
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Callable
import threading
import queue

class BotStatusLevel(Enum):
    """Status levels for different types of updates"""
    INFO = "info"
    SUCCESS = "success" 
    WARNING = "warning"
    ERROR = "error"
    PROGRESS = "progress"

class BotActivity(Enum):
    """Specific bot activities for detailed tracking"""
    STARTING = "starting"
    LOGGING_IN = "logging_in"
    SEARCHING_JOBS = "searching_jobs"
    FILTERING_JOBS = "filtering_jobs"
    ANALYZING_JOB = "analyzing_job"
    FILLING_APPLICATION = "filling_application"
    UPLOADING_RESUME = "uploading_resume"
    SUBMITTING_APPLICATION = "submitting_application"
    WAITING_COOLDOWN = "waiting_cooldown"
    HANDLING_ERROR = "handling_error"
    STOPPING = "stopping"
    COMPLETED = "completed"

class EnhancedBotStatusManager:
    """Enhanced status manager with detailed logging and real-time updates"""
    
    def __init__(self, user_id: str, db_path: str = "backend/easyapply.db"):
        self.user_id = user_id
        self.db_path = db_path
        self.status_callbacks = []
        self.activity_log = []
        self.start_time = None
        self.current_activity = None
        self.performance_metrics = {
            'jobs_found': 0,
            'jobs_filtered': 0,
            'applications_attempted': 0,
            'applications_successful': 0,
            'applications_failed': 0,
            'errors_encountered': 0,
            'total_time_seconds': 0
        }
        self.session_stats = {
            'session_start': None,
            'last_activity': None,
            'estimated_completion': None,
            'current_job_title': None,
            'current_company': None,
            'jobs_per_hour': 0
        }
        self._init_database()
    
    def _init_database(self):
        """Initialize enhanced status tracking tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced status table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_bot_status (
                user_id TEXT PRIMARY KEY,
                current_activity TEXT,
                status_level TEXT,
                progress_percentage INTEGER DEFAULT 0,
                current_task TEXT,
                estimated_completion TEXT,
                session_start_time TEXT,
                last_update TEXT,
                performance_metrics TEXT,
                session_stats TEXT
            )
        ''')
        
        # Activity log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                timestamp TEXT,
                activity TEXT,
                status_level TEXT,
                message TEXT,
                details TEXT,
                duration_seconds REAL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Error tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_error_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                timestamp TEXT,
                error_type TEXT,
                error_message TEXT,
                stack_trace TEXT,
                context TEXT,
                resolution_attempted TEXT,
                resolved BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_session(self):
        """Start a new bot session"""
        self.start_time = datetime.now()
        self.session_stats['session_start'] = self.start_time.isoformat()
        self.session_stats['last_activity'] = self.start_time.isoformat()
        
        self.log_activity(
            BotActivity.STARTING,
            BotStatusLevel.INFO,
            "🚀 Starting LinkedIn Easy Apply bot session",
            {"max_applications": 10, "target_positions": ["AI Engineer", "Software Engineer"]}
        )
        
        self._update_database()
    
    def log_activity(self, activity: BotActivity, level: BotStatusLevel, message: str, details: Dict = None):
        """Log a detailed activity with timing and context"""
        timestamp = datetime.now()
        
        activity_entry = {
            'timestamp': timestamp.isoformat(),
            'activity': activity.value,
            'level': level.value,
            'message': message,
            'details': details or {}
        }
        
        # Calculate duration since last activity
        duration = 0
        if self.activity_log:
            last_time = datetime.fromisoformat(self.activity_log[-1]['timestamp'])
            duration = (timestamp - last_time).total_seconds()
        
        activity_entry['duration_seconds'] = duration
        self.activity_log.append(activity_entry)
        
        # Update current activity
        self.current_activity = activity
        self.session_stats['last_activity'] = timestamp.isoformat()
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bot_activity_log 
            (user_id, timestamp, activity, status_level, message, details, duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.user_id, timestamp.isoformat(), activity.value, level.value,
            message, json.dumps(details or {}), duration
        ))
        
        conn.commit()
        conn.close()
        
        # Trigger callbacks for real-time updates
        self._notify_callbacks(activity_entry)
        
        print(f"🔄 [{timestamp.strftime('%H:%M:%S')}] {message}")
        if details:
            print(f"   📋 Details: {details}")
    
    def update_progress(self, percentage: int, current_task: str, eta_minutes: Optional[int] = None):
        """Update progress with detailed information"""
        self.session_stats['current_task'] = current_task
        
        if eta_minutes:
            eta_time = datetime.now() + timedelta(minutes=eta_minutes)
            self.session_stats['estimated_completion'] = eta_time.isoformat()
        
        # Calculate jobs per hour
        if self.start_time:
            elapsed_hours = (datetime.now() - self.start_time).total_seconds() / 3600
            if elapsed_hours > 0:
                self.session_stats['jobs_per_hour'] = round(
                    self.performance_metrics['applications_successful'] / elapsed_hours, 1
                )
        
        progress_details = {
            'percentage': percentage,
            'current_task': current_task,
            'eta_minutes': eta_minutes,
            'jobs_per_hour': self.session_stats['jobs_per_hour']
        }
        
        self.log_activity(
            BotActivity.ANALYZING_JOB,
            BotStatusLevel.PROGRESS,
            f"📊 Progress: {percentage}% - {current_task}",
            progress_details
        )
        
        self._update_database()
    
    def log_job_found(self, job_title: str, company: str, location: str, job_url: str):
        """Log when a new job is found"""
        self.performance_metrics['jobs_found'] += 1
        self.session_stats['current_job_title'] = job_title
        self.session_stats['current_company'] = company
        
        job_details = {
            'job_title': job_title,
            'company': company,
            'location': location,
            'job_url': job_url,
            'total_jobs_found': self.performance_metrics['jobs_found']
        }
        
        self.log_activity(
            BotActivity.ANALYZING_JOB,
            BotStatusLevel.INFO,
            f"🎯 Found job: {job_title} at {company}",
            job_details
        )
    
    def log_application_attempt(self, job_title: str, company: str):
        """Log when starting to apply to a job"""
        self.performance_metrics['applications_attempted'] += 1
        
        self.log_activity(
            BotActivity.FILLING_APPLICATION,
            BotStatusLevel.INFO,
            f"📝 Applying to: {job_title} at {company}",
            {'attempt_number': self.performance_metrics['applications_attempted']}
        )
    
    def log_application_success(self, job_title: str, company: str, application_time_seconds: float):
        """Log successful application submission"""
        self.performance_metrics['applications_successful'] += 1
        
        application_details = {
            'job_title': job_title,
            'company': company,
            'application_time_seconds': round(application_time_seconds, 2),
            'total_successful': self.performance_metrics['applications_successful']
        }
        
        self.log_activity(
            BotActivity.SUBMITTING_APPLICATION,
            BotStatusLevel.SUCCESS,
            f"✅ Successfully applied to {job_title} at {company} ({application_time_seconds:.1f}s)",
            application_details
        )
        
        # Save application to main applications table
        self._save_application_to_db(job_title, company, "applied")
    
    def log_application_error(self, job_title: str, company: str, error: str, error_type: str = "application_error"):
        """Log application error with detailed information"""
        self.performance_metrics['applications_failed'] += 1
        self.performance_metrics['errors_encountered'] += 1
        
        error_details = {
            'job_title': job_title,
            'company': company,
            'error_type': error_type,
            'error_message': error,
            'total_failed': self.performance_metrics['applications_failed']
        }
        
        self.log_activity(
            BotActivity.HANDLING_ERROR,
            BotStatusLevel.ERROR,
            f"❌ Failed to apply to {job_title} at {company}: {error}",
            error_details
        )
        
        # Save detailed error to error log
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bot_error_log 
            (user_id, timestamp, error_type, error_message, context)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            self.user_id, datetime.now().isoformat(), error_type, error,
            json.dumps(error_details)
        ))
        
        conn.commit()
        conn.close()
    
    def log_cooldown(self, cooldown_seconds: int, reason: str = "Rate limiting"):
        """Log cooldown periods with countdown"""
        cooldown_details = {
            'cooldown_seconds': cooldown_seconds,
            'reason': reason,
            'resume_time': (datetime.now() + timedelta(seconds=cooldown_seconds)).isoformat()
        }
        
        self.log_activity(
            BotActivity.WAITING_COOLDOWN,
            BotStatusLevel.WARNING,
            f"⏱️ Waiting {cooldown_seconds}s - {reason}",
            cooldown_details
        )
    
    def add_status_callback(self, callback: Callable):
        """Add callback for real-time status updates"""
        self.status_callbacks.append(callback)
    
    def _notify_callbacks(self, activity_data: Dict):
        """Notify all registered callbacks of status updates"""
        for callback in self.status_callbacks:
            try:
                callback(activity_data)
            except Exception as e:
                print(f"Error in status callback: {e}")
    
    def _save_application_to_db(self, job_title: str, company: str, status: str):
        """Save application to main applications table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO job_applications 
            (user_id, job_title, company, status, applied_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.user_id, job_title, company, status, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def _update_database(self):
        """Update the main status in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO enhanced_bot_status 
            (user_id, current_activity, status_level, current_task, 
             session_start_time, last_update, performance_metrics, session_stats)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.user_id,
            self.current_activity.value if self.current_activity else 'idle',
            BotStatusLevel.INFO.value,
            self.session_stats.get('current_task', 'Ready'),
            self.session_stats.get('session_start'),
            datetime.now().isoformat(),
            json.dumps(self.performance_metrics),
            json.dumps(self.session_stats)
        ))
        
        conn.commit()
        conn.close()
    
    def get_status_summary(self) -> Dict:
        """Get comprehensive status summary for API"""
        elapsed_time = 0
        if self.start_time:
            elapsed_time = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'status': 'running' if self.current_activity else 'idle',
            'current_activity': self.current_activity.value if self.current_activity else 'idle',
            'session_stats': self.session_stats,
            'performance_metrics': self.performance_metrics,
            'recent_activities': self.activity_log[-10:],  # Last 10 activities
            'elapsed_time_seconds': elapsed_time,
            'last_update': datetime.now().isoformat()
        }
    
    def get_activity_log(self, limit: int = 50) -> List[Dict]:
        """Get recent activity log from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, activity, status_level, message, details, duration_seconds
            FROM bot_activity_log 
            WHERE user_id = ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (self.user_id, limit))
        
        activities = []
        for row in cursor.fetchall():
            activities.append({
                'timestamp': row[0],
                'activity': row[1],
                'status_level': row[2],
                'message': row[3],
                'details': json.loads(row[4]) if row[4] else {},
                'duration_seconds': row[5]
            })
        
        conn.close()
        return activities
    
    def get_error_log(self, limit: int = 20) -> List[Dict]:
        """Get recent error log"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, error_type, error_message, context, resolved
            FROM bot_error_log 
            WHERE user_id = ?
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (self.user_id, limit))
        
        errors = []
        for row in cursor.fetchall():
            errors.append({
                'timestamp': row[0],
                'error_type': row[1],
                'error_message': row[2],
                'context': json.loads(row[3]) if row[3] else {},
                'resolved': bool(row[4])
            })
        
        conn.close()
        return errors

# Example usage with the existing bot
class EnhancedLinkedInBot:
    """Example of how to integrate enhanced status into existing bot"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.status_manager = EnhancedBotStatusManager(user_id)
        
    def run_applications(self, max_applications: int = 10):
        """Enhanced application runner with detailed status tracking"""
        self.status_manager.start_session()
        
        try:
            # Simulate login
            self.status_manager.log_activity(
                BotActivity.LOGGING_IN,
                BotStatusLevel.INFO,
                "🔐 Logging into LinkedIn...",
                {"email": "user@example.com"}
            )
            time.sleep(2)  # Simulate login time
            
            # Simulate job search
            self.status_manager.log_activity(
                BotActivity.SEARCHING_JOBS,
                BotStatusLevel.INFO,
                "🔍 Searching for job opportunities...",
                {"search_terms": ["AI Engineer", "Software Engineer"]}
            )
            
            applications_made = 0
            for i in range(max_applications):
                # Simulate finding a job
                job_title = f"AI Engineer {i+1}"
                company = f"TechCorp {i+1}"
                
                self.status_manager.log_job_found(
                    job_title, company, "San Francisco, CA", 
                    f"https://linkedin.com/jobs/job-{i+1}"
                )
                
                # Update progress
                progress = int((i / max_applications) * 100)
                eta_minutes = int((max_applications - i) * 2)  # Estimate 2 min per application
                
                self.status_manager.update_progress(
                    progress, 
                    f"Processing application {i+1} of {max_applications}",
                    eta_minutes
                )
                
                # Simulate application process
                start_time = time.time()
                self.status_manager.log_application_attempt(job_title, company)
                
                # Simulate application time (1-3 seconds)
                app_time = time.sleep(1 + (i % 3))
                application_duration = time.time() - start_time
                
                # 80% success rate simulation
                if i % 5 != 4:  # Success
                    self.status_manager.log_application_success(
                        job_title, company, application_duration
                    )
                    applications_made += 1
                else:  # Failure
                    self.status_manager.log_application_error(
                        job_title, company, 
                        "Form submission failed - LinkedIn detected automation",
                        "linkedin_detection"
                    )
                
                # Simulate cooldown
                if i < max_applications - 1:
                    cooldown = 30 + (i % 60)  # 30-90 second cooldown
                    self.status_manager.log_cooldown(cooldown, "Anti-detection delay")
                    time.sleep(min(cooldown, 3))  # Shortened for demo
            
            # Completion
            self.status_manager.log_activity(
                BotActivity.COMPLETED,
                BotStatusLevel.SUCCESS,
                f"🎉 Session completed! Applied to {applications_made} jobs",
                {"total_applications": applications_made, "session_duration_minutes": 15}
            )
            
            return applications_made
            
        except Exception as e:
            self.status_manager.log_activity(
                BotActivity.HANDLING_ERROR,
                BotStatusLevel.ERROR,
                f"💥 Session failed: {str(e)}",
                {"error_type": "unexpected_error"}
            )
            raise

if __name__ == "__main__":
    # Demo the enhanced status system
    print("🚀 ENHANCED BOT STATUS SYSTEM DEMO")
    print("=" * 50)
    
    # Create a demo bot
    bot = EnhancedLinkedInBot("demo_user_123")
    
    # Add a status callback for real-time updates
    def real_time_callback(activity_data):
        level_emoji = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'progress': '📊'
        }
        
        emoji = level_emoji.get(activity_data['level'], '🔄')
        print(f"🔴 REAL-TIME: {emoji} {activity_data['message']}")
    
    bot.status_manager.add_status_callback(real_time_callback)
    
    # Run demo applications
    try:
        applications = bot.run_applications(max_applications=5)
        print(f"\n✅ Demo completed! {applications} applications submitted")
        
        # Show final status
        status = bot.status_manager.get_status_summary()
        print(f"\n📊 Final Status:")
        print(f"   Applications Successful: {status['performance_metrics']['applications_successful']}")
        print(f"   Errors Encountered: {status['performance_metrics']['errors_encountered']}")
        print(f"   Jobs per Hour: {status['session_stats']['jobs_per_hour']}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}") 