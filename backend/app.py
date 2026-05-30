from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from datetime import datetime, timedelta
import pandas as pd
import threading
import secrets
import os
from pathlib import Path

from model_pipeline import (
    extract_text_from_pdf,
    extract_keywords_from_text,
    find_similar_jobs,
    recommend_courses,
    build_job_index
)

# Import new modules
from competency_quiz import CompetencyQuiz
from skill_gap_analyzer import SkillGapAnalyzer
from learning_pathways import LearningPathways
from resume_wizard import ResumeWizard
from market_insights import MarketInsights
from community_forum import CommunityForum
from certification_system import CertificationSystem

# ---------------- APP SETUP ---------------- #
app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:5177",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "http://127.0.0.1:5177",

        "https://smart-competency-diagnostic-and-can-pi.vercel.app"
    ]}},
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Authorization"]
)
bcrypt = Bcrypt(app)

app.config["JWT_SECRET_KEY"] = "fixed-secret-key-for-development"  # Fixed for development
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
jwt = JWTManager(app)

# JWT error handlers return JSON so frontend can handle auth failures cleanly
@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({"error": "Missing Authorization Header"}), 401

@jwt.invalid_token_loader
def invalid_token_response(callback):
    return jsonify({"error": "Invalid token"}), 401

@jwt.expired_token_loader
def expired_token_response(jwt_header, jwt_payload):
    return jsonify({"error": "Token has expired"}), 401

def get_current_user_id():
    identity = get_jwt_identity()
    return int(identity)

# ---------------- DATABASE ---------------- #
try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root"),
        database=os.getenv("DB_NAME", "db11"),
        charset="utf8",
        collation="utf8_general_ci"
    )

    # Alias for compatibility
    db = conn
    cursor = conn.cursor(dictionary=True)

except Exception as e:
    # Fail-open: if DB is not reachable at import time (common during deploy),
    # create lightweight dummy objects so the app can start and return
    # graceful errors from endpoints instead of crashing Gunicorn.
    print("Warning: could not connect to MySQL at startup:", e)

    class _DummyCursor:
        def execute(self, *args, **kwargs):
            return None

        def fetchone(self):
            return None

        def fetchall(self):
            return []

        def close(self):
            return None

    class _DummyConn:
        def cursor(self, *args, **kwargs):
            return _DummyCursor()

        def commit(self):
            return None

        def rollback(self):
            return None

        def close(self):
            return None

    conn = None
    db = _DummyConn()
    cursor = db.cursor()

# Memory-optimized: No FAISS or sentence-transformers
# Using lightweight TF-IDF for job matching instead
BASE_DIR = Path(__file__).resolve().parent
JOB_DF = None
COURSES_DF = None

JOB_VECTORIZER = None  # TF-IDF vectorizer instead of FAISS index
JOB_TFIDF_MATRIX = None  # Sparse matrix instead of dense embeddings

MODEL_READY = False
MODEL_ERROR = None

MODEL_PROGRESS = {
    "loaded": 0,
    "total": 100
}

# Initialize new modules
COMPETENCY_QUIZ = CompetencyQuiz()
SKILL_ANALYZER = None  # Will be initialized after data loading
LEARNING_PATHWAYS = None  # Will be initialized after data loading
RESUME_WIZARD = ResumeWizard()
MARKET_INSIGHTS = None  # Will be initialized after data loading
COMMUNITY_FORUM = CommunityForum()
CERTIFICATION_SYSTEM = CertificationSystem()
LEARNING_PROGRESS = {}

