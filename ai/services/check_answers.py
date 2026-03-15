import json
import re

from ai.services.llm_service import generate_response
from ai.services.pinecone_service import query_embeddings, upsert_embeddings


def check_answer_correctness(question: str, answer: str, student_id: str):
    ltm = query_embeddings(question, student_id=student_id)

    prompt = f"""Question: {question}
Student's Answer: {answer}

Evaluate the correctness of the student's answer.

Return ONLY valid JSON:
{{
  "score": 85,
  "explanation": "Short explanation",
  "feedback": "Improvement suggestion"
}}
"""

    response = generate_response(prompt, ltm=ltm)

    try:
        # Extract JSON safely
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found")

        clean_json = json_match.group()
        result = json.loads(clean_json)

        score = result.get("score", 0)
        explanation = result.get("explanation", "")
        feedback = result.get("feedback", "")

        # Skill level classification
        if score < 40:
            level = "Weak"
        elif score < 70:
            level = "Average"
        elif score < 90:
            level = "Strong"
        else:
            level = "Excellent"

        # Save to vector memory
        upsert_embeddings(
            text=f"Question: {question}\nStudent's Answer: {answer}\nScore: {score}\nExplanation: {explanation}\nFeedback: {feedback}",
            record_id=f"{student_id}_{abs(hash(question))}",
            student_id=student_id,
        )

        return {
            "score": score,
            "level": level,
            "explanation": explanation,
            "feedback": feedback,
        }

    except Exception:
        return {
            "score": 0,
            "level": "Error",
            "explanation": "Could not evaluate answer correctness due to response parsing error.",
            "feedback": "",
        }
