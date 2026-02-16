"""
Shared FastAPI dependencies.
"""
from fastapi import Depends, HTTPException

from core.security import oauth2_scheme
from core.jwt_handler import decode_access_token, JWTError
from db.session import SessionLocal


def get_db():
    """Yield a SQLAlchemy session, closing it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Decode JWT and return user info.  Used as a dependency for protected endpoints."""
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        name: str = payload.get("name", "")
        user_id: int = payload.get("user_id")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"email": email, "name": name, "user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
