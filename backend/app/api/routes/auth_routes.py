"""
auth_routes.py

Thin HTTP layer for authentication endpoints.
Only concerns: declare routes, rate limiting, dependency injection.
All logic lives in auth_controller → auth_service.
"""
import logging

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.controllers import auth_controller
from app.core.dependencies import get_current_user
from database.session import get_db
from app.schemas.auth_schema import GoogleLoginRequest, LoginRequest, SignupRequest
from app.utils.response import StandardResponse

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


@router.post("/signup", status_code=201, response_model=StandardResponse)
@limiter.limit("5/minute")
def signup(request: Request, payload: SignupRequest, db: Session = Depends(get_db)):
    """
    Registers a new user in the system.

    Args:
        request (Request): the incoming HTTP request (used for rate limiting)
        payload (SignupRequest): user signup credentials
        db (Session): database session

    Returns:
        dict: authentication token and user data
    """
    return auth_controller.handle_signup(db, payload)


@router.post("/login", response_model=StandardResponse)
@limiter.limit("5/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates a user and returns a token.

    Args:
        request (Request): the incoming HTTP request (used for rate limiting)
        payload (LoginRequest): user login credentials
        db (Session): database session

    Returns:
        dict: authentication token and user data
    """
    return auth_controller.handle_login(db, payload)


@router.post("/google", response_model=StandardResponse)
def google_auth(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates a user via a Google OAuth token.

    Args:
        payload (GoogleLoginRequest): Google ID token
        db (Session): database session

    Returns:
        dict: authentication token and user profile data
    """
    return auth_controller.handle_google_login(db, payload)
