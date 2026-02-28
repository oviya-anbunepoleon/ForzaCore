from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database.db import get_db
from backend.database import models
from backend.core.psychometric_questions import psychometric_questions

router = APIRouter(
    prefix="/psychometric",
    tags=["Psychometric"]
)


class Answer(BaseModel):
    user_id: int
    question_id: int
    score: float


@router.get("/questions")
def get_questions():
    return psychometric_questions


@router.post("/submit")
def submit_answer(answer: Answer, db: Session = Depends(get_db)):

    question = next(
        (q for q in psychometric_questions if q["id"] == answer.question_id),
        None
    )

    if not question:
        return {"error": "Invalid question"}

    response = models.PsychometricResponse(
        user_id=answer.user_id,
        question_id=answer.question_id,
        trait=question["trait"],
        score=answer.score
    )

    db.add(response)
    db.commit()

    return {"message": "Answer stored successfully"}


@router.get("/result/{user_id}")
def calculate_result(user_id: int, db: Session = Depends(get_db)):

    responses = db.query(models.PsychometricResponse).filter(
        models.PsychometricResponse.user_id == user_id
    ).all()

    trait_scores = {}
    trait_counts = {}

    for r in responses:
        trait_scores[r.trait] = trait_scores.get(r.trait, 0) + r.score
        trait_counts[r.trait] = trait_counts.get(r.trait, 0) + 1

    trait_percentages = {}

    for trait in trait_scores:
        max_score = trait_counts[trait] * 5
        trait_percentages[trait] = round((trait_scores[trait] / max_score) * 100, 2)

    return {
        "raw_scores": trait_scores,
        "percentages": trait_percentages
    }