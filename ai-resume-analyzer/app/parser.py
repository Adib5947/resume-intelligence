import pdfplumber
import re
import spacy

nlp = spacy.load("en_core_web_sm")


# ─────────────────────────────────────────
# 📄 Extract raw text from PDF
# ─────────────────────────────────────────
def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


# ─────────────────────────────────────────
# 📧 Email
# ─────────────────────────────────────────
def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else None


# ─────────────────────────────────────────
# 👤 Name
# ─────────────────────────────────────────
def extract_name(text):
    lines = text.split("\n")
    for line in lines[:5]:
        line = line.strip()
        if 2 < len(line) <= 40 and len(line.split()) <= 5:
            if not any(char.isdigit() for char in line):
                if "@" not in line and "http" not in line:
                    return line.title()

    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.title()

    return None


# ─────────────────────────────────────────
# 🧠 Skills from resume
# ─────────────────────────────────────────
def extract_skills(text):
    skills_db = [
        # Languages
        "python", "java", "c++", "c#", "javascript", "typescript",
        "php", "ruby", "swift", "kotlin", "go", "rust", "scala",
        # Frontend
        "react", "vue", "angular", "html", "css", "tailwind",
        "bootstrap", "next.js", "gatsby",
        # Backend
        "node", "fastapi", "django", "flask", "express", "spring",
        "laravel", "asp.net",
        # Data / AI
        "machine learning", "deep learning", "nlp", "computer vision",
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas",
        "numpy", "matplotlib", "data analysis", "data science",
        "artificial intelligence",
        # Databases
        "sql", "mysql", "postgresql", "mongodb", "redis", "firebase",
        "sqlite", "oracle",
        # Cloud / DevOps
        "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd",
        "github actions", "jenkins", "terraform",
        # Tools
        "git", "linux", "api", "rest api", "graphql",
        "microservices", "agile", "scrum",
        # Mobile
        "flutter", "react native", "android", "ios",
    ]

    text_lower = f" {text.lower()} "
    found_skills = set()

    for skill in skills_db:
        pattern = r'(?<!\w)' + re.escape(skill) + r'(?!\w)'
        if re.search(pattern, text_lower):
            found_skills.add(skill)

    return sorted(list(found_skills))