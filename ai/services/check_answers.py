from groq import Groq
from app.core.config import GROQ_API_KEY
from app.services.pinecone import query_embeddings, upsert_embeddings
import json
import re

client = Groq(
    api_key=GROQ_API_KEY,
)

def generate_response(prompt: str, ltm=None) -> str:
    try:
        system_text = (
            "You are an AI assistant. "
            "Follow instructions exactly. "
            "If asked for JSON, return ONLY valid JSON."
        )

        if ltm:
            system_text += f" Memory: {ltm}"

        chat_response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_text},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

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
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
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
        record_id = f"{student_id}_{abs(hash(question))}"
        text_to_save = f"Question: {question}\nStudent's Answer: {answer}\nScore: {score}\nExplanation: {explanation}\nFeedback: {feedback}"
        
        print(f"[Pinecone] Saving to Pinecone...")
        print(f"[Pinecone] Record ID: {record_id}")
        print(f"[Pinecone] Student ID: {student_id}")
        print(f"[Pinecone] Text preview: {text_to_save[:100]}...")
        
        upsert_result = upsert_embeddings(
            text=text_to_save,
            record_id=record_id,
            student_id=student_id
        )
        
        print(f"[Pinecone] Upsert completed: {upsert_result}")

        return {
            "score": score,
            "level": level,
            "explanation": explanation,
            "feedback": feedback
        }

    except Exception:
        return {
            "score": 0,
            "level": "Error",
            "explanation": "Could not evaluate answer correctness due to response parsing error.",
            "feedback": ""
        }