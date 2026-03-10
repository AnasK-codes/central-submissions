from fastapi import Depends, HTTPException, status
from app.core.auth import get_current_user

def require_role(required_role: str):
    def role_dependency(user=Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user

    return role_dependency