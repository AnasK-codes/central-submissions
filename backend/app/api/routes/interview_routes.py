"""
interview_routes.py

Thin HTTP layer for interview session endpoints.
Only concerns: route definitions, dependency injection.
All logic lives in interview_controller → interview_service.
"""
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session

from app.controllers import interview_controller
from app.core.dependencies import get_current_user
from database.session import get_db
from app.schemas.interview_schema import InterviewStartRequest, SubmitAnswerRequest
from app.core.rate_limit import limiter

router = APIRouter()


@router.post("/start", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def start_interview(
    request: Request,
    payload: InterviewStartRequest,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Initializes a new interview session.

    Args:
        request (Request): the incoming HTTP request (used for rate limiting)
        payload (InterviewStartRequest): interview configuration payload
        current_user_id (int): id of the currently authenticated user
        db (Session): database session

    Returns:
        dict: the newly created session id and initial questions
    """
    return await interview_controller.handle_start_interview(db, payload, current_user_id)


@router.get("/{session_id}/next")
async def get_next_question(
    session_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves the next unanswered question for an active interview session.

    Args:
        session_id (int): the ID of the interview session
        current_user_id (int): id of the currently authenticated user
        db (Session): database session

    Returns:
        dict: details of the next question or completion status
    """
    return interview_controller.handle_get_next_question(db, session_id, current_user_id)


@router.post("/{session_id}/answer")
@limiter.limit("20/minute")
async def submit_answer(
    request: Request,
    session_id: int,
    body: SubmitAnswerRequest,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submits an answer for an interview question.

    Args:
        request (Request): the incoming HTTP request (used for rate limiting)
        session_id (int): the ID of the interview session
        body (SubmitAnswerRequest): the answer submission payload
        current_user_id (int): id of the currently authenticated user
        db (Session): database session

    Returns:
        dict: evaluation results for the submitted answer
    """
    return await interview_controller.handle_submit_answer(db, session_id, body, current_user_id)


@router.get("/{session_id}/summary")
async def get_summary(
    session_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Gets the comprehensive summary and AI breakdown of a completed interview session.

    Args:
        session_id (int): the ID of the interview session
        current_user_id (int): id of the currently authenticated user
        db (Session): database session

    Returns:
        dict: aggregated score, performance level, and question breakdown
    """
    return await interview_controller.handle_get_summary(db, session_id, current_user_id)


@router.get("/{session_id}/result")
async def get_result(
    session_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves the simple final result string/score for an interview.

    Args:
        session_id (int): the ID of the interview session
        current_user_id (int): id of the currently authenticated user
        db (Session): database session

    Returns:
        dict: simplified result object containing final score
    """
    return interview_controller.handle_get_result(db, session_id, current_user_id)
