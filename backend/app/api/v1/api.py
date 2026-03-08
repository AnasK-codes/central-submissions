from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import interview

# 1. Initialize the master router for version 1
api_router = APIRouter()

# 2. Include sub-routers
# The 'prefix' here means all auth routes will start with /api/v1/auth
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(interview.router, prefix="/interview", tags=["interview"])