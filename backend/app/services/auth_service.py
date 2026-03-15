"""
auth_service.py

Business logic for authentication workflows.
Calls user_repository for DB operations and core/security for crypto ops.
"""
import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.google_auth import verify_google_token
from app.core.security import create_access_token, hash_password, verify_password
from database.repositories.user_repository import user_repository
from app.schemas.auth_schema import GoogleLoginRequest, LoginRequest, SignupRequest

logger = logging.getLogger(__name__)


def signup(db: Session, payload: SignupRequest) -> dict:
    """
    Registers a new user, hashes their password, and issues an access token.

    Args:
        db (Session): database session
        payload (SignupRequest): user signup credentials (name, email, password)

    Returns:
        dict: a dictionary containing the access "token" and "user" profile data

    Raises:
        HTTPException: if the email is already registered
    """
    existing_user = user_repository.get_user_by_email(db, payload.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": "Email already registered",
                "code": "ERR_VALIDATION",
            },
        )

    # hash password for secure storage
    hashed_pwd = hash_password(payload.password)
    
    # store new user in database
    new_user = user_repository.create_user(db, payload, hashed_pwd)
    
    # generate JWT for authenticated session
    token = create_access_token(new_user.id)

    return {
        "token": token,
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
        },
    }


def login(db: Session, payload: LoginRequest) -> dict:
    """
    Verifies user credentials and issues a JWT access token upon success.

    Args:
        db (Session): database session
        payload (LoginRequest): user login credentials (email, password)

    Returns:
        dict: a dictionary containing the access "token" and "user" profile data

    Raises:
        HTTPException: if the user is not found or password does not match
    """
    user = user_repository.get_user_by_email(db, payload.email)
    
    # perform constant-time password verification to prevent timing attacks
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "message": "Invalid email or password",
                "code": "ERR_AUTH",
            },
        )

    # generate JWT for authenticated session
    token = create_access_token(user.id)
    return {
        "token": token,
        "user": {"id": user.id, "name": user.name, "email": user.email},
    }


def google_login(db: Session, payload: GoogleLoginRequest) -> dict:
    """
    Verifies a Google OAuth token and logs in (or registers) the corresponding local user.

    Args:
        db (Session): database session
        payload (GoogleLoginRequest): Google ID token

    Returns:
        dict: a dictionary containing the access "token" and "user" profile data
    """
    # decode the google token via google auth libraries to get user info
    google_data = verify_google_token(payload.id_token)

    # either lookup existing linked user, or create a brand new account record
    user = user_repository.get_or_create_google_user(
        db,
        email=google_data["email"],
        name=google_data["name"],
        google_id=google_data["google_id"],
        picture=google_data.get("picture"),
    )

    # generate internal JWT for authenticated session
    token = create_access_token(user.id)
    return {
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "profile_picture": user.profile_picture,
        },
    }

