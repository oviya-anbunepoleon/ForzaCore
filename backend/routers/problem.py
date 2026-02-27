from fastapi import APIRouter
from pydantic import BaseModel
from core.scoring import calculate_score

router = APIRouter(
    prefix="/problems",
    tags=["Problems"]
)

# Temporary in-memory storage
problems_db = []
users_db = []


# -----------------------
# MODELS
# -----------------------

class Problem(BaseModel):
    title: str
    description: str
    difficulty: str


class User(BaseModel):
    username: str


class Submission(BaseModel):
    username: str
    problem_title: str


# -----------------------
# PROBLEM ENDPOINTS
# -----------------------

@router.post("/")
def create_problem(problem: Problem):
    score = calculate_score(problem.difficulty)

    problem_data = problem.dict()
    problem_data["score"] = score

    problems_db.append(problem_data)

    return {
        "message": "Problem added successfully",
        "score": score
    }


@router.get("/")
def get_problems():
    return problems_db


# -----------------------
# USER ENDPOINTS
# -----------------------

@router.post("/users")
def create_user(user: User):
    user_data = {
        "username": user.username,
        "total_score": 0
    }

    users_db.append(user_data)

    return {"message": "User created successfully"}


# -----------------------
# SUBMISSION ENDPOINT
# -----------------------

@router.post("/submit")
def submit_problem(submission: Submission):

    # Find user
    user = next((u for u in users_db if u["username"] == submission.username), None)

    if not user:
        return {"error": "User not found"}

    # Find problem
    problem = next((p for p in problems_db if p["title"] == submission.problem_title), None)

    if not problem:
        return {"error": "Problem not found"}

    # Add score
    user["total_score"] += problem["score"]

    return {
        "message": "Submission successful",
        "earned_score": problem["score"],
        "total_score": user["total_score"]
    }


# -----------------------
# LEADERBOARD
# -----------------------

@router.get("/leaderboard")
def get_leaderboard():
    sorted_users = sorted(users_db, key=lambda x: x["total_score"], reverse=True)
    return sorted_users