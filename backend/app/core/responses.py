"""
app/core/responses.py — backward-compatibility shim.

Response helpers have been moved to app.utils.response.
This module re-exports them so any external code that still imports
from app.core.responses continues to work without modification.
"""
from app.utils.response import (  # noqa: F401
    StandardResponse,
    ErrorDetail,
    ErrorResponse,
    success_response,
    error_response,
)

__all__ = [
    "StandardResponse",
    "ErrorDetail",
    "ErrorResponse",
    "success_response",
    "error_response",
]