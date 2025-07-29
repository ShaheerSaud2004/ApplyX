import re
from typing import Tuple

def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format with comprehensive checks
    Returns (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    # Basic format check
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    # Additional checks
    if '..' in email:
        return False, "Email cannot contain consecutive dots"
    
    if email.startswith('.') or email.startswith('@') or email.endswith('.'):
        return False, "Invalid email format"
    
    # Check for common invalid patterns
    local_part, domain_part = email.rsplit('@', 1)
    
    if not local_part or not domain_part:
        return False, "Invalid email format"
    
    if len(local_part) > 64:
        return False, "Email local part too long"
    
    if len(domain_part) > 255:
        return False, "Email domain too long"
    
    # Domain must contain at least one dot
    if '.' not in domain_part:
        return False, "Invalid domain format"
    
    return True, ""

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength with comprehensive requirements
    Returns (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    # Minimum length check
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Maximum length check (for security)
    if len(password) > 128:
        return False, "Password cannot be longer than 128 characters"
    
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    # Check for common weak passwords
    weak_passwords = [
        'password', '12345678', 'qwerty123', 'abc123456', 
        'password123', '123456789', 'welcome123', 'admin123',
        'letmein123', 'password1', '123123123'
    ]
    
    if password.lower() in weak_passwords:
        return False, "Password is too common and weak"
    
    # Check for repeated characters (more than 3 in a row)
    if re.search(r'(.)\1{3,}', password):
        return False, "Password cannot contain more than 3 repeated characters in a row"
    
    return True, ""

def validate_user_registration(data: dict) -> Tuple[bool, str]:
    """
    Validate user registration data
    Returns (is_valid, error_message)
    """
    # Check required fields
    required_fields = ['email', 'password']
    for field in required_fields:
        if not data.get(field):
            return False, f"{field.capitalize()} is required"
    
    # Validate email
    email_valid, email_error = validate_email(data['email'])
    if not email_valid:
        return False, email_error
    
    # Validate password
    password_valid, password_error = validate_password(data['password'])
    if not password_valid:
        return False, password_error
    
    # Validate optional fields if provided
    if data.get('first_name') and len(data['first_name']) > 50:
        return False, "First name cannot be longer than 50 characters"
    
    if data.get('last_name') and len(data['last_name']) > 50:
        return False, "Last name cannot be longer than 50 characters"
    
    if data.get('phone'):
        phone_pattern = r'^\+?[\d\s\-\(\)]{10,15}$'
        if not re.match(phone_pattern, data['phone']):
            return False, "Invalid phone number format"
    
    return True, ""

def sanitize_input(input_str: str) -> str:
    """
    Sanitize input to prevent XSS and other injection attacks
    """
    if not input_str:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', 'script', 'javascript:', 'onload', 'onerror']
    
    sanitized = str(input_str)
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip() 