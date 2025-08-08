"""
Quota Management Module
Handles user quota checking and updating to avoid circular imports
"""

import sqlite3
import uuid
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

def get_db_path():
    """Get the correct database path"""
    # Always use backend/easyapply.db as it contains the main application data
    return 'backend/easyapply.db' if os.path.exists('backend/easyapply.db') else 'easyapply.db'

# Subscription plans configuration
import os

SUBSCRIPTION_PLANS = {
    'free': {
        'name': 'Free', 
        'price': 0, 
        'daily_quota': 10,
        'monthly_quota': 300,
        'features': ['basic_application', 'manual_apply']
    },
    'basic': {
        'name': 'Basic', 
        'price': 9.99, 
        'daily_quota': 60, 
        'monthly_quota': 1800,
        'stripe_price_id': os.environ.get('STRIPE_BASIC_PRICE_ID'),
        'features': ['basic_application', 'manual_apply', 'priority_support']
    },
    'pro': {
        'name': 'Pro', 
        'price': 19.99, 
        'daily_quota': 100,
        'monthly_quota': 3000,
        'stripe_price_id': os.environ.get('STRIPE_PRO_PRICE_ID'),
        'features': ['basic_application', 'manual_apply', 'ai_optimization', 'analytics', 'priority_support']
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 50,
        'daily_quota': 200,
        'monthly_quota': 6000,
        'features': ['basic_application', 'manual_apply', 'ai_optimization', 'analytics', 'priority_support', 'dedicated_manager']
    }
}

def can_use_quota(user_id, amount=1):
    """Check if user can use quota"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Check and reset daily quota if needed
        success, daily_usage, daily_quota = check_and_reset_daily_quota(user_id)
        if not success:
            conn.close()
            return False
        
        # Get current usage after potential reset
        cursor.execute('''
            SELECT daily_usage, daily_quota 
            FROM users WHERE id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            current_usage, quota = result
            return (current_usage + amount) <= quota
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking quota for user {user_id}: {e}")
        return False

def check_and_reset_daily_quota(user_id):
    """Check and reset daily quota if needed"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Get user's last reset time and current usage
        cursor.execute('''
            SELECT last_usage_reset, daily_usage, daily_quota, subscription_plan 
            FROM users WHERE id = ?
        ''', (user_id,))
        
        user_data = cursor.fetchone()
        if not user_data:
            conn.close()
            return False, 0, 0
        
        last_reset, daily_usage, daily_quota, subscription_plan = user_data
        
        # Handle None values
        if last_reset:
            try:
                last_reset_date = datetime.fromisoformat(last_reset).date()
            except:
                last_reset_date = date.today()
        else:
            last_reset_date = date.today()
            
        today = date.today()
        
        # Reset usage if it's a new day
        if last_reset_date < today:
            # Update quota based on current subscription plan
            plan_quota = SUBSCRIPTION_PLANS.get(subscription_plan or 'free', {}).get('daily_quota', 10)
            cursor.execute('''
                UPDATE users 
                SET daily_usage = 0, daily_quota = ?, last_usage_reset = ?
                WHERE id = ?
            ''', (plan_quota, datetime.now().isoformat(), user_id))
            daily_usage = 0
            daily_quota = plan_quota
            conn.commit()
            logger.info(f"✅ QUOTA RESET: Daily quota reset for user {user_id} - new quota: {plan_quota}")
        
        conn.close()
        return True, daily_usage, daily_quota
        
    except Exception as e:
        logger.error(f"Error checking/resetting quota for user {user_id}: {e}")
        return False, 0, 0

def use_quota(user_id, amount=1, action_type='application'):
    """Use quota and log the usage"""
    try:
        if not can_use_quota(user_id, amount):
            logger.warning(f"⚠️ QUOTA WARNING: User {user_id} cannot use {amount} quota (insufficient remaining)")
            return False
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Update usage
        cursor.execute('''
            UPDATE users 
            SET daily_usage = daily_usage + ?
            WHERE id = ?
        ''', (amount, user_id))
        
        # Get remaining quota
        cursor.execute('''
            SELECT daily_quota - daily_usage as remaining 
            FROM users WHERE id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        remaining = result[0] if result else 0
        
        # Log usage
        try:
            cursor.execute('''
                INSERT INTO usage_logs (id, user_id, action_type, quota_used, remaining_quota, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (str(uuid.uuid4()), user_id, action_type, amount, remaining, datetime.now().isoformat()))
        except Exception as log_error:
            logger.warning(f"Could not log usage to usage_logs table: {log_error}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ QUOTA UPDATED: Used {amount} {action_type} quota for user {user_id} - {remaining} remaining")
        return True
        
    except Exception as e:
        logger.error(f"Error using quota for user {user_id}: {e}")
        return False

def get_user_quota_status(user_id):
    """Get current quota status for a user"""
    try:
        # Ensure quota is reset if needed
        success, daily_usage, daily_quota = check_and_reset_daily_quota(user_id)
        if not success:
            return None
            
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT daily_usage, daily_quota, subscription_plan
            FROM users WHERE id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            daily_usage, daily_quota, subscription_plan = result
            return {
                'daily_usage': daily_usage or 0,
                            'daily_quota': daily_quota or 10,
            'remaining': (daily_quota or 10) - (daily_usage or 0),
                'subscription_plan': subscription_plan or 'free'
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting quota status for user {user_id}: {e}")
        return None 