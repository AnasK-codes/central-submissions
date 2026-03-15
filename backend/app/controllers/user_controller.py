"""
user_controller.py

Placeholder controller for user profile endpoints.
Extend this as user management features are added.
"""
import logging

from sqlalchemy.orm import Session

from app.services import user_service

logger = logging.getLogger(__name__)


def handle_get_me(db: Session, user_id: int) -> dict:
    """
    Handles fetching profile information for the currently authenticated user.

    Args:
        db (Session): database session
        user_id (int): id of the user whose profile is being requested

    Returns:
        dict: the serialized user profile data
        
    Raises:
        HTTPException: if the user does not exist in the database
    """
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found.")
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "auth_provider": user.auth_provider,
    }
