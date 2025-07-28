import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Tuple, Optional
import re
import secrets

def get_encryption_key() -> bytes:
    """
    Get encryption key for sensitive data.
    Priority:
    1. Environment variable ENCRYPTION_KEY
    2. Generate a new one from user-specific data
    
    This ensures each user/deployment has their own key and nothing is committed to git.
    """
    # Try to get key from environment first
    env_key = os.getenv('ENCRYPTION_KEY')
    if env_key:
        try:
            # If it's a hex string, convert it
            if len(env_key) == 64:  # 32 bytes = 64 hex chars
                key_bytes = bytes.fromhex(env_key)
            else:
                # If it's base64 encoded
                key_bytes = base64.urlsafe_b64decode(env_key.encode())
            
            # Validate key length
            if len(key_bytes) == 32:
                return base64.urlsafe_b64encode(key_bytes)
            else:
                print("⚠️ ENCRYPTION_KEY has invalid length, generating new one")
        except Exception as e:
            print(f"⚠️ ENCRYPTION_KEY invalid format: {e}, generating new one")
    
    # Generate a deterministic key based on system/user info
    # This ensures consistency across sessions but uniqueness per system
    key_material = generate_user_specific_key_material()
    
    # Use PBKDF2 to derive a proper encryption key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'ApplyX_LinkedIn_Bot_2024',  # Fixed salt for consistency
        iterations=100000,
    )
    
    derived_key = kdf.derive(key_material.encode())
    return base64.urlsafe_b64encode(derived_key)

def generate_user_specific_key_material() -> str:
    """
    Generate user-specific key material that's consistent but unique per system.
    This prevents credentials from being decryptable across different systems.
    """
    import platform
    import getpass
    
    # Get system-specific information
    username = getpass.getuser()
    hostname = platform.node()
    system = platform.system()
    
    # Create a unique but consistent identifier for this user/system
    user_system_id = f"{username}@{hostname}-{system}"
    
    # Add some additional entropy from environment
    home_dir = os.path.expanduser("~")
    
    # Combine all factors
    key_material = f"ApplyX-{user_system_id}-{home_dir}-LinkedIn-Encryption-2024"
    
    return key_material

# Global encryption instance
_fernet = None

def get_fernet():
    """Get Fernet encryption instance"""
    global _fernet
    if _fernet is None:
        key = get_encryption_key()
        _fernet = Fernet(key)
    return _fernet

def encrypt_data(data: str) -> Optional[str]:
    """Encrypt sensitive data (user credentials)"""
    if not data:
        return None
    
    try:
        fernet = get_fernet()
        encrypted = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    except Exception as e:
        print(f"🔒 Encryption error: {e}")
        return None

def decrypt_data(encrypted_data: str) -> Optional[str]:
    """Decrypt sensitive data (user credentials)"""
    if not encrypted_data:
        return None
    
    try:
        fernet = get_fernet()
        decoded = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = fernet.decrypt(decoded)
        return decrypted.decode()
    except Exception as e:
        print(f"🔒 Decryption error: {e}")
        return None

def validate_linkedin_credentials(email: str, password: str) -> Tuple[bool, str]:
    """Validate LinkedIn credentials format"""
    if not email or not password:
        return False, "Email and password are required"
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    # Password length check
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if len(password) > 200:
        return False, "Password is too long"
    
    return True, ""

def validate_file_upload(file) -> Tuple[bool, str]:
    """Validate uploaded file"""
    if not file:
        return False, "No file provided"
    
    if not file.filename:
        return False, "No filename provided"
    
    # Check file extension
    allowed_extensions = ['.pdf', '.doc', '.docx']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)     # Reset to beginning
    
    max_size = 16 * 1024 * 1024  # 16MB
    if file_size > max_size:
        return False, f"File too large. Maximum size: {max_size // (1024*1024)}MB"
    
    if file_size < 1024:  # Less than 1KB
        return False, "File too small. Minimum size: 1KB"
    
    # Check for suspicious file patterns
    dangerous_patterns = [
        b'<script', b'javascript:', b'<?php', b'<%', b'#!/bin/sh'
    ]
    
    # Read first 1KB to check for dangerous patterns
    file_start = file.read(1024)
    file.seek(0)  # Reset
    
    for pattern in dangerous_patterns:
        if pattern in file_start.lower():
            return False, "File contains suspicious content"
    
    return True, ""

def hash_sensitive_data(data: str, salt: str = None) -> str:
    """Hash sensitive data with salt"""
    if not salt:
        salt = os.urandom(32)
    elif isinstance(salt, str):
        salt = salt.encode()
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(data.encode()))
    return key.decode()

def verify_hashed_data(data: str, hashed: str, salt: str) -> bool:
    """Verify hashed data"""
    try:
        new_hash = hash_sensitive_data(data, salt)
        return new_hash == hashed
    except:
        return False

def generate_secure_encryption_key() -> str:
    """Generate a new secure encryption key for environment variables"""
    key = Fernet.generate_key()
    return base64.urlsafe_b64decode(key).hex()

def test_encryption_system():
    """Test the encryption system to ensure it's working"""
    test_data = "test@linkedin.com"
    
    encrypted = encrypt_data(test_data)
    if not encrypted:
        return False, "Failed to encrypt test data"
    
    decrypted = decrypt_data(encrypted)
    if decrypted != test_data:
        return False, "Failed to decrypt test data correctly"
    
    return True, "Encryption system working correctly" 