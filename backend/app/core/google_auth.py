from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.config import settings
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


def verify_google_token(token: str):
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        # 🟡 FIX: Reject login if the Google account's email is not verified.
        # Unverified emails could be spoofed or represent abandoned accounts.
        if not idinfo.get("email_verified"):
            raise HTTPException(
                status_code=401,
                detail="Google account email is not verified.",
            )

        return {
            "email": idinfo["email"],
            "name": idinfo.get("name"),
            "google_id": idinfo["sub"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Google token verification failed: %s", e)
        raise HTTPException(status_code=401, detail="Invalid Google token")