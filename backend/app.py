from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import yaml
import json
import sqlite3
from datetime import datetime, timedelta, date
import threading
import subprocess
import sys
import uuid
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import time
from functools import wraps
import stripe
import secrets
from dotenv import load_dotenv
import logging
from pathlib import Path

# Load email configuration from environment file
email_config_path = os.path.join(os.path.dirname(__file__), '..', 'email_config.sh')
if os.path.exists(email_config_path):
    try:
        with open(email_config_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    # Remove quotes from value
                    value = value.strip('"\'')
                    os.environ[key] = value
        print("✅ Email configuration loaded from email_config.sh")
    except Exception as e:
        print(f"⚠️ Could not load email config: {e}")

# Load environment variables
load_dotenv()

# Import existing LinkedIn bot functionality
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Conditional imports for GUI-dependent modules (only import locally)
LinkedinEasyApply = None
ContinuousApplyBot = None
WebPlatformLinkedInBot = None

# Only import GUI-dependent modules if we're not in a headless environment
if os.environ.get('DISPLAY') or os.environ.get('RUNNING_LOCALLY'):
    try:
        from linkedineasyapply import LinkedinEasyApply
        from main_fast import ContinuousApplyBot
        from web_agent import WebPlatformLinkedInBot
    except ImportError as e:
        print(f"Warning: Could not import GUI-dependent modules: {e}")
        print("This is expected in headless environments like DigitalOcean")
from enhanced_status_api import register_enhanced_status_routes
from job_api import register_job_routes
from email_service import email_service
from daily_job_scheduler import start_job_scheduler
from daily_application_scheduler import start_daily_application_scheduler

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

CORS(app, origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", 
                   "https://apply-9sp9tevcp-shaheers-projects-02efc33d.vercel.app",
                   "https://apply-x.vercel.app",
                   "https://*.vercel.app"], 
     allow_headers=["Content-Type", "Authorization"], 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True)

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Subscription plans moved to quota_manager.py

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variables for bot management
active_bots = {}
bot_status = {}

logger = logging.getLogger(__name__)

