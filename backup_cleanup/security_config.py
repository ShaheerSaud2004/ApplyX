"""
Security Configuration for ApplyX Backend
This file contains security best practices and configuration recommendations
"""

import os
from typing import List, Dict

class SecurityConfig:
    """Security configuration and best practices"""
    
    # Password requirements
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_MAX_LENGTH = 128
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    # Session security
    SESSION_TIMEOUT = 3600  # 1 hour
    TOKEN_EXPIRY = 3600     # 1 hour
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 900  # 15 minutes
    
    # Rate limiting
    RATE_LIMIT_WINDOW = 60  # 1 minute
    MAX_REQUESTS_PER_WINDOW = 100
    AUTH_RATE_LIMIT = 5     # 5 attempts per 5 minutes
    
    # File upload security
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    ALLOWED_FILE_EXTENSIONS = ['.pdf', '.doc', '.docx']
    UPLOAD_PATH = 'uploads'
    
    # Database security
    DB_PATH = 'easyapply.db'
    DB_BACKUP_ENABLED = True
    DB_BACKUP_INTERVAL = 24  # hours
    
    # Encryption
    ENCRYPTION_ALGORITHM = 'AES-256-GCM'
    KEY_ROTATION_INTERVAL = 90  # days
    
    # Logging
    SECURITY_LOG_LEVEL = 'WARNING'
    LOG_ROTATION_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_RETENTION_DAYS = 30
    
    # CORS settings
    ALLOWED_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:3001',
        'https://apply-x.vercel.app',
        'https://*.vercel.app'
    ]
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; frame-ancestors 'none';",
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
    }
    
    # Suspicious patterns for detection
    SUSPICIOUS_PATTERNS = [
        # SQL Injection patterns
        r'(\b(union|select|insert|update|delete|drop|create|alter)\b)',
        r'(\b(union|select)\b.*\bfrom\b)',
        r'(\b(union|select)\b.*\bwhere\b)',
        r'(\b(and|or)\b\s+\d+\s*[=<>])',
        r'(\b(and|or)\b\s+\'\w+\'\s*[=<>])',
        r'(\b(and|or)\b\s+\"\w+\"\s*[=<>])',
        
        # XSS patterns
        r'<script[^>]*>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
        r'data:text/html',
        r'vbscript:',
        
        # Path traversal
        r'\.\./',
        r'\.\.\\',
        r'%2e%2e',
        r'%5c%5c',
        
        # Command injection
        r'(\b(exec|execute|system|eval)\b)',
        r'(\b(import|include|require)\b)',
        r'(\b(file|ftp|gopher)://)',
    ]
    
    # Blocked user agents
    BLOCKED_USER_AGENTS = [
        'sqlmap', 'nikto', 'nmap', 'wget', 'curl', 'python-requests',
        'scanner', 'bot', 'crawler', 'spider', 'masscan', 'dirb'
    ]
    
    # Environment-specific settings
    @classmethod
    def get_production_settings(cls) -> Dict:
        """Get production security settings"""
        return {
            'DEBUG': False,
            'TESTING': False,
            'SESSION_COOKIE_SECURE': True,
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Strict',
            'PERMANENT_SESSION_LIFETIME': cls.SESSION_TIMEOUT,
            'MAX_CONTENT_LENGTH': cls.MAX_FILE_SIZE,
        }
    
    @classmethod
    def get_development_settings(cls) -> Dict:
        """Get development security settings"""
        return {
            'DEBUG': True,
            'TESTING': False,
            'SESSION_COOKIE_SECURE': False,  # Allow HTTP in dev
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Lax',  # More permissive in dev
            'PERMANENT_SESSION_LIFETIME': cls.SESSION_TIMEOUT,
            'MAX_CONTENT_LENGTH': cls.MAX_FILE_SIZE,
        }
    
    @classmethod
    def validate_environment(cls) -> List[str]:
        """Validate environment variables for security"""
        errors = []
        
        required_vars = [
            'SECRET_KEY',
            'ENCRYPTION_KEY',
            'DATABASE_URL',
            'OPENAI_API_KEY'
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                errors.append(f"Missing required environment variable: {var}")
        
        # Check for weak secret keys
        secret_key = os.getenv('SECRET_KEY', '')
        if len(secret_key) < 32:
            errors.append("SECRET_KEY must be at least 32 characters long")
        
        # Check for weak encryption keys
        encryption_key = os.getenv('ENCRYPTION_KEY', '')
        if len(encryption_key) < 32:
            errors.append("ENCRYPTION_KEY must be at least 32 characters long")
        
        return errors
    
    @classmethod
    def get_security_recommendations(cls) -> List[str]:
        """Get security recommendations for deployment"""
        return [
            "1. Use HTTPS in production",
            "2. Set strong SECRET_KEY and ENCRYPTION_KEY environment variables",
            "3. Enable database backups",
            "4. Monitor security logs regularly",
            "5. Keep dependencies updated",
            "6. Use a reverse proxy (nginx) in production",
            "7. Enable rate limiting",
            "8. Implement proper error handling",
            "9. Use secure session management",
            "10. Regular security audits",
            "11. Enable two-factor authentication (future enhancement)",
            "12. Implement API versioning",
            "13. Use environment-specific configurations",
            "14. Enable request logging",
            "15. Implement proper CORS policies"
        ]

# Security checklist for deployment
SECURITY_CHECKLIST = [
    "Environment variables configured",
    "HTTPS enabled",
    "Security headers implemented",
    "Rate limiting active",
    "Input validation working",
    "Password requirements enforced",
    "Session management secure",
    "File upload restrictions active",
    "Database backups configured",
    "Logging enabled",
    "Error handling implemented",
    "CORS policies configured",
    "Dependencies updated",
    "Security monitoring active"
]

# Security monitoring events
SECURITY_EVENTS = [
    'failed_login',
    'successful_login',
    'registration_attempt',
    'suspicious_activity',
    'rate_limit_exceeded',
    'file_upload_attempt',
    'admin_action',
    'token_validation_failed',
    'input_validation_failed',
    'sql_injection_attempt',
    'xss_attempt',
    'path_traversal_attempt'
] 