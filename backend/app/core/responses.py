from typing import Any, Optional, List
from pydantic import BaseModel
from fastapi import HTTPException


class StandardResponse(BaseModel):
    success: bool = True
    data: Any


class ErrorDetail(BaseModel):
    field: str
    error: str


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    code: str
    details: Optional[List[ErrorDetail]] = None


def success_response(data: Any):
    return {
        "success": True,
        "data": data,
    }


def error_response(message: str, code: str, status_code: int = 400):
    """Raise an HTTPException with the standard error envelope."""
    raise HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "message": message,
            "code": code,
        },
    )