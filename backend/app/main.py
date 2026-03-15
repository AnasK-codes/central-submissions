import sys
import os

# Add project root to sys.path so the ai/ module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.rate_limit import limiter
from database.base import Base
from database.session import engine

# Configure structured logging at startup
configure_logging()

# 1. APP INITIALIZATION
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
)

# Attach the rate limiter and its error handler to the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


# 2. CORS SETUP
origins = [
    "http://localhost:3000",  # Standard React port
    "http://localhost:5173",  # Standard Vite port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. DATABASE INITIALIZATION
Base.metadata.create_all(bind=engine)


# 4. GLOBAL EXCEPTION HANDLER
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    details = [{"field": str(e["loc"][-1]), "error": e["msg"]} for e in exc.errors()]
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": "Validation failed",
            "code": "ERR_VALIDATION",
            "details": details,
        },
    )


# 5. ROUTER INCLUSION
app.include_router(api_router, prefix=settings.API_V1_STR)

