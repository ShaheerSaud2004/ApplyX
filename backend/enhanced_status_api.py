"""
ENHANCED STATUS API ENDPOINTS
============================

Add these endpoints to your Flask app.py for enhanced bot status functionality.
These provide real-time status updates, activity logs, and detailed monitoring.
"""

from flask import jsonify, request
from functools import wraps
import sqlite3
import json
from datetime import datetime

def register_enhanced_status_routes(app, token_required):
    """Register enhanced status API routes with the Flask app"""
    
    @app.route('/api/bot/status/enhanced', methods=['GET'])
    @token_required
    def get_enhanced_bot_status(current_user_id):
        """Get comprehensive enhanced bot status"""
        try:
            conn = sqlite3.connect('easyapply.db')
            cursor = conn.cursor()
            
            # Get latest enhanced status
            cursor.execute('''
                SELECT * FROM enhanced_bot_status 
                ORDER BY timestamp DESC LIMIT 1
            ''')
            latest_status = cursor.fetchone()
            
            if not latest_status:
                # Create default status if none exists
                default_status = {
                    'user_id': current_user_id,
                    'status': 'idle',
                    'current_action': 'Waiting for instructions',
                    'progress_percentage': 0,
                    'jobs_applied': 0,
                    'jobs_remaining': 0,
                    'success_rate': 0.0,
                    'errors_count': 0,
                    'session_duration': 0,
                    'last_activity': datetime.now().isoformat()
                }
                
                cursor.execute('''
                    INSERT INTO enhanced_bot_status 
                    (user_id, status, current_action, progress_percentage, jobs_applied, 
                     jobs_remaining, success_rate, errors_count, session_duration, 
                     last_activity, metadata) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    current_user_id,
                    default_status['status'],
                    default_status['current_action'],
                    default_status['progress_percentage'],
                    default_status['jobs_applied'],
                    default_status['jobs_remaining'],
                    default_status['success_rate'],
                    default_status['errors_count'],
                    default_status['session_duration'],
                    default_status['last_activity'],
                    json.dumps({})
                ))
                conn.commit()
                
                return jsonify({
                    'success': True,
                    'status': default_status
                })
            
            # Parse the existing status
            status_data = {
                'id': latest_status[0],
                'user_id': latest_status[1],
                'status': latest_status[2],
                'current_action': latest_status[3],
                'progress_percentage': latest_status[4],
                'jobs_applied': latest_status[5],
                'jobs_remaining': latest_status[6],
                'success_rate': latest_status[7],
                'errors_count': latest_status[8],
                'session_duration': latest_status[9],
                'last_activity': latest_status[10],
                'timestamp': latest_status[11],
                'metadata': json.loads(latest_status[12] or '{}')
            }
            
            conn.close()
            
            return jsonify({
                'success': True,
                'status': status_data
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get enhanced status: {str(e)}'
            }), 500

    @app.route('/api/bot/status/enhanced', methods=['POST'])
    @token_required  
    def update_enhanced_bot_status(current_user_id):
        """Update enhanced bot status"""
        try:
            data = request.get_json()
            
            conn = sqlite3.connect('easyapply.db')
            cursor = conn.cursor()
            
            # Update or insert enhanced status
            cursor.execute('''
                INSERT OR REPLACE INTO enhanced_bot_status
                (user_id, status, current_action, progress_percentage, jobs_applied,
                 jobs_remaining, success_rate, errors_count, session_duration,
                 last_activity, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                current_user_id,
                data.get('status', 'idle'),
                data.get('current_action', 'Unknown'),
                data.get('progress_percentage', 0),
                data.get('jobs_applied', 0),
                data.get('jobs_remaining', 0),
                data.get('success_rate', 0.0),
                data.get('errors_count', 0),
                data.get('session_duration', 0),
                datetime.now().isoformat(),
                json.dumps(data.get('metadata', {}))
            ))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Enhanced status updated successfully'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to update enhanced status: {str(e)}'
            }), 500

    @app.route('/api/bot/activity/log', methods=['GET'])
    @token_required
    def get_activity_log(current_user_id):
        """Get bot activity log"""
        try:
            limit = request.args.get('limit', 50, type=int)
            offset = request.args.get('offset', 0, type=int)
            
            # Use the correct database path
            import os
            db_path = os.path.join(os.path.dirname(__file__), 'easyapply.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM activity_log 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ? OFFSET ?
            ''', (current_user_id, limit, offset))
            
            activities = cursor.fetchall()
            
            activity_list = []
            for activity in activities:
                activity_list.append({
                    'id': activity[0],
                    'user_id': activity[1],
                    'action': activity[2],
                    'details': activity[3],
                    'status': activity[4],
                    'timestamp': activity[5],
                    'metadata': json.loads(activity[6] or '{}')
                })
            
            conn.close()
            
            return jsonify({
                'success': True,
                'activities': activity_list,
                'total': len(activity_list)
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get activity log: {str(e)}'
            }), 500

    @app.route('/api/bot/activity/log', methods=['POST'])
    @token_required
    def add_activity_log(current_user_id):
        """Add new activity to log"""
        try:
            data = request.get_json()
            
            conn = sqlite3.connect('easyapply.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO activity_log (user_id, action, details, status, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                current_user_id,
                data.get('action', 'Unknown Action'),
                data.get('details', ''),
                data.get('status', 'completed'),
                json.dumps(data.get('metadata', {}))
            ))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Activity logged successfully'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to add activity log: {str(e)}'
            }), 500

    @app.route('/api/bot/statistics', methods=['GET'])
    @token_required
    def get_bot_statistics(current_user_id):
        """Get comprehensive bot statistics"""
        try:
            conn = sqlite3.connect('easyapply.db')
            cursor = conn.cursor()
            
            # Get basic application stats
            cursor.execute('''
                SELECT COUNT(*) as total_applications,
                       SUM(CASE WHEN status = 'applied' THEN 1 ELSE 0 END) as successful_applications,
                       SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_applications
                FROM applications WHERE user_id = ?
            ''', (current_user_id,))
            
            stats = cursor.fetchone()
            
            # Get recent activity count
            cursor.execute('''
                SELECT COUNT(*) FROM activity_log 
                WHERE user_id = ? AND timestamp > datetime('now', '-24 hours')
            ''', (current_user_id,))
            
            recent_activity = cursor.fetchone()[0]
            
            # Calculate success rate
            total_apps = stats[0] if stats[0] else 0
            successful_apps = stats[1] if stats[1] else 0
            success_rate = (successful_apps / total_apps * 100) if total_apps > 0 else 0
            
            statistics = {
                'total_applications': total_apps,
                'successful_applications': successful_apps,
                'failed_applications': stats[2] if stats[2] else 0,
                'success_rate': round(success_rate, 2),
                'recent_activity_24h': recent_activity,
                'last_updated': datetime.now().isoformat()
            }
            
            conn.close()
            
            return jsonify({
                'success': True,
                'statistics': statistics
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to get statistics: {str(e)}'
            }), 500

    return app 