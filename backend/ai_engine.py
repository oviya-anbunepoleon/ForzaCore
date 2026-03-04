import os
from langchain_openai import ChatOpenAI


def generate_ai_report(
    role,
    analytical,
    creative,
    communication,
    coding,
    problem_solving
):
    try:

        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7
        )

        prompt = f"""
Career Intelligence Report

Role: {role}

Strengths:
Analytical: {analytical}
Creative: {creative}
Communication: {communication}
Coding: {coding}
Problem Solving: {problem_solving}

6 Month Roadmap
Month 1-2: Strengthen core fundamentals
Month 3-4: Build 2 real-world projects
Month 5: Learn deployment & optimization
Month 6: Build portfolio & apply to internships

Recommended Tools
Python
Git & GitHub
FastAPI
SQL / MongoDB
Docker

Suggested Projects
AI Resume Analyzer
Real-time Chat Application
Data Dashboard

Keep it structured, clear, and motivating.
"""

        response = llm.invoke(prompt)

        return response.content

    except Exception as e:
        print("AI ERROR:", e)
        return "AI service temporarily unavailable."