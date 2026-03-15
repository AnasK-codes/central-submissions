import logging

from fastapi import HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token

from app.core.config import settings

logger = logging.getLogger(__name__)


def verify_google_token(token: str) -> dict:
    """
    Verify a Google ID token and return the extracted user info.

    Returns a dict with keys: email, name, picture, google_id.
    Raises HTTPException(401) on any failure — invalid token, wrong
    audience, unverified email, etc.
    """
    if not settings.GOOGLE_CLIENT_ID:
        logger.error("GOOGLE_CLIENT_ID is not configured.")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Google authentication is not configured on this server.",
                "code": "ERR_CONFIG",
            },
        )

    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError as exc:
        # Covers: expired tokens, wrong audience, malformed JWTs
        logger.warning("Google token validation failed: %s", exc)
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "message": "Google token invalid or expired.",
                "code": "ERR_AUTH",
            },
        )
    except Exception as exc:
        logger.error("Unexpected error during Google token verification: %s", exc)
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "message": "Google token verification failed.",
                "code": "ERR_AUTH",
            },
        )

    # Reject unverified emails — could be spoofed or abandoned accounts
    if not idinfo.get("email_verified"):
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "message": "Google account email is not verified.",
                "code": "ERR_AUTH",
            },
        )

    return {
        "email": idinfo["email"],
        "name": idinfo.get("name") or idinfo["email"].split("@")[0],
        "picture": idinfo.get("picture"),  # Profile photo URL from Google
        "google_id": idinfo["sub"],        # Stable, unique Google user ID
    }