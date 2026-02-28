from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.core.scoring import calculate_score
from backend.database.db import get_db
from backend.database import models

router = APIRouter(
    prefix="/problems",
    tags=["Problems"]
)


# -----------------------
# Pydantic Schemas
# -----------------------

class ProblemCreate(BaseModel):
    title: str
    description: str
    difficulty: str


class UserCreate(BaseModel):
    username: str


class SubmissionCreate(BaseModel):
    username: str
    problem_title: str


# -----------------------
# Create Problem
# -----------------------

@router.post("/")
def create_problem(problem: ProblemCreate, db: Session = Depends(get_db)):
    score = calculate_score(problem.difficulty)

    db_problem = models.Problem(
        title=problem.title,
        description=problem.description,
        difficulty=problem.difficulty,
        score=score
    )

    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)

    return {
        "message": "Problem added successfully",
        "score": score
    }


# -----------------------
# Get All Problems
# -----------------------

@router.get("/")
def get_problems(db: Session = Depends(get_db)):
    return db.query(models.Problem).all()


# -----------------------
# Create User
# -----------------------

@router.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing_user:
        return {"error": "Username already exists"}

    db_user = models.User(
        username=user.username,
        total_score=0
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "User created successfully"}


# -----------------------
# Submit Problem
# -----------------------

@router.post("/submit")
def submit_problem(submission: SubmissionCreate, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        models.User.username == submission.username
    ).first()

    if not user:
        return {"error": "User not found"}

    problem = db.query(models.Problem).filter(
        models.Problem.title == submission.problem_title
    ).first()

    if not problem:
        return {"error": "Problem not found"}

    # 🔥 Prevent duplicate submission
    existing_submission = db.query(models.Submission).filter(
        models.Submission.user_id == user.id,
        models.Submission.problem_id == problem.id
    ).first()

    if existing_submission:
        return {"error": "Problem already submitted"}

    # Save submission
    new_submission = models.Submission(
        user_id=user.id,
        problem_id=problem.id
    )

    db.add(new_submission)

    # Add score
    user.total_score += problem.score
    db.commit()

    return {
        "message": "Submission successful",
        "earned_score": problem.score,
        "total_score": user.total_score
    }


# -----------------------
# Leaderboard
# -----------------------

@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(get_db)):

    users = db.query(models.User).order_by(
        models.User.total_score.desc()
    ).all()

    return users