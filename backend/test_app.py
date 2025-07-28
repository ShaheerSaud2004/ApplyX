#!/usr/bin/env python3

import unittest
import json
import tempfile
import os
import sqlite3
from unittest.mock import patch, MagicMock
import sys

# Add the parent directory to Python path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, init_db

class TestEasyApplyAPI(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and database"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        
        # Create temporary database for testing
        self.test_db_fd, self.test_db_path = tempfile.mkstemp()
        
        # Override database path for testing
        self.original_db_path = 'easyapply.db'
        
        self.client = self.app.test_client()
        
        # Initialize test database
        with self.app.app_context():
            conn = sqlite3.connect(self.test_db_path)
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE users (
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
            
            # Create job_applications table
            cursor.execute('''
                CREATE TABLE job_applications (
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
                    ai_generated BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create other tables
            cursor.execute('''
                CREATE TABLE billing_events (
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
            
            cursor.execute('''
                CREATE TABLE usage_logs (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    quota_used INTEGER DEFAULT 1,
                    remaining_quota INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            conn.close()
        
        # Mock database path
        self.patch_db = patch('app.sqlite3.connect')
        self.mock_connect = self.patch_db.start()
        self.mock_connect.return_value = sqlite3.connect(self.test_db_path)
    
    def tearDown(self):
        """Clean up after tests"""
        self.patch_db.stop()
        os.close(self.test_db_fd)
        os.unlink(self.test_db_path)
    
    def register_test_user(self, email="test@example.com", password="testpass123"):
        """Helper method to register a test user"""
        return self.client.post('/api/auth/register', 
            data=json.dumps({
                'email': email,
                'password': password,
                'first_name': 'Test',
                'last_name': 'User'
            }),
            content_type='application/json'
        )
    
    def login_test_user(self, email="test@example.com", password="testpass123"):
        """Helper method to login and get token"""
        response = self.client.post('/api/auth/login',
            data=json.dumps({
                'email': email,
                'password': password
            }),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = json.loads(response.data)
            return data.get('token')
        return None
    
    def get_auth_headers(self, token):
        """Helper method to get authorization headers"""
        return {'Authorization': f'Bearer {token}'}
    
    # Health Check Tests
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    # Authentication Tests
    def test_user_registration(self):
        """Test user registration"""
        response = self.register_test_user()
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], 'test@example.com')
    
    def test_duplicate_registration(self):
        """Test duplicate email registration"""
        self.register_test_user()
        response = self.register_test_user()  # Try to register again
        self.assertEqual(response.status_code, 409)
    
    def test_user_login(self):
        """Test user login"""
        self.register_test_user()
        
        response = self.client.post('/api/auth/login',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'testpass123'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)
        self.assertIn('user', data)
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = self.client.post('/api/auth/login',
            data=json.dumps({
                'email': 'nonexistent@example.com',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    # Protected Route Tests
    def test_protected_route_without_token(self):
        """Test accessing protected route without token"""
        response = self.client.get('/api/applications')
        self.assertEqual(response.status_code, 401)
    
    def test_protected_route_with_valid_token(self):
        """Test accessing protected route with valid token"""
        self.register_test_user()
        token = self.login_test_user()
        
        response = self.client.get('/api/applications',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
    
    # Applications Tests
    def test_get_empty_applications(self):
        """Test getting applications when none exist"""
        self.register_test_user()
        token = self.login_test_user()
        
        response = self.client.get('/api/applications',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)
    
    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        self.register_test_user()
        token = self.login_test_user()
        
        response = self.client.get('/api/dashboard/stats',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('totalApplications', data)
        self.assertIn('weeklyApplications', data)
    
    # Agent Control Tests
    @patch('app.WebPlatformLinkedInBot')
    def test_start_agent(self, mock_bot_class):
        """Test starting the agent"""
        self.register_test_user()
        token = self.login_test_user()
        
        mock_bot = MagicMock()
        mock_bot_class.return_value = mock_bot
        
        response = self.client.post('/api/agent/start',
            headers=self.get_auth_headers(token),
            data=json.dumps({'max_applications': 5}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
    
    def test_agent_status(self):
        """Test getting agent status"""
        self.register_test_user()
        token = self.login_test_user()
        
        response = self.client.get('/api/agent/status',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
    
    # File Upload Tests
    def test_resume_upload_no_file(self):
        """Test resume upload without file"""
        self.register_test_user()
        token = self.login_test_user()
        
        response = self.client.post('/api/upload/resume',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_resume_upload_invalid_file(self):
        """Test resume upload with invalid file type"""
        self.register_test_user()
        token = self.login_test_user()
        
        # Create a fake text file
        data = {
            'resume': (tempfile.NamedTemporaryFile(suffix='.txt'), 'test.txt')
        }
        
        response = self.client.post('/api/upload/resume',
            headers=self.get_auth_headers(token),
            data=data
        )
        
        self.assertEqual(response.status_code, 400)
    
    # Admin Tests
    def test_admin_access_non_admin(self):
        """Test admin endpoints with non-admin user"""
        self.register_test_user()
        token = self.login_test_user()
        
        response = self.client.get('/api/admin/users',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 403)
    
    # Quota Tests
    @patch('app.can_use_quota')
    def test_quota_exceeded(self, mock_quota):
        """Test quota exceeded scenario"""
        mock_quota.return_value = False
        
        self.register_test_user()
        token = self.login_test_user()
        
        response = self.client.post('/api/agent/start',
            headers=self.get_auth_headers(token),
            data=json.dumps({'max_applications': 5}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 429)
    
    # Stripe Tests
    @patch('stripe.Customer.create')
    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session(self, mock_session, mock_customer):
        """Test Stripe checkout session creation"""
        self.register_test_user()
        token = self.login_test_user()
        
        mock_customer.return_value = MagicMock(id='cus_test123')
        mock_session.return_value = MagicMock(url='https://checkout.stripe.com/test')
        
        response = self.client.post('/api/stripe/create-checkout-session',
            headers=self.get_auth_headers(token),
            data=json.dumps({'plan_id': 'basic'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('checkout_url', data)
    
    def test_invalid_stripe_plan(self):
        """Test Stripe checkout with invalid plan"""
        self.register_test_user()
        token = self.login_test_user()
        
        response = self.client.post('/api/stripe/create-checkout-session',
            headers=self.get_auth_headers(token),
            data=json.dumps({'plan_id': 'invalid'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    # Security Tests
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        # Try SQL injection in login
        response = self.client.post('/api/auth/login',
            data=json.dumps({
                'email': "'; DROP TABLE users; --",
                'password': 'anything'
            }),
            content_type='application/json'
        )
        
        # Should return 401, not cause database error
        self.assertEqual(response.status_code, 401)
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON"""
        response = self.client.post('/api/auth/login',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_missing_required_fields(self):
        """Test missing required fields in registration"""
        response = self.client.post('/api/auth/register',
            data=json.dumps({
                'email': 'test@example.com'
                # Missing password
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    # Create test database directory
    os.makedirs('test_uploads', exist_ok=True)
    
    # Run tests
    unittest.main(verbosity=2) 