def format_learning_pathway(pathway_id, pathway):
    modules = pathway.get("modules", [])
    steps = []

    for index, module in enumerate(modules):
        skills = ", ".join(module.get("skills", []))
        courses = module.get("courses", [])
        resources = []

        for course in courses:
            if isinstance(course, dict):
                title = course.get("title", "Course")
                resources.append({
                    "title": title,
                    "url": course.get("url") or f"https://www.coursera.org/search?query={title.replace(' ', '%20')}"
                })
            else:
                resources.append({
                    "title": course,
                    "url": f"https://www.coursera.org/search?query={course.replace(' ', '%20')}"
                })

        steps.append({
            "id": f"{pathway_id}-step-{index + 1}",
            "title": module.get("name", f"Step {index + 1}"),
            "description": f"Build skills in {skills}." if skills else "Complete this learning module.",
            "type": "Module",
            "duration": module.get("duration_label") or f"{module.get('duration', 1)} weeks",
            "resources": resources
        })

    duration_weeks = pathway.get("duration_weeks", 0)
    difficulty = pathway.get("difficulty") or "Beginner"
    if not pathway.get("difficulty"):
        if duration_weeks >= 24:
            difficulty = "Advanced"
        elif duration_weeks >= 20:
            difficulty = "Intermediate"

    return {
        "id": pathway_id,
        "title": pathway.get("name", pathway_id.replace("_", " ").title()),
        "description": pathway.get("description") or f"A structured {duration_weeks}-week path with {len(steps)} modules.",
        "difficulty": difficulty,
        "duration": pathway.get("duration_label") or f"{duration_weeks} weeks",
        "steps": steps
    }

def get_user_learning_progress(user_id):
    return LEARNING_PROGRESS.setdefault(user_id, {})

def ensure_market_insights():
    global JOB_DF, MARKET_INSIGHTS

    if MARKET_INSIGHTS is not None:
        return MARKET_INSIGHTS

    if JOB_DF is None:
        job_path = BASE_DIR / "data" / "job_title_des.csv"
        JOB_DF = pd.read_csv(job_path)
        JOB_DF.columns = [c.strip().lower() for c in JOB_DF.columns]

    MARKET_INSIGHTS = MarketInsights(job_df=JOB_DF)
    return MARKET_INSIGHTS

def ensure_skill_analyzer():
    global JOB_DF, SKILL_ANALYZER

    if SKILL_ANALYZER is not None:
        return SKILL_ANALYZER

    if JOB_DF is None:
        job_path = BASE_DIR / "data" / "job_title_des.csv"
        JOB_DF = pd.read_csv(job_path)
        JOB_DF.columns = [c.strip().lower() for c in JOB_DF.columns]

    SKILL_ANALYZER = SkillGapAnalyzer(job_df=JOB_DF)
    return SKILL_ANALYZER

def format_market_insights(insights):
    trending_jobs = []
    for index, job in enumerate(insights.get("trending_jobs", [])):
        trending_jobs.append({
            "title": job.get("title", "Job Role"),
            "company": job.get("company", "Multiple companies"),
            "location": job.get("location", insights.get("location", "Global")),
            "salary_range": job.get("salary_range", "60k - 140k"),
            "growth": job.get("growth", 0),
            "category": job.get("category", "Technology" if index % 2 == 0 else "Business")
        })

    salary_insights = []
    raw_salary = insights.get("salary_insights", {})
    if isinstance(raw_salary, dict):
        for role, salary in raw_salary.items():
            salary_insights.append({
                "role": role,
                "entry_level": f"{salary.get('entry', 0):,}",
                "mid_level": f"{salary.get('mid', 0):,}",
                "senior_level": f"{salary.get('senior', 0):,}",
                "demand": "High" if salary.get("growth", 0) >= 8 else "Medium"
            })
    else:
        salary_insights = raw_salary

    demand_skills = []
    for skill in insights.get("skill_demand", []):
        name = skill.get("skill", "Skill")
        demand_skills.append({
            "name": name,
            "description": f"Demand score: {skill.get('demand_score', 'N/A')}",
            "growth": f"{skill.get('growth', 0)}%",
        })

    industry_trends = []
    for industry in insights.get("industry_growth", []):
        name = industry.get("name", "Industry")
        growth = industry.get("growth_rate", 0)
        industry_trends.append({
            "title": f"{name} hiring is {industry.get('trend', 'Growing').lower()}",
            "description": f"{name} shows {growth}% projected growth with strong hiring activity.",
            "impact": "High" if growth >= 10 else "Medium" if growth >= 5 else "Low",
            "timeline": insights.get("timeframe", "month").title(),
            "industry": name
        })

    top_skills = [skill["name"] for skill in demand_skills[:3]]

    return {
        "trending_jobs": trending_jobs,
        "salary_insights": salary_insights,
        "demand_skills": demand_skills,
        "industry_trends": industry_trends,
        "personalized_recommendations": [
            {
                "title": "Focus on high-growth skills",
                "description": f"Prioritize {', '.join(top_skills) if top_skills else 'technical and communication skills'} to improve your market fit."
            },
            {
                "title": "Track roles with rising demand",
                "description": "Compare your profile against the trending roles and close the most visible skill gaps first."
            }
        ],
        "job_alerts": [
            job["title"]
            for job in trending_jobs[:5]
        ]
    }

