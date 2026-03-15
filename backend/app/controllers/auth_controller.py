"""
auth_controller.py

Request/response orchestration for authentication endpoints.
Calls auth_service and formats responses using the standard envelope.
"""
import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas.auth_schema import GoogleLoginRequest, LoginRequest, SignupRequest
from app.services import auth_service
from app.utils.response import success_response

logger = logging.getLogger(__name__)


def handle_signup(db: Session, payload: SignupRequest) -> dict:
    """
    Handles user registration by delegating to the auth service and formatting the response.

    Args:
        db (Session): database session
        payload (SignupRequest): user signup credentials

    Returns:
        dict: standardized success response containing auth token and user data
    
    Raises:
        HTTPException: if signup fails due to duplicate email or unexpected errors
    """
    try:
        data = auth_service.signup(db, payload)
        return success_response(data)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error during signup")
        raise HTTPException(status_code=500, detail="Internal Server Error")


def handle_login(db: Session, payload: LoginRequest) -> dict:
    """
    Handles user authentication by calling the auth service and returning a formatted token.

    Args:
        db (Session): database session
        payload (LoginRequest): user login credentials

    Returns:
        dict: standardized success response containing auth token and user data
    """
    data = auth_service.login(db, payload)
    return success_response(data)


def handle_google_login(db: Session, payload: GoogleLoginRequest) -> dict:
    """
    Handles Google OAuth login by translating the Google ID token into a local session.

    Args:
        db (Session): database session
        payload (GoogleLoginRequest): Google ID token

    Returns:
        dict: standardized success response containing local auth token and profile data
    """
    data = auth_service.google_login(db, payload)
    return success_response(data)
