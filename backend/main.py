from fastapi import FastAPI
from backend.database.db import engine, Base

# Import models so tables get created
from backend.database import models  

# Import routers
from backend.routers import problem
from backend.routers import psychometric

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CareerForge AI API")

# Include routers
app.include_router(problem.router)
app.include_router(psychometric.router)


@app.get("/")
def root():
    return {"message": "CareerForge AI Backend Running 🚀"}