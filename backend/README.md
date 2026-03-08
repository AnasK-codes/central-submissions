# PARIKSHAN_AI – Backend

PARIKSHAN_AI is an AI-powered interview platform built with FastAPI.
The backend uses Large Language Models (LLMs) to dynamically generate interview questions, evaluate responses in real time, and track student performance across sessions using a structured PostgreSQL database.

---

# Features

* AI-generated interview questions
* Real-time answer evaluation
* Structured interview sessions
* Student performance tracking
* Version-controlled database with Alembic migrations
* Modular FastAPI architecture
* OAuth2 + JWT authentication

---

# API Overview

All APIs are available under the base path:

```
/api/v1
```

---

## Authentication

| Method | Endpoint              | Description                       |
| ------ | --------------------- | --------------------------------- |
| POST   | `/api/v1/auth/signup` | Register a new user               |
| POST   | `/api/v1/auth/login`  | Authenticate user and receive JWT |
| POST   | `/api/v1/auth/google` | Google OAuth2 login               |

---

## Interview Engine

| Method | Endpoint                         | Description                  |
| ------ | -------------------------------- | ---------------------------- |
| POST   | `/api/v1/interview/start`        | Start an interview session   |
| GET    | `/api/v1/interview/{id}/next`    | Fetch the next question      |
| POST   | `/api/v1/interview/{id}/answer`  | Submit answer for evaluation |
| GET    | `/api/v1/interview/{id}/summary` | Get final interview report   |

---

# Database Architecture

The system uses a **PostgreSQL schema** designed for scalability and AI metadata storage.

## Identity Layer

**User**

Stores user identity information.

Fields include:

* google_id
* email
* role (student/admin)

---

## Knowledge Layer

**Subject**

Represents an academic domain such as:

* Python
* Data Structures
* Operating Systems

**Question**

Master question bank containing:

* question text
* sample_answer
* bloom_level
* difficulty

**question_subjects**

Many-to-many junction table connecting questions with subjects.

---

## Session Layer

**InterviewSession**

Tracks the lifecycle of an interview session.

Includes:

* mode
* session status
* llm_metadata

**InterviewQuestion**

Maintains the ordered list of questions asked during a session.

**Answer**

Stores:

* student response
* AI score (double_precision)
* detailed feedback
* ai_evaluation_metadata (JSONB)

---


# Setup

## 1. Install dependencies

```
pip install -r requirements.txt
```

---

## 2. Run database migrations

```
alembic upgrade head
```

This syncs the database schema with the latest migration.

---

## 3. Run the server

```
uvicorn main:app --reload
```

The API will be available at:

```
http://127.0.0.1:8000
```

---

# Testing the API

Interactive documentation is automatically available through Swagger UI.

```
http://127.0.0.1:8000/docs
```

This allows you to test all endpoints directly from the browser.

---

# Mock Mode (Development)

To run the backend without external AI API keys, enable mock mode.

Create a `.env` file and add:

```
AI_MOCK_MODE=true
```

This allows testing the interview workflow without calling real LLM services.

---

# Tech Stack

* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* JWT Authentication
* Google OAuth2
* LLM-based evaluation system

---

# Purpose

PARIKSHAN_AI is designed to simulate realistic technical interviews by combining structured backend architecture with AI-driven evaluation. The system helps students practice interviews while giving structured feedback and performance insights.

---
