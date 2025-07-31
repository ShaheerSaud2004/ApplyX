from flask import request, jsonify, current_app
import time
import re
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Security middleware for additional protection layers"""
    
    def __init__(self):
        self.request_history = {}  # Track request patterns
        self.suspicious_ips = {}   # Track suspicious IPs
        self.blocked_ips = set()   # Permanently blocked IPs
        
        # Security headers
        self.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; frame-ancestors 'none';",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }
        
        # Suspicious patterns
        self.suspicious_patterns = [
            r'(\b(union|select|insert|update|delete|drop|create|alter)\b)',
            r'(\b(exec|execute|script|javascript)\b)',
            r'(\b(union|select)\b.*\bfrom\b)',
            r'(\b(union|select)\b.*\bwhere\b)',
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'data:text/html',
            r'vbscript:',
            r'expression\(',
            r'url\(',
            r'import\(',
            r'include\(',
            r'require\(',
            r'file://',
            r'ftp://',
            r'gopher://',
            r'(\b(and|or)\b\s+\d+\s*[=<>])',
            r'(\b(and|or)\b\s+\'\w+\'\s*[=<>])',
            r'(\b(and|or)\b\s+\"\w+\"\s*[=<>])',
            r'(\b(and|or)\b\s+\d+\s*like)',
            r'(\b(and|or)\b\s+\'\w+\'\s*like)',
            r'(\b(and|or)\b\s+\"\w+\"\s*like)',
            r'(\b(and|or)\b\s+\d+\s*in\s*\()',
            r'(\b(and|or)\b\s+\'\w+\'\s*in\s*\()',
            r'(\b(and|or)\b\s+\"\w+\"\s*in\s*\()',
            r'(\b(and|or)\b\s+\d+\s*between)',
            r'(\b(and|or)\b\s+\'\w+\'\s*between)',
            r'(\b(and|or)\b\s+\"\w+\"\s*between)',
            r'(\b(and|or)\b\s+\d+\s*exists)',
            r'(\b(and|or)\b\s+\'\w+\'\s*exists)',
            r'(\b(and|or)\b\s+\"\w+\"\s*exists)',
            r'(\b(and|or)\b\s+\d+\s*not\s+exists)',
            r'(\b(and|or)\b\s+\'\w+\'\s*not\s+exists)',
            r'(\b(and|or)\b\s+\"\w+\"\s*not\s+exists)',
            r'(\b(and|or)\b\s+\d+\s*in\s*select)',
            r'(\b(and|or)\b\s+\'\w+\'\s*in\s*select)',
            r'(\b(and|or)\b\s+\"\w+\"\s*in\s*select)',
            r'(\b(and|or)\b\s+\d+\s*not\s+in\s*select)',
            r'(\b(and|or)\b\s+\'\w+\'\s*not\s+in\s*select)',
            r'(\b(and|or)\b\s+\"\w+\"\s*not\s+in\s*select)',
            r'(\b(and|or)\b\s+\d+\s*like\s*select)',
            r'(\b(and|or)\b\s+\'\w+\'\s*like\s*select)',
            r'(\b(and|or)\b\s+\"\w+\"\s*like\s*select)',
            r'(\b(and|or)\b\s+\d+\s*not\s+like\s*select)',
            r'(\b(and|or)\b\s+\'\w+\'\s*not\s+like\s*select)',
            r'(\b(and|or)\b\s+\"\w+\"\s*not\s+like\s*select)',
            r'(\b(and|or)\b\s+\d+\s*exists\s*select)',
            r'(\b(and|or)\b\s+\'\w+\'\s*exists\s*select)',
            r'(\b(and|or)\b\s+\"\w+\"\s*exists\s*select)',
            r'(\b(and|or)\b\s+\d+\s*not\s+exists\s*select)',
            r'(\b(and|or)\b\s+\'\w+\'\s*not\s+exists\s*select)',
            r'(\b(and|or)\b\s+\"\w+\"\s*not\s+exists\s*select)',
            r'(\b(and|or)\b\s+\d+\s*in\s*\(\s*select)',
            r'(\b(and|or)\b\s+\'\w+\'\s*in\s*\(\s*select)',
            r'(\b(and|or)\b\s+\"\w+\"\s*in\s*\(\s*select)',
            r'(\b(and|or)\b\s+\d+\s*not\s+in\s*\(\s*select)',
            r'(\b(and|or)\b\s+\'\w+\'\s*not\s+in\s*\(\s*select)',
            r'(\b(and|or)\b\s+\"\w+\"\s*not\s+in\s*\(\s*select)',
            r'(\b(and|or)\b\s+\d+\s*like\s*\(\s*select)',
            r'(\b(and|or)\b\s+\'\w+\'\s*like\s*\(\s*select)',
            r'(\b(and|or)\b\s+\"\w+\"\s*like\s*\(\s*select)',
            r'(\b(and|or)\b\s+\d+\s*not\s+like\s*\(\s*select)',
            r'(\b(and|or)\b\s+\'\w+\'\s*not\s+like\s*\(\s*select)',
            r'(\b(and|or)\b\s+\"\w+\"\s*not\s+like\s*\(\s*select)',
            r'(\b(and|or)\b\s+\d+\s*exists\s*\(\s*select)',
            r'(\b(and|or)\b\s+\'\w+\'\s*exists\s*\(\s*select)',
            r'(\b(and|or)\b\s+\"\w+\"\s*exists\s*\(\s*select)',
            r'(\b(and|or)\b\s+\d+\s*not\s+exists\s*\(\s*select)',
            r'(\b(and|or)\b\s+\'\w+\'\s*not\s+exists\s*\(\s*select)',
            r'(\b(and|or)\b\s+\"\w+\"\s*not\s+exists\s*\(\s*select)',
        ]
    
    def check_suspicious_patterns(self, data: str) -> bool:
        """Check for suspicious patterns in request data"""
        if not data:
            return False
        
        data_lower = data.lower()
        
        for pattern in self.suspicious_patterns:
            if re.search(pattern, data_lower, re.IGNORECASE):
                return True
        
        return False
    
    def check_request_anomalies(self, request_data: dict) -> Dict[str, bool]:
        """Check for request anomalies"""
        anomalies = {
            'suspicious_headers': False,
            'suspicious_user_agent': False,
            'suspicious_content': False,
            'unusual_method': False,
            'path_traversal': False
        }
        
        # Check for suspicious headers
        suspicious_headers = [
            'x-forwarded-for', 'x-real-ip', 'x-forwarded-host',
            'x-forwarded-proto', 'x-forwarded-port'
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                anomalies['suspicious_headers'] = True
                break
        
        # Check for suspicious user agent
        user_agent = request.headers.get('User-Agent', '').lower()
        suspicious_agents = [
            'sqlmap', 'nikto', 'nmap', 'wget', 'curl', 'python-requests',
            'scanner', 'bot', 'crawler', 'spider'
        ]
        
        for agent in suspicious_agents:
            if agent in user_agent:
                anomalies['suspicious_user_agent'] = True
                break
        
        # Check for path traversal attempts
        path = request.path.lower()
        traversal_patterns = [
            '..', '../', '..\\', '..%2f', '..%5c', '%2e%2e', '%5c%5c'
        ]
        
        for pattern in traversal_patterns:
            if pattern in path:
                anomalies['path_traversal'] = True
                break
        
        # Check for unusual HTTP methods
        unusual_methods = ['PUT', 'DELETE', 'PATCH', 'TRACE', 'OPTIONS']
        if request.method in unusual_methods:
            anomalies['unusual_method'] = True
        
        return anomalies
    
    def add_security_headers(self, response):
        """Add security headers to response"""
        for header, value in self.security_headers.items():
            response.headers[header] = value
        return response
    
    def log_suspicious_activity(self, ip: str, activity_type: str, details: dict):
        """Log suspicious activity"""
        log_entry = {
            'timestamp': time.time(),
            'ip_address': ip,
            'activity_type': activity_type,
            'user_agent': request.headers.get('User-Agent', ''),
            'path': request.path,
            'method': request.method,
            'details': details
        }
        
        logger.warning(f"SUSPICIOUS_ACTIVITY: {log_entry}")
        
        # Track suspicious IPs
        if ip not in self.suspicious_ips:
            self.suspicious_ips[ip] = []
        
        self.suspicious_ips[ip].append(log_entry)
        
        # Block IP if too many suspicious activities
        if len(self.suspicious_ips[ip]) > 10:
            self.blocked_ips.add(ip)
            logger.error(f"IP {ip} has been blocked due to suspicious activity")

# Global middleware instance
security_middleware = SecurityMiddleware() 