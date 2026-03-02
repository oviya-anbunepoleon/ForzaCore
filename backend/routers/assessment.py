from fastapi import APIRouter
from backend.database.storage import assessments_db
from backend.models.assessment import Assessment

router = APIRouter()


# ----------------------------
# Psychometric Submission
# ----------------------------
@router.post("/submit-psychometric")
def submit_psychometric(user_id: str, score: float):

    if user_id not in assessments_db:
        assessments_db[user_id] = Assessment(user_id=user_id)

    user = assessments_db[user_id]
    user.psychometric_score = score

    check_and_calculate(user)

    return {"message": "Psychometric score saved"}


# ----------------------------
# Communication Submission
# ----------------------------
@router.post("/submit-communication")
def submit_communication(user_id: str, score: float):

    if user_id not in assessments_db:
        assessments_db[user_id] = Assessment(user_id=user_id)

    user = assessments_db[user_id]
    user.communication_score = score

    check_and_calculate(user)

    return {"message": "Communication score saved"}


# ----------------------------
# Coding Submission
# ----------------------------
@router.post("/submit-coding")
def submit_coding(user_id: str, score: float):

    if user_id not in assessments_db:
        assessments_db[user_id] = Assessment(user_id=user_id)

    user = assessments_db[user_id]
    user.coding_score = score

    check_and_calculate(user)

    return {"message": "Coding score saved"}


# ----------------------------
# Career Index Engine
# ----------------------------
def check_and_calculate(user):

    if (
        user.psychometric_score is not None and
        user.communication_score is not None and
        user.coding_score is not None
    ):

        final_score = (
            user.psychometric_score * 0.4 +
            user.communication_score * 0.2 +
            user.coding_score * 0.4
        )

        user.career_index_score = final_score

        if final_score > 80:
            user.career_recommendation = "AI & Data Science"
        elif final_score > 65:
            user.career_recommendation = "Software Engineering"
        else:
            user.career_recommendation = "General Technology Path"


# ----------------------------
# Final Dashboard API
# ----------------------------
@router.get("/final-dashboard/{user_id}")
def get_final_dashboard(user_id: str):

    if user_id not in assessments_db:
        return {"error": "User not found"}

    return assessments_db[user_id]