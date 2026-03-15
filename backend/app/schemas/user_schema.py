from typing import Optional
from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    """
    Pydantic schema for serializing user profile data in API responses.
    Excludes sensitive information like password hashes.
    """
    id: int
    name: str
    email: EmailStr
    profile_picture: Optional[str] = None

    class Config:
        from_attributes = True
