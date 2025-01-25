import datetime
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
import sqlalchemy
from sqlalchemy.orm import Session
from datetime import timedelta
import jwt
import uuid

from catifier.auth.database import get_db
from catifier.auth.models import User, CatifierUser, APIKey
from catifier.auth.utils import (
    blacklist_token,
    expire_token,
    authenticate_user,
    create_access_token,
    get_user,
    get_user_from_token,
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
            status_code=401,
            detail="Invalid username or password",
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
            user = get_user(token, None)
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


@router.put("/create-api-key")
async def create_api_key(
    token: str = Header(..., alias="Authorization"), db: Session = Depends(get_db)
):
    api_key = uuid.uuid4().hex
    user = get_user(token, None)

    new_api_key = APIKey(user_id=user.id, api_key=api_key)
    db.add(new_api_key)
    db.commit()

    return {"message": "API key created successfully", "api_key": api_key}


@router.get("/api-key")
async def get_api_key(
    user: User = Depends(get_user_from_token), db: Session = Depends(get_db)
):
    api_key = db.query(APIKey).filter(APIKey.user_id == user.id).first()

    if api_key is None:
        raise HTTPException(status_code=404, detail="API key not found")

    return {"message": "API key retrieved successfully", "api_key": api_key.api_key}


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
