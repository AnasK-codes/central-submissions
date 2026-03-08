import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.core.google_auth import verify_google_token
from app.core.responses import StandardResponse, success_response
from app.core.security import create_access_token, hash_password, verify_password
from app.db.repository.user_repo import user_repo
from app.db.session import get_db
from app.schemas.user import GoogleLoginRequest, LoginRequest, SignupRequest

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


# 🔴 FIX: Rate limit signup to 5 requests/minute per IP to prevent spam account creation
@router.post("/signup", status_code=201, response_model=StandardResponse)
@limiter.limit("5/minute")
def signup(request: Request, payload: SignupRequest, db: Session = Depends(get_db)):
    try:
        # 1. Check uniqueness
        existing_user = user_repo.get_user_by_email(db, payload.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "message": "Email already registered",
                    "code": "ERR_VALIDATION",
                },
            )

        # 2. Create User
        hashed_pwd = hash_password(payload.password)
        new_user = user_repo.create_user(db, payload, hashed_pwd)

        # 3. Issue JWT
        token = create_access_token(new_user.id)

        return success_response(
            {
                "token": token,
                "user": {
                    "id": new_user.id,
                    "name": new_user.name,
                    "email": new_user.email,
                },
            }
        )

    except HTTPException:
        raise
    except Exception:
        # 🟡 FIX: Log the full traceback internally; never expose it in the response
        logger.exception("Unexpected error during signup")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# 🔴 FIX: Rate limit login to 5 requests/minute per IP to prevent brute-force attacks
@router.post("/login", response_model=StandardResponse)
@limiter.limit("5/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and issue JWT.
    """
    # 1. Verify User
    user = user_repo.get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "message": "Invalid email or password",
                "code": "ERR_AUTH",
            },
        )

    # 2. Issue JWT
    token = create_access_token(user.id)

    return success_response(
        {
            "token": token,
            "user": {"id": user.id, "name": user.name, "email": user.email},
        }
    )


@router.post("/google", response_model=StandardResponse)
def google_auth(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    """
    1. Verify Google ID Token.
    2. Get or create user in local DB.
    3. Issue local JWT for our API.
    """
    # 1. Verify the token with Google's servers
    google_data = verify_google_token(payload.id_token)

    # 2. Sync with our Database — now passing google_id
    user = user_repo.get_or_create_google_user(
        db,
        email=google_data["email"],
        name=google_data.get("name") or google_data["email"].split("@")[0],
        google_id=google_data["google_id"],
    )

    # 3. Issue our own system's JWT
    token = create_access_token(user.id)

    return success_response(
        {
            "token": token,
            "user": {"id": user.id, "name": user.name, "email": user.email},
        }
    )