def safe_split_to_list(value, delimiter=','):
    """Safely convert string or list to a list of trimmed strings"""
    if not value:
        return []
    
    # If it's already a list, return it cleaned
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    
    # If it's a string, split it
    if isinstance(value, str):
        return [item.strip() for item in value.split(delimiter) if item.strip()]
    
    # Fallback for other types
    return [str(value).strip()] if str(value).strip() else []

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            linkedin TEXT,
            website TEXT,
            linkedin_email_encrypted TEXT,
            linkedin_password_encrypted TEXT,
            subscription_plan TEXT DEFAULT 'free',
            stripe_customer_id TEXT,
            subscription_id TEXT,
            subscription_status TEXT,
            current_period_end TIMESTAMP,
            daily_quota INTEGER DEFAULT 5,
            daily_usage INTEGER DEFAULT 0,
            last_usage_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin BOOLEAN DEFAULT FALSE,
            status TEXT DEFAULT 'pending',
            referral_code TEXT,
            referred_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if LinkedIn credential columns exist, add them if not
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'linkedin_email_encrypted' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN linkedin_email_encrypted TEXT')
    
    if 'linkedin_password_encrypted' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN linkedin_password_encrypted TEXT')
    
    # Add Easy Apply bot configuration columns
    if 'personal_info' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN personal_info TEXT')
    
    if 'job_preferences' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN job_preferences TEXT')
    
    if 'bot_config' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN bot_config TEXT')
    
    if 'daily_usage' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN daily_usage INTEGER DEFAULT 0')
        
    if 'last_daily_run' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN last_daily_run TEXT')
        
    if 'auto_restart' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN auto_restart INTEGER DEFAULT 1')
        print("✅ Added auto_restart column to users table (default: enabled)")

    # Password resets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            token TEXT NOT NULL UNIQUE,
            expires_at TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            used BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Job applications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_applications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            job_title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            job_url TEXT,
            status TEXT DEFAULT 'applied',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resume_used TEXT,
            cover_letter_used TEXT,
            notes TEXT,
            ai_generated BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # User preferences table - updated schema for better job preferences storage
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            job_titles TEXT,
            locations TEXT,
            remote BOOLEAN DEFAULT TRUE,
            experience TEXT DEFAULT 'mid',
            salary_min TEXT,
            skills TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Check if new preference columns exist and add them
    cursor.execute("PRAGMA table_info(user_preferences)")
    pref_columns = [column[1] for column in cursor.fetchall()]
    
    # Update old column names to new ones
    if 'positions' in pref_columns and 'job_titles' not in pref_columns:
        cursor.execute('ALTER TABLE user_preferences ADD COLUMN job_titles TEXT')
        cursor.execute('UPDATE user_preferences SET job_titles = positions WHERE job_titles IS NULL')
    
    if 'experience_level' in pref_columns and 'experience' not in pref_columns:
        cursor.execute('ALTER TABLE user_preferences ADD COLUMN experience TEXT DEFAULT "mid"')
        cursor.execute('UPDATE user_preferences SET experience = experience_level WHERE experience IS NULL')
    
    if 'salary_minimum' in pref_columns and 'salary_min' not in pref_columns:
        cursor.execute('ALTER TABLE user_preferences ADD COLUMN salary_min TEXT')
        cursor.execute('UPDATE user_preferences SET salary_min = salary_minimum WHERE salary_min IS NULL')
    
    if 'skills_required' in pref_columns and 'skills' not in pref_columns:
        cursor.execute('ALTER TABLE user_preferences ADD COLUMN skills TEXT')
        cursor.execute('UPDATE user_preferences SET skills = skills_required WHERE skills IS NULL')

    # Agent tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_tasks (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            type TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            progress INTEGER DEFAULT 0,
            parameters TEXT,
            results TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            error TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Billing events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS billing_events (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            stripe_event_id TEXT UNIQUE,
            event_type TEXT NOT NULL,
            subscription_plan TEXT,
            amount INTEGER,
            currency TEXT DEFAULT 'usd',
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Usage logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_logs (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            quota_used INTEGER DEFAULT 1,
            remaining_quota INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Referrals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            id TEXT PRIMARY KEY,
            referrer_id TEXT NOT NULL,
            referred_id TEXT NOT NULL,
            referral_code TEXT NOT NULL,
            bonus_granted BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (referrer_id) REFERENCES users (id),
            FOREIGN KEY (referred_id) REFERENCES users (id)
        )
    ''')
    
    # Activity log table for live bot tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            status TEXT DEFAULT 'info',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Enhanced bot status table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enhanced_bot_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            status TEXT DEFAULT 'idle',
            current_action TEXT,
            progress_percentage INTEGER DEFAULT 0,
            jobs_applied INTEGER DEFAULT 0,
            jobs_remaining INTEGER DEFAULT 0,
            success_rate REAL DEFAULT 0.0,
            errors_count INTEGER DEFAULT 0,
            session_duration INTEGER DEFAULT 0,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid'}), 401
        
        return f(current_user_id, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user_id, *args, **kwargs):
        # Check if user is admin
        conn = sqlite3.connect('easyapply.db')
        cursor = conn.cursor()
        cursor.execute('SELECT is_admin FROM users WHERE id = ?', (current_user_id,))
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data or not user_data[0]:
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(current_user_id, *args, **kwargs)
    return decorated

# Quota functions moved to quota_manager.py to avoid circular imports
from quota_manager import check_and_reset_daily_quota, can_use_quota, use_quota, SUBSCRIPTION_PLANS

def generate_referral_code(user_id):
    """Generate a unique referral code"""
    import hashlib
    import random
    raw = f"{user_id}{random.randint(1000, 9999)}{datetime.now().timestamp()}"
    return hashlib.md5(raw.encode()).hexdigest()[:8].upper()

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'LinkedIn Easy Apply Bot API is running'})

@app.route('/', methods=['GET'])
def home():
    """Home page endpoint"""
    return jsonify({
        'message': 'LinkedIn Easy Apply Bot API',
        'status': 'running',
        'version': '1.0.0'
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        from validation import validate_user_registration, sanitize_input
        from rate_limiter import auth_rate_limit
    except ImportError:
        pass  # Use fallback validation
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate registration data
    try:
        is_valid, error_msg = validate_user_registration(data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
    except:
        # Fallback validation
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
    
    # Sanitize inputs
    try:
        data['email'] = sanitize_input(data['email'])
        if data.get('first_name'):
            data['first_name'] = sanitize_input(data['first_name'])
        if data.get('last_name'):
            data['last_name'] = sanitize_input(data['last_name'])
    except:
        pass  # Continue with original data if sanitize fails
    
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute('SELECT id FROM users WHERE email = ?', (data['email'],))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create new user
    user_id = str(uuid.uuid4())
    password_hash = generate_password_hash(data['password'])
    referral_code = generate_referral_code(user_id)
    
    cursor.execute('''
        INSERT INTO users (id, email, password_hash, first_name, last_name, phone, linkedin, website, 
                          subscription_plan, daily_quota, daily_usage, referral_code, referred_by, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, data['email'], password_hash,
        data.get('first_name', ''), data.get('last_name', ''),
        data.get('phone', ''), data.get('linkedin', ''), data.get('website', ''),
        'free', 5, 0, referral_code, data.get('referred_by', ''), 'pending'
    ))
    
    conn.commit()
    conn.close()
    
    # Return success response
    return jsonify({
        'message': 'Account created successfully! Your account is pending admin approval. You will receive an email once approved.',
        'status': 'pending',
        'user': {
            'id': user_id,
            'email': data['email'],
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', ''),
            'status': 'pending'
        },
        'token': None  # No token until approved
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        from rate_limiter import auth_rate_limit
    except ImportError:
        pass
    
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, password_hash, first_name, last_name, status, is_admin FROM users WHERE email = ?', (data['email'],))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check password with error handling for different hash formats
    try:
        password_valid = check_password_hash(user[1], data['password'])
    except (TypeError, ValueError) as e:
        # Handle old or incompatible password hash formats
        print(f"Password hash check failed for user {data['email']}: {e}")
        # Regenerate password hash for this user
        from werkzeug.security import generate_password_hash
        new_hash = generate_password_hash(data['password'], method='pbkdf2:sha256:260000')
        cursor.execute('UPDATE users SET password_hash = ? WHERE email = ?', (new_hash, data['email']))
        conn.commit()
        password_valid = True  # Accept the login since they provided the correct password
    
    if not password_valid:
        conn.close()
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check user approval status
    user_status = user[4]
    is_admin = user[5]
    
    if user_status == 'pending':
        conn.close()
        return jsonify({
            'error': 'Account pending approval', 
            'message': 'Your account is awaiting admin approval. You will receive an email once approved.',
            'status': 'pending'
        }), 403
    elif user_status == 'rejected':
        conn.close()
        return jsonify({
            'error': 'Account access denied',
            'message': 'Your account has been declined. Please contact support for more information.',
            'status': 'rejected'
        }), 403
    elif user_status != 'approved':
        conn.close()
        return jsonify({'error': 'Account status invalid'}), 403
    
    conn.close()
    
    # Generate token
    token = jwt.encode({
        'user_id': user[0],
        'exp': datetime.utcnow() + timedelta(days=30)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    # Ensure token is a string (PyJWT 2.x returns string, but let's be safe)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    return jsonify({
        'token': token,
        'user': {
            'id': user[0],
            'email': data['email'],
            'first_name': user[2],
            'last_name': user[3],
            'isAdmin': bool(is_admin)  # Ensure proper boolean conversion and use camelCase
        }
    })

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Handle forgot password requests"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].lower().strip()
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        conn = sqlite3.connect('easyapply.db')
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id, first_name FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user:
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            reset_expires = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
            
            # Store reset token in database
            cursor.execute('''
                INSERT OR REPLACE INTO password_resets (user_id, token, expires_at, created_at)
                VALUES (?, ?, ?, ?)
            ''', (user[0], reset_token, reset_expires.isoformat(), datetime.utcnow().isoformat()))
            
            conn.commit()
            
            # Create reset URL
            reset_url = f"{request.host_url}auth/reset-password?token={reset_token}"
            
            # TODO: Send email with reset link
            # For now, we'll just log it (in production, integrate with email service)
            print(f"Password reset requested for {email}")
            print(f"Reset URL: {reset_url}")
            
            # Always return success to prevent email enumeration
            conn.close()
            return jsonify({
                'message': 'If an account with that email exists, you will receive password reset instructions.',
                'success': True
            })
        else:
            # Still return success to prevent email enumeration
            conn.close()
            return jsonify({
                'message': 'If an account with that email exists, you will receive password reset instructions.',
                'success': True
            })
            
    except Exception as e:
        print(f"Forgot password error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/applications', methods=['GET'])
@token_required
def get_applications(current_user_id):
    # Use the correct database path
    db_path = os.path.join(os.path.dirname(__file__), 'easyapply.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"🔍 APPLICATIONS API: Looking for applications for user_id: {current_user_id}")
    
    cursor.execute('''
        SELECT id, job_title, company, location, job_url, status, applied_at, 
               resume_used, cover_letter_used, notes, ai_generated
        FROM job_applications 
        WHERE user_id = ? 
        ORDER BY applied_at DESC
    ''', (current_user_id,))
    
    applications = []
    for row in cursor.fetchall():
        applications.append({
            'id': row[0],
            'jobTitle': row[1],
            'company': row[2],
            'location': row[3],
            'jobUrl': row[4],
            'status': row[5],
            'appliedAt': row[6],
            'resumeUsed': row[7],
            'coverLetterUsed': row[8],
            'notes': row[9],
            'aiGenerated': bool(row[10])
        })
    
    print(f"🔍 APPLICATIONS API: Found {len(applications)} applications for user {current_user_id}")
    
    # Check if no applications found, let's see what's in the database
    if len(applications) == 0:
        cursor.execute('SELECT DISTINCT user_id FROM job_applications')
        all_users = cursor.fetchall()
        print(f"🔍 APPLICATIONS API: All user_ids in database: {[user[0] for user in all_users]}")
        
        cursor.execute('SELECT COUNT(*) FROM job_applications')
        total_count = cursor.fetchone()[0]
        print(f"🔍 APPLICATIONS API: Total applications in database: {total_count}")
    
    conn.close()
    
    # FIX: Return in the format the frontend expects
    return jsonify({
        'applications': applications,
        'total': len(applications)
    })

@app.route('/api/applications/<application_id>', methods=['PUT'])
@token_required
def update_application(current_user_id, application_id):
    """Update an application's status and notes"""
    try:
        data = request.get_json()
        status = data.get('status')
        notes = data.get('notes', '')
        
        conn = sqlite3.connect('easyapply.db')
        cursor = conn.cursor()
        
        # Update the application
        cursor.execute('''
            UPDATE job_applications 
            SET status = ?, notes = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
        ''', (status, notes, datetime.now().isoformat(), application_id, current_user_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'message': 'Application not found or unauthorized'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Application updated successfully'})
        
    except Exception as e:
        return jsonify({'message': f'Error updating application: {str(e)}'}), 500

@app.route('/api/jobs/discovered', methods=['POST'])
@token_required
def save_discovered_job(current_user_id):
    """Save a job discovered during bot runs to the manual apply database"""
    try:
        data = request.get_json()
        title = data.get('title')
        company = data.get('company')
        location = data.get('location')
        url = data.get('url')
        description = data.get('description', '')
        salary = data.get('salary')
        
        # Generate a unique ID for the job
        import hashlib
        job_id = hashlib.md5(f"{title}_{company}_{url}".encode()).hexdigest()
        
        # Connect to job listings database
        conn = sqlite3.connect('backend/job_listings.db')
        cursor = conn.cursor()
        
        # Check if job already exists
        cursor.execute('SELECT id FROM job_listings WHERE id = ?', (job_id,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'message': 'Job already exists', 'job_id': job_id})
        
        # Categorize the job based on title/company
        category = categorize_job(title, company, description)
        experience_level = determine_experience_level(title, description)
        is_remote = 1 if 'remote' in location.lower() or 'remote' in title.lower() else 0
        
        # Insert the job
        cursor.execute('''
            INSERT INTO job_listings 
            (id, title, company, location, salary, posted_date, url, category, 
             description, is_remote, experience_level, source, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_id, title, company, location, salary, datetime.now().isoformat(),
            url, category, description, is_remote, experience_level,
            f'Bot Discovery - User {current_user_id}', '[]',
            datetime.now().isoformat(), datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Job saved successfully',
            'job_id': job_id,
            'category': category
        })
        
    except Exception as e:
        return jsonify({'message': f'Error saving job: {str(e)}'}), 500

def categorize_job(title, company, description):
    """Categorize a job based on title, company, and description"""
    title_lower = title.lower()
    desc_lower = description.lower() if description else ""
    
    if any(keyword in title_lower for keyword in ['software', 'engineer', 'developer', 'programming', 'coding', 'frontend', 'backend', 'fullstack', 'react', 'python', 'javascript']):
        return 'software'
    elif any(keyword in title_lower for keyword in ['data', 'analytics', 'scientist', 'machine learning', 'ai', 'ml']):
        return 'data'
    elif any(keyword in title_lower for keyword in ['security', 'cybersecurity', 'infosec']):
        return 'cybersecurity'
    elif any(keyword in title_lower for keyword in ['devops', 'infrastructure', 'cloud', 'aws', 'sysadmin']):
        return 'it'
    elif any(keyword in title_lower for keyword in ['product', 'pm', 'product manager']):
        return 'product'
    elif any(keyword in title_lower for keyword in ['design', 'ui', 'ux', 'designer']):
        return 'design'
    elif any(keyword in title_lower for keyword in ['sales', 'business development', 'account']):
        return 'sales'
    elif any(keyword in title_lower for keyword in ['marketing', 'growth', 'content']):
        return 'marketing'
    elif any(keyword in title_lower for keyword in ['finance', 'financial', 'accounting']):
        return 'finance'
    elif any(keyword in title_lower for keyword in ['hr', 'human resources', 'recruiting']):
        return 'hr'
    elif any(keyword in title_lower for keyword in ['operations', 'ops', 'logistics']):
        return 'operations'
    elif any(keyword in title_lower for keyword in ['legal', 'lawyer', 'attorney']):
        return 'legal'
    elif any(keyword in title_lower for keyword in ['education', 'teacher', 'instructor']):
        return 'education'
    elif any(keyword in title_lower for keyword in ['consulting', 'consultant']):
        return 'consulting'
    elif any(keyword in title_lower for keyword in ['engineering', 'mechanical', 'electrical']):
        return 'engineering'
    elif any(keyword in title_lower for keyword in ['startup', 'founder']):
        return 'startup'
    else:
        return 'other'

def determine_experience_level(title, description):
    """Determine experience level from job title and description"""
    text = (title + " " + (description or "")).lower()
    
    if any(keyword in text for keyword in ['intern', 'internship', 'entry', 'graduate', 'junior', 'new grad']):
        return 'entry'
    elif any(keyword in text for keyword in ['senior', 'lead', 'principal', 'staff', 'architect']):
        return 'senior'
    else:
        return 'mid'

@app.route('/api/applications/stats', methods=['GET'])
@token_required
def get_applications_stats(current_user_id):
    """Get statistics specifically for applications"""
    # Use the correct database path
    db_path = os.path.join(os.path.dirname(__file__), 'easyapply.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"🔍 APPLICATIONS STATS: Getting stats for user_id: {current_user_id}")
    
    # Total applications
    cursor.execute('SELECT COUNT(*) FROM job_applications WHERE user_id = ?', (current_user_id,))
    total_applications = cursor.fetchone()[0]
    
    # Applications this week
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    cursor.execute('SELECT COUNT(*) FROM job_applications WHERE user_id = ? AND applied_at > ?', 
                  (current_user_id, week_ago))
    applications_this_week = cursor.fetchone()[0]
    
    # Applications this month
    month_ago = (datetime.now() - timedelta(days=30)).isoformat()
    cursor.execute('SELECT COUNT(*) FROM job_applications WHERE user_id = ? AND applied_at > ?', 
                  (current_user_id, month_ago))
    applications_this_month = cursor.fetchone()[0]
    
    # Success rate (interviews + offers / total applications)
    cursor.execute('''
        SELECT COUNT(*) FROM job_applications 
        WHERE user_id = ? AND status IN ('interview', 'offer', 'accepted')
    ''', (current_user_id,))
    successful_applications = cursor.fetchone()[0]
    success_rate = (successful_applications / total_applications * 100) if total_applications > 0 else 0
    
    # Top companies
    cursor.execute('''
        SELECT company, COUNT(*) as count 
        FROM job_applications 
        WHERE user_id = ? 
        GROUP BY company 
        ORDER BY count DESC 
        LIMIT 5
    ''', (current_user_id,))
    top_companies = [{'company': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Applications by status
    cursor.execute('''
        SELECT status, COUNT(*) as count 
        FROM job_applications 
        WHERE user_id = ? 
        GROUP BY status
    ''', (current_user_id,))
    applications_by_status = [{'status': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    print(f"🔍 APPLICATIONS STATS: Found {total_applications} total applications for user {current_user_id}")
    
    # Check if no applications found, let's see what's in the database
    if total_applications == 0:
        cursor.execute('SELECT DISTINCT user_id FROM job_applications')
        all_users = cursor.fetchall()
        print(f"🔍 APPLICATIONS STATS: All user_ids in database: {[user[0] for user in all_users]}")
        
        cursor.execute('SELECT COUNT(*) FROM job_applications')
        total_count = cursor.fetchone()[0]
        print(f"🔍 APPLICATIONS STATS: Total applications in database: {total_count}")
    
    conn.close()
    
    return jsonify({
        'totalApplications': total_applications,
        'applicationsThisWeek': applications_this_week,
        'applicationsThisMonth': applications_this_month,
        'successRate': round(success_rate, 1),
        'averageResponseTime': 5.2,  # Mock data for now
        'topCompanies': top_companies,
        'applicationsByStatus': applications_by_status
    })

@app.route('/api/applications/<application_id>/status', methods=['PUT'])
@token_required
def update_application_status(current_user_id, application_id):
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'error': 'Status is required'}), 400
    
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE job_applications 
        SET status = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ? AND user_id = ?
    ''', (new_status, application_id, current_user_id))
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Application not found'}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Status updated successfully'})

@app.route('/api/dashboard/stats', methods=['GET'])
@token_required
def get_dashboard_stats(current_user_id):
    # Use the correct database path
    db_path = os.path.join(os.path.dirname(__file__), 'easyapply.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Total applications
    cursor.execute('SELECT COUNT(*) FROM job_applications WHERE user_id = ?', (current_user_id,))
    total_applications = cursor.fetchone()[0]
    
    # Applications this week
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    cursor.execute('SELECT COUNT(*) FROM job_applications WHERE user_id = ? AND applied_at > ?', 
                  (current_user_id, week_ago))
    applications_this_week = cursor.fetchone()[0]
    
    # Applications this month
    month_ago = (datetime.now() - timedelta(days=30)).isoformat()
    cursor.execute('SELECT COUNT(*) FROM job_applications WHERE user_id = ? AND applied_at > ?', 
                  (current_user_id, month_ago))
    applications_this_month = cursor.fetchone()[0]
    
    # Success rate (interviews + offers / total applications)
    cursor.execute('''
        SELECT COUNT(*) FROM job_applications 
        WHERE user_id = ? AND status IN ('interview', 'offer', 'accepted')
    ''', (current_user_id,))
    successful_applications = cursor.fetchone()[0]
    success_rate = (successful_applications / total_applications * 100) if total_applications > 0 else 0
    
    # Top companies
    cursor.execute('''
        SELECT company, COUNT(*) as count 
        FROM job_applications 
        WHERE user_id = ? 
        GROUP BY company 
        ORDER BY count DESC 
        LIMIT 5
    ''', (current_user_id,))
    top_companies = [{'company': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Applications by status
    cursor.execute('''
        SELECT status, COUNT(*) as count 
        FROM job_applications 
        WHERE user_id = ? 
        GROUP BY status
    ''', (current_user_id,))
    applications_by_status = [{'status': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'totalApplications': total_applications,
        'applicationsThisWeek': applications_this_week,
        'applicationsThisMonth': applications_this_month,
        'successRate': round(success_rate, 1),
        'averageResponseTime': 5.2,  # Mock data for now
        'topCompanies': top_companies,
        'applicationsByStatus': applications_by_status
    })

@app.route('/api/resume/upload', methods=['POST'])
@app.route('/api/upload/resume', methods=['POST'])
@token_required
def upload_resume(current_user_id):
    if 'file' not in request.files and 'resume' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files.get('file') or request.files.get('resume')
    if not file or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Enhanced file validation
    try:
        from security import validate_file_upload
        is_valid, error_msg = validate_file_upload(file)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
    except ImportError:
        # Fallback validation if security module not available
        allowed_extensions = ['.pdf', '.doc', '.docx']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Invalid file type. Please upload PDF, DOC, or DOCX files.'}), 400
        
        # Check file size (16MB limit)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)     # Reset to beginning
        if file_size > 16 * 1024 * 1024:
            return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 400
    
    # Generate secure filename
    file_ext = os.path.splitext(file.filename)[1].lower()
    timestamp = int(time.time())
    filename = f"{current_user_id}_{timestamp}_{secure_filename(file.filename)}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        # Save the file
        file.save(file_path)
        
        # Store resume info in database
        conn = sqlite3.connect('easyapply.db')
        cursor = conn.cursor()
        
        # Create resumes table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                original_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_type TEXT NOT NULL,
                is_default BOOLEAN DEFAULT FALSE,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Insert resume record
        resume_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO resumes (id, user_id, filename, original_name, file_path, 
                                file_size, file_type, is_default)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            resume_id, current_user_id, filename, file.filename,
            file_path, file_size if 'file_size' in locals() else 0, 
            file_ext, True  # Set as default if it's the first resume
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Resume uploaded successfully',
            'filename': filename,
            'originalName': file.filename,
            'resumeId': resume_id,
            'path': file_path,
            'size': file_size if 'file_size' in locals() else 0
        })
        
    except Exception as e:
        # Clean up file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': f'Failed to save resume: {str(e)}'}), 500

@app.route('/api/resumes', methods=['GET'])
@token_required
def get_user_resumes(current_user_id):
    """Get all resumes for the current user"""
    try:
        conn = sqlite3.connect('easyapply.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, filename, original_name, file_size, file_type, 
                   is_default, uploaded_at
            FROM resumes 
            WHERE user_id = ? 
            ORDER BY uploaded_at DESC
        ''', (current_user_id,))
        
        resumes = []
        for row in cursor.fetchall():
            resumes.append({
                'id': row[0],
                'filename': row[1],
                'originalName': row[2],
                'fileSize': row[3],
                'fileType': row[4],
                'isDefault': bool(row[5]),
                'uploadedAt': row[6]
            })
        
        conn.close()
        return jsonify({'resumes': resumes})
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve resumes: {str(e)}'}), 500

@app.route('/api/resumes/<resume_id>/download', methods=['GET'])
@token_required
def download_resume(current_user_id, resume_id):
    """Download a specific resume"""
    try:
        conn = sqlite3.connect('easyapply.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT file_path, original_name FROM resumes 
            WHERE id = ? AND user_id = ?
        ''', (resume_id, current_user_id))
        
        resume = cursor.fetchone()
        conn.close()
        
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        file_path, original_name = resume
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Resume file not found on disk'}), 404
        
        return send_file(file_path, as_attachment=True, 
                        download_name=original_name)
        
    except Exception as e:
        return jsonify({'error': f'Failed to download resume: {str(e)}'}), 500

@app.route('/api/resumes/<resume_id>', methods=['DELETE'])
@token_required
def delete_resume(current_user_id, resume_id):
    """Delete a specific resume"""
    try:
        conn = sqlite3.connect('easyapply.db')
        cursor = conn.cursor()
        
        # Get file path before deleting
        cursor.execute('''
            SELECT file_path FROM resumes 
            WHERE id = ? AND user_id = ?
        ''', (resume_id, current_user_id))
        
        resume = cursor.fetchone()
        if not resume:
            conn.close()
            return jsonify({'error': 'Resume not found'}), 404
        
        file_path = resume[0]
        
        # Delete from database
        cursor.execute('''
            DELETE FROM resumes WHERE id = ? AND user_id = ?
        ''', (resume_id, current_user_id))
        
        conn.commit()
        conn.close()
        
        # Delete file from disk
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({'message': 'Resume deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete resume: {str(e)}'}), 500

@app.route('/api/stripe/create-checkout-session', methods=['POST'])
@token_required
def create_checkout_session(current_user_id):
    try:
        data = request.get_json()
        plan_id = data.get('plan_id')
        
        if plan_id not in ['basic', 'pro']:
            return jsonify({'error': 'Invalid plan'}), 400
        
        plan = SUBSCRIPTION_PLANS[plan_id]
        
        # Get or create Stripe customer
        conn = sqlite3.connect('easyapply.db')
        cursor = conn.cursor()
        cursor.execute('SELECT email, stripe_customer_id FROM users WHERE id = ?', (current_user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        email, stripe_customer_id = user_data
        
        # Create or retrieve Stripe customer
        if not stripe_customer_id:
            customer = stripe.Customer.create(
                email=email,
                metadata={'user_id': current_user_id}
            )
            stripe_customer_id = customer.id
            
            # Update user with Stripe customer ID
            cursor.execute('''
                UPDATE users SET stripe_customer_id = ? WHERE id = ?
            ''', (stripe_customer_id, current_user_id))
            conn.commit()
        
        conn.close()
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': plan['stripe_price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/dashboard?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/pricing",
            metadata={
                'user_id': current_user_id,
                'plan_id': plan_id
            }
        )
        
        return jsonify({'checkout_url': session.url})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stripe/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle subscription events
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_completed(session)
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        handle_payment_succeeded(invoice)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_cancelled(subscription)
    
    return jsonify({'status': 'success'})

def handle_checkout_completed(session):
    """Handle successful checkout"""
    user_id = session['metadata']['user_id']
    plan_id = session['metadata']['plan_id']
    subscription_id = session['subscription']
    
    # Get subscription details
    subscription = stripe.Subscription.retrieve(subscription_id)
    plan_quota = SUBSCRIPTION_PLANS[plan_id]['daily_quota']
    
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    # Update user subscription
    cursor.execute('''
        UPDATE users 
        SET subscription_plan = ?, subscription_id = ?, subscription_status = ?,
            current_period_end = ?, daily_quota = ?, daily_usage = 0
        WHERE id = ?
    ''', (
        plan_id, subscription_id, subscription['status'],
        datetime.fromtimestamp(subscription['current_period_end']).isoformat(),
        plan_quota, user_id
    ))
    
    # Log billing event
    cursor.execute('''
        INSERT INTO billing_events (id, user_id, stripe_event_id, event_type, 
                                   subscription_plan, amount, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        str(uuid.uuid4()), user_id, session['id'], 'checkout_completed',
        plan_id, session['amount_total'], 'succeeded'
    ))
    
    conn.commit()
    conn.close()

def handle_payment_succeeded(invoice):
    """Handle successful payment"""
    customer_id = invoice['customer']
    subscription_id = invoice['subscription']
    
    # Get user by Stripe customer ID
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, subscription_plan FROM users WHERE stripe_customer_id = ?', (customer_id,))
    user_data = cursor.fetchone()
    
    if user_data:
        user_id, plan = user_data
        
        # Log billing event
        cursor.execute('''
            INSERT INTO billing_events (id, user_id, stripe_event_id, event_type,
                                       subscription_plan, amount, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(uuid.uuid4()), user_id, invoice['id'], 'payment_succeeded',
            plan, invoice['amount_paid'], 'succeeded'
        ))
        
        conn.commit()
    
    conn.close()

def handle_subscription_cancelled(subscription):
    """Handle subscription cancellation"""
    customer_id = subscription['customer']
    
    # Get user by Stripe customer ID
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE stripe_customer_id = ?', (customer_id,))
    user_data = cursor.fetchone()
    
    if user_data:
        user_id = user_data[0]
        
        # Downgrade to free plan
        cursor.execute('''
            UPDATE users 
            SET subscription_plan = 'free', subscription_id = NULL, 
                subscription_status = 'cancelled', daily_quota = 5
            WHERE id = ?
        ''', (user_id,))
        
        # Log billing event
        cursor.execute('''
            INSERT INTO billing_events (id, user_id, stripe_event_id, event_type,
                                       subscription_plan, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            str(uuid.uuid4()), user_id, subscription['id'], 'subscription_cancelled',
            'free', 'cancelled'
        ))
        
        conn.commit()
    
    conn.close()

@app.route('/api/agent/start', methods=['POST'])
@token_required
def start_agent(current_user_id):
    if current_user_id in active_bots:
        return jsonify({'error': 'Agent is already running'}), 409
    
    # Check if user has LinkedIn credentials
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT linkedin_email_encrypted, linkedin_password_encrypted 
        FROM users WHERE id = ?
    ''', (current_user_id,))
    
    creds = cursor.fetchone()
    conn.close()
    
    if not creds or not creds[0] or not creds[1]:
        return jsonify({
            'error': 'LinkedIn credentials not configured',
            'message': 'Please go to your Profile page to add your LinkedIn credentials before starting the agent.'
        }), 400

    # Check quota before starting
    if not can_use_quota(current_user_id, 1):
        success, usage, quota = check_and_reset_daily_quota(current_user_id)
        return jsonify({
            'error': 'Daily quota exceeded',
            'usage': usage,
            'quota': quota,
            'message': f'You have used {usage}/{quota} applications today. Upgrade your plan for more applications.'
        }), 429
    
    data = request.get_json()
    max_applications = data.get('max_applications', 10)
    
    # Limit max applications to remaining quota
    success, usage, quota = check_and_reset_daily_quota(current_user_id)
    remaining_quota = quota - usage
    max_applications = min(max_applications, remaining_quota)
    
    # Load user's config or create default
    config = load_user_config(current_user_id)
    
    # Decrypt LinkedIn credentials and load user data
    try:
        from security import decrypt_data
        linkedin_email = decrypt_data(creds[0])
        linkedin_password = decrypt_data(creds[1])
        
        if not linkedin_email or not linkedin_password:
            return jsonify({
                'error': 'Failed to decrypt LinkedIn credentials',
                'message': 'Please update your LinkedIn credentials in your profile.'
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Security module error',
            'message': 'Failed to decrypt credentials. Please contact support.'
        }), 500
    
    # Load full user data for config creation
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT linkedin_email_encrypted, linkedin_password_encrypted, personal_info, job_preferences, subscription_plan
        FROM users WHERE id = ?
    ''', (current_user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if not user_data:
        return jsonify({
            'error': 'User data not found',
            'message': 'Unable to load user configuration.'
        }), 404
    
    def log_activity(action, details, status='info', metadata=None):
        """Log bot activity for live updates"""
        try:
            conn = sqlite3.connect('easyapply.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO activity_log (user_id, action, details, status, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (current_user_id, action, details, status, json.dumps(metadata or {})))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Failed to log activity: {e}")

    def run_bot():
        try:
            log_activity("Bot Starting", "🚀 Initializing LinkedIn Easy Apply bot...", "info")
            
            # Create user-specific config file
            user_config_path = f'user_config_{current_user_id}.yaml'
            user_config = create_user_config(user_data, linkedin_email, linkedin_password, current_user_id)
            
            with open(user_config_path, 'w') as f:
                import yaml
                yaml.dump(user_config, f)
                
            log_activity("Configuration", f"✅ User configuration created for {linkedin_email}", "success")
            
            # Create web platform bot instance
            if WebPlatformLinkedInBot is None:
                raise Exception("Bot functionality is not available in this environment. Please run locally for full bot features.")
            
            bot = WebPlatformLinkedInBot(current_user_id, user_config)
            active_bots[current_user_id] = bot
            
            log_activity("LinkedIn Login", "🔐 Connecting to LinkedIn...", "info")
            
            # Set up status callback that also logs activities
            def status_callback(status_data):
                bot_status[current_user_id] = {
                    **status_data,
                    'started_at': bot_status.get(current_user_id, {}).get('started_at', datetime.now().isoformat())
                }
                
                # Log status changes as activities
                if status_data.get('current_task'):
                    log_activity("Status Update", status_data['current_task'], "info", {
                        'progress': status_data.get('progress', 0),
                        'applications': status_data.get('applications_submitted', 0)
                    })
                
                if status_data['status'] in ['completed', 'error', 'stopped']:
                    bot_status[current_user_id]['completed_at'] = datetime.now().isoformat()
                    if status_data['status'] == 'completed':
                        log_activity("Bot Completed", "✅ Bot session completed successfully", "success")
                    elif status_data['status'] == 'error':
                        log_activity("Bot Error", f"❌ Bot encountered an error: {status_data.get('error', 'Unknown error')}", "error")
                    elif status_data['status'] == 'stopped':
                        log_activity("Bot Stopped", "⏹️ Bot stopped by user", "info")
            
            bot.set_status_callback(status_callback)
            
            # Initialize status
            bot_status[current_user_id] = {
                'status': 'starting',
                'progress': 0,
                'current_task': 'Initializing agent...',
                'applications_submitted': 0,
                'started_at': datetime.now().isoformat()
            }
            
            log_activity("Job Search", "🔍 Starting job search and application process...", "info")
            
            # Run the bot
            applications_made = bot.run_applications(
                max_applications=max_applications, 
                continuous=data.get('continuous', False)
            )
            
            log_activity("Session Complete", f"🎉 Applied to {applications_made} jobs in this session", "success", {
                'applications_made': applications_made,
                'session_duration': (datetime.now() - datetime.fromisoformat(bot_status[current_user_id]['started_at'])).total_seconds()
            })
            
        except Exception as e:
            error_msg = str(e)
            log_activity("Bot Error", f"❌ Fatal error: {error_msg}", "error", {'error_details': error_msg})
            bot_status[current_user_id] = {
                'status': 'error',
                'error': error_msg,
                'completed_at': datetime.now().isoformat()
            }
        finally:
            if current_user_id in active_bots:
                del active_bots[current_user_id]
    
    # Start bot in background thread
    thread = threading.Thread(target=run_bot)
    thread.start()
    
    return jsonify({'message': 'Agent started successfully'})

@app.route('/api/agent/stop', methods=['POST'])
@token_required
def stop_agent(current_user_id):
    if current_user_id not in active_bots:
        return jsonify({'error': 'No agent is currently running'}), 404
    
    # Stop the bot
    bot = active_bots[current_user_id]
    bot.stop_applications()
    
    return jsonify({'message': 'Stop signal sent to agent'})

@app.route('/api/agent/status', methods=['GET'])
@token_required
def get_agent_status(current_user_id):
    status = bot_status.get(current_user_id, {
        'status': 'idle',
        'progress': 0,
        'current_task': 'Agent is not running',
        'applications_submitted': 0
    })
    
    return jsonify(status)

def load_user_config(user_id):
    """Load user-specific configuration from database"""
    try:
        # Ensure we use the correct database path
        db_path = os.path.join(os.path.dirname(__file__), '..', 'easyapply.db')
        if not os.path.exists(db_path):
            db_path = 'easyapply.db'  # fallback to current directory
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get user data and LinkedIn credentials
        cursor.execute('''
            SELECT first_name, last_name, phone, website, linkedin_email_encrypted, linkedin_password_encrypted
            FROM users WHERE id = ?
        ''', (user_id,))
        
        user_data = cursor.fetchone()
        if not user_data:
            conn.close()
            return None
        
        # Get user preferences
        cursor.execute('''
            SELECT job_titles, locations, remote, experience, salary_min, skills
            FROM user_preferences WHERE user_id = ?
        ''', (user_id,))
        
        preferences = cursor.fetchone()
        conn.close()
        
        # Decrypt LinkedIn credentials
        linkedin_email = ''
        linkedin_password = ''
        if user_data[4] and user_data[5]:  # linkedin_email_encrypted, linkedin_password_encrypted
            try:
                from security import decrypt_data
                linkedin_email = decrypt_data(user_data[4]) or ''
                linkedin_password = decrypt_data(user_data[5]) or ''
            except Exception as e:
                print(f"Failed to decrypt LinkedIn credentials for user {user_id}: {e}")
        
        # Create user-specific config
        config = {
            # LinkedIn credentials
            'email': linkedin_email,
            'password': linkedin_password,
            
            # Personal info
            'personalInfo': {
                'First Name': user_data[0] or '',
                'Last Name': user_data[1] or '',
                'Phone': user_data[2] or '',
                'Website': user_data[3] or '',
            },
            
            # Job search preferences
            'positions': [],
            'locations': [],
            'remote': True,
            'experience': 'mid',
            'salary': '',
            'skills': '',
            
            # Default settings
            'uploads': {},
            'debug': False,
            'eeo': {
                'veteran': False,
                'disability': False,
                'citizenship': True,
                'clearance': False
            }
        }
        
        # Add job preferences if they exist
        if preferences:
            if preferences[0]:  # job_titles
                config['positions'] = safe_split_to_list(preferences[0])
            if preferences[1]:  # locations
                config['locations'] = safe_split_to_list(preferences[1])
            if preferences[2] is not None:  # remote
                config['remote'] = bool(preferences[2])
            if preferences[3]:  # experience
                config['experience'] = preferences[3]
            if preferences[4]:  # salary_min
                config['salary'] = preferences[4]
            if preferences[5]:  # skills
                config['skills'] = preferences[5]
        
        # Set defaults if no preferences
        if not config['positions']:
            config['positions'] = ['Software Engineer', 'Developer']
        if not config['locations']:
            config['locations'] = ['Remote', 'Any']
        
        # Load base config for additional settings
        try:
            with open('config.yaml', 'r') as f:
                base_config = yaml.safe_load(f)
                # Merge base config settings (excluding user-specific ones)
                for key in ['uploads', 'debug', 'eeo', 'personalInfo']:
                    if key in base_config and key not in ['email', 'password', 'positions', 'locations']:
                        if key == 'personalInfo':
                            # Merge personal info, prioritizing user database data
                            base_personal = base_config.get('personalInfo', {})
                            user_personal = config.get('personalInfo', {})
                            merged_personal = {**base_personal, **user_personal}
                            config['personalInfo'] = merged_personal
                        else:
                            config[key] = base_config[key]
        except Exception as e:
            print(f"Could not load base config.yaml: {e}")
        
        return config
        
    except Exception as e:
        print(f"Error loading user config for {user_id}: {e}")
        # Return basic default config
        return {
            'email': '',
            'password': '',
            'positions': ['Software Engineer'],
            'locations': ['Remote'],
            'remote': True,
            'personalInfo': {
                'First Name': '',
                'Last Name': '',
            }
        }

# Admin endpoints
@app.route('/api/admin/users', methods=['GET'])
@token_required
@admin_required
def get_all_users(current_user_id):
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, email, first_name, last_name, subscription_plan, 
               daily_quota, daily_usage, subscription_status, created_at,
               stripe_customer_id, current_period_end, status, is_admin
        FROM users 
        ORDER BY created_at DESC
    ''')
    
    users = []
    for row in cursor.fetchall():
        users.append({
            'id': row[0],
            'email': row[1],
            'first_name': row[2],
            'last_name': row[3],
            'subscription_plan': row[4],
            'daily_quota': row[5],
            'daily_usage': row[6],
            'subscription_status': row[7],
            'created_at': row[8],
            'stripe_customer_id': row[9],
            'current_period_end': row[10],
            'status': row[11],
            'is_admin': row[12]
        })
    
    conn.close()
    return jsonify(users)

@app.route('/api/admin/stats', methods=['GET'])
@token_required
@admin_required
def get_admin_stats(current_user_id):
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    # Total users
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    # Pending users
    cursor.execute('SELECT COUNT(*) FROM users WHERE status = "pending"')
    pending_users = cursor.fetchone()[0]
    
    # Users by plan
    cursor.execute('''
        SELECT subscription_plan, COUNT(*) as count 
        FROM users 
        GROUP BY subscription_plan
    ''')
    users_by_plan = [{'plan': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Total applications
    cursor.execute('SELECT COUNT(*) FROM job_applications')
    total_applications = cursor.fetchone()[0]
    
    # Applications this month
    month_ago = (datetime.now() - timedelta(days=30)).isoformat()
    cursor.execute('SELECT COUNT(*) FROM job_applications WHERE applied_at > ?', (month_ago,))
    applications_this_month = cursor.fetchone()[0]
    
    # Revenue (from billing events)
    cursor.execute('''
        SELECT SUM(amount) FROM billing_events 
        WHERE event_type = 'payment_succeeded' AND created_at > ?
    ''', (month_ago,))
    revenue_result = cursor.fetchone()[0]
    monthly_revenue = revenue_result / 100 if revenue_result else 0  # Convert from cents
    
    conn.close()
    
    return jsonify({
        'total_users': total_users,
        'pending_users': pending_users,
        'users_by_plan': users_by_plan,
        'total_applications': total_applications,
        'applications_this_month': applications_this_month,
        'monthly_revenue': monthly_revenue
    })

@app.route('/api/admin/users/<user_id>', methods=['GET'])
@token_required
@admin_required
def get_user_details(current_user_id, user_id):
    """Get detailed information about a specific user"""
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, email, first_name, last_name, phone, linkedin, website,
               subscription_plan, daily_quota, daily_usage, subscription_status,
               is_admin, status, referral_code, referred_by, created_at, updated_at,
               stripe_customer_id, current_period_end
        FROM users WHERE id = ?
    ''', (user_id,))
    
    user_data = cursor.fetchone()
    if not user_data:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    # Get user's application count
    cursor.execute('SELECT COUNT(*) FROM job_applications WHERE user_id = ?', (user_id,))
    application_count = cursor.fetchone()[0]
    
    # Get user's recent applications
    cursor.execute('''
        SELECT job_title, company, location, status, applied_at
        FROM job_applications 
        WHERE user_id = ? 
        ORDER BY applied_at DESC 
        LIMIT 10
    ''', (user_id,))
    
    recent_applications = []
    for app in cursor.fetchall():
        recent_applications.append({
            'job_title': app[0],
            'company': app[1],
            'location': app[2],
            'status': app[3],
            'applied_at': app[4]
        })
    
    conn.close()
    
    user_details = {
        'id': user_data[0],
        'email': user_data[1],
        'first_name': user_data[2],
        'last_name': user_data[3],
        'phone': user_data[4],
        'linkedin': user_data[5],
        'website': user_data[6],
        'subscription_plan': user_data[7],
        'daily_quota': user_data[8],
        'daily_usage': user_data[9],
        'subscription_status': user_data[10],
        'is_admin': user_data[11],
        'status': user_data[12],
        'referral_code': user_data[13],
        'referred_by': user_data[14],
        'created_at': user_data[15],
        'updated_at': user_data[16],
        'stripe_customer_id': user_data[17],
        'current_period_end': user_data[18],
        'application_count': application_count,
        'recent_applications': recent_applications
    }
    
    return jsonify(user_details)

@app.route('/api/admin/users/<user_id>', methods=['PUT'])
@token_required
@admin_required
def update_user(current_user_id, user_id):
    """Update user information (admin only)"""
    data = request.get_json()
    
    # Map frontend camelCase to database snake_case
    field_mapping = {
        'first_name': 'first_name',
        'last_name': 'last_name', 
        'email': 'email',
        'phone': 'phone',
        'linkedin': 'linkedin',
        'website': 'website',
        'subscription_plan': 'subscription_plan',
        'daily_quota': 'daily_quota',
        'isAdmin': 'is_admin',  # Map camelCase to snake_case
        'status': 'status'
    }
    
    update_fields = []
    update_values = []
    
    for frontend_field, db_field in field_mapping.items():
        if frontend_field in data:
            update_fields.append(f'{db_field} = ?')
            update_values.append(data[frontend_field])
    
    if not update_fields:
        return jsonify({'error': 'No valid fields to update'}), 400
    
    update_values.append(user_id)
    
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    try:
        query = f"UPDATE users SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        cursor.execute(query, update_values)
        
        if cursor.rowcount == 0:
            conn.rollback()
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'User updated successfully'})
    
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/admin/users/<user_id>/approve', methods=['POST'])
@token_required
@admin_required
def approve_user(current_user_id, user_id):
    """Approve a pending user"""
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    try:
        # First get user details before updating
        cursor.execute('''
            SELECT email, first_name, last_name
            FROM users 
            WHERE id = ? AND status = 'pending'
        ''', (user_id,))
        
        user_data = cursor.fetchone()
        if not user_data:
            conn.close()
            return jsonify({'error': 'User not found or already processed'}), 404
        
        user_email, first_name, last_name = user_data
        user_name = f"{first_name} {last_name}".strip()
        
        # Update user status
        cursor.execute('''
            UPDATE users 
            SET status = 'approved', updated_at = CURRENT_TIMESTAMP 
            WHERE id = ? AND status = 'pending'
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        # Send approval email notification
        try:
            email_sent = email_service.send_approval_email(user_email, user_name)
            if email_sent:
                print(f"✅ Approval email sent to {user_email}")
            else:
                print(f"⚠️ Failed to send approval email to {user_email}")
        except Exception as e:
            print(f"❌ Email error for {user_email}: {e}")
        
        return jsonify({
            'message': 'User approved successfully',
            'email_sent': email_sent if 'email_sent' in locals() else False
        })
    
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/admin/users/<user_id>/reject', methods=['POST'])
@token_required
@admin_required
def reject_user(current_user_id, user_id):
    """Reject a pending user"""
    data = request.get_json() or {}
    reason = data.get('reason', '')
    
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    try:
        # First get user details before updating
        cursor.execute('''
            SELECT email, first_name, last_name
            FROM users 
            WHERE id = ? AND status = 'pending'
        ''', (user_id,))
        
        user_data = cursor.fetchone()
        if not user_data:
            conn.close()
            return jsonify({'error': 'User not found or already processed'}), 404
        
        user_email, first_name, last_name = user_data
        user_name = f"{first_name} {last_name}".strip()
        
        # Update user status
        cursor.execute('''
            UPDATE users 
            SET status = 'rejected', updated_at = CURRENT_TIMESTAMP 
            WHERE id = ? AND status = 'pending'
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        # Send rejection email notification
        try:
            email_sent = email_service.send_rejection_email(user_email, user_name, reason)
            if email_sent:
                print(f"✅ Rejection email sent to {user_email}")
            else:
                print(f"⚠️ Failed to send rejection email to {user_email}")
        except Exception as e:
            print(f"❌ Email error for {user_email}: {e}")
        
        return jsonify({
            'message': 'User rejected successfully',
            'email_sent': email_sent if 'email_sent' in locals() else False
        })
    
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/admin/trigger-daily-applications', methods=['POST'])
@token_required
@admin_required
def trigger_daily_applications(current_user_id):
    """Manually trigger daily applications for testing (admin only)"""
    try:
        from daily_application_scheduler import daily_app_scheduler
        
        # Run in background thread to avoid blocking the request
        import threading
        thread = threading.Thread(target=daily_app_scheduler.run_daily_applications)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'Daily applications triggered successfully for all eligible users',
            'status': 'running',
            'triggered_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'message': f'Error triggering daily applications: {str(e)}'}), 500

@app.route('/api/admin/users/pending', methods=['GET'])
@token_required
@admin_required
def get_pending_users(current_user_id):
    """Get all users pending approval"""
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, email, first_name, last_name, created_at
        FROM users 
        WHERE status = 'pending'
        ORDER BY created_at ASC
    ''')
    
    pending_users = []
    for row in cursor.fetchall():
        pending_users.append({
            'id': row[0],
            'email': row[1],
            'first_name': row[2],
            'last_name': row[3],
            'created_at': row[4]
        })
    
    conn.close()
    return jsonify(pending_users)

@app.route('/api/admin/users/<user_id>/delete', methods=['DELETE'])
@token_required
@admin_required
def delete_user(current_user_id, user_id):
    """Delete a user and all associated data"""
    if user_id == current_user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    try:
        # Delete user's applications first (foreign key constraint)
        cursor.execute('DELETE FROM job_applications WHERE user_id = ?', (user_id,))
        
        # Delete user's agent tasks
        cursor.execute('DELETE FROM agent_tasks WHERE user_id = ?', (user_id,))
        
        # Delete user's usage logs
        cursor.execute('DELETE FROM usage_logs WHERE user_id = ?', (user_id,))
        
        # Delete user's billing events
        cursor.execute('DELETE FROM billing_events WHERE user_id = ?', (user_id,))
        
        # Delete the user
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        if cursor.rowcount == 0:
            conn.rollback()
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'User deleted successfully'})
    
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

# Profile management endpoints
@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user_id):
    """Get user profile including encrypted LinkedIn credentials"""
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    # Get user data including JSON fields
    cursor.execute('''
        SELECT first_name, last_name, email, phone, linkedin, website,
               linkedin_email_encrypted, linkedin_password_encrypted,
               personal_info, job_preferences
        FROM users WHERE id = ?
    ''', (current_user_id,))
    
    user_data = cursor.fetchone()
    if not user_data:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    # Get job preferences (stored in config table)
    cursor.execute('''
        SELECT job_titles, locations, remote, experience, salary_min, skills
        FROM user_preferences WHERE user_id = ?
    ''', (current_user_id,))
    
    preferences = cursor.fetchone()
    
    # Get expanded profile data
    # Personal Details
    cursor.execute('''
        SELECT pronouns, phone_country_code, street_address, city, state, zip_code,
               linkedin_url, portfolio_website, message_to_manager, university_gpa,
               notice_period, weekend_work, evening_work, drug_test, background_check
        FROM user_personal_details WHERE user_id = ?
    ''', (current_user_id,))
    personal_details = cursor.fetchone()
    
    # Work Authorization
    cursor.execute('''
        SELECT drivers_license, require_visa, legally_authorized, security_clearance,
               us_citizen, degree_completed
        FROM user_work_authorization WHERE user_id = ?
    ''', (current_user_id,))
    work_auth = cursor.fetchone()
    
    # Skills & Experience
    cursor.execute('''
        SELECT languages_json, technical_skills_json, years_experience_json
        FROM user_skills_experience WHERE user_id = ?
    ''', (current_user_id,))
    skills_exp = cursor.fetchone()
    
    # EEO Information
    cursor.execute('''
        SELECT gender, race, veteran, disability
        FROM user_eeo_info WHERE user_id = ?
    ''', (current_user_id,))
    eeo_info = cursor.fetchone()
    
    conn.close()
    
    # Parse JSON fields
    personal_info_json = json.loads(user_data[8]) if user_data[8] else {}
    job_preferences_json = json.loads(user_data[9]) if user_data[9] else {}
    
    # Decrypt LinkedIn credentials
    linkedin_creds = {'email': '', 'password': '', 'hasCredentials': False}
    if user_data[6] and user_data[7]:  # linkedin_email_encrypted, linkedin_password_encrypted
        linkedin_creds['hasCredentials'] = True  # Mark that credentials exist in database
        try:
            from security import decrypt_data
            linkedin_email = decrypt_data(user_data[6])
            linkedin_password = decrypt_data(user_data[7])
            if linkedin_email and linkedin_password:
                linkedin_creds = {
                    'email': linkedin_email,
                    'password': linkedin_password,
                    'hasCredentials': True
                }
        except Exception as e:
            print(f"Failed to decrypt LinkedIn credentials: {e}")
            # Keep hasCredentials=True even if decryption fails
    
    response_data = {
        'user': {
            'firstName': user_data[0] or '',
            'lastName': user_data[1] or '',
            'email': user_data[2] or '',
            'phone': user_data[3] or '',
            'linkedin': user_data[4] or '',
            'website': user_data[5] or ''
        },
        'linkedinCreds': linkedin_creds,
        'jobPreferences': {
            'jobTitles': job_preferences_json.get('jobTitles') or (preferences[0] if preferences else ''),
            'locations': job_preferences_json.get('locations') or (preferences[1] if preferences else ''),
            'remote': job_preferences_json.get('remote') if 'remote' in job_preferences_json else (bool(preferences[2]) if preferences else True),
            'experience': job_preferences_json.get('experience') or (preferences[3] if preferences else 'mid'),
            'salaryMin': job_preferences_json.get('salaryMin') or (preferences[4] if preferences else ''),
            'skills': job_preferences_json.get('skills') or (preferences[5] if preferences else '')
        },
        'personalDetails': {
            'pronouns': personal_info_json.get('pronouns') or (personal_details[0] if personal_details else ''),
            'phoneCountryCode': personal_info_json.get('phoneCountryCode') or (personal_details[1] if personal_details else 'US'),
            'streetAddress': personal_info_json.get('streetAddress') or (personal_details[2] if personal_details else ''),
            'city': personal_info_json.get('city') or (personal_details[3] if personal_details else ''),
            'state': personal_info_json.get('state') or (personal_details[4] if personal_details else ''),
            'zipCode': personal_info_json.get('zipCode') or (personal_details[5] if personal_details else ''),
            'linkedinUrl': personal_info_json.get('linkedinUrl') or (personal_details[6] if personal_details else ''),
            'portfolioWebsite': personal_info_json.get('portfolioWebsite') or (personal_details[7] if personal_details else ''),
            'messageToManager': personal_info_json.get('messageToManager') or (personal_details[8] if personal_details else ''),
            'universityGpa': personal_info_json.get('universityGpa') or (personal_details[9] if personal_details else ''),
            'noticePeriod': personal_info_json.get('noticePeriod') or (personal_details[10] if personal_details else '2'),
            'weekendWork': personal_info_json.get('weekendWork') if 'weekendWork' in personal_info_json else (bool(personal_details[11]) if personal_details else True),
            'eveningWork': personal_info_json.get('eveningWork') if 'eveningWork' in personal_info_json else (bool(personal_details[12]) if personal_details else True),
            'drugTest': personal_info_json.get('drugTest') if 'drugTest' in personal_info_json else (bool(personal_details[13]) if personal_details else True),
            'backgroundCheck': personal_info_json.get('backgroundCheck') if 'backgroundCheck' in personal_info_json else (bool(personal_details[14]) if personal_details else True)
        },
        'workAuthorization': {
            'driversLicense': bool(work_auth[0]) if work_auth else True,
            'requireVisa': bool(work_auth[1]) if work_auth else False,
            'legallyAuthorized': bool(work_auth[2]) if work_auth else True,
            'securityClearance': bool(work_auth[3]) if work_auth else False,
            'usCitizen': bool(work_auth[4]) if work_auth else True,
            'degreeCompleted': [work_auth[5]] if work_auth else ["Bachelor's Degree"]
        },
        'skillsExperience': {
            'languages': json.loads(skills_exp[0]) if skills_exp and skills_exp[0] else {'english': 'Native or bilingual'},
            'technicalSkills': json.loads(skills_exp[1]) if skills_exp and skills_exp[1] else {},
            'yearsExperience': json.loads(skills_exp[2]) if skills_exp and skills_exp[2] else {}
        },
        'eeoInfo': {
            'gender': eeo_info[0] if eeo_info else '',
            'race': eeo_info[1] if eeo_info else '',
            'veteran': bool(eeo_info[2]) if eeo_info else False,
            'disability': bool(eeo_info[3]) if eeo_info else False
        }
    }
    
    return jsonify(response_data)

@app.route('/api/linkedin/verify', methods=['POST'])
@token_required
def verify_linkedin_credentials(current_user_id):
    """Verify LinkedIn credentials by attempting a test login"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'LinkedIn email and password are required'}), 400
    
    linkedin_email = data['email']
    linkedin_password = data['password']
    
    try:
        # Simple verification - in a real app, you'd want to test actual LinkedIn login
        # For now, we'll do basic validation and return success
        # In production, you could use LinkedIn API or automation to verify
        
        if '@' not in linkedin_email or len(linkedin_password) < 6:
            return jsonify({
                'verified': False,
                'message': 'Invalid email format or password too short.'
            })
        
        # For demo purposes, return success after basic validation
        # In production, implement actual LinkedIn login verification
        return jsonify({
            'verified': True,
            'message': 'LinkedIn credentials verified successfully!'
        })
        
    except Exception as e:
        print(f"LinkedIn verification error: {e}")
        return jsonify({
            'verified': False,
            'message': 'Verification failed due to technical error.'
        })

@app.route('/api/user/plan', methods=['GET'])
@token_required
def get_user_plan(current_user_id):
    """Get user subscription plan and usage information"""
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT subscription_plan, daily_quota, daily_usage, email, first_name, last_name 
        FROM users WHERE id = ?
    ''', (current_user_id,))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        # Get quota from quota manager based on plan
        from quota_manager import QuotaManager
        quota_manager = QuotaManager()
        user_plan = user[0] or 'free'
        default_quota = quota_manager.get_plan_details(user_plan)['daily_quota']
        
        return jsonify({
            'plan': user_plan,
            'dailyQuota': user[1] or default_quota,
            'dailyUsage': user[2] or 0,
            'email': user[3],
            'firstName': user[4],
            'lastName': user[5]
        })
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/api/pricing', methods=['GET'])
def get_pricing():
    """Get pricing information for the application"""
    return jsonify({
        'plans': [
            {
                'id': 'free',
                'name': 'Free',
                'price': 0,
                'dailyQuota': 5,
                'features': [
                    '5 applications per day',
                    'Basic job discovery',
                    'Email support'
                ]
            },
            {
                'id': 'basic',
                'name': 'Basic',
                'price': 9.99,
                'dailyQuota': 25,
                'features': [
                    '25 applications per day',
                    'Advanced job discovery',
                    'Priority support',
                    'Resume optimization'
                ]
            },
            {
                'id': 'pro',
                'name': 'Pro',
                'price': 19.99,
                'dailyQuota': 100,
                'features': [
                    '100 applications per day',
                    'Unlimited job discovery',
                    'Priority support',
                    'AI-powered resume optimization',
                    'Advanced analytics'
                ]
            }
        ]
    })

@app.route('/api/user/auto-restart', methods=['GET', 'POST'])
@token_required
def manage_auto_restart(current_user_id):
    """Get or set auto-restart preference for user"""
    try:
        conn = sqlite3.connect('easyapply.db')
        cursor = conn.cursor()
        
        if request.method == 'GET':
            # Get current auto-restart setting
            cursor.execute('SELECT auto_restart FROM users WHERE id = ?', (current_user_id,))
            result = cursor.fetchone()
            conn.close()
            
            auto_restart = bool(result[0]) if result else True  # Default to enabled
            return jsonify({
                'auto_restart': auto_restart,
                'description': 'Bot will automatically restart at midnight when quota resets' if auto_restart else 'Auto-restart disabled'
            })
            
        elif request.method == 'POST':
            # Set auto-restart preference
            data = request.get_json()
            auto_restart = bool(data.get('auto_restart', True))
            
            cursor.execute(
                'UPDATE users SET auto_restart = ? WHERE id = ?',
                (1 if auto_restart else 0, current_user_id)
            )
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'auto_restart': auto_restart,
                'message': f'Auto-restart {"enabled" if auto_restart else "disabled"}. Bot will {"" if auto_restart else "NOT "}automatically restart at midnight when quota resets.'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile', methods=['PUT'])
@token_required
def update_profile(current_user_id):
    """Update user profile including LinkedIn credentials"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        print(f"🔍 Profile update data received: {data}")
        
        conn = sqlite3.connect('easyapply.db')
        cursor = conn.cursor()
        
        # Update user information
        user_data = data.get('user', {})
        if user_data:
            # Safely handle None values by converting to empty strings
            first_name = user_data.get('firstName') or ''
            last_name = user_data.get('lastName') or ''
            phone = user_data.get('phone') or ''
            website = user_data.get('website') or ''
            
            cursor.execute('''
                UPDATE users 
                SET first_name = ?, last_name = ?, phone = ?, website = ?, updated_at = ?
                WHERE id = ?
            ''', (
                str(first_name),
                str(last_name),
                str(phone),
                str(website),
                datetime.now().isoformat(),
                current_user_id
            ))
        
        # Update LinkedIn credentials (encrypted)
        linkedin_creds = data.get('linkedinCreds', {})
        if linkedin_creds and linkedin_creds.get('email') and linkedin_creds.get('password'):
            try:
                from security import encrypt_data, validate_linkedin_credentials
                
                # Validate credentials format
                valid, msg = validate_linkedin_credentials(
                    linkedin_creds.get('email'), 
                    linkedin_creds.get('password')
                )
                
                if not valid:
                    conn.close()
                    return jsonify({'error': f'LinkedIn credentials invalid: {msg}'}), 400
                
                # Encrypt credentials
                encrypted_email = encrypt_data(linkedin_creds['email'])
                encrypted_password = encrypt_data(linkedin_creds['password'])
                
                if not encrypted_email or not encrypted_password:
                    conn.close()
                    return jsonify({'error': 'Failed to encrypt LinkedIn credentials'}), 500
                
                cursor.execute('''
                    UPDATE users 
                    SET linkedin_email_encrypted = ?, linkedin_password_encrypted = ?, updated_at = ?
                    WHERE id = ?
                ''', (encrypted_email, encrypted_password, datetime.now().isoformat(), current_user_id))
                
            except Exception as e:
                conn.close()
                return jsonify({'error': f'Failed to save LinkedIn credentials: {str(e)}'}), 500
        
        # Update job preferences
        preferences = data.get('jobPreferences', {})
        if preferences:
            import json
            
            # Convert lists to JSON strings for SQLite storage
            job_titles = preferences.get('jobTitles', [])
            job_titles_json = json.dumps(job_titles) if isinstance(job_titles, list) else str(job_titles)
            
            locations = preferences.get('locations', [])
            locations_json = json.dumps(locations) if isinstance(locations, list) else str(locations)
            
            experience = preferences.get('experience', [])
            experience_json = json.dumps(experience) if isinstance(experience, list) else str(experience)
            
            # Convert numbers properly
            salary_min = preferences.get('salaryMin', 0)
            salary_min_val = int(salary_min) if isinstance(salary_min, (int, float)) else 0
            
            skills = preferences.get('skills', '')
            skills_str = str(skills) if skills else ''
            
            remote = bool(preferences.get('remote', False))
            
            # First check if preferences exist
            cursor.execute('SELECT id FROM user_preferences WHERE user_id = ?', (current_user_id,))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute('''
                    UPDATE user_preferences 
                    SET job_titles = ?, locations = ?, remote = ?, experience = ?, 
                        salary_min = ?, skills = ?, updated_at = ?
                    WHERE user_id = ?
                ''', (
                    job_titles_json,
                    locations_json, 
                    remote,
                    experience_json,
                    salary_min_val,
                    skills_str,
                    datetime.now().isoformat(),
                    current_user_id
                ))
            else:
                cursor.execute('''
                    INSERT INTO user_preferences 
                    (id, user_id, job_titles, locations, remote, experience, salary_min, skills, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(uuid.uuid4()),
                    current_user_id,
                    job_titles_json,
                    locations_json,
                    remote,
                    experience_json,
                    salary_min_val,
                    skills_str,
                    datetime.now().isoformat()
                ))
        
        # Update expanded profile data
        current_time = datetime.now().isoformat()
        
        # Personal Details
        personal_details = data.get('personalDetails', {})
        if personal_details:
            cursor.execute('SELECT id FROM user_personal_details WHERE user_id = ?', (current_user_id,))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute('''
                    UPDATE user_personal_details 
                    SET pronouns = ?, phone_country_code = ?, street_address = ?, 
                        city = ?, state = ?, zip_code = ?, linkedin_url = ?, 
                        portfolio_website = ?, message_to_manager = ?, university_gpa = ?,
                        notice_period = ?, weekend_work = ?, evening_work = ?,
                        drug_test = ?, background_check = ?, updated_at = ?
                    WHERE user_id = ?
                ''', (
                    str(personal_details.get('pronouns') or ''),
                    str(personal_details.get('phoneCountryCode') or 'US'),
                    str(personal_details.get('streetAddress') or ''),
                    str(personal_details.get('city') or ''),
                    str(personal_details.get('state') or ''),
                    str(personal_details.get('zipCode') or ''),
                    str(personal_details.get('linkedinUrl') or ''),
                    str(personal_details.get('portfolioWebsite') or ''),
                    str(personal_details.get('messageToManager') or ''),
                    float(personal_details.get('universityGpa') or 0.0),
                    int(personal_details.get('noticePeriod') or 2),
                    bool(personal_details.get('weekendWork', True)),
                    bool(personal_details.get('eveningWork', True)),
                    bool(personal_details.get('drugTest', True)),
                    bool(personal_details.get('backgroundCheck', True)),
                    current_time,
                    current_user_id
                ))
            else:
                cursor.execute('''
                    INSERT INTO user_personal_details 
                    (id, user_id, pronouns, phone_country_code, street_address, city, state, 
                     zip_code, linkedin_url, portfolio_website, message_to_manager, university_gpa,
                     notice_period, weekend_work, evening_work, drug_test, background_check, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(uuid.uuid4()), current_user_id,
                    personal_details.get('pronouns', ''),
                    personal_details.get('phoneCountryCode', 'US'),
                    personal_details.get('streetAddress', ''),
                    personal_details.get('city', ''),
                    personal_details.get('state', ''),
                    personal_details.get('zipCode', ''),
                    personal_details.get('linkedinUrl', ''),
                    personal_details.get('portfolioWebsite', ''),
                    personal_details.get('messageToManager', ''),
                    personal_details.get('universityGpa', 0.0),
                    personal_details.get('noticePeriod', 2),
                    personal_details.get('weekendWork', True),
                    personal_details.get('eveningWork', True),
                    personal_details.get('drugTest', True),
                    personal_details.get('backgroundCheck', True),
                    current_time
                ))
        
        # Work Authorization
        work_auth = data.get('workAuthorization', {})
        if work_auth:
            cursor.execute('SELECT id FROM user_work_authorization WHERE user_id = ?', (current_user_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Safely handle degreeCompleted list
                degree_completed = work_auth.get('degreeCompleted', [])
                if isinstance(degree_completed, list) and len(degree_completed) > 0:
                    degree_completed_str = degree_completed[0]
                elif isinstance(degree_completed, str):
                    degree_completed_str = degree_completed
                else:
                    degree_completed_str = "Bachelor's Degree"
                
                cursor.execute('''
                    UPDATE user_work_authorization 
                    SET drivers_license = ?, require_visa = ?, legally_authorized = ?,
                        security_clearance = ?, us_citizen = ?, degree_completed = ?, updated_at = ?
                    WHERE user_id = ?
                ''', (
                    bool(work_auth.get('driversLicense', True)),
                    bool(work_auth.get('requireVisa', False)),
                    bool(work_auth.get('legallyAuthorized', True)),
                    bool(work_auth.get('securityClearance', False)),
                    bool(work_auth.get('usCitizen', True)),
                    degree_completed_str,
                    current_time,
                    current_user_id
                ))
            else:
                # Safely handle degreeCompleted list for INSERT
                degree_completed = work_auth.get('degreeCompleted', [])
                if isinstance(degree_completed, list) and len(degree_completed) > 0:
                    degree_completed_str = degree_completed[0]
                elif isinstance(degree_completed, str):
                    degree_completed_str = degree_completed
                else:
                    degree_completed_str = "Bachelor's Degree"
                
                cursor.execute('''
                    INSERT INTO user_work_authorization 
                    (id, user_id, drivers_license, require_visa, legally_authorized,
                     security_clearance, us_citizen, degree_completed, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(uuid.uuid4()), current_user_id,
                    bool(work_auth.get('driversLicense', True)),
                    bool(work_auth.get('requireVisa', False)),
                    bool(work_auth.get('legallyAuthorized', True)),
                    bool(work_auth.get('securityClearance', False)),
                    bool(work_auth.get('usCitizen', True)),
                    degree_completed_str,
                    current_time
                ))
        
        # Skills & Experience
        skills_exp = data.get('skillsExperience', {})
        if skills_exp:
            cursor.execute('SELECT id FROM user_skills_experience WHERE user_id = ?', (current_user_id,))
            exists = cursor.fetchone()
            
            import json
            languages_json = json.dumps(skills_exp.get('languages', {'english': 'Native or bilingual'}))
            technical_skills_json = json.dumps(skills_exp.get('technicalSkills', {}))
            years_experience_json = json.dumps(skills_exp.get('yearsExperience', {}))
            
            if exists:
                cursor.execute('''
                    UPDATE user_skills_experience 
                    SET languages_json = ?, technical_skills_json = ?, years_experience_json = ?, updated_at = ?
                    WHERE user_id = ?
                ''', (languages_json, technical_skills_json, years_experience_json, current_time, current_user_id))
            else:
                cursor.execute('''
                    INSERT INTO user_skills_experience 
                    (id, user_id, languages_json, technical_skills_json, years_experience_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (str(uuid.uuid4()), current_user_id, languages_json, technical_skills_json, years_experience_json, current_time))
        
        # EEO Information
        eeo_info = data.get('eeoInfo', {})
        if eeo_info:
            cursor.execute('SELECT id FROM user_eeo_info WHERE user_id = ?', (current_user_id,))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute('''
                    UPDATE user_eeo_info 
                    SET gender = ?, race = ?, veteran = ?, disability = ?, updated_at = ?
                    WHERE user_id = ?
                ''', (
                    eeo_info.get('gender', ''),
                    eeo_info.get('race', ''),
                    eeo_info.get('veteran', False),
                    eeo_info.get('disability', False),
                    current_time,
                    current_user_id
                ))
            else:
                cursor.execute('''
                    INSERT INTO user_eeo_info 
                    (id, user_id, gender, race, veteran, disability, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(uuid.uuid4()), current_user_id,
                    eeo_info.get('gender', ''),
                    eeo_info.get('race', ''),
                    eeo_info.get('veteran', False),
                    eeo_info.get('disability', False),
                    current_time
                ))
        
        # IMPORTANT: Also update the JSON fields that the bot reads from
        job_preferences_json = json.dumps(data.get('jobPreferences', {}))
        personal_info_json = json.dumps(data.get('personalDetails', {}))
        
        cursor.execute('''
            UPDATE users 
            SET personal_info = ?, job_preferences = ?, updated_at = ?
            WHERE id = ?
        ''', (personal_info_json, job_preferences_json, datetime.now().isoformat(), current_user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Profile updated successfully'})
        
    except Exception as e:
        print(f"❌ Error updating profile: {str(e)}")
        print(f"📄 Error details: {type(e).__name__}: {e}")
        if 'conn' in locals():
            conn.close()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500

@app.route('/api/profile/ai-complete', methods=['POST'])
@token_required
def ai_complete_profile(current_user_id):
    """Use AI to automatically complete profile based on uploaded resume"""
    try:
        import openai
        import json
        from resume_parser import parse_resume_file
        
        # Get OpenAI API key from environment
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        # Get user's latest resume
        conn = sqlite3.connect('easyapply.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT file_path, original_name 
            FROM resumes 
            WHERE user_id = ? 
            ORDER BY uploaded_at DESC 
            LIMIT 1
        ''', (current_user_id,))
        
        resume_data = cursor.fetchone()
        if not resume_data:
            conn.close()
            return jsonify({'error': 'No resume found. Please upload a resume first.'}), 404
            
        resume_path, original_name = resume_data
        
        if not os.path.exists(resume_path):
            conn.close()
            return jsonify({'error': 'Resume file not found'}), 404
            
        # Parse the resume first to extract basic information
        parsed_resume = parse_resume_file(resume_path)
        
        if 'error' in parsed_resume:
            conn.close()
            return jsonify({'error': f'Failed to parse resume: {parsed_resume["error"]}'}), 500
            
        # Create a comprehensive prompt for OpenAI
        resume_text = parsed_resume.get('text', '')[:4000]  # Limit text length
        
        prompt = f"""
Based on the following resume content, generate a comprehensive JSON response for a job application profile. 
Extract and infer professional information to populate all relevant fields.

Resume Content:
{resume_text}

Please provide a JSON response with the following structure:
{{
    "personalDetails": {{
        "pronouns": "he/him, she/her, they/them, or blank",
        "phoneCountryCode": "United States (+1) or appropriate country",
        "streetAddress": "extracted or inferred address",
        "city": "extracted city",
        "state": "extracted state/province",
        "zipCode": "extracted zip/postal code",
        "linkedinUrl": "extracted LinkedIn URL or blank",
        "portfolioWebsite": "extracted website or GitHub URL",
        "messageToManager": "Professional 2-3 sentence message expressing interest",
        "universityGpa": "extracted GPA if mentioned, otherwise blank",
        "noticePeriod": "2",
        "weekendWork": true,
        "eveningWork": true,
        "drugTest": true,
        "backgroundCheck": true
    }},
    "workAuthorization": {{
        "driversLicense": true,
        "requireVisa": false,
        "legallyAuthorized": true,
        "securityClearance": false,
        "usCitizen": true,
        "degreeCompleted": "extracted highest degree or 'Bachelor's Degree'"
    }},
    "skillsExperience": {{
        "languages": {{
            "english": "Native or bilingual"
        }},
        "technicalSkills": {{"skill_name": proficiency_level_1_to_5}},
        "yearsExperience": {{"skill_name": years_of_experience}}
    }},
    "jobPreferences": {{
        "jobTitles": ["extracted or inferred job titles based on experience"],
        "locations": ["extracted locations or common tech hubs"],
        "remote": true,
        "experienceLevel": {{
            "internship": false,
            "entry": "true if early career",
            "associate": "true if 2-4 years experience", 
            "mid-senior level": "true if 5+ years experience",
            "director": "true if director/manager experience",
            "executive": "true if executive experience"
        }},
        "jobTypes": {{
            "full-time": true,
            "contract": true,
            "part-time": false,
            "temporary": false,
            "internship": "true if entry level",
            "other": false,
            "volunteer": false
        }},
        "salaryMin": "estimated based on experience and role",
        "datePreference": "all time"
    }},
    "applicationResponses": {{
        "referral": "",
        "citizenship": "U.S. Citizen/Permanent Resident",
        "salary": "estimated annual salary based on experience",
        "startDate": "Immediately available",
        "weekends": "Yes",
        "evenings": "Yes", 
        "references": "Available upon request"
    }},
    "eeoInfo": {{
        "gender": "",
        "race": "",
        "veteran": false,
        "disability": false
    }}
}}

Important: Return ONLY valid JSON. Ensure all boolean values are true/false (not strings). 
Infer reasonable professional values when information isn't explicitly stated.
"""

        try:
            # Call OpenAI API using the new v1+ format
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional resume analyzer and profile completion assistant. Generate accurate, professional profile data based on resume content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Parse the AI response as JSON
            try:
                profile_data = json.loads(ai_response)
            except json.JSONDecodeError:
                # Try to extract JSON if wrapped in markdown
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL)
                if json_match:
                    profile_data = json.loads(json_match.group(1))
                else:
                    raise ValueError("Could not parse AI response as JSON")
                    
            # Add some basic info from parsed resume
            if parsed_resume.get('name'):
                name_parts = parsed_resume['name'].split(' ', 1)
                profile_data['user'] = {
                    'firstName': name_parts[0] if name_parts else '',
                    'lastName': name_parts[1] if len(name_parts) > 1 else '',
                    'email': parsed_resume.get('email', ''),
                    'phone': parsed_resume.get('phone', ''),
                    'website': parsed_resume.get('website', '')
                }
                
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Profile data generated successfully! Please review and modify as needed.',
                'data': profile_data
            })
            
        except Exception as openai_error:
            conn.close()
            logger.error(f"OpenAI API error: {str(openai_error)}")
            return jsonify({'error': f'AI processing failed: {str(openai_error)}'}), 500
            
    except ImportError:
        return jsonify({'error': 'OpenAI library not installed. Please install openai package.'}), 500
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        logger.error(f"Error in AI profile completion: {str(e)}")
        return jsonify({'error': f'Failed to complete profile: {str(e)}'}), 500

# Easy Apply Bot Management - Persistent Version
import threading
import subprocess
import signal
import psutil
from enhanced_bot_manager import get_enhanced_bot_manager
from persistent_bot_manager import PersistentBotManager

# Get the enhanced bot manager instance
enhanced_bot_manager = get_enhanced_bot_manager()

# Get the persistent bot manager instance
persistent_bot_manager = PersistentBotManager('easyapply.db')

# Legacy dictionary for backward compatibility
running_bots = {}

@app.route('/api/bot/start', methods=['POST'])
@token_required
def start_easy_apply_bot(current_user_id):
    """Start the Enhanced Easy Apply bot for the current user"""
    try:
        # **FIRST: CHECK QUOTA BEFORE STARTING BOT**
        from quota_manager import can_use_quota, get_user_quota_status
        
        # Check if user can use quota (has remaining applications)
        if not can_use_quota(current_user_id, 1):
            quota_status = get_user_quota_status(current_user_id)
            if quota_status:
                return jsonify({
                    'error': f'Daily quota reached ({quota_status["daily_usage"]}/{quota_status["daily_quota"]}). Bot will restart automatically at midnight when quota resets.',
                    'code': 'QUOTA_EXCEEDED',
                    'quota_info': quota_status,
                    'next_reset': 'Midnight (24 hours after last reset)',
                    'auto_restart': True
                }), 403
            else:
                return jsonify({
                    'error': 'Unable to check quota status. Please try again.',
                    'code': 'QUOTA_CHECK_FAILED'
                }), 500

        # Get user configuration for the bot
        conn = sqlite3.connect('easyapply.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT linkedin_email_encrypted, linkedin_password_encrypted, 
                   personal_info, job_preferences, bot_config, subscription_plan
            FROM users WHERE id = ?
        ''', (current_user_id,))
        
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data or not user_data[0] or not user_data[1]:
            return jsonify({
                'error': 'LinkedIn credentials not configured',
                'code': 'CREDENTIALS_MISSING'
            }), 400
        
        # Decrypt credentials
        try:
            from security import decrypt_data
            linkedin_email = decrypt_data(user_data[0])
            linkedin_password = decrypt_data(user_data[1])
        except Exception as e:
            return jsonify({
                'error': 'Failed to decrypt credentials',
                'code': 'DECRYPTION_FAILED'
            }), 500
        
        # Parse user configurations
        try:
            personal_info = json.loads(user_data[2]) if user_data[2] else {}
            job_preferences = json.loads(user_data[3]) if user_data[3] else {}
            bot_config = json.loads(user_data[4]) if user_data[4] else {}
        except:
            personal_info = {}
            job_preferences = {}
            bot_config = {}
        
        # Set daily quota based on subscription
        subscription_plan = user_data[5] or 'free'
        quota_map = {'free': 5, 'basic': 30, 'pro': 50}
        daily_quota = quota_map.get(subscription_plan, 5)
        
        # Create enhanced bot configuration
        enhanced_config = {
            'email': linkedin_email,
            'password': linkedin_password,
            'user_id': current_user_id,
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
        
        # Use the persistent bot manager for session persistence across page refreshes
        print(f"🚀 Starting persistent bot for user {current_user_id}...")
        result = persistent_bot_manager.start_persistent_bot(current_user_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        print(f"✅ Persistent bot started successfully for user {current_user_id}")
        print(f"📋 Session persists across page refreshes: {result.get('survives_refresh', False)}")
        
        # Success response with enhanced persistence information
        return jsonify({
            'message': 'Enhanced persistent bot started successfully with auto-restart and quota tracking',
            'user_id': current_user_id,
            'session_info': result.get('session_info', {}),
            'quota_info': result.get('quota_info', {}),
            'features': {
                'auto_restart': True,
                'quota_tracking': True,
                'timeout_detection': True,
                'timeout_minutes': 5,
                'max_restarts': 10,
                'visible_chrome': True,
                'real_time_monitoring': True,
                'application_logging': True,
                'persistent_sessions': result.get('persistent', False),
                'survives_refresh': result.get('survives_refresh', False),
                'survives_logout': result.get('survives_refresh', False)
            },
            'note': 'Enhanced persistent bot with auto-restart, intelligent quota management, and session persistence is now running!',
            'persistent': result.get('persistent', False)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to start persistent bot: {str(e)}',
            'code': 'PERSISTENT_BOT_STARTUP_FAILED'
        }), 500

@app.route('/api/bot/stop', methods=['POST'])
@token_required
def stop_easy_apply_bot(current_user_id):
    """Stop the Enhanced Easy Apply bot for the current user"""
    try:
        # Use the persistent bot manager
        print(f"🛑 Stopping persistent bot for user {current_user_id}...")
        result = persistent_bot_manager.stop_persistent_bot(current_user_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        print(f"✅ Persistent bot stopped successfully for user {current_user_id}")
        
        # Success response
        return jsonify({
            'message': 'Enhanced persistent bot stopped successfully',
            'user_id': current_user_id,
            'stopped_at': datetime.now().isoformat(),
            'session_ended': True
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to stop persistent bot: {str(e)}',
            'code': 'PERSISTENT_BOT_STOP_FAILED'
        }), 500

@app.route('/api/bot/status', methods=['GET'])
@token_required
def get_bot_status(current_user_id):
    """Get the persistent status of the Easy Apply bot for the current user"""
    try:
        # Use the persistent bot manager for comprehensive status that survives page refreshes
        status_data = persistent_bot_manager.get_persistent_status(current_user_id)
        
        # Transform to match frontend expectations while adding enhanced features
        if status_data and status_data['is_running']:
            # Calculate estimated time remaining based on quota and current rate
            applications_remaining = status_data['quota_remaining']
            estimated_minutes = applications_remaining * 3  # Estimate 3 minutes per application
            
            progress_percentage = int((status_data['applications_count'] / status_data['daily_quota']) * 100) if status_data['daily_quota'] > 0 else 0
            
            status_response = {
                'status': 'running',
                'currentTask': f"Applying to jobs ({status_data['applications_count']}/{status_data['daily_quota']} completed)",
                'progress': progress_percentage,
                'tasksCompleted': status_data['applications_count'],
                'applicationsSubmitted': status_data['applications_count'],
                'lastRun': status_data['start_time'],
                'sessionStartTime': status_data['start_time'],
                'estimatedTimeRemaining': estimated_minutes * 60,  # Convert to seconds
                'quotaInfo': {
                    'daily_quota': status_data['daily_quota'],
                    'actual_applications': status_data['applications_count'],
                    'remaining_quota': status_data['quota_remaining']
                },
                'sessionInfo': {
                    'session_id': status_data['user_id'],
                    'applications_made': status_data['applications_count'],
                    'target_applications': status_data['daily_quota'],
                    'restart_count': status_data['restart_count'],
                    'duration_seconds': status_data['runtime_seconds'],
                    'process_id': status_data.get('process_id'),
                    'last_activity': status_data['last_activity'],
                    'is_timeout': status_data['is_timeout']
                },
                'enhancedFeatures': {
                    'auto_restart': True,
                    'quota_tracking': True,
                    'intelligent_retry': True,
                    'real_time_logging': True
                },
                'detailedSteps': [
                    {
                        'step': 'Enhanced Bot Initialized',
                        'status': 'completed',
                        'timestamp': status_data['start_time']
                    },
                    {
                        'step': f"Quota Management ({status_data['applications_count']}/{status_data['daily_quota']})",
                        'status': 'current',
                        'timestamp': datetime.now().isoformat()
                    },
                    {
                        'step': 'Auto-Restart Monitor',
                        'status': 'active',
                        'timestamp': datetime.now().isoformat()
                    },
                    {
                        'step': 'Enhanced Job Search with Timeout Detection',
                        'status': 'running',
                        'timestamp': status_data['last_activity']
                    }
                ],
                'recentActivities': status_data.get('recent_activities', [])
            }
            
            # Add persistent session information if available
            if 'persistent_session' in status_data:
                status_response['persistent_session'] = status_data['persistent_session']
            
            # Add restart information if any restarts occurred
            if status_data['restart_count'] > 0:
                status_response['restartInfo'] = {
                    'count': status_data['restart_count'],
                    'max_allowed': 10,
                    'last_restart': 'Auto-restart due to timeout or error'
                }
        
        else:
            # Bot is not running - get quota info from database
            try:
                conn = sqlite3.connect('easyapply.db')
                cursor = conn.cursor()
                
                # Get user's subscription plan for quota
                cursor.execute('SELECT subscription_plan FROM users WHERE id = ?', (current_user_id,))
                user_data = cursor.fetchone()
                subscription_plan = user_data[0] if user_data else 'free'
                
                # Get daily quota based on subscription
                quota_map = {'free': 5, 'basic': 30, 'pro': 50}
                daily_quota = quota_map.get(subscription_plan, 5)
                
                # Get today's applications count
                cursor.execute('''
                    SELECT COUNT(*) FROM job_applications 
                    WHERE user_id = ? AND date(applied_at) = date('now')
                ''', (current_user_id,))
                actual_applications = cursor.fetchone()[0] or 0
                
                # Get last run info
                cursor.execute('''
                    SELECT applied_at FROM job_applications 
                    WHERE user_id = ? 
                    ORDER BY applied_at DESC LIMIT 1
                ''', (current_user_id,))
                last_app = cursor.fetchone()
                last_run = last_app[0] if last_app else None
                conn.close()
                
            except Exception as e:
                daily_quota = 5
                actual_applications = 0
                last_run = None
            
            remaining_quota = max(0, daily_quota - actual_applications)
            progress = min(100, int((actual_applications / daily_quota) * 100)) if daily_quota > 0 else 0
            
            status_response = {
                'status': 'stopped',
                'currentTask': f"Ready to start enhanced job search ({remaining_quota} applications remaining)",
                'progress': progress,
                'tasksCompleted': actual_applications,
                'applicationsSubmitted': actual_applications,
                'lastRun': last_run,
                'sessionStartTime': None,
                'estimatedTimeRemaining': 0,
                'quotaInfo': {
                    'daily_quota': daily_quota,
                    'actual_applications': actual_applications,
                    'remaining_quota': remaining_quota
                },
                'enhancedFeatures': {
                    'auto_restart': True,
                    'quota_tracking': True,
                    'intelligent_retry': True,
                    'real_time_logging': True
                },
                'detailedSteps': [
                    {
                        'step': 'Enhanced Bot Ready',
                        'status': 'pending',
                        'timestamp': None
                    }
                ]
            }
        
        return jsonify(status_response)
        
    except Exception as e:
        # Fallback to basic status if enhanced manager fails
        print(f"Enhanced status error: {e}")
        
        # Basic fallback status
        try:
            conn = sqlite3.connect('easyapply.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM job_applications 
                WHERE user_id = ? AND date(applied_at) = date('now')
            ''', (current_user_id,))
            today_applications = cursor.fetchone()[0] or 0
            
            cursor.execute('''
                SELECT daily_quota, daily_usage FROM users WHERE id = ?
            ''', (current_user_id,))
            quota_info = cursor.fetchone()
            daily_quota = quota_info[0] if quota_info else 5
            
            conn.close()
            
            progress = min(100, int((today_applications / daily_quota) * 100))
            
            return jsonify({
                'status': 'stopped',
                'currentTask': 'Ready to start job search',
                'progress': progress,
                'tasksCompleted': today_applications,
                'applicationsSubmitted': today_applications,
                'error': 'Enhanced features temporarily unavailable'
            })
            
        except Exception as fallback_error:
            return jsonify({
                'status': 'error',
                'currentTask': 'Unable to determine status',
                'progress': 0,
                'error': f'Status check failed: {str(fallback_error)}'
            }), 500

@app.route('/api/bot/clear-status', methods=['POST'])
@token_required
def clear_bot_status(current_user_id):
    """Clear any stale bot status for debugging"""
    try:
        cleared_legacy = False
        cleared_enhanced = False
        
        # Clear legacy running_bots
        global running_bots
        if current_user_id in running_bots:
            bot_info = running_bots[current_user_id]
            
            # Try to clean up config file
            if 'config_path' in bot_info and os.path.exists(bot_info['config_path']):
                try:
                    os.remove(bot_info['config_path'])
                except:
                    pass
            
            # Remove from running bots
            del running_bots[current_user_id]
            cleared_legacy = True
        
        # Clear enhanced bot manager state
        if current_user_id in enhanced_bot_manager.active_sessions:
            del enhanced_bot_manager.active_sessions[current_user_id]
            cleared_enhanced = True
        
        # Clear database status records
        try:
            conn = sqlite3.connect('easyapply.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM enhanced_bot_status WHERE user_id = ?', (current_user_id,))
            db_cleared = cursor.rowcount
            conn.commit()
            conn.close()
        except:
            db_cleared = 0
        
        return jsonify({
            'message': 'Bot status cleared successfully',
            'cleared': cleared_legacy or cleared_enhanced or db_cleared > 0,
            'details': {
                'legacy_cleared': cleared_legacy,
                'enhanced_cleared': cleared_enhanced,
                'database_records_cleared': db_cleared
            }
        })
        
    except Exception as e:
        logger.error(f"Error clearing bot status for user {current_user_id}: {e}")
        return jsonify({
            'error': 'Unable to clear bot status. Please try refreshing the page and try again.',
            'details': str(e) if app.debug else None,
            'cleared': False
        }), 500

@app.route('/api/bot/sync-status', methods=['POST'])
@token_required
def sync_bot_status(current_user_id):
    """Synchronize bot status across all systems"""
    try:
        # Clear any legacy running_bots entries
        global running_bots
        legacy_cleared = current_user_id in running_bots
        if legacy_cleared:
            del running_bots[current_user_id]
        
        # Clear enhanced bot manager state for this user
        enhanced_cleared = False
        if current_user_id in enhanced_bot_manager.active_sessions:
            del enhanced_bot_manager.active_sessions[current_user_id]
            enhanced_cleared = True
        
        # Get fresh status from persistent manager
        status_data = persistent_bot_manager.get_persistent_status(current_user_id)
        
        # Log sync activity
        enhanced_bot_manager.log_activity(
            current_user_id,
            "Status Synchronized",
            "🔄 Bot status synchronized across all systems. Dashboard should now show correct state.",
            "success",
            {
                "sync_type": "api_sync",
                "legacy_cleared": legacy_cleared,
                "enhanced_cleared": enhanced_cleared
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Bot status synchronized successfully',
            'status': status_data,
            'sync_details': {
                'legacy_cleared': legacy_cleared,
                'enhanced_cleared': enhanced_cleared
            }
        })
        
    except Exception as e:
        logger.error(f"Error syncing bot status for user {current_user_id}: {e}")
        return jsonify({
            'error': 'Unable to sync bot status. Please try again or contact support.',
            'details': str(e) if app.debug else None
        }), 500

@app.route('/api/user/reset-account', methods=['POST'])
@token_required
def reset_user_account(current_user_id):
    """Reset user account data - applications, activity logs, bot sessions"""
    try:
        conn = sqlite3.connect('easyapply.db')
        cursor = conn.cursor()
        
        # Count data before deletion for reporting
        cursor.execute('SELECT COUNT(*) FROM job_applications WHERE user_id = ?', (current_user_id,))
        applications_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM activity_log WHERE user_id = ?', (current_user_id,))
        activity_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM enhanced_bot_sessions WHERE user_id = ?', (current_user_id,))
        sessions_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM enhanced_activity_log WHERE user_id = ?', (current_user_id,))
        enhanced_activity_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM enhanced_applications WHERE user_id = ?', (current_user_id,))
        enhanced_apps_count = cursor.fetchone()[0]
        
        # Delete all user data
        tables_to_clear = [
            'job_applications',
            'activity_log', 
            'enhanced_bot_sessions',
            'enhanced_activity_log',
            'enhanced_applications',
            'enhanced_bot_status'
        ]
        
        total_deleted = 0
        for table in tables_to_clear:
            try:
                cursor.execute(f'DELETE FROM {table} WHERE user_id = ?', (current_user_id,))
                total_deleted += cursor.rowcount
            except sqlite3.OperationalError:
                # Table might not exist
                continue
        
        conn.commit()
        conn.close()
        
        # Clear any active bot sessions
        global running_bots
        if current_user_id in running_bots:
            del running_bots[current_user_id]
        
        if current_user_id in enhanced_bot_manager.active_sessions:
            del enhanced_bot_manager.active_sessions[current_user_id]
        
        # Log the reset action
        enhanced_bot_manager.log_activity(
            current_user_id,
            "Account Reset",
            f"🔄 Account data reset successfully. Cleared {applications_count} applications, {activity_count + enhanced_activity_count} activity logs, and {sessions_count} bot sessions.",
            "info",
            {
                "reset_type": "full_account",
                "applications_deleted": applications_count,
                "activity_logs_deleted": activity_count + enhanced_activity_count,
                "bot_sessions_deleted": sessions_count,
                "enhanced_apps_deleted": enhanced_apps_count,
                "total_records_deleted": total_deleted
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Account data reset successfully! Your application history, activity logs, and bot sessions have been cleared.',
            'summary': {
                'applications_deleted': applications_count,
                'activity_logs_deleted': activity_count + enhanced_activity_count,
                'bot_sessions_deleted': sessions_count,
                'enhanced_applications_deleted': enhanced_apps_count,
                'total_records_deleted': total_deleted
            }
        })
        
    except Exception as e:
        logger.error(f"Error resetting account for user {current_user_id}: {e}")
        return jsonify({
            'error': 'Unable to reset account data. Please try again or contact support.',
            'details': str(e) if app.debug else None
        }), 500

def create_user_config(user_data, linkedin_email, linkedin_password, user_id):
    """Create a user-specific configuration dict from user data"""
    linkedin_email_encrypted, linkedin_password_encrypted, personal_info, job_preferences, bot_config = user_data
    
    import json
    personal_info = json.loads(personal_info) if personal_info else {}
    job_preferences = json.loads(job_preferences) if job_preferences else {}
    bot_config = json.loads(bot_config) if bot_config else {}
    
    # Get user's uploaded resume
    resume_path = ''
    try:
        conn = sqlite3.connect('easyapply.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT file_path FROM resumes 
            WHERE user_id = ? AND (is_default = 1 OR is_default = TRUE)
            ORDER BY uploaded_at DESC 
            LIMIT 1
        ''', (user_id,))
        resume_result = cursor.fetchone()
        if resume_result:
            resume_path = os.path.abspath(resume_result[0])
        else:
            # If no default resume, get the most recent one
            cursor.execute('''
                SELECT file_path FROM resumes 
                WHERE user_id = ? 
                ORDER BY uploaded_at DESC 
                LIMIT 1
            ''', (user_id,))
            resume_result = cursor.fetchone()
            if resume_result:
                resume_path = os.path.abspath(resume_result[0])
        conn.close()
    except Exception as e:
        print(f"Could not fetch user resume: {e}")
    
    # If no resume found, provide helpful error message
    if not resume_path:
        print(f"⚠️  No resume found for user {user_id}. Please upload a resume before starting the bot.")
        # You could also check the default resume from config.yaml as fallback
        try:
            with open('config.yaml', 'r') as f:
                import yaml
                base_config = yaml.safe_load(f)
                fallback_resume = base_config.get('uploads', {}).get('resume', '')
                if fallback_resume and os.path.exists(fallback_resume):
                    resume_path = os.path.abspath(fallback_resume)
                    print(f"📄 Using fallback resume from config: {resume_path}")
        except Exception as e:
            print(f"Could not load fallback resume from config: {e}")
    
    # Extract job preferences with proper defaults
    job_titles = safe_split_to_list(job_preferences.get('jobTitles'))
    if not job_titles:
        job_titles = ['Software Engineer']
    
    job_locations = safe_split_to_list(job_preferences.get('locations'))
    if not job_locations:
        job_locations = ['United States']
    
    # Get user's personal info for LinkedIn login
    user_personal_info = {
        'First Name': personal_info.get('firstName', personal_info.get('first_name', '')),
        'Last Name': personal_info.get('lastName', personal_info.get('last_name', '')),
        'Email': personal_info.get('email', linkedin_email),
        'Phone': personal_info.get('phone', personal_info.get('phoneNumber', ''))
    }
    
    config = {
        'email': linkedin_email,
        'password': linkedin_password,
        'openaiApiKey': bot_config.get('openai_api_key', ''),
        'disableAntiLock': False,
        'remote': job_preferences.get('remote', True),
        'lessthanTenApplicants': False,
        'newestPostingsFirst': False,
        'experienceLevel': {
            'internship': job_preferences.get('experience') == 'entry',
            'entry': job_preferences.get('experience') in ['entry', 'mid'],
            'associate': job_preferences.get('experience') == 'mid',
            'mid-senior level': job_preferences.get('experience') in ['mid', 'senior'],
            'director': job_preferences.get('experience') == 'lead',
            'executive': False
        },
        'jobTypes': {
            'full-time': True,
            'contract': True,
            'part-time': False,
            'temporary': False,
            'internship': job_preferences.get('experience') == 'entry',
            'other': False,
            'volunteer': False
        },
        'date': {'all time': True, 'month': False, 'week': False, '24 hours': False},
        'positions': job_titles,
        'locations': job_locations,
        'residentStatus': False,
        'distance': 100,
        'outputFileDirectory': '~/Documents/Applications/EasyApplyBot/',
        'companyBlacklist': None,
        'titleBlacklist': None,
        'posterBlacklist': None,
        'uploads': {
            'resume': resume_path,
            'coverLetter': bot_config.get('uploads', {}).get('coverLetter', ''),
            **bot_config.get('uploads', {})
        },
        'checkboxes': bot_config.get('checkboxes', {}),
        'universityGpa': bot_config.get('university_gpa', 3.7),
        'salaryMinimum': int(job_preferences.get('salaryMin', 65000)) if job_preferences.get('salaryMin') else 65000,
        'languages': bot_config.get('languages', {'english': 'Native or bilingual'}),
        'noticePeriod': bot_config.get('notice_period', 2),
        'experience': {
            'default': 0,
            'Python': 4,
            'JavaScript': 4,
            'Java': 4,
            'SQL': 4,
            'Git': 3,
            'Docker': 3,
            'AWS': 2,
            'Linux': 2,
            'Cybersecurity': 4,
            'AI': 4,
            'Machine Learning': 3,
            'Data Analytics': 3,
            'Network Security': 3,
            'Incident Response': 3,
            'Threat Detection': 2,
            'Data Science': 3,
            'Statistics': 3,
            'Flask': 4,
            'FastAPI': 4,
            'Selenium': 4,
            'PowerShell': 4,
            'RESTful APIs': 4,
            'NLP': 2,
            'HTML/CSS': 4,
            'C/C++': 4,
            'Networking': 3,
            'Automation': 3,
            'Web Development': 3,
            'Databases': 3,
            'Cloud Technologies': 3,
            'DevOps': 2,
            'Engineering': 2,
            'Information Technology': 2,
            'Project Management': 4,
            'Research': 1,
            'Sales': 2,
            **bot_config.get('experience', {})
        },
        'personalInfo': user_personal_info,  # Use properly formatted personal info
        'eeo': bot_config.get('eeo', {}),
        'evaluateJobFit': bot_config.get('evaluate_job_fit', True),
        'textResume': bot_config.get('uploads', {}).get('resume', ''),
        'debug': False,
        'applicationResponses': bot_config.get('application_responses', {}),
        'usCitizen': bot_config.get('us_citizen', True),
        'requireVisaSponsorship': bot_config.get('require_visa_sponsorship', False)
    }
    
    return config

# Register enhanced status API routes
register_enhanced_status_routes(app, token_required)
register_job_routes(app)

@app.route('/api/activity/clear', methods=['POST'])
@token_required
def clear_activity_logs(current_user_id):
    """Clear activity logs for the current user"""
    try:
        # Use the correct database path
        import os
        db_path = os.path.join(os.path.dirname(__file__), 'easyapply.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear activity logs for the current user
        cursor.execute('DELETE FROM activity_log WHERE user_id = ?', (current_user_id,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Cleared {deleted_count} activity log entries for user {current_user_id}")
        
        return jsonify({
            'success': True,
            'message': f'Cleared {deleted_count} activity log entries',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to clear activity logs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/debug/user-info', methods=['GET'])
@token_required
def debug_user_info(current_user_id):
    """Debug endpoint to show current user information and application count"""
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    # Get current user info
    cursor.execute('SELECT email, first_name, last_name FROM users WHERE id = ?', (current_user_id,))
    user_info = cursor.fetchone()
    
    # Get application count for this user
    cursor.execute('SELECT COUNT(*) FROM job_applications WHERE user_id = ?', (current_user_id,))
    app_count = cursor.fetchone()[0]
    
    # Get the bot user info (hardcoded user with applications)
    bot_user_id = "bf5acf53-8862-48af-b9ab-3b73d3c5527a"
    cursor.execute('SELECT email, first_name, last_name FROM users WHERE id = ?', (bot_user_id,))
    bot_user_info = cursor.fetchone()
    
    cursor.execute('SELECT COUNT(*) FROM job_applications WHERE user_id = ?', (bot_user_id,))
    bot_app_count = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'currentUser': {
            'id': current_user_id,
            'email': user_info[0] if user_info else 'Unknown',
            'name': f"{user_info[1]} {user_info[2]}" if user_info else 'Unknown',
            'applicationCount': app_count
        },
        'botUser': {
            'id': bot_user_id,
            'email': bot_user_info[0] if bot_user_info else 'Unknown',
            'name': f"{bot_user_info[1]} {bot_user_info[2]}" if bot_user_info else 'Unknown',
            'applicationCount': bot_app_count
        },
        'userMatch': current_user_id == bot_user_id,
        'solution': "Log in with shaheersaud2004@gmail.com to see bot applications" if current_user_id != bot_user_id else "User accounts match!"
    })

@app.route('/api/admin/analytics', methods=['GET'])
@token_required
@admin_required
def get_admin_analytics(current_user_id):
    """Get comprehensive analytics for admin dashboard"""
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    # Top companies by applications
    cursor.execute('''
        SELECT company, COUNT(*) as count 
        FROM job_applications 
        GROUP BY company 
        ORDER BY count DESC 
        LIMIT 10
    ''')
    top_companies = [{'company': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Top job titles
    cursor.execute('''
        SELECT job_title, COUNT(*) as count 
        FROM job_applications 
        GROUP BY job_title 
        ORDER BY count DESC 
        LIMIT 10
    ''')
    top_job_titles = [{'title': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Applications by status
    cursor.execute('''
        SELECT status, COUNT(*) as count 
        FROM job_applications 
        GROUP BY status 
        ORDER BY count DESC
    ''')
    applications_by_status = [{'status': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Daily application trends (last 7 days)
    cursor.execute('''
        SELECT DATE(applied_at) as date, COUNT(*) as count
        FROM job_applications 
        WHERE applied_at >= date('now', '-7 days')
        GROUP BY DATE(applied_at)
        ORDER BY date DESC
    ''')
    daily_trends = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # User success rates (users with >5 applications)
    cursor.execute('''
        SELECT u.email, u.first_name, u.last_name,
               COUNT(ja.id) as total_apps,
               COUNT(CASE WHEN ja.status IN ('interview', 'offer', 'accepted') THEN 1 END) as successful,
               ROUND(COUNT(CASE WHEN ja.status IN ('interview', 'offer', 'accepted') THEN 1 END) * 100.0 / COUNT(ja.id), 2) as success_rate
        FROM users u
        JOIN job_applications ja ON u.id = ja.user_id
        GROUP BY u.id, u.email, u.first_name, u.last_name
        HAVING COUNT(ja.id) >= 5
        ORDER BY success_rate DESC
    ''')
    user_success_rates = []
    for row in cursor.fetchall():
        user_success_rates.append({
            'email': row[0],
            'name': f"{row[1]} {row[2]}".strip(),
            'total_applications': row[3],
            'successful_applications': row[4],
            'success_rate': row[5]
        })
    
    # Most active users (by applications)
    cursor.execute('''
        SELECT u.email, u.first_name, u.last_name, COUNT(ja.id) as app_count
        FROM users u
        JOIN job_applications ja ON u.id = ja.user_id
        GROUP BY u.id, u.email, u.first_name, u.last_name
        ORDER BY app_count DESC
        LIMIT 10
    ''')
    most_active_users = []
    for row in cursor.fetchall():
        most_active_users.append({
            'email': row[0],
            'name': f"{row[1]} {row[2]}".strip(),
            'applications': row[3]
        })
    
    conn.close()
    
    return jsonify({
        'top_companies': top_companies,
        'top_job_titles': top_job_titles,
        'applications_by_status': applications_by_status,
        'daily_trends': daily_trends,
        'user_success_rates': user_success_rates,
        'most_active_users': most_active_users
    })

@app.route('/api/admin/users/<user_id>/applications', methods=['GET'])
@token_required
@admin_required
def get_user_applications(current_user_id, user_id):
    """Get all applications for a specific user"""
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    # Get user details
    cursor.execute('SELECT email, first_name, last_name FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    if not user_data:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    # Get applications
    cursor.execute('''
        SELECT id, job_title, company, location, job_url, status, applied_at, notes
        FROM job_applications 
        WHERE user_id = ?
        ORDER BY applied_at DESC
    ''', (user_id,))
    
    applications = []
    for row in cursor.fetchall():
        applications.append({
            'id': row[0],
            'job_title': row[1],
            'company': row[2],
            'location': row[3],
            'job_url': row[4],
            'status': row[5],
            'applied_at': row[6],
            'notes': row[7]
        })
    
    conn.close()
    
    return jsonify({
        'user': {
            'email': user_data[0],
            'name': f"{user_data[1]} {user_data[2]}".strip()
        },
        'applications': applications,
        'total_count': len(applications)
    })

@app.route('/api/admin/users/<user_id>/activity', methods=['GET'])
@token_required
@admin_required
def get_user_activity(current_user_id, user_id):
    """Get activity log for a specific user"""
    limit = request.args.get('limit', 50, type=int)
    
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    # Get recent activity
    cursor.execute('''
        SELECT action, details, status, timestamp, metadata
        FROM activity_log 
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (user_id, limit))
    
    activities = []
    for row in cursor.fetchall():
        activities.append({
            'action': row[0],
            'details': row[1],
            'status': row[2],
            'timestamp': row[3],
            'metadata': row[4]
        })
    
    conn.close()
    
    return jsonify({'activities': activities})

@app.route('/api/admin/system-health', methods=['GET'])
@token_required
@admin_required
def get_system_health(current_user_id):
    """Get system health metrics"""
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    # Database stats
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM job_applications')
    total_applications = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM activity_log WHERE timestamp > datetime("now", "-1 hour")')
    recent_activity = cursor.fetchone()[0]
    
    # Check if enhanced_bot_status table exists and has data
    try:
        cursor.execute('SELECT COUNT(*) FROM enhanced_bot_status WHERE status != "idle"')
        active_bots = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        # Table doesn't exist or has different schema, use fallback
        active_bots = 0
    
    # Recent errors
    cursor.execute('''
        SELECT COUNT(*) FROM activity_log 
        WHERE status = "error" AND timestamp > datetime("now", "-24 hours")
    ''')
    recent_errors = cursor.fetchone()[0]
    
    # Database size (approximate)
    cursor.execute('PRAGMA page_count')
    page_count = cursor.fetchone()[0]
    cursor.execute('PRAGMA page_size')
    page_size = cursor.fetchone()[0]
    db_size_mb = (page_count * page_size) / (1024 * 1024)
    
    # User activity in last 24 hours
    cursor.execute('''
        SELECT COUNT(DISTINCT user_id) FROM activity_log 
        WHERE timestamp > datetime("now", "-24 hours")
    ''')
    active_users_24h = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'database': {
            'total_users': total_users,
            'total_applications': total_applications,
            'size_mb': round(db_size_mb, 2)
        },
        'activity': {
            'recent_activity_1h': recent_activity,
            'active_users_24h': active_users_24h,
            'recent_errors_24h': recent_errors
        },
        'bots': {
            'active_sessions': active_bots
        },
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/admin/recent-activity', methods=['GET'])
@token_required
@admin_required
def get_recent_activity(current_user_id):
    """Get recent platform activity across all users"""
    limit = request.args.get('limit', 20, type=int)
    
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT al.action, al.details, al.status, al.timestamp, al.metadata,
               u.email, u.first_name, u.last_name
        FROM activity_log al
        JOIN users u ON al.user_id = u.id
        ORDER BY al.timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    activities = []
    for row in cursor.fetchall():
        activities.append({
            'action': row[0],
            'details': row[1],
            'status': row[2],
            'timestamp': row[3],
            'metadata': row[4],
            'user': {
                'email': row[5],
                'name': f"{row[6]} {row[7]}".strip() if row[6] and row[7] else row[5]
            }
        })
    
    conn.close()
    
    return jsonify({'activities': activities})

@app.route('/api/admin/export/users', methods=['GET'])
@token_required
@admin_required  
def export_users(current_user_id):
    """Export users data as CSV"""
    import csv
    import io
    
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.email, u.first_name, u.last_name, u.subscription_plan, u.status,
               u.created_at, u.daily_quota, u.daily_usage,
               COUNT(ja.id) as total_applications
        FROM users u
        LEFT JOIN job_applications ja ON u.id = ja.user_id
        GROUP BY u.id, u.email, u.first_name, u.last_name, u.subscription_plan, 
                 u.status, u.created_at, u.daily_quota, u.daily_usage
        ORDER BY u.created_at DESC
    ''')
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Email', 'First Name', 'Last Name', 'Plan', 'Status', 
        'Created', 'Daily Quota', 'Daily Usage', 'Total Applications'
    ])
    
    # Write data
    for row in cursor.fetchall():
        writer.writerow(row)
    
    conn.close()
    
    csv_data = output.getvalue()
    output.close()
    
    from flask import Response
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=users_export.csv'}
    )

@app.route('/api/resume/parse', methods=['POST'])
@token_required
def parse_resume_endpoint(current_user_id):
    """Parse an uploaded resume and extract structured information"""
    try:
        data = request.get_json()
        if not data or 'resume_id' not in data:
            return jsonify({'error': 'Resume ID is required'}), 400
        
        resume_id = data['resume_id']
        
        # Get resume file path from database
        conn = sqlite3.connect('easyapply.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT file_path, original_name FROM resumes 
            WHERE id = ? AND user_id = ?
        ''', (resume_id, current_user_id))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'error': 'Resume not found'}), 404
        
        file_path, original_name = result
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'Resume file not found on disk'}), 404
        
        # Parse the resume
        try:
            from resume_parser import parse_resume_file
            parsed_data = parse_resume_file(file_path)
            
            if 'error' in parsed_data:
                return jsonify({'error': parsed_data['error']}), 400
            
            return jsonify({
                'success': True,
                'resume_id': resume_id,
                'original_name': original_name,
                'parsed_data': parsed_data,
                'message': 'Resume parsed successfully'
            })
            
        except ImportError as e:
            return jsonify({
                'error': 'Resume parsing dependencies not available. Please install PyPDF2, python-docx, and docx2txt packages.',
                'details': str(e)
            }), 500
            
    except Exception as e:
        logger.error(f"Error in parse_resume_endpoint: {str(e)}")
        return jsonify({'error': f'Failed to parse resume: {str(e)}'}), 500

if __name__ == '__main__':
    init_db()
    print("✅ Database initialized and migrations applied")
    
    # Start the daily job scheduler
    print("📅 Starting daily job scheduler...")
    start_job_scheduler()
    
    # Start the daily application scheduler
    print("🚀 Starting daily application scheduler...")
    start_daily_application_scheduler()
    
    # Start the auto-restart scheduler
    print("🔄 Starting auto-restart scheduler...")
    try:
        from auto_restart_scheduler import start_auto_restart_scheduler
        start_auto_restart_scheduler()
    except ImportError as e:
        print(f"⚠️ Auto-restart scheduler disabled (missing dependencies): {e}")
    
    print("🚀 Starting ApplyX Backend Server...")
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080))) 