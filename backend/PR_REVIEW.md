# PR Review: `feature/auth-and-db-setup → main`

**Branch:** `feature/auth-and-db-setup`  
**Commits:** 3 (auth + DB models, interview functionality with AI integration)  
**Files changed:** 36 | **+1441 / -40**

---

## Summary

This PR implements core authentication (email/password + Google OAuth), the full database schema, and an AI-powered interview session flow backed by Groq LLM and Pinecone vector memory. The overall architecture is clean and well-thought-out. There are **4 critical bugs** that will cause runtime crashes or security regressions, several security improvements needed, and a few code-quality issues.

---

## 🔴 Critical Bugs (Must Fix Before Merge)

### 1. `create_user` — broken static method call

**File:** [`app/db/repository/user_repo.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/db/repository/user_repo.py)

```python
# CURRENT (broken) — create_user is a static method but doesn't have @staticmethod
# and it is called as user_repo.create_user(...) on an instance
def create_user(db: Session, user_in: SignupRequest, hashed_password: str):
    ...
```

Missing `self` parameter and no `@staticmethod` decorator. Calling `user_repo.create_user(db, payload, hashed_pwd)` will raise `TypeError: create_user() takes 3 positional arguments but 4 were given`.

```diff
-    def create_user(db: Session, user_in: SignupRequest, hashed_password: str):
+    def create_user(self, db: Session, user_in: SignupRequest, hashed_password: str):
```

---

### 2. `Base.metadata.create_all` called twice in `main.py`

**File:** [`app/main.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/main.py)

```python
# Called once near the top, and again inside a try/except at the bottom
Base.metadata.create_all(bind=engine)   # line ~18
...
try:
    Base.metadata.create_all(bind=engine)  # duplicate — remove this
except Exception as e:
    print(e)
```

This is harmless for SQLite/Postgres (`IF NOT EXISTS` is implied) but it's dead code that signals a mistake. Remove the second call entirely.

---

### 3. `AuthService` errors are silently swallowed — broken auth flow

**File:** [`app/services/auth_service.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/services/auth_service.py)

```python
def signup(self, db, payload):
    existing_user = user_repo.get_user_by_email(db, payload.email)
    if existing_user:
        error_response("Email already registered", "ERR_VALIDATION", 400)  # ← NOT raised!
```

`error_response` in `app/core/responses.py` is not defined — only `success_response` exists. Even if it were defined, the return value is never raised as an `HTTPException`. The route will silently continue and attempt to create a duplicate user.

`AuthService` in `auth_service.py` isn't even used by the auth endpoints — `app/api/v1/endpoints/auth.py` inlines all the same logic. Either remove `auth_service.py` or replace the inline logic in the endpoint with the service. Right now you have two parallel, diverging code paths.

---

### 4. Interview endpoints have **no authentication guard**

**File:** [`app/api/v1/endpoints/interview.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/api/v1/endpoints/interview.py)

Every `/interview/*` route accepts an arbitrary `student_id: str` as a query/body parameter. Anyone can start an interview session or read another user's session by passing any `student_id`. There is no JWT verification or `Depends(get_current_user)` on any interview route.

```python
# Example — expose a dependency for the current user
from app.core.auth import get_current_user   # needs to be created

@router.post("/start")
async def start_interview(
    payload: InterviewStartRequest,
    current_user: User = Depends(get_current_user),  # ← add this
    db: Session = Depends(get_db)
):
    student_id = str(current_user.id)  # derive from token, not from payload
```

---

## 🟠 Security Issues

### 5. CORS: `"*"` combined with `allow_credentials=True`

**File:** [`app/main.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/main.py)

```python
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "*",   # ← this overrides the specific origins and is invalid with credentials
]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, ...)
```

Per the CORS spec, `allow_credentials=True` with `allow_origins=["*"]` will be rejected by browsers. Starlette silently ignores the wildcard, but the `"*"` in the list is confusing and wrong. For dev, just use the two localhost origins; for prod add the actual domain.

---

### 6. Google token error detail leaked to client

**File:** [`app/core/google_auth.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/core/google_auth.py)

