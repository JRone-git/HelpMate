"""
Security utilities for ClawMate Core
"""
import secrets
import hashlib
import hmac
from typing import Optional
import os
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token and return the payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(provided_key: str, stored_hash: str) -> bool:
    """Verify an API key against its stored hash"""
    return hash_api_key(provided_key) == stored_hash


def is_safe_path(basedir: str, path: str) -> bool:
    """Check if a path is safe (prevents directory traversal attacks)"""
    try:
        # Resolve both paths
        base = os.path.abspath(basedir)
        target = os.path.abspath(path)
        
        # Check if target is within base directory
        return os.path.commonpath([base]) == os.path.commonpath([base, target])
    except (ValueError, OSError):
        return False


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and other attacks"""
    # Remove path separators
    filename = filename.replace('/', '').replace('\\', '')
    
    # Remove dangerous characters
    filename = ''.join(c for c in filename if c.isalnum() or c in ('-', '_', '.'))
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename


def rate_limit_key(identifier: str, action: str = "default") -> str:
    """Generate a rate limiting key"""
    return f"rate_limit:{action}:{identifier}"


def validate_input_length(value: str, max_length: int = 1000) -> str:
    """Validate and truncate input length"""
    if len(value) > max_length:
        raise ValueError(f"Input too long (max {max_length} characters)")
    return value.strip()


def is_valid_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


class SecurityHeaders:
    """Security headers configuration"""
    
    @staticmethod
    def get_headers():
        """Get recommended security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
        }