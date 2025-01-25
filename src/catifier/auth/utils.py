import hashlib
from typing import Any, cast

from fastapi import HTTPException, Header
from fastapi.responses import JSONResponse
import jwt
from sqlalchemy.orm import Session
from catifier.auth.models import Blacklist, User
from catifier.auth.database import get_db
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from functools import wraps
from typing import Callable, TypeVar


from catifier.logger import LOG
from catifier.auth.constants import get_secret, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

F = TypeVar("F", bound=Callable[..., Any])


def requires_credit(func: F) -> F:
    """
    Decorator that requires a user to have credits to use the function.

    Attaches the user's credits to the response, after decrementing the user's credits.
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        user = kwargs.get("user")

        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = cast(User, user)

        LOG.info(f"User: {user.username}, has {user.credits} credits")

        if user.credits == 0:
            raise HTTPException(status_code=403, detail="User has no credits")

        result = await func(*args, **kwargs)

        decrement_credit(user)
        result["credits"] = user.credits - 1

        return JSONResponse(content=result)

    return wrapper  # pyright: ignore[reportReturnType]


def get_user_credits(user: User) -> int | None:
    db = next(get_db())
    user = db.query(User).filter(User.id == user.id).first()

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    if user.credits == 0:
        raise HTTPException(status_code=403, detail="User has no credits")

    return user.credits


def decrement_credit(user: User):
    db = next(get_db())

    db_user = db.query(User).filter(User.id == user.id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.credits -= 1  # pyright: ignore[reportAttributeAccessIssue]
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


def remove_token(jti: str):
    db = next(get_db())
    _ = db.query(Blacklist).filter(Blacklist.jti == jti).delete()
    db.commit()


def is_expired(jti: str):
    db = next(get_db())
    blacklist = db.query(Blacklist).filter(Blacklist.jti == jti).first()

    return blacklist is not None and blacklist.expires_at > datetime.now()


def get_user_from_access_token(access_token: str) -> User:
    access_token = access_token.split(" ")[1] if " " in access_token else access_token
    is_token_expired = is_expired(access_token)

    if is_token_expired:
        raise HTTPException(
            status_code=401,
            detail="Token expired",
            headers={"expired": "true"},
        )

    try:
        decoded = jwt.decode(access_token, get_secret(), algorithms=[ALGORITHM])

    except jwt.exceptions.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid token or expired",
            headers={"expired": "true"},
        ) from e

    user = User(
        id=decoded["id"], username=decoded["username"], credits=decoded["credits"]
    )

    return user


def get_user_from_api_key(api_key: str) -> User:
    db = next(get_db())
    user = db.query(User).filter(User.api_key == api_key).first()
    return user


def get_user(access_token: str | None, api_key: str | None) -> User:
    if access_token:
        return get_user_from_access_token(access_token)
    elif api_key:
        return get_user_from_api_key(api_key)
    else:
        raise HTTPException(status_code=401, detail="Missing token or API key")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    hashed_password = hash_password(password)

    if user is None or not (user.hashed_password == hashed_password):
        return False

    return user


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    if expires_delta:
        expire = datetime.now() + expires_delta

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_secret(), algorithm=ALGORITHM)
    print(f"GET SECRET: {get_secret()}")

    return encoded_jwt


async def get_user_from_token(
    token: str | None = Header(None, alias="Authorization"),
    api_key: str | None = Header(None, alias="X-API-Key"),
) -> User:
    LOG.info(f"Token: {token}, API Key: {api_key}")

    if not token and not api_key:
        raise HTTPException(status_code=401, detail="Missing token or API key")

    user = get_user(token, api_key)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user
