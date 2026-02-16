"""
Pydantic schemas for user-related request / response models.
"""
import re
from pydantic import BaseModel, field_validator


class UserRegister(BaseModel):
    name: str
    email: str
    password: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name must not be empty")
        return v.strip()

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid email address")
        return v.lower().strip()

    @field_validator("password")
    @classmethod
    def password_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r'[A-Za-z]', v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    name: str
    email: str

    class Config:
        from_attributes = True  # allows .from_orm()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut
