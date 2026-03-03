from langchain_openai import ChatOpenAI

# 🔥 Paste your OpenRouter key directly for stability
API_KEY = "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"

llm = ChatOpenAI(
    model="openai/gpt-4o-mini",   # stable model
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1",
    temperature=0.4
)

def generate_ai_report(role, analytical, creative, communication, coding, confidence):
    try:
        prompt = f"""
You are a professional AI Career Mentor.

Student Profile:
Role: {role}
Analytical Score: {analytical}
Creative Score: {creative}
Communication Score: {communication}
Coding Score: {coding}
Confidence: {confidence}%

Generate structured output with:

1. Why this role suits them
2. Strength analysis
3. Areas to focus
4. 6-month roadmap (month-wise)
5. Recommended tools & technologies
6. 3 strong project ideas

Keep it structured, clear, and motivating.
"""

        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        print("AI ERROR:", e)
        return "AI service temporarily unavailable."