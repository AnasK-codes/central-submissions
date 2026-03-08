from pydantic import BaseModel, Field
from typing import Optional


class Constraints(BaseModel):
    max_words_per_question: int = 50
    include_real_world_examples: bool = True


class InterviewStartRequest(BaseModel):
    """Request body for starting a new interview session.
    student_id is derived server-side from the JWT token — not client-supplied.
    """
    subject: str
    mode: str = Field(..., description="single_bloom or mixed_bloom")
    bloom_level: Optional[str] = "L1"
    difficulty: str = Field(..., pattern="^(easy|medium|hard)$")
    num_questions: int = Field(..., ge=1, le=20)
    language: str = "en"
    bloom_strategy: str = "fixed"  # "increasing" or "random"
    constraints: Optional[Constraints] = None


class SubmitAnswerRequest(BaseModel):
    """Request body for submitting an answer to an interview question."""
    interview_question_id: int
    user_answer: str