from sqlalchemy import (
    Column, Integer, String, Boolean, Text, 
    DateTime, ForeignKey, BigInteger, Float, Table
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


# --- INTERVIEW SESSIONS ---
class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    subject_id = Column(BigInteger, ForeignKey("subjects.id"))
    mode = Column(String(20), nullable=False)
    bloom_strategy = Column(String(20), server_default="fixed")
    selected_bloom_level = Column(String(5), nullable=True)
    difficulty = Column(String(10), nullable=False)
    language = Column(String(10), server_default="en")
    num_questions_requested = Column(Integer, nullable=False)
    num_questions_generated = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)
    llm_metadata = Column(JSONB, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

# --- INTERVIEW QUESTIONS (Session Content) ---
class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    interview_session_id = Column(BigInteger, ForeignKey("interview_sessions.id"))
    question_id = Column(BigInteger, ForeignKey("questions.id"))
    sequence_number = Column(Integer, nullable=False)
    bloom_level_at_time = Column(String(5), nullable=True)
    estimated_answer_time_sec = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

# --- ANSWERS ---
class Answer(Base):
    __tablename__ = "answers"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    interview_question_id = Column(BigInteger, ForeignKey("interview_questions.id"))
    answer_text = Column(Text, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    evaluation_score = Column(Float, nullable=True) # Maps to double_precision
    feedback = Column(Text, nullable=True)
    ai_evaluation_metadata = Column(JSONB, nullable=True)