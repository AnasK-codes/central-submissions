import os
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt


from app.core.deps import oauth2_scheme
from app.core.config import SECRET_KEY
from app.core.security import ALGORITHM
from app.database.database import SessionLocal
from app.database.models import User


# Optional: Get auth token from environment variable for MCP usage
MCP_AUTH_TOKEN = os.getenv("SAARTHI_AUTH_TOKEN")
MCP_USER_EMAIL = os.getenv("SAARTHI_USER_EMAIL")


def get_current_user(token: str = Depends(oauth2_scheme)):
    # If MCP auth is configured, use it
    if MCP_AUTH_TOKEN and MCP_USER_EMAIL and token == MCP_AUTH_TOKEN:
        db = SessionLocal()
        user = db.query(User).filter(User.email == MCP_USER_EMAIL).first()
        db.close()
        if user:
            return user
    
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email: str | None = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


