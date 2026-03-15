from typing import List
from pydantic import BaseModel, Field


class GeneratedQuestionConfig(BaseModel):
    """Schema for a single AI-generated interview question."""
    id: int
    question_text: str = Field(..., min_length=5)
    bloom_level: str
    difficulty: str
    topic_tags: List[str] = Field(default_factory=list)
    estimated_answer_time_sec: int = Field(default=60)


class QuestionGenerationResponse(BaseModel):
    """Schema for the full JSON response from the question generation model."""
    questions: List[GeneratedQuestionConfig]


class AnswerEvaluationResponse(BaseModel):
    """Schema for the full JSON response from the answer evaluation model."""
    score: float = Field(..., ge=0, le=100)
    explanation: str = Field(..., min_length=1)
    feedback: str = Field(default="")
