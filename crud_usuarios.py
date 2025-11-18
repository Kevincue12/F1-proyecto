from sqlalchemy.orm import Session
from fastapi import HTTPException

import models, schemas
from auth import get_password_hash


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    if get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="El usuario ya existe.")

    db_user = models.User(
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
