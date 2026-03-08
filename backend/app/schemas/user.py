import re
from pydantic import BaseModel, EmailStr, Field, field_validator

# This is for the POST /auth/signup endpoint
class SignupRequest(BaseModel):
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

# This is for the POST /auth/login endpoint 
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# This is the "User" object we return in the data envelope
class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True

class GoogleLoginRequest(BaseModel):
    id_token: str