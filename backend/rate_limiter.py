import time
from collections import defaultdict, deque
from functools import wraps
from flask import request, jsonify
import threading

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(deque)
        self.lock = threading.Lock()
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """
        Check if a request is allowed based on rate limiting rules
        key: identifier (IP address, user ID, etc.)
        limit: maximum number of requests allowed
        window: time window in seconds
        """
        current_time = time.time()
        
        with self.lock:
            # Clean old requests outside the window
            while self.requests[key] and self.requests[key][0] < current_time - window:
                self.requests[key].popleft()
            
            # Check if limit is exceeded
            if len(self.requests[key]) >= limit:
                return False
            
            # Add current request
            self.requests[key].append(current_time)
            return True
    
    def get_remaining_requests(self, key: str, limit: int, window: int) -> int:
        """Get number of remaining requests for a key"""
        current_time = time.time()
        
        with self.lock:
            # Clean old requests
            while self.requests[key] and self.requests[key][0] < current_time - window:
                self.requests[key].popleft()
            
            return max(0, limit - len(self.requests[key]))
    
    def get_reset_time(self, key: str, window: int) -> float:
        """Get when the rate limit resets for a key"""
        with self.lock:
            if not self.requests[key]:
                return time.time()
            return self.requests[key][0] + window

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(limit: int = 60, window: int = 60, per: str = 'ip'):
    """
    Rate limiting decorator
    limit: maximum number of requests
    window: time window in seconds
    per: what to rate limit by ('ip', 'user', 'endpoint')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Determine the key for rate limiting
            if per == 'ip':
                key = f"ip:{request.remote_addr}"
            elif per == 'user':
                # Extract user ID from JWT token if available
                auth_header = request.headers.get('Authorization')
                if auth_header and auth_header.startswith('Bearer '):
                    try:
                        import jwt
                        from flask import current_app
                        token = auth_header[7:]
                        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                        key = f"user:{data['user_id']}"
                    except:
                        key = f"ip:{request.remote_addr}"
                else:
                    key = f"ip:{request.remote_addr}"
            elif per == 'endpoint':
                key = f"endpoint:{request.endpoint}:{request.remote_addr}"
            else:
                key = f"ip:{request.remote_addr}"
            
            # Check rate limit
            if not rate_limiter.is_allowed(key, limit, window):
                remaining = rate_limiter.get_remaining_requests(key, limit, window)
                reset_time = rate_limiter.get_reset_time(key, window)
                
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Limit: {limit} per {window} seconds',
                    'remaining': remaining,
                    'reset_time': reset_time,
                    'retry_after': max(0, reset_time - time.time())
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Predefined rate limiters for common use cases
def auth_rate_limit(f):
    """Rate limiter for authentication endpoints (stricter)"""
    return rate_limit(limit=5, window=60, per='ip')(f)

def api_rate_limit(f):
    """Rate limiter for general API endpoints"""
    return rate_limit(limit=100, window=60, per='user')(f)

def public_rate_limit(f):
    """Rate limiter for public endpoints"""
    return rate_limit(limit=30, window=60, per='ip')(f) 