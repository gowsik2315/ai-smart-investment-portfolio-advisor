"""
Security Utilities
JWT token creation and verification, bcrypt password hashing
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.

    A malformed or non-bcrypt stored value is a verification FAILURE, not
    a reason to try something else. An earlier version fell back to
    comparing the two strings directly, to carry over dev accounts
    created before hashing existed. No such account remains, and the
    fallback turned any non-hash written into `password_hash` into a
    working password — so it is gone. Authentication has exactly one
    path now.
    """
    try:
        password_bytes = plain_password.encode("utf-8")
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception:
        # Corrupt hash, wrong format, or an over-long input: all mean
        # "cannot verify", which is the same as "no".
        return False


# bcrypt truncates/rejects beyond 72 bytes of input
BCRYPT_MAX_PASSWORD_BYTES = 72


def get_password_hash(password: str) -> str:
    """
    Hash a plain-text password with bcrypt (cost factor 12).

    Raises:
        ValueError: if the password exceeds bcrypt's 72-byte input limit.

    `UserCreate` already validates this, so the check here is defensive —
    it keeps any other call path (a future admin tool, a seed script)
    from surfacing bcrypt's own error as an opaque 500. Deliberately not
    truncating: two passwords sharing a 72-byte prefix would otherwise
    hash identically.
    """
    password_bytes = password.encode("utf-8")

    if len(password_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
        raise ValueError(
            f"Password exceeds bcrypt's {BCRYPT_MAX_PASSWORD_BYTES}-byte limit "
            f"({len(password_bytes)} bytes)"
        )

    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Dictionary containing claims to encode
        expires_delta: Optional expiration time delta
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create JWT refresh token
    
    Args:
        data: Dictionary containing claims to encode
    
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and verify JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user_id(token: str) -> Optional[int]:
    """
    Extract user ID from JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        User ID or None if invalid
    """
    payload = decode_token(token)
    if payload:
        user_id = payload.get("sub")
        return int(user_id) if user_id else None
    return None
