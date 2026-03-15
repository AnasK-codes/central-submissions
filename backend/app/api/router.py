"""
router.py

Central API router. Aggregates all sub-routers for v1.
"""
from fastapi import APIRouter

from app.api.routes import auth_routes, interview_routes, user_routes

api_router = APIRouter()

api_router.include_router(
    auth_routes.router, prefix="/auth", tags=["authentication"]
)
api_router.include_router(
    interview_routes.router, prefix="/interview", tags=["interview"]
)
api_router.include_router(
    user_routes.router, prefix="/users", tags=["users"]
)
