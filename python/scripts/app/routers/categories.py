from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime
from database import SessionLocal, engine, Base
from models import Category, User
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
class CategoryCreate(BaseModel):
    name: str

class CategoryUpdate(BaseModel):
    name: str

class CategoryResponse(BaseModel):
    category_id: int
    name: str
    created_at: datetime
    updated_at: datetime

class Message(BaseModel):
    message: str

# Routes
@router.get("/api/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    categories = db.query(Category).filter(Category.user_id == current_user.id).all()
    return categories

@router.post("/api/categories", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_category = Category(name=category.name, user_id=current_user.id)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.put("/api/categories/{category_id}", response_model=Message)
def update_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_category = db.query(Category).filter(Category.id == category_id, Category.user_id == current_user.id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db_category.name = category.name
    db.commit()
    return {"message": "Category updated successfully"}

@router.delete("/api/categories/{category_id}", response_model=Message)
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_category = db.query(Category).filter(Category.id == category_id, Category.user_id == current_user.id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}