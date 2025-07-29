#!/usr/bin/env python3

import threading
import subprocess
import time
import logging
import psutil
import os
import signal
import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Callable, Any
import queue

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotSession:
    """Represents a bot session with tracking and timeout management"""
    
    def __init__(self, user_id: str, bot_config: Dict[str, Any]):
        self.user_id = user_id
        self.bot_config = bot_config
        self.process: Optional[subprocess.Popen] = None
        self.start_time = datetime.now()
        self.last_activity = datetime.now()
        self.applications_count = 0
        self.daily_quota = bot_config.get('daily_quota', 5)
        self.is_running = False
        self.restart_count = 0
        self.max_restarts = 10
        self.timeout_minutes = 5
        self.activity_log = []
        
    def is_alive(self) -> bool:
        """Check if the bot process is still alive"""
        if not self.process:
            return False
        return self.process.poll() is None
    
    def is_timeout(self) -> bool:
        """Check if bot has been inactive for too long"""
        time_since_activity = datetime.now() - self.last_activity
        return time_since_activity.total_seconds() > (self.timeout_minutes * 60)
    
    def update_activity(self, activity: str):
        """Update bot activity with timestamp"""
        self.last_activity = datetime.now()
        self.activity_log.append({
            'timestamp': self.last_activity.isoformat(),
            'activity': activity
        })
        logger.info(f"Bot {self.user_id}: {activity}")
    
    def increment_applications(self):
        """Increment application count"""
        self.applications_count += 1
        self.update_activity(f"Applied to job #{self.applications_count}")
    
    def has_reached_quota(self) -> bool:
        """Check if daily quota has been reached"""
        return self.applications_count >= self.daily_quota

