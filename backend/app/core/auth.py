"""
app/core/auth.py — backward-compatibility shim.

The JWT dependency has been moved to app.core.dependencies.
This module re-exports it so any external code that still imports
from app.core.auth continues to work without modification.
"""
from app.core.dependencies import get_current_user  # noqa: F401

__all__ = ["get_current_user"]
