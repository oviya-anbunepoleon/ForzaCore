from pydantic import BaseModel
from typing import Optional

class Assessment(BaseModel):
    user_id: str
    psychometric_score: Optional[float] = None
    communication_score: Optional[float] = None
    coding_score: Optional[float] = None
    career_index_score: Optional[float] = None
    career_recommendation: Optional[str] = None