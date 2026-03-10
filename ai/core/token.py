from datetime import datetime,timedelta
from jose import jwt,JWTError
from app.core.config import SECRET_KEY
from app.core.security import ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES,REFRESH_TOKEN_EXPIRE_DAYS

def create_access_token(data:dict)->str:
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({
        "exp":expire
    })
    encoded_jwt=jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(data:dict)->str:
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({
        "exp":expire,
        "type":"refresh"
    })
    encoded_jwt=jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt

