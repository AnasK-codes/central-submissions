import re
from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    """
    Pydantic schema for user registration requests.
    Validates name length, email format, and enforces strong password complexity.
    """
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

    # 🟡 FIX: Enforce password complexity.
    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character.")
        return v


class LoginRequest(BaseModel):
    """
    Pydantic schema for standard email/password login requests.
    """
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    """
    Pydantic schema for Google OAuth login requests.
    Expects the ID token provided by the Google front-end client.
    """
    id_token: str
