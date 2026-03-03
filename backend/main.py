from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from starlette.middleware.sessions import SessionMiddleware

from backend.ai_engine import generate_ai_report

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from langchain_openai import ChatOpenAI

# =====================================================
# AI SETUP (HARDCODED FOR HACKATHON STABILITY)
# =====================================================




# =====================================================
# APP INIT
# =====================================================

app = FastAPI(title="CareerForge AI - AI Powered")
app.add_middleware(SessionMiddleware, secret_key="careerforge_secret")

templates = Jinja2Templates(directory="backend/templates")

leaderboard_data = []

# =====================================================
# HOME
# =====================================================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# =====================================================
# LOGIN
# =====================================================

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    request.session.clear()
    request.session["username"] = username
    request.session["level_xp"] = 0
    request.session["codelab_xp"] = 0
    request.session["coding_score"] = 0
    request.session["speak_xp"] = 0

    existing = next((u for u in leaderboard_data if u["username"] == username), None)
    if not existing:
        leaderboard_data.append({
            "username": username,
            "level_xp": 0,
            "codelab_xp": 0,
            "speak_xp": 0
        })

    return RedirectResponse("/dashboard", status_code=303)

# =====================================================
# DASHBOARD
# =====================================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    if "username" not in request.session:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": request.session.get("username"),
        "role": request.session.get("role", "Not Assigned"),
        "xp": request.session.get("level_xp", 0),
        "codelab_xp": request.session.get("codelab_xp", 0),
        "speak_xp": request.session.get("speak_xp", 0)
    })

# =====================================================
# SPEAKLAB
# =====================================================

@app.get("/speaklab", response_class=HTMLResponse)
def speaklab_page(request: Request):
    return templates.TemplateResponse("speaklab.html", {"request": request})


@app.post("/speaklab-submit")
def speaklab_submit(request: Request,
                    transcript: str = Form(...),
                    duration: int = Form(...)):

    word_count = len(transcript.split())
    xp = min(word_count // 5 + duration // 10, 50)

    # Safe session update
    current_xp = request.session.get("speak_xp", 0)
    request.session["speak_xp"] = current_xp + xp

    feedback = (
        f"You spoke {word_count} words in {duration} seconds. "
        f"Earned {xp} XP!"
    )

    return templates.TemplateResponse("speaklab.html", {
        "request": request,
        "feedback": feedback
    })

# =====================================================
# CODELAB
# =====================================================

codelab_questions = {
    "easy": [
        {"id": 1, "question": "Reverse a String (Without built-in reverse)."},
        {"id": 2, "question": "Check if a number is Prime."}
    ],
    "medium": [
        {"id": 3, "question": "Two Sum – Return indices that add to target."},
        {"id": 4, "question": "Longest Substring Without Repeating Characters."}
    ],
    "hard": [
        {"id": 5, "question": "Merge K Sorted Linked Lists."},
        {"id": 6, "question": "Detect Cycle in Linked List (Floyd’s Algorithm)."}
    ]
}


@app.get("/codelab", response_class=HTMLResponse)
def codelab_page(request: Request):
    return templates.TemplateResponse("codelab.html", {
        "request": request,
        "questions": codelab_questions
    })


@app.post("/codelab-submit")
def codelab_submit(request: Request,
                   difficulty: str = Form(...),
                   question_id: int = Form(...),
                   code_answer: str = Form(...)):

    xp_map = {"easy": 20, "medium": 40, "hard": 60}

    if len(code_answer.strip()) < 20:
        earned_xp = 0
        feedback = "Solution too short."
    else:
        earned_xp = xp_map.get(difficulty, 0)
        feedback = f"You earned {earned_xp} XP!"

    current_xp = request.session.get("codelab_xp", 0)
    request.session["codelab_xp"] = current_xp + earned_xp

    return templates.TemplateResponse("codelab.html", {
        "request": request,
        "questions": codelab_questions,
        "feedback": feedback
    })
# =====================================================
# ASSESSMENT
# =====================================================

@app.get("/assessment", response_class=HTMLResponse)
def assessment_page(request: Request):
    return templates.TemplateResponse("assessment.html", {"request": request})

@app.post("/assessment-submit")
def assessment_submit(request: Request,
    q1: str = Form(...), q2: str = Form(...), q3: str = Form(...),
    q4: str = Form(...), q5: str = Form(...), q6: str = Form(...),
    q7: str = Form(...), q8: str = Form(...), q9: str = Form(...)
):
    answers = [q1,q2,q3,q4,q5,q6,q7,q8,q9]
    request.session["analytical"] = answers.count("analytical")
    request.session["creative"] = answers.count("creative")
    return RedirectResponse("/communication", status_code=303)

# =====================================================
# COMMUNICATION
# =====================================================

@app.get("/communication", response_class=HTMLResponse)
def communication_page(request: Request):
    return templates.TemplateResponse("communication.html", {"request": request})

@app.post("/communication-result")
def communication_submit(request: Request,
                         text_answer: str = Form(...),
                         mcq_answer: int = Form(...)):

    score = len(text_answer)//40
    if mcq_answer == 1:
        score += 1

    request.session["communication_score"] = score
    return RedirectResponse("/coding", status_code=303)

# =====================================================
# CODING ROLE LOGIC
# =====================================================

@app.get("/coding", response_class=HTMLResponse)
def coding_page(request: Request):
    return templates.TemplateResponse("coding.html", {"request": request})

@app.post("/coding-result")
def coding_submit(request: Request,
                  text_answer: str = Form(...),
                  mcq_answer: int = Form(...)):

    score = len(text_answer)//40
    if mcq_answer == 1:
        score += 1

    request.session["coding_score"] = score

    analytical = request.session.get("analytical", 0)
    creative = request.session.get("creative", 0)
    comm = request.session.get("communication_score", 0)

    ai_score = analytical*3 + score*4
    fs_score = creative*3 + comm*4
    da_score = analytical*4 + comm*2

    scores = {
        "AI Engineer": ai_score,
        "Full Stack Developer": fs_score,
        "Data Analyst": da_score
    }

    best_role = max(scores, key=scores.get)
    total = ai_score + fs_score + da_score
    confidence = int((scores[best_role] / total) * 100) if total else 0

    request.session["role"] = best_role
    request.session["confidence"] = confidence
    request.session["level_xp"] = 0

    request.session.pop("ai_report", None)

    return RedirectResponse("/loading", status_code=303)

# =====================================================
# LOADING PAGE
# =====================================================

@app.get("/loading", response_class=HTMLResponse)
def loading_page(request: Request):
    return templates.TemplateResponse("loading.html", {"request": request})

# =====================================================
# ROLE RESULT (AI GENERATED)
# =====================================================

@app.get("/role-result", response_class=HTMLResponse)
def role_result(request: Request):

    role = request.session.get("role")
    confidence = request.session.get("confidence", 0)

    analytical = request.session.get("analytical", 0)
    creative = request.session.get("creative", 0)
    communication = request.session.get("communication_score", 0)
    coding = request.session.get("coding_score", 0)

    if "ai_report" not in request.session:
        ai_text = generate_ai_report(
            role, analytical, creative, communication, coding, confidence
        )
        request.session["ai_report"] = ai_text
    else:
        ai_text = request.session["ai_report"]

    return templates.TemplateResponse("role_result.html", {
        "request": request,
        "role": role,
        "confidence": confidence,
        "analytical": analytical,
        "creative": creative,
        "communication": communication,
        "coding": coding,
        "problem_solving": request.session.get("level_xp", 0),
        "ai_report": ai_text
    })

# =====================================================
# ROLE RESULT (AI POWERED)
# =====================================================

@app.get("/role-result", response_class=HTMLResponse)
def role_result(request: Request):

    role = request.session.get("role")
    confidence = request.session.get("confidence", 0)

    analytical = request.session.get("analytical", 0)
    creative = request.session.get("creative", 0)
    communication = request.session.get("communication_score", 0)
    coding = request.session.get("coding_score", 0)

    if "ai_report" not in request.session:
        ai_text = generate_ai_report(
            role, analytical, creative, communication, coding, confidence
        )
        request.session["ai_report"] = ai_text
    else:
        ai_text = request.session["ai_report"]

    return templates.TemplateResponse("role_result.html", {
        "request": request,
        "role": role,
        "confidence": confidence,
        "ai_report": ai_text
    })

# =====================================================
# (Remaining LEVEL, FINAL, LEADERBOARD, PDF
#  sections remain EXACTLY SAME as your original)
# =====================================================


# =====================================================
# LEVEL SYSTEM (3 × 5 × 2)
# =====================================================

role_levels = {
    "AI Engineer": {
        1: [
            {"question":"Which algorithm is used for classification?","options":["Logistic Regression","Linear Regression"],"answer":1},
            {"question":"Which library is used for ML?","options":["Scikit-learn","MS Paint"],"answer":1}
        ],
        2: [
            {"question":"Overfitting means?","options":["Model memorizes training data","Model improves automatically"],"answer":1},
            {"question":"Reduce overfitting?","options":["Regularization","Ignore validation"],"answer":1}
        ],
        3: [
            {"question":"Gradient Descent is used to?","options":["Minimize loss","Increase RAM"],"answer":1},
            {"question":"Accuracy measures?","options":["Correct predictions","Training time"],"answer":1}
        ],
        4: [
            {"question":"Confusion matrix shows?","options":["Prediction performance","Disk usage"],"answer":1},
            {"question":"Deployment tool?","options":["Docker","Excel"],"answer":1}
        ],
        5: [
            {"question":"Model accuracy drops in production. First step?","options":["Check data drift","Buy new laptop"],"answer":1},
            {"question":"Model fails on server. Best action?","options":["Check dependencies","Rewrite blindly"],"answer":1}
        ]
    },
    "Full Stack Developer": {
        1: [
            {"question":"Which runs in browser?","options":["JavaScript","C++"],"answer":1},
            {"question":"CSS is used for?","options":["Styling","Database"],"answer":1}
        ],
        2: [
            {"question":"REST API is used for?","options":["Client-server communication","Video editing"],"answer":1},
            {"question":"HTTP 404 means?","options":["Not Found","Success"],"answer":1}
        ],
        3: [
            {"question":"Relational DB?","options":["MySQL","MongoDB"],"answer":1},
            {"question":"Backend Python framework?","options":["FastAPI","Bootstrap"],"answer":1}
        ],
        4: [
            {"question":"JWT used for?","options":["Authentication","Animation"],"answer":1},
            {"question":"Improve performance?","options":["Caching","Heavy images"],"answer":1}
        ],
        5: [
            {"question":"Users report slow dashboard. First check?","options":["API response time","Ignore"],"answer":1},
            {"question":"Production server crashes. What to check?","options":["Logs and memory","Restart blindly"],"answer":1}
        ]
    },
    "Data Analyst": {
        1: [
            {"question":"SQL stands for?","options":["Structured Query Language","Simple Question List"],"answer":1},
            {"question":"Histogram shows?","options":["Distribution","Navigation bar"],"answer":1}
        ],
        2: [
            {"question":"Mean affected by?","options":["Outliers","Column names"],"answer":1},
            {"question":"GROUP BY used to?","options":["Aggregate data","Delete table"],"answer":1}
        ],
        3: [
            {"question":"Correlation measures?","options":["Relationship between variables","Color scheme"],"answer":1},
            {"question":"Pivot table used for?","options":["Summarization","Gaming"],"answer":1}
        ],
        4: [
            {"question":"ETL means?","options":["Extract Transform Load","Edit Transfer Loop"],"answer":1},
            {"question":"Best visualization tool?","options":["Tableau","Notepad"],"answer":1}
        ],
        5: [
            {"question":"Client wants insights from raw data. First step?","options":["Understand business problem","Build dashboard instantly"],"answer":1},
            {"question":"30% missing values. What do you do?","options":["Analyze missing pattern","Delete dataset"],"answer":1}
        ]
    }
}

@app.get("/level", response_class=HTMLResponse)
def level_page(request: Request, role: str, level: int):
    return templates.TemplateResponse("level.html", {
        "request": request,
        "role": role,
        "level": level,
        "questions": role_levels[role][level]
    })

@app.post("/level-submit")
def level_submit(request: Request,
                 role: str = Form(...),
                 level: int = Form(...),
                 q1: int = Form(...),
                 q2: int = Form(...)):

    questions = role_levels[role][level]
    score = (q1 == questions[0]["answer"]) + (q2 == questions[1]["answer"])
    request.session["level_xp"] += score * 20

    for user in leaderboard_data:
        if user["username"] == request.session.get("username"):
            user["level_xp"] = request.session.get("level_xp")

    if level < 5:
        return RedirectResponse(f"/level?role={role}&level={level+1}", status_code=303)
    else:
        return RedirectResponse("/final", status_code=303)


# =====================================================
# FINAL
# =====================================================

@app.get("/final", response_class=HTMLResponse)
def final_page(request: Request):

    xp = request.session.get("level_xp", 0)

    if xp >= 160:
        badge = "Expert 🏆"
    elif xp >= 100:
        badge = "Advanced ⭐"
    elif xp >= 40:
        badge = "Intermediate 🔥"
    else:
        badge = "Beginner 🌱"

    return templates.TemplateResponse("final.html", {
        "request": request,
        "role": request.session.get("role"),
        "xp": xp,
        "badge": badge,
        "confidence": request.session.get("confidence", 0)
    })


# =====================================================
# LEADERBOARD
# =====================================================

@app.get("/leaderboard", response_class=HTMLResponse)
def leaderboard_page(request: Request):

    sorted_users = sorted(
        leaderboard_data,
        key=lambda x: (
            x.get("level_xp", 0) +
            x.get("codelab_xp", 0) +
            x.get("speak_xp", 0)
        ),
        reverse=True
    )

    current_username = request.session.get("username")
    current_rank = None

    for index, user in enumerate(sorted_users):
        user["total_xp"] = (
            user.get("level_xp", 0) +
            user.get("codelab_xp", 0) +
            user.get("speak_xp", 0)
        )
        user["rank"] = index + 1

        if user["username"] == current_username:
            current_rank = user["rank"]

    return templates.TemplateResponse("leaderboard.html", {
        "request": request,
        "users": sorted_users,
        "current_user": current_username,
        "current_rank": current_rank
    })


# =====================================================
# PDF
# =====================================================

@app.get("/download")
def download_pdf(request: Request):

    filename = "CareerForge_Report.pdf"
    doc = SimpleDocTemplate(filename)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("CareerForge AI Report", styles["Heading1"]))
    elements.append(Spacer(1, 0.4 * inch))
    elements.append(Paragraph(f"Name: {request.session.get('username','User')}", styles["Normal"]))
    elements.append(Paragraph(f"Role: {request.session.get('role','Not Assigned')}", styles["Normal"]))
    elements.append(Paragraph(f"XP: {request.session.get('level_xp',0)}", styles["Normal"]))
    elements.append(Paragraph(f"Confidence: {request.session.get('confidence',0)}%", styles["Normal"]))

    doc.build(elements)

    return FileResponse(filename, media_type="application/pdf", filename=filename)