def format_certification(certification):
    return {
        "id": certification.get("id"),
        "title": certification.get("name", certification.get("title", "Certification")),
        "description": certification.get("description", ""),
        "skills": certification.get("skills_tested", certification.get("skills", [])),
        "difficulty": certification.get("difficulty", "Beginner"),
        "duration": f"{certification.get('duration_minutes', 0)} minutes",
        "prerequisites": certification.get("prerequisites", "None"),
        "passing_score": certification.get("passing_score", 70),
        "eligible": certification.get("eligible", True),
        "user_has_cert": certification.get("user_has_cert", False)
    }

def format_user_certificate(certificate):
    return {
        "id": certificate.get("certification_id", certificate.get("id")),
        "certificate_id": certificate.get("id"),
        "title": certificate.get("certification_name", "Certification"),
        "description": f"Score: {round(certificate.get('score', 0), 1)}%",
        "earned_date": certificate.get("issued_at", datetime.now().isoformat()),
        "expires_at": certificate.get("expires_at"),
        "download_url": certificate.get("verification_url", "#")
    }

def score_certification_quiz(certification_id, answers, user_id):
    certification = CERTIFICATION_SYSTEM.certifications.get(certification_id)
    if not certification:
        raise ValueError(f"Certification {certification_id} not found")

    questions = CERTIFICATION_SYSTEM.get_assessment_questions(certification_id)[:10]
    if not questions:
        questions = CERTIFICATION_SYSTEM.get_certification_quiz(certification_id)

    score_map = {
        "Beginner": 25,
        "Intermediate": 50,
        "Advanced": 75,
        "Expert": 100
    }

    total = len(questions) or 1
    earned = 0
    details = []

    for question in questions:
        answer = answers.get(question["id"])
        correct_answer = question.get("correct_answer")

        if correct_answer is not None:
            passed_question = str(answer or "").strip() == str(correct_answer).strip()
            points = 100 if passed_question else 0
        else:
            points = score_map.get(answer, 0)
            passed_question = points >= 50

        earned += points
        details.append({
            "question": question["question"],
            "correct": passed_question
        })

    score = round(earned / total, 1)
    passed = score >= certification.get("passing_score", 70)

    result = {
        "score": score,
        "passed": passed,
        "passing_score": certification.get("passing_score", 70),
        "details": details
    }

    if passed:
        result["certificate"] = CERTIFICATION_SYSTEM.issue_certificate(
            user_id,
            certification_id,
            score
        )

    return result

# ---------------- LOAD DATA ---------------- #
def load_data():
    global JOB_DF, COURSES_DF, SKILL_ANALYZER, LEARNING_PATHWAYS, MARKET_INSIGHTS, CERTIFICATION_SYSTEM

    print("Loading datasets...")
    job_path = BASE_DIR / "data" / "job_title_des.csv"
    course_path = BASE_DIR / "data" / "Courses.csv"
    pathway_path = BASE_DIR / "data" / "Learning_Pathway_Index.csv"
    certification_path = BASE_DIR / "data" / "Placement_Interview_Quiz_Questions.csv"

    JOB_DF = pd.read_csv(job_path)
    JOB_DF.columns = [c.strip().lower() for c in JOB_DF.columns]

    COURSES_DF = pd.read_csv(course_path)
    COURSES_DF.columns = [c.strip().lower() for c in COURSES_DF.columns]

    PATHWAY_DF = pd.read_csv(pathway_path)
    PATHWAY_DF.columns = [c.strip().lower() for c in PATHWAY_DF.columns]

    CERTIFICATION_DF = pd.read_csv(certification_path)
    CERTIFICATION_DF.columns = [c.strip().lower() for c in CERTIFICATION_DF.columns]

    # Initialize dependent modules
    SKILL_ANALYZER = SkillGapAnalyzer(job_df=JOB_DF)
    LEARNING_PATHWAYS = LearningPathways(courses_df=PATHWAY_DF)
    MARKET_INSIGHTS = MarketInsights(job_df=JOB_DF)
    CERTIFICATION_SYSTEM = CertificationSystem(questions_df=CERTIFICATION_DF)

    print("Datasets loaded and modules initialized")

# ---------------- PROGRESS CALLBACK ---------------- #
def progress_callback(done, total):
    MODEL_PROGRESS["loaded"] = done
    MODEL_PROGRESS["total"] = total if total != 0 else 1

# Memory-optimized background loader (no FAISS/embeddings)
def background_load_pipeline():
    global JOB_VECTORIZER, JOB_TFIDF_MATRIX, MODEL_READY, MODEL_ERROR

    try:
        print("Building lightweight TF-IDF job index...")
        job_df = JOB_DF
        if job_df is None:
            raise RuntimeError("Job dataset not loaded")

        # Returns (vectorizer, tfidf_matrix, job_df) - all lightweight
        vectorizer, tfidf_matrix, job_df_indexed = build_job_index(
            job_df,
            cache_path=str(BASE_DIR / "data" / "job_embs.npy"),
            progress_callback=progress_callback
        )

        JOB_VECTORIZER = vectorizer
        JOB_TFIDF_MATRIX = tfidf_matrix

        MODEL_READY = True
        MODEL_PROGRESS["loaded"] = MODEL_PROGRESS["total"]

        print("✓ TF-IDF index built successfully (memory-efficient)")

    except Exception as e:
        MODEL_ERROR = str(e)
        MODEL_READY = False
        print("Error while building job index:", e)

def start_background_loading():
    thread = threading.Thread(
        target=background_load_pipeline,
        daemon=True
    )
    thread.start()

# ---------------- ROUTES ---------------- #
@app.route('/')
def home():
    return "Welcome!"

#  Register
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    hashed_pass = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_pass)
        )
        db.commit()

        return jsonify({"message": "User registered successfully!"}), 200

    except mysql.connector.Error as err:
        print(err)
        db.rollback()
        return jsonify({"error": "Email already exists or invalid data"}), 400

# 🔑 Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if bcrypt.check_password_hash(user['password'], password):
        access_token = create_access_token(identity=str(user['id']))

        return jsonify({
            "message": "Login successful!",
            "token": access_token,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        }), 200

    return jsonify({"error": "Invalid password"}), 401

