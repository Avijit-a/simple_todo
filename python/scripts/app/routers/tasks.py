from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import SessionLocal, engine, Base
from models import Task, User
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
class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str
    category_id: int
    due_date: datetime

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category_id: Optional[int] = None
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = None

class TaskResponse(BaseModel):
    task_id: int
    title: str
    description: str
    priority: str
    category_id: int
    due_date: datetime
    is_completed: bool
    created_at: datetime
    updated_at: datetime

class Message(BaseModel):
    message: str

# Routes
@router.get("/api/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks

@router.post("/api/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        category_id=task.category_id,
        due_date=task.due_date,
        user_id=current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.put("/api/tasks/{task_id}", response_model=Message)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task.dict(exclude_unset=True).items():
        setattr(db_task, key, value)
    db.commit()
    return {"message": "Task updated successfully"}

@router.delete("/api/tasks/{task_id}", response_model=Message)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}

@router.get("/api/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.post("/api/tasks/{task_id}/complete", response_model=Message)
def complete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.is_completed = True
    db.commit()
    return {"message": "Task marked as completed"}

@router.get("/api/tasks/completed", response_model=List[TaskResponse])
def get_completed_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.user_id == current_user.id, Task.is_completed == True).all()
    return tasks

@router.get("/api/tasks/pending", response_model=List[TaskResponse])
def get_pending_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.user_id == current_user.id, Task.is_completed == False).all()
    return tasks

@router.get("/api/tasks/overdue", response_model=List[TaskResponse])
def get_overdue_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.user_id == current_user.id, Task.due_date < datetime.utcnow(), Task.is_completed == False).all()
    return tasks

@router.get("/api/tasks/upcoming", response_model=List[TaskResponse])
def get_upcoming_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.user_id == current_user.id, Task.due_date >= datetime.utcnow(), Task.is_completed == False).all()
    return tasks

@router.get("/api/tasks/category/{category_id}", response_model=List[TaskResponse])
def get_tasks_by_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.user_id == current_user.id, Task.category_id == category_id).all()
    return tasks

@router.get("/api/tasks/priority/{priority}", response_model=List[TaskResponse])
def get_tasks_by_priority(priority: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.user_id == current_user.id, Task.priority == priority).all()
    return tasks

@router.get("/api/tasks/search/{query}", response_model=List[TaskResponse])
def search_tasks(query: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.user_id == current_user.id, Task.title.contains(query)).all()
    return tasks

@router.post("/api/tasks/{task_id}/reminder", response_model=Message)
def set_task_reminder(task_id: int, reminder: TaskReminder, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.reminder_date = reminder.reminder_date
    db_task.reminder_time = reminder.reminder_time
    db.commit()
    return {"message": "Reminder set successfully"}

@router.delete("/api/tasks/{task_id}/reminder", response_model=Message)
def delete_task_reminder(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.reminder_date = None
    db_task.reminder_time = None
    db.commit()
    return {"message": "Reminder deleted successfully"}

@router.get("/api/tasks/{task_id}/reminder", response_model=TaskReminder)
def get_task_reminder(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"reminder_date": db_task.reminder_date, "reminder_time": db_task.reminder_time}