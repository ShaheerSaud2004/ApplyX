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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import existing LinkedIn bot functionality
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from linkedineasyapply import LinkedinEasyApply
from main_fast import ContinuousApplyBot
from web_agent import WebPlatformLinkedInBot

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

CORS(app)

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Subscription plans
SUBSCRIPTION_PLANS = {
    'free': {'name': 'Free', 'price': 0, 'daily_quota': 5},
    'basic': {'name': 'Basic', 'price': 10, 'daily_quota': 30, 'stripe_price_id': os.environ.get('STRIPE_BASIC_PRICE_ID')},
    'pro': {'name': 'Pro', 'price': 20, 'daily_quota': 50, 'stripe_price_id': os.environ.get('STRIPE_PRO_PRICE_ID')}
}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variables for bot management
active_bots = {}
bot_status = {}

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
            subscription_plan TEXT DEFAULT 'free',
            stripe_customer_id TEXT,
            subscription_id TEXT,
            subscription_status TEXT,
            current_period_end TIMESTAMP,
            daily_quota INTEGER DEFAULT 5,
            daily_usage INTEGER DEFAULT 0,
            last_usage_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin BOOLEAN DEFAULT FALSE,
            referral_code TEXT,
            referred_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    # User preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            positions TEXT,
            locations TEXT,
            remote BOOLEAN DEFAULT FALSE,
            experience_level TEXT,
            job_types TEXT,
            salary_minimum INTEGER,
            preferred_industries TEXT,
            skills_required TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
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

def check_and_reset_daily_quota(user_id):
    """Check and reset daily quota if needed"""
    conn = sqlite3.connect('easyapply.db')
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
    last_reset_date = datetime.fromisoformat(last_reset).date() if last_reset else date.today()
    today = date.today()
    
    # Reset usage if it's a new day
    if last_reset_date < today:
        # Update quota based on current subscription plan
        plan_quota = SUBSCRIPTION_PLANS.get(subscription_plan, {}).get('daily_quota', 5)
        cursor.execute('''
            UPDATE users 
            SET daily_usage = 0, daily_quota = ?, last_usage_reset = ?
            WHERE id = ?
        ''', (plan_quota, datetime.now().isoformat(), user_id))
        daily_usage = 0
        daily_quota = plan_quota
        conn.commit()
    
    conn.close()
    return True, daily_usage, daily_quota

def can_use_quota(user_id, amount=1):
    """Check if user can use quota"""
    success, usage, quota = check_and_reset_daily_quota(user_id)
    if not success:
        return False
    return usage + amount <= quota

