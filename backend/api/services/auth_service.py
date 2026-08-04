"""
auth_service.py — Production Authentication & JWT Service for FastAPI Backend
Handles token verification, JWT issuance, and authentication security.
"""
from __future__ import annotations

import os
import time
import jwt
from typing import Optional
from fastapi import Header, HTTPException, Depends, status
from pydantic import BaseModel

# ── JWT Configuration ─────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "sfa_production_jwt_secret_key_change_in_env_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 86400 * 30  # 30 days


class UserProfile(BaseModel):
    uid: str
    email: Optional[str] = None
    name: Optional[str] = None
    photoURL: Optional[str] = None
    provider: str = "email"


def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """Create a signed JWT access token for user sessions."""
    to_encode = data.copy()
    now = int(time.time())
    expire = now + (expires_delta if expires_delta else ACCESS_TOKEN_EXPIRE_SECONDS)
    to_encode.update({"iat": now, "exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token has expired. Please sign in again.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """FastAPI Dependency: Extracts and verifies user token from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing.",
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'.",
        )
    
    token = parts[1]
    return decode_access_token(token)
