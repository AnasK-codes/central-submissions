"""
interview_service.py

Business logic for interview session workflows.
Orchestrates AI question generation, answer evaluation, and session lifecycle.
Delegates all DB queries to interview_repository.
"""
import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from database.repositories.interview_repository import interview_repository
from database.repositories.user_repository import user_repository
from ai.services.question_generator import generate_questions
from ai.services.check_answers import check_answer_correctness
from app.schemas.interview_schema import InterviewStartRequest, SubmitAnswerRequest

logger = logging.getLogger(__name__)


async def start_interview(db: Session, payload: InterviewStartRequest, user_id: int) -> dict:
    """
    Creates a new interview session, triggers AI question generation,
    persists the questions, and returns the session details with the question list.

    Args:
        db (Session): database session
        payload (InterviewStartRequest): interview configuration payload
        user_id (int): id of the currently authenticated user

    Returns:
        dict: a dictionary containing the new 'session_id' and 'questions' list

    Raises:
        HTTPException: if user is not found or AI generation fails
    """
    from fastapi.concurrency import run_in_threadpool

    # Verify user exists before starting an interview
    student = user_repository.get_user_by_id(db, user_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please register first.",
        )

    student_id = str(student.id)

    # 2. Create the persistent session record
    new_session = interview_repository.create_session(
        db=db,
        user_id=student.id,
        mode=payload.mode,
        bloom_strategy=payload.bloom_strategy,
        selected_bloom_level=payload.bloom_level,
        difficulty=payload.difficulty,
        language=payload.language,
        num_questions_requested=payload.num_questions,
        started_at=datetime.now(timezone.utc),
    )

    # 3. Trigger AI Generation in a threadpool to avoid blocking the event loop
    try:
        ai_response = await run_in_threadpool(generate_questions, payload, student_id=student_id)

        generated_questions = ai_response.get("questions", [])
        questions_to_return = []

        # 4. Persist questions and session links
        for i, q_data in enumerate(generated_questions):
            question = interview_repository.create_question(db, q_data)
            link = interview_repository.create_session_question_link(
                db=db,
                session_id=new_session.id,
                question_id=question.id,
                sequence_number=i + 1,
                bloom_level_at_time=q_data.get("bloom_level"),
                estimated_answer_time_sec=q_data.get("estimated_answer_time_sec", 60),
            )
            questions_to_return.append(
                {
                    "interview_question_id": link.id,
                    "text": question.question_text,
                    "bloom": link.bloom_level_at_time,
                    "sequence": link.sequence_number,
                    "time_limit": link.estimated_answer_time_sec,
                }
            )

        interview_repository.update_session_status(
            db, new_session, "active", num_questions_generated=len(generated_questions)
        )
        db.commit()

        return {"session_id": new_session.id, "questions": questions_to_return}

    except Exception:
        logger.exception("AI generation failed for session %s", new_session.id)
        interview_repository.update_session_status(db, new_session, "failed")
        raise HTTPException(
            status_code=500,
            detail="Question generation failed. Please try again.",
        )


def get_next_question(db: Session, session_id: int, user_id: int) -> dict:
    """
    Retrieves the next unanswered question for a given interview session.

    Args:
        db (Session): database session
        session_id (int): the ID of the interview session
        user_id (int): id of the currently authenticated user

    Returns:
        dict: the next question payload, or a status indicating the session is complete

    Raises:
        HTTPException: if session is not found or access is forbidden
    """
    session = interview_repository.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    # enforce session ownership
    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access forbidden.")

    # Reject requests on non-active sessions
    if session.status not in ("active", "initializing"):
        return {"status": "completed", "message": "This interview session has already ended."}

    # Query database for the next unanswered question
    next_unanswered_question = interview_repository.get_next_unanswered_question(db, session_id)

    if not next_unanswered_question:
        return {"status": "completed", "message": "All questions have been answered."}

    return {
        "status": "in_progress",
        "interview_question_id": next_unanswered_question.InterviewQuestion.id,
        "question_text": next_unanswered_question.Question.question_text,
        "bloom_level": next_unanswered_question.InterviewQuestion.bloom_level_at_time,
        "sequence": next_unanswered_question.InterviewQuestion.sequence_number,
        "time_limit": next_unanswered_question.InterviewQuestion.estimated_answer_time_sec,
    }


