# Temporary Mock logic to replace the AI Team's code
def generate_questions_mock(payload, student_id):
    return {
        "questions": [
            {
                "question_text": f"Mock Question {i} for {payload.subject}",
                "bloom_level": "L1",
                "difficulty": payload.difficulty,
                "topic_tags": ["testing", "mock"],
                "estimated_answer_time_sec": 45,
                "id": i
            } for i in range(1, payload.num_questions + 1)
        ]
    }

def check_answer_correctness_mock(question, answer, student_id):
    return {
        "score": 85.0,
        "explanation": "This is a mock feedback because API keys are not set.",
        "level": "Good",
        "feedback": "Keep practicing with mock data!"
    }