```python
raise HTTPException(status_code=401, detail=str(e))   # leaks internal error message
```

Change to a generic message: `detail="Invalid Google token"`.

---

### 7. No JWT validation dependency (`get_current_user`) exists

There's no `app/core/auth.py` with a `get_current_user` dependency that decodes and validates the JWT. This means issued tokens are never verified on protected endpoints. This needs to be created before any endpoint can be secured.

```python
# app/core/auth.py  (needs to be created)
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings

bearer = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_id
```

---

### 8. `datetime.utcnow()` deprecated in Python 3.12+

**File:** [`app/core/security.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/core/security.py)

```diff
-expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
+expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
# from datetime import datetime, timedelta, UTC
```

---

## 🟡 Code Quality & Architecture

### 9. `question_generator.py` imports `GROQ_API_KEY` incorrectly

**File:** [`app/services/question_generator.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/services/question_generator.py)

```python
from app.core.config import GROQ_API_KEY   # ← wrong, it's settings.GROQ_API_KEY
```

This will produce an `ImportError` at startup when `AI_MOCK_MODE=false`. Should be:

```python
from app.core.config import settings
client = Groq(api_key=settings.GROQ_API_KEY)
```

---

### 10. Pinecone client initialized at module-level (will crash at import)

**File:** [`app/services/pinecone.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/services/pinecone.py)

```python
pc = Pinecone(api_key=settings.PINECONE_API_KEY)   # runs at import time
if not pc.has_index(index_name): ...               # network call at import time
```

Even when `AI_MOCK_MODE=true`, importing this module will make a real Pinecone API call. Any missing/invalid `PINECONE_API_KEY` will crash the server at startup. Wrap initialization in a function or lazy-load it only when `AI_MOCK_MODE=false` is confirmed.

---

### 11. `get_or_create_google_user` — missing `google_id` parameter in `user_repo.py`

**File:** [`app/db/repository/user_repo.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/db/repository/user_repo.py)

The method signature only accepts `(self, db, email, name)` but the `auth_service.py` calls it with `google_id=google_data["google_id"]`. The route in `endpoints/auth.py` calls it without `google_id`. Neither the `User` model's `google_id` field nor the `auth_provider` field is populated on Google sign-up.

---

### 12. `config.py` — redundant `load_dotenv()` + `os.getenv()` pattern

