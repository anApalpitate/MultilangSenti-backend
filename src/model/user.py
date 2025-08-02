from datetime import datetime, timezone

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String

from database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime
    last_login: datetime

    class Config:
        from_attributes = True
