import datetime
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
import sqlalchemy
from sqlalchemy.orm import Session
from datetime import timedelta
import jwt

from catifier.auth.database import get_db
from catifier.auth.models import User, CatifierUser
from catifier.auth.utils import (
    blacklist_token,
    expire_token,
    authenticate_user,
    create_access_token,
    get_user,
    hash_password,
    remove_token,
)
from catifier.auth.constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter()


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "credits": user.credits,
        },
        expires_delta=access_token_expires,
    )

    blacklist_token(
        access_token, expires_at=datetime.datetime.now() + access_token_expires
    )

    response = JSONResponse(content={"message": "User logged in successfully"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
    )

    return response


@router.post("/logout")
async def logout_user(token: str = Header(..., alias="Authorization")):
    try:
        try:
            user = get_user(token)
        except HTTPException:
            remove_token(token)  # already expired
            return {"message": "User logged out successfully"}

        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except jwt.PyJWTError as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

    expire_token(token)

    return {"message": "User logged out successfully"}


@router.post("/register")
async def register_user(user: CatifierUser, db: Session = Depends(get_db)):
    try:
        new_user = User(
            username=user.username,
            hashed_password=hash_password(user.password),
        )

        db.add(new_user)
        db.commit()
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(
            status_code=400, detail=str("User with this username already exists")
        )

    return {"message": "User registered successfully"}
