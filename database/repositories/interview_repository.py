"""
interview_repository.py

Sole owner of all SQLAlchemy queries related to interview sessions,
questions, and answers. No business logic lives here.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from database.models.interview_model import Answer, InterviewQuestion, InterviewSession
from database.models.question_model import Question


class InterviewRepository:
    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------
    def get_session_by_id(self, db: Session, session_id: int) -> Optional[InterviewSession]:
        return (
            db.query(InterviewSession)
            .filter(InterviewSession.id == session_id)
            .first()
        )

    def create_session(
        self,
        db: Session,
        user_id: int,
        mode: str,
        bloom_strategy: str,
        selected_bloom_level: Optional[str],
        difficulty: str,
        language: str,
        num_questions_requested: int,
        started_at: datetime,
    ) -> InterviewSession:
        session = InterviewSession(
            user_id=user_id,
            mode=mode,
            bloom_strategy=bloom_strategy,
            selected_bloom_level=selected_bloom_level,
            difficulty=difficulty,
            language=language,
            num_questions_requested=num_questions_requested,
            num_questions_generated=0,
            status="initializing",
            started_at=started_at,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def update_session_status(
        self,
        db: Session,
        session: InterviewSession,
        status: str,
        num_questions_generated: Optional[int] = None,
        ended_at: Optional[datetime] = None,
    ) -> None:
        session.status = status
        if num_questions_generated is not None:
            session.num_questions_generated = num_questions_generated
        if ended_at is not None:
            session.ended_at = ended_at
        db.commit()

    # ------------------------------------------------------------------
    # Questions
    # ------------------------------------------------------------------
    def create_question(self, db: Session, q_data: dict) -> Question:
        question = Question(
            question_text=q_data["question_text"],
            bloom_level=q_data["bloom_level"],
            difficulty=q_data["difficulty"],
            topic_tags=q_data.get("topic_tags", []),
            estimated_answer_time_sec=q_data.get("estimated_answer_time_sec"),
            source_type="AI_GENERATED",
        )
        db.add(question)
        db.flush()
        return question

    def create_session_question_link(
        self,
        db: Session,
        session_id: int,
        question_id: int,
        sequence_number: int,
        bloom_level_at_time: Optional[str],
        estimated_answer_time_sec: int,
    ) -> InterviewQuestion:
        link = InterviewQuestion(
            interview_session_id=session_id,
            question_id=question_id,
            sequence_number=sequence_number,
            bloom_level_at_time=bloom_level_at_time,
            estimated_answer_time_sec=estimated_answer_time_sec,
        )
        db.add(link)
        db.flush()
        return link

    def get_next_unanswered_question(
        self, db: Session, session_id: int
    ) -> Optional[tuple]:
        """Returns (Question, InterviewQuestion) or None if all answered."""
        return (
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

    def get_question_link(
        self, db: Session, interview_question_id: int, session_id: int
    ) -> Optional[tuple]:
        """Returns (Question, InterviewQuestion) for the given link ID."""
        return (
            db.query(Question, InterviewQuestion)
            .join(InterviewQuestion, Question.id == InterviewQuestion.question_id)
            .filter(
                InterviewQuestion.id == interview_question_id,
                InterviewQuestion.interview_session_id == session_id,
            )
            .first()
        )

    # ------------------------------------------------------------------
    # Answers
    # ------------------------------------------------------------------
    def save_answer(
        self,
        db: Session,
        interview_question_id: int,
        answer_text: str,
        evaluation_score: float,
        feedback: str,
        ai_evaluation_metadata: dict,
    ) -> Answer:
        answer = Answer(
            interview_question_id=interview_question_id,
            answer_text=answer_text,
            evaluation_score=evaluation_score,
            feedback=feedback,
            ai_evaluation_metadata=ai_evaluation_metadata,
        )
        db.add(answer)
        db.commit()
        db.refresh(answer)
        return answer

    def get_answers_for_session(self, db: Session, session_id: int):
        return (
            db.query(Answer)
            .join(InterviewQuestion)
            .filter(InterviewQuestion.interview_session_id == session_id)
            .all()
        )

    def get_answer_for_question(
        self, db: Session, interview_question_id: int
    ) -> Optional[Answer]:
        """Check if an answer already exists for a given interview question."""
        return (
            db.query(Answer)
            .filter(Answer.interview_question_id == interview_question_id)
            .first()
        )


interview_repository = InterviewRepository()
