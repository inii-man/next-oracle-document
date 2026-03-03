"""
JWT Bearer token authentication dependency.
Set REQUIRE_AUTH=False in .env to disable for local testing.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

load_dotenv()

SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-2026")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)
REQUIRE_AUTH: bool = os.getenv("REQUIRE_AUTH", "false").lower() == "true"

security = HTTPBearer(auto_error=False)


class TokenData(BaseModel):
    sub: str
    exp: Optional[datetime] = None


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT token."""
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[str]:
    """
    Decode and validate Bearer token.
    Returns the subject (username/id) or None if auth is disabled.
    Raises 401 if auth is enabled and token is missing/invalid.
    """
    if not REQUIRE_AUTH:
        return "anonymous"  # auth disabled for local dev/testing

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        subject: str = payload.get("sub", "")
        if not subject:
            raise JWTError("Empty subject")
        return subject
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
