"""
user_service.py

Business logic for user profile operations.
"""
import logging

from sqlalchemy.orm import Session

from database.repositories.user_repository import user_repository

logger = logging.getLogger(__name__)


def get_user_by_id(db: Session, user_id: int):
    """
    Fetches a user completely by their unique ID from the database.

    Args:
        db (Session): database session
        user_id (int): primary key ID of the user

    Returns:
        User: user database ORM model, or None if not found
    """
    return user_repository.get_user_by_id(db, user_id)
