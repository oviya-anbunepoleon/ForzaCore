from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.database.db import Base

class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    role = Column(String)
    confidence = Column(Integer)
    xp = Column(Integer, default=0)
    completed_levels = Column(Integer, default=0)
    career_readiness = Column(Integer, default=0)

    user = relationship("User")