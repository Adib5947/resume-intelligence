from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import re

from app.parser import (
    extract_text_from_pdf,
    extract_email,
    extract_name,
    extract_skills,
)
from app.scorer import calculate_score
from app.semantic_matcher import semantic_match
from app.database import init_db, create_user, get_user_by_email, get_user_by_id
from app.auth import hash_password, verify_password, create_access_token, decode_access_token

# ─────────────────────────────────────────
# APP INIT
# ─────────────────────────────────────────
app = FastAPI(title="AI Resume Analyzer", version="2.0")

# Initialize SQLite database on startup
init_db()


# ─────────────────────────────────────────
# CORS
# ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ─────────────────────────────────────────
# REQUEST MODELS
# ─────────────────────────────────────────
class SignupRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


# ─────────────────────────────────────────
# EMAIL VALIDATION HELPER
# ─────────────────────────────────────────
def is_valid_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return re.match(pattern, email) is not None


# ─────────────────────────────────────────
# 🏠 ROOT
# ─────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "AI Resume Analyzer is running 🚀", "version": "2.0"}


# ─────────────────────────────────────────
# 📝 SIGNUP
# ─────────────────────────────────────────
@app.post("/auth/signup")
def signup(body: SignupRequest):
    if not body.username or len(body.username.strip()) < 2:
        raise HTTPException(status_code=400, detail="Username must be at least 2 characters.")

    if not is_valid_email(body.email):
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")

    if not body.password or len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    existing = get_user_by_email(body.email)
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    password_hash = hash_password(body.password)
    try:
        user = create_user(
            username=body.username.strip(),
            email=body.email.lower().strip(),
            password_hash=password_hash,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not create account: {str(e)}")

    token = create_access_token(
        user_id=user["id"],
        email=user["email"],
        username=user["username"],
    )

    return {
        "message": "Account created successfully!",
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
        }
    }


# ─────────────────────────────────────────
# 🔐 LOGIN
# ─────────────────────────────────────────
@app.post("/auth/login")
def login(body: LoginRequest):
    if not body.email or not body.password:
        raise HTTPException(status_code=400, detail="Email and password are required.")

    user = get_user_by_email(body.email.lower().strip())
    if not user:
        raise HTTPException(status_code=401, detail="No account found with this email.")

    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect password.")

    token = create_access_token(
        user_id=user["id"],
        email=user["email"],
        username=user["username"],
    )

    return {
        "message": "Logged in successfully!",
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
        }
    }


# ─────────────────────────────────────────
# 👤 GET CURRENT USER
# ─────────────────────────────────────────
@app.get("/auth/me")
def get_me(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header.")

    token = authorization.split(" ")[1]
    payload = decode_access_token(token)

    user_id = int(payload["sub"])
    user = get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
    }


# ─────────────────────────────────────────
# 📄 UPLOAD RESUME
# ─────────────────────────────────────────
@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text_from_pdf(file_path)
    if not text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from PDF.")

    name = extract_name(text)
    email = extract_email(text)
    skills = extract_skills(text)
    score_result = calculate_score(name, email, skills, text)

    return {
        "name": name,
        "email": email,
        "skills": skills,
        "score": score_result["score"],
        "feedback": score_result["feedback"],
    }


# ─────────────────────────────────────────
# 🔥 MATCH RESUME vs JOB DESCRIPTION
# ─────────────────────────────────────────
@app.post("/match")
async def match_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    if not job_description or len(job_description.strip()) < 30:
        raise HTTPException(status_code=400, detail="Job description is too short.")

    safe_filename = file.filename.replace(" ", "_")
    file_path = os.path.join(UPLOAD_FOLDER, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text_from_pdf(file_path)
    if not text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from PDF.")

    resume_skills = extract_skills(text)
    result = semantic_match(resume_skills, job_description)

    return result