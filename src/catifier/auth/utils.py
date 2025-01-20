import hashlib
from typing import Any

import jwt
from sqlalchemy.orm import Session
from catifier.auth.models import Blacklist, User
from catifier.auth.database import get_db
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer

from catifier.auth.constants import SECRET, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_credits(user_id: int) -> int | None:
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        return None

    return user.credits


def decrement_credit(user_id: int):
    db = next(get_db())
    _ = db.query(User).filter(User.id == user_id).update({"credits": User.credits - 1})
    db.commit()


def blacklist_token(jti: str, expires_at: datetime):
    db = next(get_db())
    _ = (
        db.query(Blacklist)
        .filter(Blacklist.jti == jti)
        .update({"expires_at": expires_at})
    )

    db.commit()


def expire_token(jti: str):
    db = next(get_db())
    _ = (
        db.query(Blacklist)
        .filter(Blacklist.jti == jti)
        .update({"expires_at": datetime.now()})
    )

    db.commit()


def is_expired(jti: str):
    db = next(get_db())
    blacklist = db.query(Blacklist).filter(Blacklist.jti == jti).first()

    return blacklist is not None and blacklist.expires_at > datetime.now()


def get_user(access_token: str) -> User | None:
    access_token = access_token.split(" ")[1] if " " in access_token else access_token
    is_token_expired = is_expired(access_token)

    if is_token_expired:  # pyright: ignore[reportGeneralTypeIssues]
        return None

    return jwt.decode(access_token, SECRET, algorithms=[ALGORITHM])


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    hashed_password = hash_password(password)

    if user is None or not (
        user.hashed_password == hashed_password
    ):  # pyright: ignore[reportGeneralTypeIssues]
        return False

    return user


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=15)

    if expires_delta:
        expire = datetime.now() + expires_delta

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)

    return encoded_jwt
