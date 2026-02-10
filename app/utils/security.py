"""Security utilities."""

import hashlib
import secrets
from typing import Optional

try:
    import jwt  # type: ignore
except Exception:
    jwt = None  # type: ignore
from datetime import datetime, timedelta

from app.config import settings


def generate_random_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(length)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    import bcrypt
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    import bcrypt
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def create_jwt_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    
    if jwt is None:
        raise RuntimeError("pyjwt is not installed; cannot create JWT token")
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm="HS256"
    )
    
    return encoded_jwt


def decode_jwt_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token."""
    if jwt is None:
        return None
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"]
        )
        return payload
    except Exception:
        return None


def generate_callback_data(prefix: str, *args) -> str:
    """Generate callback data string for Telegram."""
    parts = [prefix] + [str(arg) for arg in args]
    return ":".join(parts)


def parse_callback_data(data: str) -> list:
    """Parse callback data string."""
    return data.split(":")
