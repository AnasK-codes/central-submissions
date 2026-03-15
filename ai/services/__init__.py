"""
ai/services/__init__.py

Public API for the AI module. Backend code should import from here:

    from ai.services import generate_questions, evaluate_answers
"""
from ai.services.question_generator import generate_questions
from ai.services.check_answers import check_answer_correctness as evaluate_answers

__all__ = ["generate_questions", "evaluate_answers"]
