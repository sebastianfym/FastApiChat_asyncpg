import asyncio
from datetime import timedelta, datetime

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from src.config.config import SECRET_KEY
from src.database.database import get_user
from starlette.authentication import AuthenticationBackend


ALGORITHM = "HS256"
EXPIRATION_TIME = timedelta(minutes=180)
SECRET_KEY = SECRET_KEY #openssl rand -hex 32 <--- команда для получения токена


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_jwt_token(data: dict):
    expiration = datetime.utcnow() + EXPIRATION_TIME
    data.update({"exp": expiration})
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_jwt_token(token: str):
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_data
    except jwt.PyJWTError:
        return None


def get_current_user(token: str = Depends(oauth2_scheme)):
    decoded_data = verify_jwt_token(token)
    if not decoded_data:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = asyncio.run(get_user(decoded_data["sub"]))
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return {"sub": user}


class JWTBearer(AuthenticationBackend):
    async def authenticate(self, request):
        authorization = request.headers.get('Authorization')
        if not authorization or not authorization.startswith('Bearer '):
            return None

        token = authorization.split(' ')[1]
        payload = verify_jwt_token(token)
        if payload is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return {"sub": payload.get("sub")}, None

