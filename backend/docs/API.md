# Interview API Documentation

This directory documents the endpoints related to interview sessions.

---

### Endpoint
`POST /api/v1/interview/start`

### Method
POST

### Description
Starts a new interview session and initializes the interview questions based on the provided configuration. Returns the session details or the first question depending on the engine design.

### Request Body
```json
{
  "subject": "Python",
  "mode": "single_bloom",
  "difficulty": "medium",
  "num_questions": 5,
  "language": "en",
  "bloom_strategy": "fixed"
}
```

### Response
```json
{
  "session_id": 12345,
  "status": "active",
  "message": "Interview session started successfully."
}
```

### Example
**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/interview/start" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <your_token>" \
     -d '{
           "subject": "Python",
           "mode": "single_bloom",
           "difficulty": "medium",
           "num_questions": 5
         }'
```

---

### Endpoint
`POST /api/v1/interview/{session_id}/answer`

### Method
POST

### Description
Submits the user's answer for a specific question in an active interview session. The backend stores the answer and returns an updated status (does not evaluate immediately to improve UX speed).

### Request Body
```json
{
  "interview_question_id": 42,
  "user_answer": "A dictionary in Python is an unordered collection of data values, used to store data values like a map..."
}
```

### Response
```json
{
  "message": "Answer submitted successfully",
  "status": "next" 
}
```

### Example
**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/interview/12345/answer" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <your_token>" \
     -d '{
           "interview_question_id": 42,
           "user_answer": "My answer here."
         }'
```

---

### Endpoint
`GET /api/v1/interview/{session_id}/result`

### Method
GET

### Description
Retrieves the simple final result string, score, and percentage for a completed interview session.

### Request Body
Empty

### Response
```json
{
  "score": 4,
  "total": 5,
  "percentage": 80.0
}
```

### Example
**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/interview/12345/result" \
     -H "Authorization: Bearer <your_token>"
```
