from fastapi import FastAPI
from auth import router as auth_router
from tasks import router as tasks_router
from categories import router as categories_router
from database import engine, Base

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include the authentication, tasks, and categories routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(categories_router)