**File:** [`app/core/config.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/core/config.py)

`pydantic-settings` handles `.env` loading natively. Mixing `os.getenv()` defaults with `pydantic_settings.BaseSettings` fields is redundant and bypasses Pydantic's validation and type coercion. Restore `model_config = SettingsConfigDict(env_file=".env")`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    GOOGLE_CLIENT_ID: str
    PINECONE_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    AI_MOCK_MODE: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
```

---

### 13. `get_db` silently re-raises without rollback

**File:** [`app/db/session.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/db/session.py)

The `except Exception: raise` adds no value; but more importantly there's no `db.rollback()` on error:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```

---

### 14. Missing `source_type` values and `Question` model field name mismatch

**File:** [`app/api/v1/endpoints/interview.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/api/v1/endpoints/interview.py)

The comment says `'estimated_time' in Question table vs 'estimated_answer_time_sec'` — the `Question` model does not have an `estimated_time` field at all. This comment signals a field was forgotten. Consider adding `estimated_answer_time_sec` to `Question` or clarifying the design intent.

---

### 15. No automated tests

The `tests/` directory exists but contains no test files. Given the security-critical nature of auth, at minimum add:

- `test_signup` (success, duplicate email)
- `test_login` (success, wrong password, google-only user)
- `test_google_auth` (mocked token verification)
- `test_interview_unauthorized` (no token → 401)

---

## 🔴 Missing: `.env.example` — And Real Secrets Are Exposed

**File:** `.env.example` — **does not exist** in the repo.

Worse, `.env` **is in`.gitignore`** but the actual `.env` file contains real production secrets that were clearly used during development:

```
GOOGLE_CLIENT_SECRET="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"
GOOGLE_CLIENT_ID="491923001474-..."
SECRET_KEY="f20205e70b09..."
```

> [!CAUTION]
> **Rotate all secrets immediately.** Even though `.env` is gitignored _now_, if it was ever committed (even briefly), GitHub's history retains it. Revoke the Google OAuth credentials and generate a new `SECRET_KEY`.

A `.env.example` must be added listing every required variable with placeholder values, so new contributors know what to configure:

```ini
# .env.example
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
PINECONE_API_KEY=your-pinecone-api-key
GROQ_API_KEY=your-groq-api-key
AI_MOCK_MODE=true
```

Also note: `PINECONE_API_KEY` and `GROQ_API_KEY` are used in the code (see `config.py`) but are completely absent from the `.env` file — anyone cloning this repo will get a startup crash with no guidance.

---

## 🔴 Missing Packages in `requirements.txt`

The following packages are imported directly in the codebase but **not listed** in `requirements.txt`. The app will fail to install on any fresh environment:

| Package (import name)           | Install name                | Used in                              |
| ------------------------------- | --------------------------- | ------------------------------------ |
| `jose`                          | `python-jose[cryptography]` | `app/core/security.py`               |
| `passlib`                       | `passlib[bcrypt]`           | `app/core/security.py`               |
| `groq`                          | `groq`                      | `app/services/question_generator.py` |
| `pinecone`                      | `pinecone-client`           | `app/services/pinecone.py`           |
| `sentence_transformers`         | `sentence-transformers`     | `app/services/embedding.py`          |
| `google.oauth2` / `google.auth` | `google-auth`               | `app/core/google_auth.py`            |

Add these to `requirements.txt`:

```
# --- Auth & Security ---
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# --- Google Auth ---
google-auth==2.29.0

# --- AI / ML ---
groq==0.9.0
pinecone-client==3.2.2
sentence-transformers==3.0.1
```

> [!NOTE]
> `sentence-transformers` pulls in PyTorch and will make the install ~2GB. Consider pinning a CPU-only torch version or using a lighter embedding model/API in production to avoid bloating the deployment image.

---

## 🔴 Additional Bugs Found in Deep Scan

### 16. `check_answers.py` — same broken `GROQ_API_KEY` as `question_generator.py`

**File:** [`app/services/check_answers.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/services/check_answers.py)

```python
client = Groq(api_key=GROQ_API_KEY)   # GROQ_API_KEY is never imported or defined
```

`GROQ_API_KEY` is referenced but never imported — `NameError` at first non-mock answer evaluation. Fix: `api_key=settings.GROQ_API_KEY`.

---

### 17. `generate_questions_mock` called with wrong number of arguments

**File:** [`app/api/v1/endpoints/interview.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/api/v1/endpoints/interview.py) line 46

```python
# mock_ai.py defines:
def generate_questions_mock(payload, student_id):  # 2 required args

# endpoint calls:
ai_response = generate_questions_mock(payload)     # ← only 1 arg — TypeError!
```

Every mock interview start will crash. Fix: `generate_questions_mock(payload, student_id=payload.student_id)`.

---

### 18. `InterviewSession` created with non-existent columns + missing required fields

**File:** [`app/api/v1/endpoints/interview.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/api/v1/endpoints/interview.py) lines 29–35

```python
new_session = InterviewSession(
    subject_name=payload.subject,           # ❌ column doesn't exist (model has subject_id)
    total_questions=payload.num_questions,  # ❌ column doesn't exist (model has num_questions_requested)
    # Missing nullable=False fields: mode, num_questions_requested,
    #   num_questions_generated, started_at  → IntegrityError on commit
)
```

This will always raise an `IntegrityError` — `started_at`, `mode`, `num_questions_requested`, and `num_questions_generated` are all `nullable=False` but none are set.

---

### 19. Student existence check filters on `google_id` instead of `id`

**File:** [`app/api/v1/endpoints/interview.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/api/v1/endpoints/interview.py) line 20

```python
student = db.query(User).filter(User.google_id == payload.student_id).first()
```

`google_id` is `NULL` for all email/password users. Every email-registered user will get a 404 when trying to start an interview, even with a valid token.

---

### 20. `submit_answer` sends free-text answer as a URL query parameter

**File:** [`app/api/v1/endpoints/interview.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/api/v1/endpoints/interview.py)

```python
async def submit_answer(session_id: int, interview_question_id: int,
                        user_answer: str, student_id: str, ...):
```

FastAPI treats plain `str` args on POST routes as query parameters. Student answers can be many paragraphs — URLs cap at ~2000 chars and are logged in plaintext in every server/proxy log. Create a Pydantic `SubmitAnswerRequest` body schema instead.

---

### 21. `get_summary` raises `TypeError` if any `evaluation_score` is `None`

**File:** [`app/api/v1/endpoints/interview.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/api/v1/endpoints/interview.py) line 196

```python
avg_score = sum(ans.evaluation_score for ans in results) / len(results)
# Answer.evaluation_score is nullable=True — None + int = TypeError
```

Fix: `sum(ans.evaluation_score or 0 for ans in results)`

---

### 22. `student_id` in `InterviewStartRequest` enables IDOR

**File:** [`app/schemas/interview.py`](file:///Users/anaskhan/Documents/GitHub/team-backend/app/schemas/interview.py)

Client-supplied `student_id: str` in request body means any authenticated user can start an interview session attributed to any other student's ID. This field must be removed from the schema and derived from the JWT token server-side (linked to fix #7).

---

## ✅ What's Done Well

- Clean layered architecture: `endpoints → service → repo`.
- `AI_MOCK_MODE` toggle is excellent for dev/test without real keys.
- `StandardResponse` / `ErrorResponse` envelope is consistent.
- `InterviewSession` lifecycle management (pending → active → completed/failed) is well-designed.
- Alembic properly set up for future migrations.
- `Subject → Question` many-to-many with junction table is the right model.
- `check_answers.py` JSON regex extraction guard is nicely handled.
- `UserOut` schema correctly excludes `password_hash` from responses.

---

## Priority Fix Order

| #    | Issue                                                               | Priority |
| ---- | ------------------------------------------------------------------- | -------- |
| —    | **Rotate all secrets** (Google OAuth + SECRET_KEY)                  | 🔴 P0    |
| —    | 6 missing packages in `requirements.txt`                            | 🔴 P0    |
| 4    | No auth guard on interview endpoints                                | 🔴 P0    |
| 3    | `error_response` missing + auth service unused                      | 🔴 P0    |
| 1    | `create_user` broken method signature                               | 🔴 P0    |
| 9/16 | `GROQ_API_KEY` undefined in both AI service files                   | 🔴 P0    |
| 7    | `get_current_user` dependency missing                               | 🔴 P0    |
| 17   | `generate_questions_mock` called with wrong # of args               | 🔴 P0    |
| 18   | `InterviewSession` wrong column names + missing non-nullable fields | 🔴 P0    |
| 19   | Student lookup filters on `google_id` (email users always get 404)  | 🔴 P0    |
| —    | Add `.env.example` with all required keys                           | 🟠 P1    |
| 10   | Pinecone module-level init crashes startup                          | 🟠 P1    |
| 11   | `google_id` missing in `get_or_create_google_user`                  | 🟠 P1    |
| 5    | CORS wildcard + credentials                                         | 🟠 P1    |
| 6    | Google error detail leak                                            | 🟠 P1    |
| 20   | `submit_answer` free-text answer sent as URL query param            | 🟠 P1    |
| 21   | `get_summary` crashes on `None` evaluation_score                    | 🟠 P1    |
| 22   | `student_id` in request body enables IDOR                           | 🟠 P1    |
| 2    | Double `create_all` call                                            | 🟡 P2    |
| 12   | Redundant `os.getenv` in config                                     | 🟡 P2    |
| 13   | Missing `db.rollback()`                                             | 🟡 P2    |
| 8    | `datetime.utcnow()` deprecated                                      | 🟡 P2    |
| 14   | Missing `estimated_answer_time_sec` field in `Question` model       | 🟡 P2    |
| 15   | No tests                                                            | 🟡 P2    |
