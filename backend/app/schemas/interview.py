"""
app/schemas/interview.py — backward-compatibility shim.

Schemas moved to interview_schema.py.
"""
from app.schemas.interview_schema import (  # noqa: F401
    Constraints,
    InterviewStartRequest,
    SubmitAnswerRequest,
)