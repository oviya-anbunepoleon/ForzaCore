from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from .db import Base


# -----------------------
# USER TABLE
# -----------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    total_score = Column(Integer, default=0)


# -----------------------
# CODING PROBLEM TABLE
# -----------------------

class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    difficulty = Column(String)
    score = Column(Integer)


# -----------------------
# CODING SUBMISSION TABLE
# -----------------------

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    problem_id = Column(Integer, ForeignKey("problems.id"))


# -----------------------
# PSYCHOMETRIC RESPONSES TABLE
# -----------------------

class PsychometricResponse(Base):
    __tablename__ = "psychometric_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer)
    trait = Column(String)
    score = Column(Float)