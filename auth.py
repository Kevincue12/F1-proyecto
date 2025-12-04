from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import models
from database import SessionLocal
import crud_usuarios

SECRET_KEY = "super-secret-key-change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# === ⬇ NUEVO SISTEMA CON COOKIES ⬇ ===
async def get_current_user(
    access_token: str = Cookie(default=None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = crud_usuarios.get_user_by_username(db, username=username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# === LOGIN ===
def authenticate_and_create_token(db: Session, username: str, password: str):
    user = crud_usuarios.get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    access_token = create_access_token(
        data={"sub": user.username}
    )

    return {"access_token": access_token, "token_type": "bearer"}
