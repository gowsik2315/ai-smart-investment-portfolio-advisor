"""
User Schemas
Pydantic models for user-related requests and responses
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime

# bcrypt hashes at most 72 BYTES of input and raises on anything longer.
# The limit is in bytes, not characters, so a password of accented or
# non-Latin characters can exceed it well before 72 characters.
BCRYPT_MAX_PASSWORD_BYTES = 72


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=BCRYPT_MAX_PASSWORD_BYTES)
    phone: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_within_bcrypt_limit(cls, v: str) -> str:
        """
        Reject passwords longer than bcrypt can hash.

        `max_length` above counts characters; this counts bytes, which is
        what bcrypt actually limits. Previously the schema allowed 100
        characters while bcrypt rejected anything over 72 bytes, so a
        long passphrase produced an unhandled 500 on registration rather
        than a validation error.

        Truncating instead of rejecting would be worse: two distinct
        passwords sharing a 72-byte prefix would become the same hash.
        """
        if len(v.encode("utf-8")) > BCRYPT_MAX_PASSWORD_BYTES:
            raise ValueError(
                f"Password must be at most {BCRYPT_MAX_PASSWORD_BYTES} bytes "
                f"when UTF-8 encoded (yours is {len(v.encode('utf-8'))}). "
                f"Note that accented and non-Latin characters use more than "
                f"one byte each."
            )
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    phone: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[dict] = None


class TokenData(BaseModel):
    """Schema for token payload"""
    user_id: Optional[int] = None
    email: Optional[str] = None
