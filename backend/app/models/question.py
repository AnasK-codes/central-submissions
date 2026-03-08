from sqlalchemy import (
    Column, Integer, String, Boolean, Text, 
    DateTime, ForeignKey, BigInteger, Float, Table
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

# --- MANY-TO-MANY JUNCTION ---
question_subjects = Table(
    "question_subjects",
    Base.metadata,
    Column("question_id", BigInteger, ForeignKey("questions.id"), primary_key=True),
    Column("subject_id", BigInteger, ForeignKey("subjects.id"), primary_key=True),
)

# --- SUBJECTS ---
class Subject(Base):
    __tablename__ = "subjects"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- QUESTION BANK ---
class Question(Base):
    __tablename__ = "questions"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    question_text = Column(Text, nullable=False)
    sample_answer = Column(Text, nullable=True)
    bloom_level = Column(String(5), nullable=False)
    difficulty = Column(String(10), nullable=False)
    source_type = Column(String(20), nullable=False)
    topic_tags = Column(JSONB, nullable=True)
    estimated_answer_time_sec = Column(Integer, nullable=True)
    is_active = Column(Boolean, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    subjects = relationship("Subject", secondary=question_subjects, backref="questions")



