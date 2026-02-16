"""
JWT token creation and verification.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from config import settings

try:
    from jose import JWTError, jwt
except ImportError:
    from jwt import PyJWTError as JWTError  # type: ignore
    import jwt as _jwt  # type: ignore

    class jwt:  # type: ignore
        @staticmethod
        def encode(claims, key, algorithm):
            return _jwt.encode(claims, key, algorithm=algorithm)

        @staticmethod
        def decode(token, key, algorithms):
            return _jwt.decode(token, key, algorithms=algorithms)


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Create a signed JWT with the given payload."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT.
    Raises JWTError on invalid / expired tokens.
    """
    return jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )


# Re-export so callers can catch the right exception.
__all__ = ["create_access_token", "decode_access_token", "JWTError"]
