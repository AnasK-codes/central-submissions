"""
user_routes.py

Placeholder routes for user profile endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers import user_controller
from app.core.dependencies import get_current_user
from database.session import get_db
from app.utils.response import StandardResponse, success_response

router = APIRouter()


@router.get("/me", response_model=StandardResponse)
def get_me(
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves the profile information of the currently authenticated user.

    Args:
        current_user_id (int): id of the currently authenticated user
        db (Session): database session

    Returns:
        StandardResponse: standardized response containing user profile data
    """
    data = user_controller.handle_get_me(db, current_user_id)
    return success_response(data)
