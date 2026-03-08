import json
from groq import Groq

from app.core.config import settings

_client = None


def _get_client():
    global _client
    if _client is None:
        from app.services.pinecone_service import query_embeddings, upsert_embeddings  # noqa: F401
        _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


def build_prompt(data, context=""):
    system_prompt = """
You are an AI interview question generator.
You must output strictly valid JSON only.
Do not add explanations or text outside JSON.
Follow Bloom taxonomy, difficulty, and subject.
Also consider student's past interactions for personalized questions.
If context is provided, use it to generate questions that build on student's prior knowledge and weaknesses.

"""

    user_prompt = f"""
Generate {data.num_questions} technical interview questions.

Subject: {data.subject}
Mode: {data.mode}
Bloom Level: {data.bloom_level}
Difficulty: {data.difficulty}
Language: {data.language}

Student memory context:
{context}

Return strictly this JSON format:

{{
  "questions": [
    {{
      "id": 1,
      "question_text": "...",
      "bloom_level": "...",
      "difficulty": "...",
      "topic_tags": ["tag1", "tag2"],
      "estimated_answer_time_sec": 60
    }}
  ]
}}
"""
    return system_prompt, user_prompt


def generate_questions(data, student_id: str):
    from app.services.pinecone_service import query_embeddings, upsert_embeddings

    try:
        ltm = query_embeddings(data.subject, student_id=student_id)
        context = ""
        if ltm and hasattr(ltm, "matches"):
            for match in ltm.matches:
                context += match.metadata.get("text", "") + "\n"

        system_prompt, user_prompt = build_prompt(data, context)
        client = _get_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
        )
        raw = response.choices[0].message.content

        try:
            parsed = json.loads(raw)
            if "questions" in parsed:
                for q in parsed["questions"]:
                    upsert_embeddings(
                        q["question_text"],
                        str(hash(q["question_text"])),
                        student_id=student_id,
                    )
            return parsed
        except json.JSONDecodeError:
            print("Failed to parse JSON. Raw response:")
            print(raw)
            raise ValueError("AI response was not valid JSON.")
    except Exception:
        import traceback

        traceback.print_exc()
        raise