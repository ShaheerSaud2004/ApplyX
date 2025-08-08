#!/usr/bin/env python3
"""
Persistent Bot Manager
======================

This manager ensures bot sessions persist across page refreshes, logouts, and server restarts.
Bot sessions are stored in the database and automatically restored on startup.
"""

import threading
import time
import sqlite3
import json
import uuid
import subprocess
import os
import signal
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from enhanced_bot_manager import EnhancedBotManager

class PersistentBotManager:
    """Bot manager that persists sessions across restarts"""
    
    def __init__(self, db_path: str = "easyapply.db"):
        self.db_path = db_path
        self.enhanced_manager = EnhancedBotManager(db_path)
        self.logger = self._setup_logging()
        self._ensure_tables()
        self._restore_sessions_on_startup()
    
    def _setup_logging(self):
        """Setup logging for persistent bot manager"""
        logger = logging.getLogger('persistent_bot_manager')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _ensure_tables(self):
        """Ensure persistent bot session tables exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS persistent_bot_sessions (
                    user_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'running',
                    started_at TEXT NOT NULL,
                    last_heartbeat TEXT NOT NULL,
                    applications_made INTEGER DEFAULT 0,
                    target_applications INTEGER DEFAULT 0,
                    restart_count INTEGER DEFAULT 0,
                    config_data TEXT,
                    process_id INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("Persistent bot sessions table ensured")
            
        except Exception as e:
            self.logger.error(f"Error creating persistent sessions table: {e}")
    
    def _restore_sessions_on_startup(self):
        """Restore active bot sessions on server startup"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find active sessions that were running before restart
            cursor.execute('''
                SELECT user_id, session_id, config_data, applications_made, target_applications, restart_count
                FROM persistent_bot_sessions
                WHERE is_active = 1 AND status = 'running'
            ''')
            
            active_sessions = cursor.fetchall()
            conn.close()
            
            if active_sessions:
                self.logger.info(f"Found {len(active_sessions)} active sessions to restore")
                
                for session in active_sessions:
                    user_id, session_id, config_data, apps_made, target_apps, restart_count = session
                    
                    try:
                        # Parse config data
                        config = json.loads(config_data) if config_data else {}
                        
                        # Restore session in enhanced manager
                        self._restore_enhanced_session(user_id, session_id, config, apps_made, target_apps, restart_count)
                        
                        # Log restoration
                        self.enhanced_manager.log_activity(
                            user_id,
                            "Session Restored",
                            f"🔄 Bot session restored after server restart. Continuing from {apps_made}/{target_apps} applications.",
                            "info",
                            {
                                "session_id": session_id,
                                "restored_applications": apps_made,
                                "remaining_applications": target_apps - apps_made
                            }
                        )
                        
                        self.logger.info(f"Restored session for user {user_id}")
                        
                    except Exception as e:
                        self.logger.error(f"Error restoring session for user {user_id}: {e}")
                        # Mark session as failed
                        self._mark_session_failed(user_id, str(e))
            else:
                self.logger.info("No active sessions to restore")
                
        except Exception as e:
            self.logger.error(f"Error restoring sessions: {e}")
    
    def _restore_enhanced_session(self, user_id: str, session_id: str, config: Dict, apps_made: int, target_apps: int, restart_count: int):
        """Restore a session in the enhanced manager"""
        try:
            # Create session info for enhanced manager
            session_info = {
                'user_id': user_id,
                'started_at': datetime.now().isoformat(),
                'status': 'running',
                'applications_made': apps_made,
                'target_applications': target_apps,
                'last_activity': datetime.now(),
                'restart_count': restart_count + 1,  # Increment for restart
                'session_id': session_id,
                'restored': True
            }
            
            # Add to enhanced manager's running bots
            self.enhanced_manager.running_bots[user_id] = session_info
            
            # Start monitor thread
            monitor_thread = threading.Thread(
                target=self.enhanced_manager._monitor_bot_session,
                args=(user_id, config),
                daemon=True
            )
            monitor_thread.start()
            
            # Add to bot monitors
            self.enhanced_manager.bot_monitors[user_id] = monitor_thread
            
        except Exception as e:
            self.logger.error(f"Error restoring enhanced session for {user_id}: {e}")
            raise
    
    def _mark_session_failed(self, user_id: str, error: str):
        """Mark a session as failed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE persistent_bot_sessions 
                SET status = 'failed', is_active = 0, updated_at = ?
                WHERE user_id = ?
            ''', (datetime.now().isoformat(), user_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error marking session failed for {user_id}: {e}")
    
    def start_persistent_bot(self, user_id: str) -> Dict[str, Any]:
        """Start a bot with persistent session"""
        try:
            # Get enhanced bot configuration
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT linkedin_email_encrypted, linkedin_password_encrypted, 
                       personal_info, job_preferences, bot_config, subscription_plan
                FROM users WHERE id = ?
            ''', (user_id,))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if not user_data or not user_data[0] or not user_data[1]:
                return {
                    'error': 'LinkedIn credentials not configured',
                    'code': 'CREDENTIALS_MISSING'
                }
            
            # Decrypt credentials
            from security import decrypt_data
            linkedin_email = decrypt_data(user_data[0])
            linkedin_password = decrypt_data(user_data[1])
            
            # Parse user configurations
            personal_info = json.loads(user_data[2]) if user_data[2] else {}
            job_preferences = json.loads(user_data[3]) if user_data[3] else {}
            bot_config = json.loads(user_data[4]) if user_data[4] else {}
            subscription_plan = user_data[5] or 'free'
            
            # Create enhanced bot configuration
            quota_map = {'free': 10, 'basic': 30, 'pro': 50}
            daily_quota = quota_map.get(subscription_plan, 10)
            
            enhanced_config = {
                'email': linkedin_email,
                'password': linkedin_password,
                'user_id': user_id,
                'daily_quota': daily_quota,
                'subscription_plan': subscription_plan,
                
                # Job search preferences
                'positions': job_preferences.get('job_titles', ['Software Engineer', 'Developer']),
                'locations': job_preferences.get('locations', ['Remote', 'United States']),
                'location_blacklist': job_preferences.get('location_blacklist', []),
                'company_blacklist': job_preferences.get('company_blacklist', []),
                'title_blacklist': job_preferences.get('title_blacklist', []),
                
                # Personal information
                'personal_info': personal_info,
                
                # Bot behavior
                'experience_level': job_preferences.get('experience_level', ['Associate', 'Mid-Senior level']),
                'job_types': job_preferences.get('job_types', ['Full-time']),
                'date_posted': job_preferences.get('date_posted', 'Past 24 hours'),
                'easy_apply_only': True,
                'auto_restart': True,
                'timeout_minutes': 5,
                'max_restarts': 10
            }
            
            # Start the enhanced manager session
            result = self.enhanced_manager.start_bot_session(user_id, enhanced_config)
            
            if not result:
                return {
                    'error': 'Failed to start bot session',
                    'code': 'STARTUP_FAILED'
                }
            
            # Get session status for result
            session_status = self.enhanced_manager.get_session_status(user_id)
            
            # Save session to database for persistence
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            session_id = f"{user_id}_{int(time.time())}"
            
            cursor.execute('''
                INSERT OR REPLACE INTO persistent_bot_sessions
                (user_id, session_id, status, started_at, last_heartbeat, 
                 applications_made, target_applications, restart_count, config_data, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                session_id,
                'running',
                session_status['start_time'],
                datetime.now().isoformat(),
                session_status['applications_count'],
                session_status['daily_quota'],
                session_status['restart_count'],
                json.dumps(enhanced_config, default=str),
                1
            ))
            
            conn.commit()
            conn.close()
            
            # Start heartbeat monitoring
            self._start_heartbeat_monitor(user_id)
            
            self.logger.info(f"Started persistent bot session for user {user_id}")
            
            # Return success response with persistence info
            return {
                'message': 'Enhanced persistent bot started successfully',
                'user_id': user_id,
                'session_info': session_status,
                'quota_info': {
                    'daily_quota': session_status['daily_quota'],
                    'applications_count': session_status['applications_count'],
                    'quota_remaining': session_status['quota_remaining']
                },
                'features': {
                    'auto_restart': True,
                    'quota_tracking': True,
                    'timeout_detection': True,
                    'timeout_minutes': 5,
                    'max_restarts': 10,
                    'visible_chrome': True,
                    'real_time_monitoring': True,
                    'application_logging': True,
                    'persistent_sessions': True,
                    'survives_refresh': True,
                    'survives_logout': True
                },
                'persistent': True,
                'session_persisted': True,
                'survives_refresh': True
            }
            
        except Exception as e:
            self.logger.error(f"Error making session persistent for {user_id}: {e}")
            # Return the original result even if persistence failed
            result['persistent'] = False
            result['persistence_error'] = str(e)
            return result
    
    def _start_heartbeat_monitor(self, user_id: str):
        """Start heartbeat monitoring for session persistence"""
        def heartbeat_loop():
            while user_id in self.enhanced_manager.active_sessions:
                try:
                    # Update heartbeat and session info
                    session_info = self.enhanced_manager.active_sessions[user_id]
                    
                    # Get session data safely - session_info is a BotSession object
                    applications_made = getattr(session_info, 'applications_made', 0)
                    status = getattr(session_info, 'status', 'running')
                    
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        UPDATE persistent_bot_sessions
                        SET last_heartbeat = ?, applications_made = ?, status = ?, updated_at = ?
                        WHERE user_id = ? AND is_active = 1
                    ''', (
                        datetime.now().isoformat(),
                        applications_made,
                        status,
                        datetime.now().isoformat(),
                        user_id
                    ))
                    
                    conn.commit()
                    conn.close()
                    
                except Exception as e:
                    self.logger.error(f"Heartbeat error for {user_id}: {e}")
                
                # Sleep for 30 seconds
                time.sleep(30)
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        heartbeat_thread.start()
    
    def stop_persistent_bot(self, user_id: str) -> Dict[str, Any]:
        """Stop a persistent bot session"""
        # Stop in enhanced manager
        result = self.enhanced_manager.stop_bot(user_id)
        
        try:
            # Mark as inactive in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE persistent_bot_sessions 
                SET status = 'stopped', is_active = 0, updated_at = ?
                WHERE user_id = ?
            ''', (datetime.now().isoformat(), user_id))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Stopped persistent bot session for user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Error stopping persistent session for {user_id}: {e}")
        
        return result
    
    def get_persistent_status(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive persistent status"""
        # First get status from enhanced manager
        status_data = self.enhanced_manager.get_session_status(user_id) or {}
        
        try:
            # Get persistent session info
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT session_id, status, started_at, last_heartbeat, applications_made, 
                       target_applications, restart_count, is_active
                FROM persistent_bot_sessions
                WHERE user_id = ? AND is_active = 1
            ''', (user_id,))
            
            session_data = cursor.fetchone()
            conn.close()
            
            if session_data:
                session_id, status, started_at, last_heartbeat, apps_made, target_apps, restart_count, is_active = session_data
                
                # Calculate session duration
                started_time = datetime.fromisoformat(started_at)
                duration_seconds = int((datetime.now() - started_time).total_seconds())
                
                # Add persistent session info
                status_data['persistent_session'] = {
                    'session_id': session_id,
                    'status': status,
                    'started_at': started_at,
                    'last_heartbeat': last_heartbeat,
                    'applications_made': apps_made,
                    'target_applications': target_apps,
                    'restart_count': restart_count,
                    'duration_seconds': duration_seconds,
                    'is_active': bool(is_active),
                    'survives_refresh': True,
                    'survives_logout': True
                }
                
                # Override running status if we have an active persistent session
                if is_active and status == 'running':
                    status_data['running'] = True
                    status_data['status'] = 'running'
                    if 'session_info' not in status_data:
                        status_data['session_info'] = {}
                    status_data['session_info'].update({
                        'session_id': session_id,
                        'applications_made': apps_made,
                        'target_applications': target_apps,
                        'restart_count': restart_count,
                        'persistent': True
                    })
            
        except Exception as e:
            self.logger.error(f"Error getting persistent status for {user_id}: {e}")
            status_data['persistent_error'] = str(e)
        
        return status_data

# Global persistent bot manager instance
persistent_bot_manager = PersistentBotManager() 