def use_quota(user_id, amount=1, action_type='application'):
    """Use quota and log the usage"""
    if not can_use_quota(user_id, amount):
        return False
    
    conn = sqlite3.connect('easyapply.db')
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
    remaining = cursor.fetchone()[0]
    
    # Log usage
    cursor.execute('''
        INSERT INTO usage_logs (id, user_id, action_type, quota_used, remaining_quota)
        VALUES (?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), user_id, action_type, amount, remaining))
    
    conn.commit()
    conn.close()
    return True

def generate_referral_code(user_id):
    """Generate a unique referral code"""
    import hashlib
    import random
    raw = f"{user_id}{random.randint(1000, 9999)}{datetime.now().timestamp()}"
    return hashlib.md5(raw.encode()).hexdigest()[:8].upper()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
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
                          subscription_plan, daily_quota, daily_usage, referral_code, referred_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, data['email'], password_hash,
        data.get('first_name', ''), data.get('last_name', ''),
        data.get('phone', ''), data.get('linkedin', ''), data.get('website', ''),
        'free', 5, 0, referral_code, data.get('referred_by', '')
    ))
    
    conn.commit()
    conn.close()
    
    # Generate token
    token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=30)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'token': token,
        'user': {
            'id': user_id,
            'email': data['email'],
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', '')
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, password_hash, first_name, last_name FROM users WHERE email = ?', (data['email'],))
    user = cursor.fetchone()
    
    if not user or not check_password_hash(user[1], data['password']):
        conn.close()
        return jsonify({'error': 'Invalid credentials'}), 401
    
    conn.close()
    
    # Generate token
    token = jwt.encode({
        'user_id': user[0],
        'exp': datetime.utcnow() + timedelta(days=30)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'token': token,
        'user': {
            'id': user[0],
            'email': data['email'],
            'first_name': user[2],
            'last_name': user[3]
        }
    })

@app.route('/api/applications', methods=['GET'])
@token_required
def get_applications(current_user_id):
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
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
    
    conn.close()
    return jsonify(applications)

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
    conn = sqlite3.connect('easyapply.db')
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
@token_required
def upload_resume(current_user_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(f"{current_user_id}_{int(time.time())}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        return jsonify({
            'message': 'Resume uploaded successfully',
            'filename': filename,
            'path': file_path
        })
    
    return jsonify({'error': 'Invalid file type. Please upload a PDF file.'}), 400

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
    
    def run_bot():
        try:
            # Create web platform bot instance
            bot = WebPlatformLinkedInBot(current_user_id, config)
            active_bots[current_user_id] = bot
            
            # Set up status callback
            def status_callback(status_data):
                bot_status[current_user_id] = {
                    **status_data,
                    'started_at': bot_status.get(current_user_id, {}).get('started_at', datetime.now().isoformat())
                }
                if status_data['status'] in ['completed', 'error', 'stopped']:
                    bot_status[current_user_id]['completed_at'] = datetime.now().isoformat()
            
            bot.set_status_callback(status_callback)
            
            # Initialize status
            bot_status[current_user_id] = {
                'status': 'starting',
                'progress': 0,
                'current_task': 'Initializing agent...',
                'applications_submitted': 0,
                'started_at': datetime.now().isoformat()
            }
            
            # Run the bot
            applications_made = bot.run_applications(
                max_applications=max_applications, 
                continuous=data.get('continuous', False)
            )
            
        except Exception as e:
            bot_status[current_user_id] = {
                'status': 'error',
                'error': str(e),
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
    """Load user configuration or return default config"""
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        # You could customize this per user
        return config
    except Exception:
        # Return default config
        return {
            'email': '',
            'password': '',
            'positions': ['Software Engineer'],
            'locations': ['Any'],
            'remote': True
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
               stripe_customer_id, current_period_end
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
            'current_period_end': row[10]
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
        'users_by_plan': users_by_plan,
        'total_applications': total_applications,
        'applications_this_month': applications_this_month,
        'monthly_revenue': monthly_revenue
    })

# Profile management endpoints
@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user_id):
    """Get user profile including encrypted LinkedIn credentials"""
    conn = sqlite3.connect('easyapply.db')
    cursor = conn.cursor()
    
    # Get user data
    cursor.execute('''
        SELECT first_name, last_name, email, phone, linkedin, website,
               linkedin_email_encrypted, linkedin_password_encrypted
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
    conn.close()
    
    # Decrypt LinkedIn credentials
    linkedin_creds = {'email': '', 'password': ''}
    if user_data[6] and user_data[7]:  # linkedin_email_encrypted, linkedin_password_encrypted
        try:
            from backend.security import decrypt_data
            linkedin_creds = {
                'email': decrypt_data(user_data[6]) or '',
                'password': decrypt_data(user_data[7]) or ''
            }
        except Exception as e:
            print(f"Failed to decrypt LinkedIn credentials: {e}")
    
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
            'jobTitles': preferences[0] if preferences else '',
            'locations': preferences[1] if preferences else '',
            'remote': bool(preferences[2]) if preferences else True,
            'experience': preferences[3] if preferences else 'mid',
            'salaryMin': preferences[4] if preferences else '',
            'skills': preferences[5] if preferences else ''
        }
    }
    
    return jsonify(response_data)

@app.route('/api/profile', methods=['PUT'])
@token_required
def update_profile(current_user_id):
    """Update user profile including LinkedIn credentials"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        conn = sqlite3.connect('easyapply.db')
        cursor = conn.cursor()
        
        # Update user information
        user_data = data.get('user', {})
        if user_data:
            cursor.execute('''
                UPDATE users 
                SET first_name = ?, last_name = ?, phone = ?, website = ?, updated_at = ?
                WHERE id = ?
            ''', (
                user_data.get('firstName', ''),
                user_data.get('lastName', ''),
                user_data.get('phone', ''),
                user_data.get('website', ''),
                datetime.now().isoformat(),
                current_user_id
            ))
        
        # Update LinkedIn credentials (encrypted)
        linkedin_creds = data.get('linkedinCreds', {})
        if linkedin_creds and linkedin_creds.get('email') and linkedin_creds.get('password'):
            try:
                from backend.security import encrypt_data, validate_linkedin_credentials
                
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
                    preferences.get('jobTitles', ''),
                    preferences.get('locations', ''),
                    preferences.get('remote', True),
                    preferences.get('experience', 'mid'),
                    preferences.get('salaryMin', ''),
                    preferences.get('skills', ''),
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
                    preferences.get('jobTitles', ''),
                    preferences.get('locations', ''),
                    preferences.get('remote', True),
                    preferences.get('experience', 'mid'),
                    preferences.get('salaryMin', ''),
                    preferences.get('skills', ''),
                    datetime.now().isoformat()
                ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Profile updated successfully'})
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001) 