"""
app/schemas/user.py — backward-compatibility shim.

Auth-related schemas moved to auth_schema.py.
User response schema moved to user_schema.py.
"""
from app.schemas.auth_schema import SignupRequest, LoginRequest, GoogleLoginRequest  # noqa: F401
from app.schemas.user_schema import UserOut  # noqa: F401