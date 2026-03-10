import json
from groq import Groq

from app.services.pinecone import query_embeddings,upsert_embeddings
from app.core.config import GROQ_API_KEY
client = Groq(
    api_key=GROQ_API_KEY,
)
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
    try:
        # Try to get context from embeddings, but don't fail if it times out
        context = ""
        try:
            ltm = query_embeddings(data.subject, student_id=student_id)
            if ltm and hasattr(ltm, "matches"):
                for match in ltm.matches:
                    context += match.metadata.get("text", "") + "\n"
        except Exception as embed_err:
            print(f"[Question Generator] Skipping context lookup due to: {embed_err}")
            context = ""

        system_prompt, user_prompt = build_prompt(data, context)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4,
        )
        raw = response.choices[0].message.content

        # Strip markdown code block markers if present
        raw = raw.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        elif raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        try:
            parsed = json.loads(raw)
            # Skip upserting during question generation to speed up response
            # Questions can be indexed later or on answer submission
            return parsed
        except json.JSONDecodeError:
            print("Failed to parse JSON. Raw response:")
            print(raw)
            raise ValueError("AI response was not valid JSON.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise
