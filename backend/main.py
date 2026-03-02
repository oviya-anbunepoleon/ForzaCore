from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from starlette.middleware.sessions import SessionMiddleware

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


app = FastAPI(title="CareerForge AI - Final Stable")
app.add_middleware(SessionMiddleware, secret_key="careerforge_secret")

templates = Jinja2Templates(directory="backend/templates")

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
    request.session["codelab_xp"] = 0  # Initialize safely
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
        "codelab_xp": request.session.get("codelab_xp", 0)
    })


# =====================================================
# CODELAB (Interview Style + Safe XP)
# =====================================================

codelab_questions = {
    "easy": [
        {"id": 1, "question": "Reverse a String (Without built-in reverse).", "example": "Input: 'hello' → Output: 'olleh'"},
        {"id": 2, "question": "Check if a number is Prime.", "example": "Input: 7 → Output: True"}
    ],
    "medium": [
        {"id": 3, "question": "Two Sum – Return indices that add to target.", "example": "Input: [2,7,11,15], target=9 → Output: [0,1]"},
        {"id": 4, "question": "Longest Substring Without Repeating Characters.", "example": "Input: 'abcabcbb' → Output: 3"}
    ],
    "hard": [
        {"id": 5, "question": "Merge K Sorted Linked Lists.", "example": "Input: [[1,4,5],[1,3,4],[2,6]] → Output: [1,1,2,3,4,4,5,6]"},
        {"id": 6, "question": "Detect Cycle in Linked List (Floyd’s Algorithm).", "example": "Return True if cycle exists."}
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

    # Ensure session key exists
    if "codelab_xp" not in request.session:
        request.session["codelab_xp"] = 0

    if len(code_answer.strip()) < 20:
        feedback = "Your solution is too short. Try adding complete logic."
        earned_xp = 0
    else:
        earned_xp = xp_map.get(difficulty, 0)
        feedback = f"Good attempt! You earned {earned_xp} XP."

    request.session["codelab_xp"] += earned_xp

    return templates.TemplateResponse("codelab.html", {
        "request": request,
        "questions": codelab_questions,
        "feedback": feedback
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

    if word_count > 120:
        feedback = "🔥 Outstanding fluency and structured explanation!"
    elif word_count > 70:
        feedback = "👏 Good communication. Improve confidence slightly."
    elif word_count > 30:
        feedback = "🙂 Decent attempt. Try adding more depth and structure."
    else:
        feedback = "⚠ Speak longer and organize your thoughts clearly."

    return templates.TemplateResponse("speaklab.html", {
        "request": request,
        "feedback": feedback
    })
# =====================================================
# PSYCHOMETRIC
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
# CODING
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
    confidence = int((scores[best_role] / total) * 100) if total != 0 else 0

    request.session["role"] = best_role
    request.session["confidence"] = confidence
    request.session["level_xp"] = 0

    return RedirectResponse("/loading", status_code=303)


# =====================================================
# LOADING
# =====================================================

@app.get("/loading", response_class=HTMLResponse)
def loading_page(request: Request):
    return templates.TemplateResponse("loading.html", {"request": request})


# =====================================================
# ROLE RESULT
# =====================================================


@app.get("/role-result", response_class=HTMLResponse)
def role_result(request: Request):

    role = request.session.get("role")

    explanations = {
        "AI Engineer": "You show strong analytical and ML problem-solving potential.",
        "Full Stack Developer": "You balance frontend creativity and backend logic.",
        "Data Analyst": "You demonstrate structured and data-driven reasoning ability."
    }

    focus = {
        "AI Engineer": "Machine Learning, Model Deployment, Data Structures",
        "Full Stack Developer": "Backend APIs, Databases, Performance Optimization",
        "Data Analyst": "SQL, Data Visualization, Business Insights"
    }

    return templates.TemplateResponse("role_result.html", {
        "request": request,
        "role": role,
        "why": explanations.get(role),
        "focus": focus.get(role),
        "confidence": request.session.get("confidence", 0),

        # 👇 ADD THESE
        "analytical": request.session.get("analytical", 0),
        "creative": request.session.get("creative", 0),
        "communication": request.session.get("communication_score", 0),
        "coding": request.session.get("coding_score", 0),
        "problem_solving": request.session.get("level_xp", 0)
    })



# =====================================================
# LEVEL SYSTEM (3 Roles × 5 Levels × 2 Questions)
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