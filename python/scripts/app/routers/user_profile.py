from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import jwt

DATABASE_URL = "postgresql://autogen:autopass@172.27.58.112:9001/autodb"

# Database setup
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Schemas
class UserProfileUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]

class UserProfileResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: str
    created_at: str
    updated_at: str

class MessageResponse(BaseModel):
    message: str

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication dependency
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# Router
router = APIRouter()

@router.put("/api/users/profile", response_model=MessageResponse)
def update_user_profile(profile: UserProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if profile.first_name:
        current_user.first_name = profile.first_name
    if profile.last_name:
        current_user.last_name = profile.last_name
    if profile.email:
        current_user.email = profile.email
    db.commit()
    db.refresh(current_user)
    return {"message": "Profile updated successfully"}

@router.get("/api/users/profile", response_model=UserProfileResponse)
def get_user_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat(),
        "updated_at": current_user.updated_at.isoformat()
    }