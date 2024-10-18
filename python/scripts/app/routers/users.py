from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from database import SessionLocal, engine, Base
from models import User
from auth import get_current_user

# Database URL
DATABASE_URL = "postgresql://autogen:autopass@172.27.58.112:9001/autodb"

# FastAPI router
router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserProfileResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

class Message(BaseModel):
    message: str

# Routes
@router.put("/api/users/profile", response_model=Message)
def update_profile(profile: UserProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if profile.email and db.query(User).filter(User.email == profile.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    for key, value in profile.dict(exclude_unset=True).items():
        setattr(current_user, key, value)
    db.commit()
    return {"message": "Profile updated successfully"}

@router.get("/api/users/profile", response_model=UserProfileResponse)
def get_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }

@router.post("/api/auth/logout", response_model=Message)
def logout(current_user: User = Depends(get_current_user)):
    # Invalidate the JWT token (implementation depends on your JWT setup)
    return {"message": "Logged out successfully"}