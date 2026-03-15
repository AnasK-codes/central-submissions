# PARIKSHAN_AI

> An AI-powered interview practice platform that generates dynamic questions, evaluates answers, and tracks student performance.

---

## Project Overview

**PARIKSHAN_AI** simulates realistic technical interviews by combining a structured FastAPI backend with a React frontend and an LLM-based AI evaluation engine.

Users configure an interview session by selecting a subject, difficulty, and Bloom's taxonomy level. The system generates targeted questions via an AI pipeline, collects answers from the user, and then batch-evaluates the entire session to provide a detailed performance breakdown.

---

## Tech Stack

### Frontend

- **React** (Vite)
- **React Router** — client-side routing
- **Axios** — HTTP client for API calls
- **Google OAuth** (`@react-oauth/google`) — social login
- **TailwindCSS** — utility-first styling

### Backend

- **FastAPI** — async Python web framework
- **SQLAlchemy** — ORM for database interaction
- **Alembic** — database migration management
- **PostgreSQL** — relational database
- **JWT (python-jose)** — stateless authentication
- **Slowapi** — rate limiting
- **Google Auth Library** — OAuth2 token verification

### AI Services

- **Groq API** — LLM inference for question generation and answer evaluation
- **Pinecone** — vector embeddings for semantic similarity
- `AI_MOCK_MODE=true` — local development mode (bypasses real AI calls)

---

## System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                    │
│  InterviewConfig → InterviewScreen → Results             │
└──────────────────────┬───────────────────────────────────┘
                       │ HTTP (JSON / JWT)
┌──────────────────────▼───────────────────────────────────┐
│                    BACKEND (FastAPI)                     │
│  Routes → Controllers → Services → Repositories → DB    │
└───────────┬──────────────────────────────────────────────┘
            │ LLM API calls
┌───────────▼──────────────────────────────────────────────┐
│              AI MODULE (Groq / Pinecone)                 │
│  Question Generator | Answer Evaluator | Embeddings      │
└──────────────────────────────────────────────────────────┘
            │
┌───────────▼──────────────────────────────────────────────┐
│                POSTGRESQL DATABASE                       │
│  Users | Sessions | Questions | Answers                  │
└──────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
central-submissions/
├── frontend/               # React frontend application
│   └── src/
│       ├── pages/          # InterviewConfig, InterviewScreen, LoginPage, etc.
│       ├── components/     # QuestionCard, ProtectedRoute
│       ├── hooks/          # useAuth, useInterview
│       ├── api/            # api.js — Axios proxy layer
│       └── context/        # AuthContext
├── backend/                # FastAPI backend application
│   └── app/
│       ├── api/routes/     # HTTP route definitions
│       ├── controllers/    # Request orchestration layer
│       ├── services/       # Business logic
│       ├── repositories/   # Database query layer
│       ├── models/         # SQLAlchemy ORM models
│       ├── schemas/        # Pydantic request/response schemas
│       ├── core/           # Auth, security, config, rate-limiting
│       └── db/             # Session and base setup
├── ai/                     # AI team module (READ ONLY)
│   └── ...
└── docs/                   # Shared documentation
    ├── API.md
    └── interview-flow.md
```

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL running locally or remotely

---

## Running the Backend

All commands below must be run from the `backend/` directory.

### 1. Create a Virtual Environment

```bash
python3 -m venv .venv
```

Activate it:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Then open `.env` and fill in your values:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GOOGLE_CLIENT_ID=your-google-client-id
PINECONE_API_KEY=your-pinecone-api-key
GROQ_API_KEY=your-groq-api-key
```

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 5. Start the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.  
Interactive Swagger docs: `http://127.0.0.1:8000/docs`

---

## Running the Frontend

All commands below must be run from the `frontend/` directory.

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment Variables

Create a `.env` file in `frontend/`:

```env
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

### 3. Start the Dev Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## Interview Flow

```
User fills InterviewConfig
        ↓
POST /interview/start  →  AI generates questions  →  session created
        ↓
GET /interview/{id}/next  →  first question returned
        ↓
User reads question + types answer
        ↓
POST /interview/{id}/answer  →  answer saved (no scoring yet)
        ↓
GET /interview/{id}/next  →  next question (repeat until done)
        ↓
Backend detects all answers submitted → session marked "completed"
        ↓
GET /interview/{id}/summary  →  AI batch-evaluates all answers
        ↓
Frontend displays score ring, performance level, question breakdown
```

---

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### Authentication

| Method | Endpoint       | Description                  |
| ------ | -------------- | ---------------------------- |
| POST   | `/auth/signup` | Register a new user          |
| POST   | `/auth/login`  | Authenticate and receive JWT |
| POST   | `/auth/google` | Google OAuth2 login          |

### Interview Engine

| Method | Endpoint                  | Description                             |
| ------ | ------------------------- | --------------------------------------- |
| POST   | `/interview/start`        | Start a new interview session           |
| GET    | `/interview/{id}/next`    | Fetch the next unanswered question      |
| POST   | `/interview/{id}/answer`  | Submit an answer (no immediate scoring) |
| GET    | `/interview/{id}/summary` | Get AI-evaluated performance summary    |
| GET    | `/interview/{id}/result`  | Get simplified score and percentage     |

> All interview endpoints require a valid `Authorization: Bearer <token>` header.

---

## Environment Variables Reference

| Variable                      | Description                                     |
| ----------------------------- | ----------------------------------------------- |
| `DATABASE_URL`                | PostgreSQL connection string                    |
| `SECRET_KEY`                  | JWT signing secret                              |
| `ALGORITHM`                   | JWT signing algorithm (default: `HS256`)        |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token validity period in minutes                |
| `GOOGLE_CLIENT_ID`            | Google OAuth2 client ID (must be a single line) |
| `PINECONE_API_KEY`            | API key for Pinecone vector database            |
| `GROQ_API_KEY`                | API key for Groq LLM inference                  |
| `AI_MOCK_MODE`                | Set to `true` to bypass real AI calls locally   |

---

## Pull Request Policy

- **Direct push to `main` is strictly prohibited.**
- All changes must be submitted via Pull Requests.
- Only Team Leads are authorized to open PRs against `main`.
- Each team may only modify their assigned folder (`frontend/`, `backend/`, `ai/`).

---

## Purpose

PARIKSHAN_AI is designed to help students practice technical interviews at any time. The AI-driven architecture dynamically tailors questions to the selected subject and cognitive level, ensuring every session is meaningful and personalized.
