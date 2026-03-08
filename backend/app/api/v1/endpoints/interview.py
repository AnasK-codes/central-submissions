import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.interview import Answer, InterviewQuestion, InterviewSession
from app.models.question import Question
from app.models.user import User
from app.schemas.interview import InterviewStartRequest, SubmitAnswerRequest

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# POST /start — Create a new interview session and generate questions
# ---------------------------------------------------------------------------
@router.post("/start", status_code=status.HTTP_201_CREATED)
async def start_interview(
    payload: InterviewStartRequest,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify the authenticated user exists in the DB
    student = db.query(User).filter(User.id == current_user_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please register first.",
        )

    student_id = str(student.id)

    # 1. Create the persistent session record with correct column names
    new_session = InterviewSession(
        user_id=student.id,
        mode=payload.mode,
        bloom_strategy=payload.bloom_strategy,
        selected_bloom_level=payload.bloom_level,
        difficulty=payload.difficulty,
        language=payload.language,
        num_questions_requested=payload.num_questions,
        num_questions_generated=0,
        status="initializing",
        started_at=datetime.now(timezone.utc),
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # 2. Trigger AI Generation
    try:
        if settings.AI_MOCK_MODE:
            from app.services.mock_ai import generate_questions_mock

            ai_response = generate_questions_mock(payload, student_id=student_id)
        else:
            from app.services.question_generator import generate_questions

            ai_response = generate_questions(payload, student_id=student_id)

        questions_to_return = []

        # 3. PERSISTENCE: Save questions and links
        generated_questions = ai_response.get("questions", [])
        for i, q_data in enumerate(generated_questions):
            new_question = Question(
                question_text=q_data["question_text"],
                bloom_level=q_data["bloom_level"],
                difficulty=q_data["difficulty"],
                topic_tags=q_data.get("topic_tags", []),
                estimated_answer_time_sec=q_data.get("estimated_answer_time_sec"),
                source_type="AI_GENERATED",
            )
            db.add(new_question)
            db.flush()

            session_link = InterviewQuestion(
                interview_session_id=new_session.id,
                question_id=new_question.id,
                sequence_number=i + 1,
                bloom_level_at_time=q_data.get("bloom_level"),
                estimated_answer_time_sec=q_data.get("estimated_answer_time_sec", 60),
            )
            db.add(session_link)
            db.flush()

            questions_to_return.append(
                {
                    "interview_question_id": session_link.id,
                    "text": new_question.question_text,
                    "bloom": session_link.bloom_level_at_time,
                    "sequence": session_link.sequence_number,
                    "time_limit": session_link.estimated_answer_time_sec,
                }
            )

        new_session.num_questions_generated = len(generated_questions)
        new_session.status = "active"
        db.commit()

        return {"session_id": new_session.id, "questions": questions_to_return}

    except Exception:
        # 🟡 FIX: Log the real error internally; return a generic message to the client
        # to avoid leaking internal architecture details (DB URLs, API keys, etc.)
        logger.exception("AI generation failed for session %s", new_session.id)
        new_session.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=500, detail="Question generation failed. Please try again."
        )


# ---------------------------------------------------------------------------
# GET /{session_id}/next — Get next unanswered question
# ---------------------------------------------------------------------------
@router.get("/{session_id}/next")
async def get_next_question(
    session_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 🔴 FIX: IDOR — verify this session belongs to the authenticated user
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access forbidden.")

    next_q = (
        db.query(Question, InterviewQuestion)
        .join(InterviewQuestion, Question.id == InterviewQuestion.question_id)
        .outerjoin(Answer, InterviewQuestion.id == Answer.interview_question_id)
        .filter(
            InterviewQuestion.interview_session_id == session_id,
            Answer.id == None,  # noqa: E711
        )
        .order_by(InterviewQuestion.sequence_number.asc())
        .first()
    )

    if not next_q:
        return {"status": "completed", "message": "All questions have been answered."}

    return {
        "status": "in_progress",
        "interview_question_id": next_q.InterviewQuestion.id,
        "question_text": next_q.Question.question_text,
        "bloom_level": next_q.InterviewQuestion.bloom_level_at_time,
        "sequence": next_q.InterviewQuestion.sequence_number,
        "time_limit": next_q.InterviewQuestion.estimated_answer_time_sec,
    }


# ---------------------------------------------------------------------------
# POST /{session_id}/answer — Submit an answer (request body, not query params)
# ---------------------------------------------------------------------------
@router.post("/{session_id}/answer")
async def submit_answer(
    session_id: int,
    body: SubmitAnswerRequest,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 🔴 FIX: IDOR — verify this session belongs to the authenticated user
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access forbidden.")

    student_id = str(current_user_id)

    result = (
        db.query(Question, InterviewQuestion)
        .join(InterviewQuestion, Question.id == InterviewQuestion.question_id)
        .filter(
            InterviewQuestion.id == body.interview_question_id,
            InterviewQuestion.interview_session_id == session_id,
        )
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=404, detail="Question link not found for this session."
        )

    # AI evaluation (mock or real)
    if settings.AI_MOCK_MODE:
        from app.services.mock_ai import check_answer_correctness_mock

        evaluation = check_answer_correctness_mock(
            question=result.Question.question_text,
            answer=body.user_answer,
            student_id=student_id,
        )
    else:
        from app.services.check_answers import check_answer_correctness

        evaluation = check_answer_correctness(
            question=result.Question.question_text,
            answer=body.user_answer,
            student_id=student_id,
        )

    new_answer = Answer(
        interview_question_id=body.interview_question_id,
        answer_text=body.user_answer,
        evaluation_score=float(evaluation.get("score", 0)),
        feedback=evaluation.get("explanation", ""),
        ai_evaluation_metadata={
            "level": evaluation.get("level"),
            "improvement": evaluation.get("feedback"),
        },
    )

    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)

    return {
        "score": new_answer.evaluation_score,
        "feedback": new_answer.feedback,
        "insights": new_answer.ai_evaluation_metadata,
    }


# ---------------------------------------------------------------------------
# GET /{session_id}/summary — Get session summary
# ---------------------------------------------------------------------------
@router.get("/{session_id}/summary")
async def get_summary(
    session_id: int,
    current_user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 🔴 FIX: IDOR — verify this session belongs to the authenticated user
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access forbidden.")

    results = (
        db.query(Answer)
        .join(InterviewQuestion)
        .filter(InterviewQuestion.interview_session_id == session_id)
        .all()
    )

    if not results:
        raise HTTPException(
            status_code=404, detail="No answers found for this session."
        )

    # Handle None evaluation_score safely
    avg_score = sum(ans.evaluation_score or 0 for ans in results) / len(results)

    if avg_score >= 90:
        final_level = "Excellent"
    elif avg_score >= 70:
        final_level = "Strong"
    elif avg_score >= 40:
        final_level = "Average"
    else:
        final_level = "Weak"

    session = (
        db.query(InterviewSession)
        .filter(InterviewSession.id == session_id)
        .first()
    )
    if session:
        session.status = "completed"
        session.ended_at = datetime.now(timezone.utc)
        db.commit()

    return {
        "average_score": round(avg_score, 2),
        "performance_level": final_level,
        "total_answered": len(results),
        "breakdown": [
            {
                "question_id": ans.interview_question_id,
                "score": ans.evaluation_score,
                "feedback": ans.feedback,
            }
            for ans in results
        ],
    }