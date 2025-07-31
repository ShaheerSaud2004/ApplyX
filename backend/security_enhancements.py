import os
import re
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from functools import wraps
from flask import request, jsonify, current_app
import jwt
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    """Comprehensive security manager for the application"""
    
    def __init__(self):
        self.failed_login_attempts = {}  # Track failed login attempts
        self.ip_blacklist = {}  # Track blacklisted IPs
        self.rate_limit_data = {}  # Rate limiting data
        self.session_tokens = {}  # Active session tokens
        
        # Security configuration
        self.max_login_attempts = 5
        self.lockout_duration = 900  # 15 minutes
        self.rate_limit_window = 60  # 1 minute
        self.max_requests_per_window = 100
        self.session_timeout = 3600  # 1 hour
        self.password_history_size = 5
        
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt with high cost factor"""
        salt = bcrypt.gensalt(rounds=14)  # High cost factor for security
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_secure_token(self, user_id: int, additional_data: dict = None) -> str:
        """Generate secure JWT token with short expiration"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=1),  # 1 hour expiration
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(32),  # Unique token ID
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')[:100]
        }
        
        if additional_data:
            payload.update(additional_data)
            
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    def validate_token(self, token: str) -> Tuple[bool, dict]:
        """Validate JWT token with additional security checks"""
        try:
            # Decode token
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            
            # Check if token is blacklisted
            if payload.get('jti') in self.session_tokens.get('blacklisted', set()):
                return False, {'error': 'Token has been revoked'}
            
            # Check IP address (prevent token reuse from different IPs)
            if payload.get('ip') != request.remote_addr:
                logger.warning(f"Token IP mismatch: {payload.get('ip')} vs {request.remote_addr}")
                return False, {'error': 'Invalid token source'}
            
            return True, payload
            
        except jwt.ExpiredSignatureError:
            return False, {'error': 'Token has expired'}
        except jwt.InvalidTokenError:
            return False, {'error': 'Invalid token'}
    
    def check_rate_limit(self, identifier: str, limit: int = None, window: int = None) -> bool:
        """Check rate limiting for requests"""
        limit = limit or self.max_requests_per_window
        window = window or self.rate_limit_window
        
        current_time = time.time()
        key = f"{identifier}:{current_time // window}"
        
        if key not in self.rate_limit_data:
            self.rate_limit_data[key] = []
        
        # Clean old entries
        self.rate_limit_data[key] = [
            timestamp for timestamp in self.rate_limit_data[key]
            if current_time - timestamp < window
        ]
        
        if len(self.rate_limit_data[key]) >= limit:
            return False
        
        self.rate_limit_data[key].append(current_time)
        return True
    
    def check_login_attempts(self, identifier: str) -> Tuple[bool, int]:
        """Check if login attempts are within limits"""
        current_time = time.time()
        
        if identifier not in self.failed_login_attempts:
            return True, 0
        
        attempts = self.failed_login_attempts[identifier]
        
        # Clean old attempts
        attempts = [timestamp for timestamp in attempts if current_time - timestamp < self.lockout_duration]
        self.failed_login_attempts[identifier] = attempts
        
        if len(attempts) >= self.max_login_attempts:
            return False, len(attempts)
        
        return True, len(attempts)
    
    def record_failed_login(self, identifier: str):
        """Record a failed login attempt"""
        current_time = time.time()
        
        if identifier not in self.failed_login_attempts:
            self.failed_login_attempts[identifier] = []
        
        self.failed_login_attempts[identifier].append(current_time)
    
    def reset_login_attempts(self, identifier: str):
        """Reset failed login attempts for successful login"""
        if identifier in self.failed_login_attempts:
            del self.failed_login_attempts[identifier]
    
    def validate_input(self, data: str, max_length: int = 1000) -> Tuple[bool, str]:
        """Validate and sanitize input data"""
        if not data or not isinstance(data, str):
            return False, "Invalid input data"
        
        if len(data) > max_length:
            return False, f"Input too long (max {max_length} characters)"
        
        # Check for SQL injection patterns
        sql_patterns = [
            r'(\b(union|select|insert|update|delete|drop|create|alter)\b)',
            r'(\b(and|or)\b\s+\d+\s*[=<>])',
            r'(\b(exec|execute|script|javascript)\b)',
            r'(\b(union|select)\b.*\bfrom\b)',
            r'(\b(union|select)\b.*\bwhere\b)',
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return False, "Invalid input detected"
        
        # Check for XSS patterns
        xss_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return False, "Invalid input detected"
        
        return True, data
    
    def validate_email(self, email: str) -> Tuple[bool, str]:
        """Enhanced email validation"""
        if not email or not isinstance(email, str):
            return False, "Email is required"
        
        # Basic format check
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        # Additional security checks
        if len(email) > 254:  # RFC 5321 limit
            return False, "Email too long"
        
        if '..' in email or email.startswith('.') or email.endswith('.'):
            return False, "Invalid email format"
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'data:text/html',
            r'vbscript:',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                return False, "Invalid email format"
        
        return True, email
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """Enhanced password strength validation"""
        if not password or not isinstance(password, str):
            return False, "Password is required"
        
        if len(password) < 12:  # Increased minimum length
            return False, "Password must be at least 12 characters long"
        
        if len(password) > 128:
            return False, "Password cannot be longer than 128 characters"
        
        # Check for common patterns
        if re.match(r'^[a-zA-Z]+$', password):
            return False, "Password must contain numbers and special characters"
        
        if re.match(r'^[0-9]+$', password):
            return False, "Password must contain letters and special characters"
        
        # Check for common weak passwords
        weak_passwords = [
            'password', '123456789012', 'qwerty123456', 'abc123456789',
            'password123', '123456789012', 'welcome123456', 'admin123456',
            'letmein123456', 'password1', '123123123123'
        ]
        
        if password.lower() in weak_passwords:
            return False, "Password is too common and weak"
        
        # Check for repeated characters
        if re.search(r'(.)\1{4,}', password):
            return False, "Password cannot contain more than 4 repeated characters"
        
        # Check for keyboard patterns
        keyboard_patterns = [
            'qwertyuiop', 'asdfghjkl', 'zxcvbnm',
            '1234567890', 'qwerty123', 'abc123'
        ]
        
        for pattern in keyboard_patterns:
            if pattern in password.lower():
                return False, "Password contains common keyboard patterns"
        
        return True, password
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data using Fernet"""
        if not data:
            return ""
        
        key = current_app.config.get('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY not configured")
        
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data.encode())
        return encrypted.decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted_data:
            return ""
        
        key = current_app.config.get('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY not configured")
        
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()
    
    def generate_secure_filename(self, original_filename: str) -> str:
        """Generate secure filename to prevent path traversal"""
        if not original_filename:
            return ""
        
        # Remove path components
        filename = os.path.basename(original_filename)
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\-_.]', '_', filename)
        
        # Add timestamp and random component
        timestamp = str(int(time.time()))
        random_component = secrets.token_urlsafe(8)
        
        name, ext = os.path.splitext(filename)
        return f"{name}_{timestamp}_{random_component}{ext}"
    
    def log_security_event(self, event_type: str, details: dict, user_id: int = None):
        """Log security events for monitoring"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'user_id': user_id,
            'details': details
        }
        
        logger.warning(f"SECURITY_EVENT: {log_entry}")
        
        # In production, you might want to send this to a security monitoring service
        # or store it in a dedicated security log table

# Global security manager instance
security_manager = SecurityManager()

# Security decorators
def secure_route(f):
    """Decorator to add security checks to routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check rate limiting
        identifier = f"{request.remote_addr}:{request.endpoint}"
        if not security_manager.check_rate_limit(identifier):
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.'
            }), 429
        
        # Log security event
        security_manager.log_security_event('route_access', {
            'endpoint': request.endpoint,
            'method': request.method,
            'path': request.path
        })
        
        return f(*args, **kwargs)
    return decorated_function

def validate_json_input(f):
    """Decorator to validate JSON input"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.is_json:
            data = request.get_json()
            if data:
                # Validate all string values in the JSON
                for key, value in data.items():
                    if isinstance(value, str):
                        is_valid, message = security_manager.validate_input(value)
                        if not is_valid:
                            return jsonify({
                                'error': 'Invalid input',
                                'message': f"Field '{key}': {message}"
                            }), 400
        
        return f(*args, **kwargs)
    return decorated_function

def require_https(f):
    """Decorator to require HTTPS in production"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and not current_app.debug:
            return jsonify({
                'error': 'HTTPS required',
                'message': 'This endpoint requires a secure connection.'
            }), 403
        return f(*args, **kwargs)
    return decorated_function 