def generate_ai_report(
    role,
    analytical,
    creative,
    communication,
    coding,
    problem_solving
):

<<<<<<< HEAD
    return f"""
    🚀 Career Intelligence Report
=======
# 🔥 Paste your OpenRouter key directly for stability
API_KEY = ""
>>>>>>> c36ae46ead5c2e0151b3f8f8b9318229590f2766

    Role: {role}

    🔥 Strengths:
    - Analytical: {analytical}
    - Creative: {creative}
    - Communication: {communication}
    - Coding: {coding}
    - Problem Solving: {problem_solving}

    📈 6 Month Roadmap:
    Month 1-2: Strengthen core fundamentals
    Month 3-4: Build 2 real-world projects
    Month 5: Learn deployment & optimization
    Month 6: Build portfolio & apply to internships

    🛠 Recommended Tools:
    - Python
    - Git & GitHub
    - FastAPI
    - SQL / MongoDB
    - Docker

    💡 Suggested Projects:
    - AI Resume Analyzer
    - Real-time Chat Application
    - Data Dashboard



=======
Keep it structured, clear, and motivating.
"""

        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        print("AI ERROR:", e)
        return "AI service temporarily unavailable."