async def submit_answer(
    db: Session, session_id: int, body: SubmitAnswerRequest, user_id: int
) -> dict:
    """
    Validates ownership, persists the user's answer, and auto-completes the session if it's the final question.
    Note: AI evaluation of the answer happens asynchronously later (during summary generation).

    Args:
        db (Session): database session
        session_id (int): the ID of the interview session
        body (SubmitAnswerRequest): the answer submission payload containing the user's text
        user_id (int): id of the currently authenticated user

    Returns:
        dict: a dictionary indicating the answer was received and whether the session is complete

    Raises:
        HTTPException: if session/question is invalid, access is forbidden, or duplicate answer
    """
    from fastapi.concurrency import run_in_threadpool

    session = interview_repository.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    # enforce session ownership
    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access forbidden.")
        
    if session.status == "completed":
        raise HTTPException(status_code=400, detail="This interview session has already ended.")

    # Fetch the link connecting the question ID to the interview session
    question_link = interview_repository.get_question_link(
        db, body.interview_question_id, session_id
    )
    if not question_link:
        raise HTTPException(
            status_code=404, detail="Question link not found for this session."
        )

    # Guard against duplicate answer submissions
    existing_answer = interview_repository.get_answer_for_question(
        db, body.interview_question_id
    )
    if existing_answer:
        raise HTTPException(
            status_code=400, detail="This question has already been answered."
        )

    student_id = str(user_id)

    # Save User Answer instantly (delay AI evaluation until summary to improve UX/speed)
    new_answer = interview_repository.save_answer(
        db=db,
        interview_question_id=body.interview_question_id,
        answer_text=body.user_answer,
        evaluation_score=None,
        feedback=None,
        ai_evaluation_metadata=None,
    )

    # Check if all questions are now answered → auto-complete the session
    remaining = interview_repository.get_next_unanswered_question(db, session_id)
    is_complete = remaining is None

    if is_complete:
        interview_repository.update_session_status(
            db, session, "completed", ended_at=datetime.now(timezone.utc)
        )
        logger.info("Session %s auto-completed after last answer.", session_id)

    return {
        "score": None,
        "feedback": None,
        "insights": None,
        "is_complete": is_complete,
    }


async def get_summary(db: Session, session_id: int, user_id: int) -> dict:
    """
    Evaluates pending answers asynchronously, finalizes the session, and returns an aggregate score breakdown.

    Args:
        db (Session): database session
        session_id (int): the ID of the interview session
        user_id (int): id of the currently authenticated user

    Returns:
        dict: a summary object containing average score, performance level, and individual answer feedback

    Raises:
        HTTPException: if session is not found, access forbidden, or no answers exist
    """
    from fastapi.concurrency import run_in_threadpool
    session = interview_repository.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    # enforce session ownership
    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access forbidden.")

    session_answers = interview_repository.get_answers_for_session(db, session_id)
    if not session_answers:
        raise HTTPException(status_code=404, detail="No answers found for this session.")

    student_id = str(user_id)
    # 1. Evaluate any answers that haven't been scored yet
    for answer_record in session_answers:
        if answer_record.evaluation_score is None:
            # We need the question text to provide context to the AI evaluator
            question_link = interview_repository.get_question_link(db, answer_record.interview_question_id, session_id)
            if not question_link:
                continue

            # pass question and answer to AI module asynchronously
            evaluation = await run_in_threadpool(
                check_answer_correctness,
                question=question_link.Question.question_text,
                answer=answer_record.answer_text,
                student_id=student_id,
            )
            
            # Update the DB record directly with AI feedback
            answer_record.evaluation_score = float(evaluation.get("score", 0))
            answer_record.feedback = evaluation.get("feedback", "")
            answer_record.ai_evaluation_metadata = {
                "level": evaluation.get("level"),
                "explanation": evaluation.get("explanation"),
            }
    
    # commit all new AI-generated scores to database payload
    db.commit()

    # 2. Calculate average score across all questions
    avg_score = sum(answer_record.evaluation_score or 0 for answer_record in session_answers) / len(session_answers)

    # 3. Determine performance level tier based on average score
    if avg_score >= 90:
        final_level = "Excellent"
    elif avg_score >= 70:
        final_level = "Strong"
    elif avg_score >= 40:
        final_level = "Average"
    else:
        final_level = "Weak"

    # Only finalize session if not already completed (idempotent operation)
    if session.status != "completed":
        interview_repository.update_session_status(
            db, session, "completed", ended_at=datetime.now(timezone.utc)
        )

    return {
        "average_score": round(avg_score, 2),
        "performance_level": final_level,
        "total_answered": len(session_answers),
        "breakdown": [
            {
                "question_id": answer_record.interview_question_id,
                "score": answer_record.evaluation_score,
                "feedback": answer_record.feedback,
            }
            for answer_record in session_answers
        ],
    }


def get_result(db: Session, session_id: int, user_id: int) -> dict:
    """
    Returns a simplified fast result containing just the aggregated score and percentage.

    Args:
        db (Session): database session
        session_id (int): the ID of the interview session
        user_id (int): id of the currently authenticated user

    Returns:
        dict: a minimal result dict showing number of correct answers and total percentage

    Raises:
        HTTPException: if session is not found or access forbidden
    """
    session = interview_repository.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    # enforce session ownership
    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access forbidden.")

    answers = interview_repository.get_answers_for_session(db, session_id)
    total = session.num_questions_generated or session.num_questions_requested

    if not answers:
        return {"score": 0, "total": total, "percentage": 0}

    # Count answers scoring >= 50 as "correct" against total requested/generated questions
    passing = sum(1 for ans in answers if (ans.evaluation_score or 0) >= 50)
    percentage = round((passing / total) * 100) if total > 0 else 0

    return {
        "score": passing,
        "total": total,
        "percentage": percentage,
    }
