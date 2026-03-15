"""
interview_controller.py

Request/response orchestration for interview endpoints.
Calls interview_service and passes results directly to the route layer.
"""
import logging

from sqlalchemy.orm import Session

from app.schemas.interview_schema import InterviewStartRequest, SubmitAnswerRequest
from app.services import interview_service

logger = logging.getLogger(__name__)


async def handle_start_interview(
    db: Session, payload: InterviewStartRequest, user_id: int
) -> dict:
    """
    Handles the initialization of an interview session by calling the interview service.

    Args:
        db (Session): database session
        payload (InterviewStartRequest): interview configuration payload
        user_id (int): id of the currently authenticated user

    Returns:
        dict: the newly created session id and initial questions
    """
    return await interview_service.start_interview(db, payload, user_id)


def handle_get_next_question(db: Session, session_id: int, user_id: int) -> dict:
    """
    Handles fetching the next unanswered question for a specific interview session.

    Args:
        db (Session): database session
        session_id (int): the ID of the interview session
        user_id (int): id of the currently authenticated user

    Returns:
        dict: details of the next question or completion status
    """
    return interview_service.get_next_question(db, session_id, user_id)


async def handle_submit_answer(
    db: Session, session_id: int, body: SubmitAnswerRequest, user_id: int
) -> dict:
    """
    Handles the submission of an answer for an interview question.

    Args:
        db (Session): database session
        session_id (int): the ID of the interview session
        body (SubmitAnswerRequest): the answer submission payload
        user_id (int): id of the currently authenticated user

    Returns:
        dict: evaluation results for the submitted answer
    """
    return await interview_service.submit_answer(db, session_id, body, user_id)


async def handle_get_summary(db: Session, session_id: int, user_id: int) -> dict:
    """
    Handles the retrieval of the comprehensive summary for an interview session.

    Args:
        db (Session): database session
        session_id (int): the ID of the interview session
        user_id (int): id of the currently authenticated user

    Returns:
        dict: aggregated score, performance level, and question breakdown
    """
    return await interview_service.get_summary(db, session_id, user_id)


def handle_get_result(db: Session, session_id: int, user_id: int) -> dict:
    """
    Handles the retrieval of the final result for an interview session.

    Args:
        db (Session): database session
        session_id (int): the ID of the interview session
        user_id (int): id of the currently authenticated user

    Returns:
        dict: simplified result object containing final score
    """
    return interview_service.get_result(db, session_id, user_id)