# 👤 Profile
@app.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    try:
        user_id = get_current_user_id()

        if request.method == 'PUT':
            data = request.get_json() or {}
            name = (data.get("name") or "").strip()
            email = (data.get("email") or "").strip()
            current_password = data.get("current_password") or ""
            new_password = data.get("new_password") or ""

            if not name or not email:
                return jsonify({"error": "Name and email are required"}), 400

            cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
            existing_user = cursor.fetchone()

            if not existing_user:
                return jsonify({"error": "User not found"}), 404

            if new_password:
                if not current_password:
                    return jsonify({"error": "Current password is required"}), 400

                if not bcrypt.check_password_hash(existing_user["password"], current_password):
                    return jsonify({"error": "Current password is incorrect"}), 400

                hashed_pass = bcrypt.generate_password_hash(new_password).decode("utf-8")
                cursor.execute(
                    "UPDATE users SET name=%s, email=%s, password=%s WHERE id=%s",
                    (name, email, hashed_pass, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET name=%s, email=%s WHERE id=%s",
                    (name, email, user_id)
                )

            db.commit()

            return jsonify({
                "message": "Profile updated successfully",
                "user": {
                    "id": user_id,
                    "name": name,
                    "email": email
                }
            }), 200

        cursor.execute(
            "SELECT id, name, email FROM users WHERE id=%s",
            (user_id,)
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"user": user}), 200

    except mysql.connector.Error as err:
        db.rollback()
        print(err)
        return jsonify({"error": "Email already exists or invalid profile data"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#  Model Status
@app.route('/model_status', methods=['GET'])
def model_status():
    try:
        if MODEL_ERROR:
            return jsonify({
                "status": "error",
                "message": MODEL_ERROR
            })

        if MODEL_READY:
            return jsonify({
                "status": "ready",
                "progress": 100
            })

        total = MODEL_PROGRESS["total"] or 1
        progress = (MODEL_PROGRESS["loaded"] / total) * 100

        return jsonify({
            "status": "loading",
            "progress": round(progress, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Resume Analyzer
@app.route("/analyze_resume", methods=["POST"])
def analyze_resume():
    try:
        if MODEL_ERROR:
            return jsonify({
                "status": "error",
                "message": MODEL_ERROR
            }), 500

        if "resume" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        pdf = request.files["resume"]
        text = extract_text_from_pdf(pdf)

        if not text.strip():
            return jsonify({"error": "Empty resume"}), 400

        keywords = extract_keywords_from_text(text)
        if isinstance(keywords, list):
            keywords = [
                {"keyword": kw} if isinstance(kw, str) else kw
                for kw in keywords
            ]
        else:
            keywords = []

        course_recs = recommend_courses(keywords, COURSES_DF)

        if not MODEL_READY:
            return jsonify({
                "status": "loading",
                "keywords": keywords,
                "matched_jobs": [],
                "recommended_courses": course_recs,
                "message": "Model is still loading..."
            }), 200

        matched_jobs = find_similar_jobs(
            text, JOB_DF, JOB_VECTORIZER, JOB_TFIDF_MATRIX, topk=5
        )

        return jsonify({
            "status": "success",
            "keywords": keywords,
            "matched_jobs": matched_jobs,
            "recommended_courses": course_recs
        }), 200

    except Exception as e:
        print("ERROR:", e)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/search_jobs", methods=["POST"])
def search_jobs():
    try:
        if MODEL_ERROR:
            return jsonify({
                "status": "error",
                "message": MODEL_ERROR
            }), 500

        if not MODEL_READY:
            return jsonify({
                "status": "loading",
                "jobs": [],
                "message": "Model is still loading..."
            }), 200

        data = request.get_json() or {}
        query = data.get("query") or request.args.get("q")

        if not query or not query.strip():
            return jsonify({"error": "Search query is required"}), 400

        matched_jobs = find_similar_jobs(query, JOB_DF, JOB_VECTORIZER, JOB_TFIDF_MATRIX, topk=10)

        return jsonify({
            "status": "success",
            "jobs": matched_jobs
        }), 200

    except Exception as e:
        print("SEARCH ERROR:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------- COMPETENCY QUIZ ENDPOINTS ---------------- #

@app.route("/quiz/questions", methods=["GET"])
@jwt_required()
def get_quiz_questions():
    """Get competency quiz questions"""
    try:
        category = request.args.get('category')
        questions = COMPETENCY_QUIZ.get_questions_by_category(category)

        return jsonify({
            "status": "success",
            "questions": questions
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/quiz/submit", methods=["POST"])
@jwt_required()
def submit_quiz():
    """Submit quiz answers and get competency scores"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        responses = data.get('responses') or []
        if not responses and isinstance(data.get('answers'), dict):
            responses = [
                {"question_id": qid, "answer": ans}
                for qid, ans in data['answers'].items()
            ]

        scores = COMPETENCY_QUIZ.calculate_competency_score(responses)

        return jsonify({
            "status": "success",
            "scores": scores
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------- SKILL GAP ANALYSIS ENDPOINTS ---------------- #

@app.route("/skill-analysis/jobs", methods=["GET"])
@jwt_required()
def get_skill_analysis_jobs():
    """Get job titles from job_title_des.csv for skill gap analysis."""
    try:
        analyzer = ensure_skill_analyzer()
        limit = int(request.args.get("limit", 200))
        return jsonify({
            "status": "success",
            "jobs": analyzer.get_available_jobs(limit=limit)
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/skill-analysis/analyze", methods=["POST"])
@jwt_required()
def analyze_selected_job_skills():
    """Analyze skill gaps for a selected job title using job_title_des.csv."""
    try:
        data = request.get_json() or {}
        job_title = data.get("job_title") or data.get("target_job") or ""
        user_skills = data.get("user_skills", {})

        if not job_title:
            return jsonify({"error": "Job title is required"}), 400

        analyzer = ensure_skill_analyzer()
        return jsonify(analyzer.analyze_job_fit(job_title, user_skills)), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/skill-gap/analyze", methods=["POST"])
@jwt_required()
def analyze_skill_gaps():
    """Analyze skill gaps for a target job"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        user_skills = data.get('user_skills', {})
        target_job = data.get('target_job') or data.get('job_title', '')

        if not target_job:
            return jsonify({"error": "Target job is required"}), 400

        analyzer = ensure_skill_analyzer()
        gaps = analyzer.analyze_skill_gaps(user_skills, target_job)

        return jsonify({
            "status": "success",
            "skill_gaps": gaps
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/learning-path/generate", methods=["POST"])
@jwt_required()
def generate_learning_path():
    """Generate personalized learning pathway"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        user_profile = data.get('user_profile', {})
        skill_gaps = data.get('skill_gaps', [])
        target_role = data.get('target_role', '')

        pathway = LEARNING_PATHWAYS.create_personalized_pathway(
            user_profile, skill_gaps, target_role
        )

        return jsonify({
            "status": "success",
            "pathway": pathway
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/learning-pathways", methods=["GET"])
@jwt_required()
def get_learning_pathways():
    """Get all available learning pathways"""
    try:
        user_id = get_current_user_id()
        raw_pathways = LEARNING_PATHWAYS.get_all_pathways()
        pathways = [
            format_learning_pathway(pathway_id, pathway)
            for pathway_id, pathway in raw_pathways.items()
        ]

        return jsonify({
            "status": "success",
            "pathways": pathways,
            "progress": get_user_learning_progress(user_id)
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/learning-pathways/<pathway_id>/enroll", methods=["POST"])
@jwt_required()
def enroll_learning_pathway(pathway_id):
    """Enroll the current user in a learning pathway"""
    try:
        user_id = get_current_user_id()
        raw_pathways = LEARNING_PATHWAYS.get_all_pathways()

        if pathway_id not in raw_pathways:
            return jsonify({"error": "Learning pathway not found"}), 404

        progress = get_user_learning_progress(user_id)
        pathway_progress = progress.setdefault(pathway_id, {
            "enrolled": True,
            "completed": 0,
            "completed_steps": []
        })
        pathway_progress["enrolled"] = True

        return jsonify({
            "success": True,
            "progress": progress
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/learning-pathways/<pathway_id>/complete/<step_id>", methods=["POST"])
@jwt_required()
def complete_learning_pathway_step(pathway_id, step_id):
    """Mark a learning pathway step as complete"""
    try:
        user_id = get_current_user_id()
        raw_pathways = LEARNING_PATHWAYS.get_all_pathways()

        if pathway_id not in raw_pathways:
            return jsonify({"error": "Learning pathway not found"}), 404

        valid_step_ids = {
            f"{pathway_id}-step-{index + 1}"
            for index, _module in enumerate(raw_pathways[pathway_id].get("modules", []))
        }
        if step_id not in valid_step_ids:
            return jsonify({"error": "Learning pathway step not found"}), 404

        progress = get_user_learning_progress(user_id)
        pathway_progress = progress.setdefault(pathway_id, {
            "enrolled": True,
            "completed": 0,
            "completed_steps": []
        })
        pathway_progress["enrolled"] = True

        if step_id not in pathway_progress["completed_steps"]:
            pathway_progress["completed_steps"].append(step_id)

        pathway_progress["completed"] = len(pathway_progress["completed_steps"])

        return jsonify({
            "success": True,
            "progress": progress
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------- MARKET INSIGHTS ENDPOINTS ---------------- #

@app.route("/market-insights", methods=["GET"])
def get_market_insights():
    """Get market insights and trends"""
    try:
        location = request.args.get('location')
        timeframe = request.args.get('timeframe', 'month')

        market_insights = ensure_market_insights()
        insights = market_insights.get_job_market_trends(location, timeframe)
        formatted_insights = format_market_insights(insights)

        return jsonify({
            "status": "success",
            "insights": formatted_insights
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/market/personalized", methods=["POST"])
@jwt_required()
def get_personalized_insights():
    """Get personalized market insights"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        user_profile = data.get('user_profile', {})

        insights = MARKET_INSIGHTS.get_personalized_insights(user_profile)

        return jsonify({
            "status": "success",
            "insights": insights
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------- RESUME WIZARD ENDPOINTS ---------------- #

@app.route("/resume/templates", methods=["GET"])
@jwt_required()
def get_resume_templates():
    """Get available resume templates"""
    try:
        templates = [
            {
                "id": template_id,
                "name": template.get("name", template_id.title()),
                "description": template.get("style", "")
            }
            for template_id, template in RESUME_WIZARD.templates.items()
        ]

        return jsonify({
            "status": "success",
            "templates": templates
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/resume/generate", methods=["POST"])
@jwt_required()
def generate_resume():
    """Generate resume from user profile"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        user_profile = data.get('user_profile') or data.get('data', {})
        job_title = data.get('job_title')
        template = data.get('template', 'modern')

        resume = RESUME_WIZARD.generate_resume(user_profile, job_title, template)

        return jsonify({
            "status": "success",
            "resume": resume
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/resume/export/<format>", methods=["POST"])
@jwt_required()
def export_resume(format):
    """Export resume in different formats"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        resume_data = data.get('resume_data', {})

        exported = RESUME_WIZARD.export_resume(resume_data, format)

        return jsonify({
            "status": "success",
            "exported_resume": exported
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------- COMMUNITY FORUM ENDPOINTS ---------------- #

@app.route("/forum/posts", methods=["GET"])
@jwt_required()
def get_forum_posts():
    """Get forum posts"""
    try:
        category = request.args.get('category')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        sort_by = request.args.get('sort_by', 'created_at')

        posts = COMMUNITY_FORUM.get_posts(category, limit, offset, sort_by)

        return jsonify({
            "status": "success",
            "posts": posts
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/forum/posts", methods=["POST"])
@jwt_required()
def create_forum_post():
    """Create a new forum post"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        title = data.get('title')
        content = data.get('content')
        category = data.get('category')
        tags = data.get('tags', [])

        if not all([title, content, category]):
            return jsonify({"error": "Title, content, and category are required"}), 400

        post = COMMUNITY_FORUM.create_post(user_id, title, content, category, tags)

        return jsonify({
            "status": "success",
            "post": post
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/forum/posts/<post_id>", methods=["GET"])
@jwt_required()
def get_forum_post(post_id):
    """Get a specific forum post"""
    try:
        post = COMMUNITY_FORUM.get_post(post_id)

        if not post:
            return jsonify({"error": "Post not found"}), 404

        return jsonify({
            "status": "success",
            "post": post
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/forum/posts/<post_id>/reply", methods=["POST"])
@jwt_required()
def reply_to_post(post_id):
    """Reply to a forum post"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        content = data.get('content')

        if not content:
            return jsonify({"error": "Reply content is required"}), 400

        reply = COMMUNITY_FORUM.add_reply(post_id, user_id, content)

        if not reply:
            return jsonify({"error": "Could not add reply"}), 400

        return jsonify({
            "status": "success",
            "reply": reply
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/forum/stats", methods=["GET"])
def get_forum_stats():
    """Get forum statistics"""
    try:
        stats = COMMUNITY_FORUM.get_forum_stats()

        return jsonify({
            "status": "success",
            "stats": stats
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------- CERTIFICATION ENDPOINTS ---------------- #

@app.route("/certifications", methods=["GET"])
@jwt_required()
def get_certifications():
    """Get available certifications"""
    try:
        user_id = get_current_user_id()

        # Get user profile for eligibility check
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()

        user_profile = {
            'id': user['id'],
            'skill_scores': {}  # In real implementation, get from user profile
        }

        certifications = [
            format_certification(certification)
            for certification in CERTIFICATION_SYSTEM.get_available_certifications(user_profile)
        ]

        return jsonify({
            "status": "success",
            "certifications": certifications
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/certifications/<certification_id>/start", methods=["POST"])
@jwt_required()
def start_certification_assessment(certification_id):
    """Start a certification assessment"""
    try:
        user_id = get_current_user_id()

        assessment = CERTIFICATION_SYSTEM.start_assessment(user_id, certification_id)

        return jsonify({
            "status": "success",
            "assessment": assessment
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/certifications/assessment/submit", methods=["POST"])
@jwt_required()
def submit_certification_assessment():
    """Submit certification assessment"""
    try:
        user_id = get_current_user_id()
        data = request.get_json()

        assessment_id = data.get('assessment_id')
        answers = data.get('answers', {})

        if not assessment_id:
            return jsonify({"error": "Assessment ID is required"}), 400

        result = CERTIFICATION_SYSTEM.submit_assessment(assessment_id, answers)

        return jsonify({
            "status": "success",
            "result": result
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/certifications/user", methods=["GET"])
@jwt_required()
def get_user_certifications():
    """Get user's certifications"""
    try:
        user_id = get_current_user_id()

        certifications = [
            format_user_certificate(certificate)
            for certificate in CERTIFICATION_SYSTEM.get_user_certifications(user_id)
        ]

        return jsonify({
            "status": "success",
            "certifications": certifications
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/certifications/<certification_id>/quiz", methods=["GET"])
@jwt_required()
def get_certification_quiz(certification_id):
    """Get quiz for a certification"""
    try:
        questions = CERTIFICATION_SYSTEM.get_certification_quiz(certification_id)
        return jsonify({
            "status": "success",
            "quiz": {
                "certification_id": certification_id,
                "questions": questions
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/certifications/<certification_id>/quiz/submit", methods=["POST"])
@jwt_required()
def submit_certification_quiz(certification_id):
    """Submit frontend certification quiz answers"""
    try:
        user_id = get_current_user_id()
        data = request.get_json() or {}
        answers = data.get("answers", {})
        result = score_certification_quiz(certification_id, answers, user_id)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/certifications/<certification_id>/download", methods=["GET"])
@jwt_required()
def download_certificate(certification_id):
    """Return a mock download link for earned certificates"""
    try:
        user_id = get_current_user_id()
        user_certificates = CERTIFICATION_SYSTEM.get_user_certifications(user_id)
        certificate = next(
            (
                cert for cert in user_certificates
                if cert.get("certification_id") == certification_id
            ),
            None
        )

        if not certificate:
            return jsonify({"error": "Certificate not found"}), 404

        return jsonify({
            "download_url": certificate.get("verification_url", f"/certificates/{certificate['id']}")
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/certifications/verify/<certificate_id>", methods=["GET"])
def verify_certificate(certificate_id):
    """Verify certificate authenticity"""
    try:
        verification = CERTIFICATION_SYSTEM.verify_certificate(certificate_id)

        return jsonify({
            "status": "success",
            "verification": verification
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ---------------- START SERVER ---------------- #
if __name__ == "__main__":
    load_data()                 # Load CSVs
    start_background_loading()  # Load model in background
    app.run(debug=True)
