from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from catifier.auth.database import Base, engine
from typing import final
from pydantic import BaseModel


class CatifierUser(BaseModel):
    username: str
    password: str


@final
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    credits = Column(Integer, default=1)


@final
class APIKey(Base):
    __tablename__ = "api_key"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    api_key = Column(String)


@final
class Image(Base):
    __tablename__ = "image"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    image_url = Column(String)


@final
class Blacklist(Base):
    __tablename__ = "blacklist"
    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, index=True)
    expires_at = Column(DateTime, index=True)


Base.metadata.create_all(bind=engine)