class EnhancedBotManager:
    """Enhanced bot manager with auto-restart, quota tracking, and monitoring"""
    
    def __init__(self, db_path: str = None):
        # Import here to avoid circular imports
        from quota_manager import get_db_path
        self.db_path = db_path if db_path else get_db_path()
        self.active_sessions: Dict[str, BotSession] = {}
        self.monitoring_thread: Optional[threading.Thread] = None
        self.is_monitoring = False
        self.activity_callbacks: List[Callable] = []
        self.application_callbacks: List[Callable] = []
        self.init_database()
        
    def init_database(self):
        """Initialize database tables for enhanced tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced bot sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_bot_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                applications_count INTEGER DEFAULT 0,
                daily_quota INTEGER DEFAULT 5,
                restart_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                config TEXT,
                activity_log TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Enhanced activity log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_id TEXT,
                activity TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Application tracking with enhanced data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_applications (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                user_id TEXT,
                job_title TEXT,
                company TEXT,
                job_url TEXT,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'applied',
                response_data TEXT,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def add_activity_callback(self, callback: Callable):
        """Add callback for activity updates"""
        self.activity_callbacks.append(callback)
        
    def add_application_callback(self, callback: Callable):
        """Add callback for application updates"""
        self.application_callbacks.append(callback)
    
    def start_bot_session(self, user_id: str, bot_config: Dict[str, Any]) -> bool:
        """Start a new bot session with enhanced process management"""
        try:
            logger.info(f"Starting enhanced bot session for user {user_id}")
            logger.info(f"Bot configuration: {bot_config}")
            
            # First, stop any existing session and clean up processes
            if user_id in self.active_sessions:
                logger.info(f"Found existing session for user {user_id}, stopping it first...")
                self.stop_bot_session(user_id, "Starting new session")
                time.sleep(3)  # Wait for cleanup
            
            # Kill any lingering processes for this user
            self._cleanup_user_processes(user_id)
            
            # Check if there are too many bot instances running
            existing_bots = self._count_running_bot_processes()
            if existing_bots > 5:  # Prevent too many simultaneous bots
                logger.warning(f"Too many bot processes running ({existing_bots}), cleaning up...")
                self._cleanup_all_bot_processes()
                time.sleep(5)
            
            # If there's still an existing session, force cleanup
            if user_id in self.active_sessions:
                session = self.active_sessions[user_id]
                if session.is_alive():
                    logger.warning(f"Force stopping existing bot process for user {user_id}")
                    try:
                        session.process.terminate()
                        session.process.wait(timeout=10)
                    except:
                        session.process.kill()
                else:
                    # Clean up dead session
                    self.stop_bot_session(user_id)
            
            # Create new session
            session = BotSession(user_id, bot_config)
            session_id = f"{user_id}_{int(time.time())}"
            
            # Save session to database
            self._save_session_to_db(session_id, session)
            
            # Start bot process
            success = self._start_bot_process(session, session_id)
            if success:
                self.active_sessions[user_id] = session
                session.update_activity("Bot session started with visible browser")
                
                # Start monitoring if not already running
                if not self.is_monitoring:
                    self.start_monitoring()
                    
                return True
            else:
                logger.error(f"Failed to start bot process for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting bot session for user {user_id}: {e}")
            return False
    
    def _start_bot_process(self, session: BotSession, session_id: str) -> bool:
        """Start the actual bot process using enhanced main_fast_user.py"""
        try:
            # Use the new enhanced user bot script
            script_path = os.path.join(os.path.dirname(__file__), '..', 'main_fast_user.py')
            
            env = os.environ.copy()
            env['SESSION_ID'] = session_id
            env['USER_ID'] = session.user_id
            env['DAILY_QUOTA'] = str(session.daily_quota)
            
            # Prepare command arguments
            cmd = [
                'python3', script_path,
                '--user-id', session.user_id,
                '--config', json.dumps(session.bot_config, default=str),
                '--max-applications', str(session.daily_quota)
            ]
            
            logger.info(f"Starting enhanced bot with command: {' '.join(cmd)}")
            
            # Start bot process with enhanced logging
            session.process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr with stdout for better logging
                preexec_fn=os.setsid,  # Create new process group
                cwd=os.path.dirname(os.path.dirname(__file__))  # Run from project root
            )
            
            session.is_running = True
            logger.info(f"Started enhanced bot process {session.process.pid} for user {session.user_id}")
            logger.info(f"Bot working directory: {os.path.dirname(os.path.dirname(__file__))}")
            logger.info(f"Bot session ID: {session_id}")
            
            # Start monitoring the process output in a separate thread
            self._start_process_monitor(session)
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting enhanced bot process: {e}")
            logger.error(f"Script path: {script_path}")
            logger.error(f"Working directory: {os.path.dirname(os.path.dirname(__file__))}")
            return False
    
    def _start_process_monitor(self, session: BotSession):
        """Start monitoring bot process output in a separate thread"""
        def monitor_output():
            try:
                for line in iter(session.process.stdout.readline, b''):
                    line_str = line.decode('utf-8').strip()
                    if line_str:
                        logger.info(f"Bot {session.user_id}: {line_str}")
                        session.update_activity(f"Bot Output: {line_str}")
            except Exception as e:
                logger.error(f"Error monitoring bot output for {session.user_id}: {e}")
        
        monitor_thread = threading.Thread(target=monitor_output, daemon=True)
        monitor_thread.start()
        logger.info(f"Started output monitoring for bot {session.user_id}")
    
    def stop_bot_session(self, user_id: str, reason: str = "Manual stop") -> bool:
        """Stop bot session gracefully"""
        try:
            if user_id not in self.active_sessions:
                logger.warning(f"No active session found for user {user_id}")
                return False
            
            session = self.active_sessions[user_id]
            session.update_activity(f"Stopping bot: {reason}")
            
            # Terminate process gracefully
            if session.process and session.is_alive():
                try:
                    # Send SIGTERM first
                    os.killpg(os.getpgid(session.process.pid), signal.SIGTERM)
                    
                    # Wait for graceful shutdown
                    session.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    os.killpg(os.getpgid(session.process.pid), signal.SIGKILL)
                    logger.warning(f"Force killed bot process for user {user_id}")
            
            session.is_running = False
            self._update_session_in_db(session, "stopped")
            
            # Remove from active sessions
            del self.active_sessions[user_id]
            
            logger.info(f"Stopped bot session for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping bot session for user {user_id}: {e}")
            return False
    
    def restart_bot_session(self, user_id: str, reason: str = "Auto-restart") -> bool:
        """Restart bot session"""
        try:
            if user_id not in self.active_sessions:
                logger.warning(f"No active session found for user {user_id}")
                return False
            
            session = self.active_sessions[user_id]
            
            # Check restart limit
            if session.restart_count >= session.max_restarts:
                logger.error(f"Max restarts reached for user {user_id}")
                session.update_activity(f"Max restarts ({session.max_restarts}) reached - stopping")
                self.stop_bot_session(user_id, "Max restarts reached")
                return False
            
            session.restart_count += 1
            session.update_activity(f"Restarting bot (attempt #{session.restart_count}): {reason}")
            
            # Store config before stopping
            bot_config = session.bot_config.copy()
            
            # Stop current session
            self.stop_bot_session(user_id, reason)
            
            # Wait a moment
            time.sleep(2)
            
            # Start new session
            return self.start_bot_session(user_id, bot_config)
            
        except Exception as e:
            logger.error(f"Error restarting bot session for user {user_id}: {e}")
            return False
    
    def stop_bot(self, user_id: str) -> Dict[str, Any]:
        """Stop bot - wrapper method for compatibility with persistent_bot_manager"""
        try:
            success = self.stop_bot_session(user_id, "Manual stop via API")
            if success:
                return {
                    'success': True,
                    'message': f'Bot stopped successfully for user {user_id}',
                    'user_id': user_id,
                    'stopped_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to stop bot session for user {user_id}',
                    'user_id': user_id
                }
        except Exception as e:
            logger.error(f"Error in stop_bot for user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Exception stopping bot: {str(e)}',
                'user_id': user_id
            }
    
    def log_application(self, user_id: str, job_data: Dict[str, Any]):
        """Log a successful job application"""
        try:
            if user_id in self.active_sessions:
                session = self.active_sessions[user_id]
                session.increment_applications()
                
                # Save to database
                self._save_application_to_db(user_id, job_data)
                
                # Trigger callbacks
                for callback in self.application_callbacks:
                    try:
                        callback(user_id, job_data)
                    except Exception as e:
                        logger.error(f"Error in application callback: {e}")
                
                # Check quota
                if session.has_reached_quota():
                    session.update_activity(f"Daily quota of {session.daily_quota} applications reached!")
                    self.stop_bot_session(user_id, "Daily quota reached")
                    
        except Exception as e:
            logger.error(f"Error logging application for user {user_id}: {e}")
    
    def log_activity(self, user_id: str, activity: str, metadata: Dict[str, Any] = None):
        """Log bot activity"""
        try:
            if user_id in self.active_sessions:
                session = self.active_sessions[user_id]
                session.update_activity(activity)
                
                # Save to database
                self._save_activity_to_db(user_id, activity, metadata)
                
                # Trigger callbacks
                for callback in self.activity_callbacks:
                    try:
                        callback(user_id, activity, metadata)
                    except Exception as e:
                        logger.error(f"Error in activity callback: {e}")
                        
        except Exception as e:
            logger.error(f"Error logging activity for user {user_id}: {e}")
    
    def get_session_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed session status"""
        if user_id not in self.active_sessions:
            return None
            
        session = self.active_sessions[user_id]
        runtime = datetime.now() - session.start_time
        
        return {
            'user_id': user_id,
            'is_running': session.is_running and session.is_alive(),
            'start_time': session.start_time.isoformat(),
            'runtime_seconds': int(runtime.total_seconds()),
            'applications_count': session.applications_count,
            'daily_quota': session.daily_quota,
            'quota_remaining': session.daily_quota - session.applications_count,
            'restart_count': session.restart_count,
            'last_activity': session.last_activity.isoformat(),
            'is_timeout': session.is_timeout(),
            'recent_activities': session.activity_log[-10:],  # Last 10 activities
            'process_id': session.process.pid if session.process else None
        }
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Started enhanced bot monitoring")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Stopped enhanced bot monitoring")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                for user_id in list(self.active_sessions.keys()):
                    session = self.active_sessions[user_id]
                    
                    # Check if process is still alive
                    if not session.is_alive():
                        logger.warning(f"Bot process died for user {user_id}")
                        if session.restart_count < session.max_restarts:
                            self.restart_bot_session(user_id, "Process died")
                        else:
                            self.stop_bot_session(user_id, "Process died - max restarts reached")
                        continue
                    
                    # Check for timeout
                    if session.is_timeout():
                        logger.warning(f"Bot timeout detected for user {user_id}")
                        if session.restart_count < session.max_restarts:
                            self.restart_bot_session(user_id, "Activity timeout")
                        else:
                            self.stop_bot_session(user_id, "Activity timeout - max restarts reached")
                        continue
                    
                    # Check quota
                    if session.has_reached_quota():
                        logger.info(f"Daily quota reached for user {user_id}")
                        self.stop_bot_session(user_id, "Daily quota reached")
                        continue
                
                # Sleep before next check
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def _save_session_to_db(self, session_id: str, session: BotSession):
        """Save session to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO enhanced_bot_sessions 
                (session_id, user_id, start_time, applications_count, daily_quota, 
                 restart_count, status, config, activity_log, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                session_id,
                session.user_id,
                session.start_time.isoformat(),
                session.applications_count,
                session.daily_quota,
                session.restart_count,
                'running' if session.is_running else 'stopped',
                json.dumps(session.bot_config),
                json.dumps(session.activity_log)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving session to database: {e}")
    
    def _update_session_in_db(self, session: BotSession, status: str):
        """Update session in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE enhanced_bot_sessions 
                SET applications_count = ?, restart_count = ?, status = ?, 
                    activity_log = ?, updated_at = CURRENT_TIMESTAMP,
                    end_time = CASE WHEN ? = 'stopped' THEN CURRENT_TIMESTAMP ELSE end_time END
                WHERE user_id = ? AND status != 'stopped'
            ''', (
                session.applications_count,
                session.restart_count,
                status,
                json.dumps(session.activity_log),
                status,
                session.user_id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating session in database: {e}")
    
    def _save_activity_to_db(self, user_id: str, activity: str, metadata: Dict[str, Any] = None):
        """Save activity to database for dashboard real-time updates"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Parse the activity to separate action and details
            if ": " in activity:
                action, details = activity.split(": ", 1)
            else:
                action = "Bot Activity"
                details = activity
            
            # Determine status from metadata or activity content
            status = "info"  # default
            if metadata:
                status = metadata.get('status', 'info')
            
            # Check activity content for status indicators
            if any(word in activity.lower() for word in ['success', 'applied', 'completed', '✅']):
                status = "success"
            elif any(word in activity.lower() for word in ['error', 'failed', 'timeout', '❌']):
                status = "error"
            elif any(word in activity.lower() for word in ['warning', 'quota', 'limit', '⚠️']):
                status = "warning"
            
            # Save to the activity_log table that the dashboard reads from
            cursor.execute('''
                INSERT INTO activity_log 
                (user_id, action, details, status, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                action,
                details,
                status,
                json.dumps(metadata) if metadata else '{}',
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving activity to database: {e}")
    
    def _save_application_to_db(self, user_id: str, job_data: Dict[str, Any]):
        """Save application to database - both main table and enhanced tracking"""
        try:
            # Import use_quota function from quota_manager to avoid circular imports
            from quota_manager import use_quota
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            app_id = str(uuid.uuid4())
            session_id = f"{user_id}_{int(time.time())}"
            
            # Save to MAIN job_applications table that dashboard reads from
            cursor.execute('''
                INSERT INTO job_applications 
                (id, user_id, job_title, company, location, job_url, status, applied_at, ai_generated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                app_id,
                user_id,
                job_data.get('job_title', ''),
                job_data.get('company', ''),
                job_data.get('location', ''),
                job_data.get('job_url', ''),
                'applied',
                datetime.now().isoformat(),
                True
            ))
            
            # Also save to enhanced_applications for detailed tracking
            cursor.execute('''
                INSERT INTO enhanced_applications 
                (id, session_id, user_id, job_title, company, job_url, response_data, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"enhanced_{app_id}",
                session_id,
                user_id,
                job_data.get('job_title', ''),
                job_data.get('company', ''),
                job_data.get('job_url', ''),
                json.dumps(job_data),
                json.dumps({'applied_via': 'enhanced_bot_manager'})
            ))
            
            conn.commit()
            conn.close()
            
            # Update daily quota usage
            quota_used = use_quota(user_id, 1, 'application')
            if quota_used:
                logger.info(f"✅ QUOTA UPDATED: Used 1 application quota for user {user_id}")
            else:
                logger.warning(f"⚠️ QUOTA WARNING: Could not update quota for user {user_id}")
            
            logger.info(f"✅ DASHBOARD UPDATE: Saved application to main table - {job_data.get('job_title', '')} at {job_data.get('company', '')}")
            
        except Exception as e:
            logger.error(f"Error saving application to database: {e}")

    def _cleanup_user_processes(self, user_id: str):
        """Clean up any existing processes for a specific user"""
        try:
            logger.info(f"Cleaning up existing processes for user {user_id}")
            
            # Kill any main_fast_user.py processes for this user
            cmd = ['pkill', '-f', f'main_fast_user.py.*{user_id}']
            subprocess.run(cmd, capture_output=True)
            
            # Clean up Chrome processes for this user
            chrome_pattern = f'chrome.*{user_id}'
            cmd = ['pkill', '-f', chrome_pattern]
            subprocess.run(cmd, capture_output=True)
            
            time.sleep(2)
            logger.info(f"Process cleanup completed for user {user_id}")
            
        except Exception as e:
            logger.warning(f"Error during process cleanup for user {user_id}: {e}")

    def _count_running_bot_processes(self) -> int:
        """Count how many bot processes are currently running"""
        try:
            result = subprocess.run(['pgrep', '-f', 'main_fast_user.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return len(result.stdout.strip().split('\n'))
            return 0
        except:
            return 0

    def _cleanup_all_bot_processes(self):
        """Emergency cleanup of all bot processes"""
        try:
            logger.warning("Performing emergency cleanup of all bot processes")
            
            # Kill all main_fast_user.py processes
            subprocess.run(['pkill', '-f', 'main_fast_user.py'], capture_output=True)
            
            # Kill all chrome processes
            subprocess.run(['pkill', '-f', 'chrome'], capture_output=True)
            
            time.sleep(3)
            logger.info("Emergency cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during emergency cleanup: {e}")

# Global instance
enhanced_bot_manager = EnhancedBotManager()

def get_enhanced_bot_manager() -> EnhancedBotManager:
    """Get the global enhanced bot manager instance"""
    return enhanced_bot_manager

if __name__ == "__main__":
    # Test the enhanced bot manager
    manager = EnhancedBotManager()
    
    # Test config
    test_config = {
        'daily_quota': 3,
        'linkedin_email': 'test@example.com',
        'linkedin_password': 'password',
        'chrome_options': ['--no-headless']
    }
    
    print("Testing Enhanced Bot Manager...")
    success = manager.start_bot_session('test_user', test_config)
    print(f"Start session result: {success}")
    
    if success:
        # Monitor for a bit
        time.sleep(10)
        status = manager.get_session_status('test_user')
        print(f"Session status: {status}")
        
        # Stop session
        manager.stop_bot_session('test_user', "Test complete")
    
    manager.stop_monitoring()
    print("Test complete") 