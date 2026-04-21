from sentence_transformers import SentenceTransformer, util
import re

model = SentenceTransformer('all-MiniLM-L6-v2')


# ─────────────────────────────────────────────────────────
# 🧠 SKILLS DATABASE (for job description extraction)
# ─────────────────────────────────────────────────────────
SKILLS_DB = [
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
    "numpy", "data analysis", "data science", "artificial intelligence",
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


# ─────────────────────────────────────────────────────────
# 📋 PARSE STRUCTURED DATA FROM JOB DESCRIPTION
# ─────────────────────────────────────────────────────────
def extract_structured_job_data(job_description):
    text = job_description
    text_lower = text.lower()
    lines = text.split("\n")
    data = {}

    # ── Company ──
    company = re.search(
        r'company\s*(name)?\s*[:\-]\s*(.+)',
        text, re.IGNORECASE
    )
    if company:
        data["company"] = company.group(2).strip()
    else:
        # Try to find "X is looking for" or "X Ltd." / "X Inc." patterns
        org_match = re.search(
            r'^([A-Z][A-Za-z0-9\s&,\.\-]+(?:Ltd|Inc|LLC|Corp|Solutions|Technologies|Systems|Group)\.?)',
            text, re.MULTILINE
        )
        data["company"] = org_match.group(1).strip() if org_match else "Not Mentioned"

    # ── Position / Job Title ──
    position = re.search(
        r'(?:position|job title|role|hiring for|looking for a?n?)\s*[:\-]?\s*(.+)',
        text, re.IGNORECASE
    )
    if position:
        data["position"] = position.group(1).strip()
    else:
        # Try first line that looks like a job title
        for line in lines[:8]:
            line = line.strip()
            job_title_keywords = [
                "engineer", "developer", "analyst", "designer", "manager",
                "intern", "consultant", "scientist", "architect", "lead",
                "officer", "specialist", "coordinator", "executive"
            ]
            if any(kw in line.lower() for kw in job_title_keywords) and len(line) < 80:
                data["position"] = line
                break
        else:
            data["position"] = "Not Mentioned"

    # ── Salary ──
    salary = re.search(
        r'(?:salary|compensation|pay|ctc|package)\s*[:\-]?\s*(.+)',
        text, re.IGNORECASE
    )
    if salary:
        data["salary"] = salary.group(1).strip()
    elif re.search(r'\$[\d,]+|\d+\s*(?:lpa|lakh|k\b)', text, re.IGNORECASE):
        sal_num = re.search(r'(\$[\d,]+[\s\-]*(?:to|–|\-)?\s*\$?[\d,]*|\d+\s*(?:lpa|lakh|k)[\s\-]*(?:to|–)?\s*\d*\s*(?:lpa|lakh|k)?)', text, re.IGNORECASE)
        data["salary"] = sal_num.group(1).strip() if sal_num else "Mentioned (see description)"
    elif "competitive" in text_lower:
        data["salary"] = "Competitive"
    elif "negotiable" in text_lower:
        data["salary"] = "Negotiable"
    else:
        data["salary"] = "Not Mentioned"

    # ── Location / Address ──
    location = re.search(
        r'(?:location|address|office|based in|city)\s*[:\-]\s*(.+)',
        text, re.IGNORECASE
    )
    if location:
        data["address"] = location.group(1).strip()
    else:
        # Look for city/country names pattern
        geo = re.search(
            r'\b(Dhaka|Chittagong|Sylhet|Khulna|Rajshahi|Rangpur|Barishal|'
            r'London|New York|San Francisco|Toronto|Dubai|Singapore|Bangalore|'
            r'Mumbai|Delhi|Karachi|remote|hybrid|on-site|onsite)\b',
            text, re.IGNORECASE
        )
        data["address"] = geo.group(1).strip() if geo else "Not Mentioned"

    # ── Experience ──
    exp = re.search(
        r'(\d+\s*[\+]?\s*[-–to]*\s*\d*\s*(?:years?|yrs?)(?:\s*of\s*experience)?)',
        text, re.IGNORECASE
    )
    if exp:
        data["experience"] = exp.group(1).strip()
    elif "fresher" in text_lower or "entry level" in text_lower or "no experience" in text_lower:
        data["experience"] = "Fresher / Entry Level"
    else:
        data["experience"] = "Not Mentioned"

    # ── Deadline ──
    deadline = re.search(
        r'(?:deadline|apply by|last date|application closes?|closing date)\s*[:\-]?\s*(.+)',
        text, re.IGNORECASE
    )
    if deadline:
        data["deadline"] = deadline.group(1).strip()
    else:
        # Look for date patterns
        date_match = re.search(
            r'\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{2,4})\b',
            text, re.IGNORECASE
        )
        data["deadline"] = date_match.group(1).strip() if date_match else "Not Mentioned"

    # ── Responsibilities ──
    responsibilities = []
    in_section = False
    section_headers = [
        "responsibilit", "your role", "what you'll do",
        "key duties", "job duties", "duties", "what you will do",
        "what we expect", "role overview"
    ]
    stop_headers = [
        "requirement", "qualification", "skill", "benefit",
        "about us", "we offer", "what we look"
    ]

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        line_lower = line_stripped.lower()

        if any(h in line_lower for h in section_headers):
            in_section = True
            continue

        if in_section:
            if any(h in line_lower for h in stop_headers):
                break
            if line_stripped and len(line_stripped) > 10:
                clean = re.sub(r'^[\•\-\*\>\→\d\.\)]+\s*', '', line_stripped).strip()
                if clean:
                    responsibilities.append(clean)
            if len(responsibilities) >= 7:
                break

    if not responsibilities:
        # Fallback: grab bullet-point-looking lines
        for line in lines:
            line_stripped = line.strip()
            if re.match(r'^[\•\-\*]', line_stripped) and len(line_stripped) > 15:
                clean = re.sub(r'^[\•\-\*]\s*', '', line_stripped).strip()
                responsibilities.append(clean)
            if len(responsibilities) >= 6:
                break

    data["responsibilities"] = responsibilities if responsibilities else ["Not specified in description"]

    # ── Requirements / Qualifications ──
    requirements = []
    in_req = False
    req_headers = [
        "requirement", "qualification", "what we look",
        "you should have", "you must have", "skills required",
        "we are looking for", "must have", "minimum qualification"
    ]

    for line in lines:
        line_stripped = line.strip()
        line_lower = line_stripped.lower()

        if any(h in line_lower for h in req_headers):
            in_req = True
            continue

        if in_req:
            if any(h in line_lower for h in ["responsibilit", "benefit", "about us", "we offer"]):
                break
            if line_stripped and len(line_stripped) > 8:
                clean = re.sub(r'^[\•\-\*\>\→\d\.\)]+\s*', '', line_stripped).strip()
                if clean:
                    requirements.append(clean)
            if len(requirements) >= 8:
                break

    data["requirements"] = requirements if requirements else []

    return data


# ─────────────────────────────────────────────────────────
# 🔍 EXTRACT REQUIRED SKILLS FROM JOB DESCRIPTION
# ─────────────────────────────────────────────────────────
def extract_job_skills(job_description):
    job_lower = f" {job_description.lower()} "
    found = set()

    for skill in SKILLS_DB:
        pattern = r'(?<!\w)' + re.escape(skill) + r'(?!\w)'
        if re.search(pattern, job_lower):
            found.add(skill)

    return sorted(list(found))


# ─────────────────────────────────────────────────────────
# 💡 GENERATE IMPROVEMENT SUGGESTIONS
# ─────────────────────────────────────────────────────────
def generate_suggestions(missing_important, match_score, resume_skills):
    suggestions = []

    if match_score < 40:
        suggestions.append("Your resume needs significant alignment with this job description.")

    if match_score < 70:
        suggestions.append("Tailor your resume summary/objective specifically for this role.")

    for skill in missing_important[:5]:
        suggestions.append(f"Learn or highlight '{skill}' — it is required for this position.")

    if len(resume_skills) < 6:
        suggestions.append("Add more technical skills to your resume to improve visibility.")

    if not suggestions:
        suggestions.append("Great match! Make sure your experience section highlights relevant projects.")

    if match_score >= 75:
        suggestions.append("Strong profile for this role. Focus on quantifying your achievements.")

    return suggestions


# ─────────────────────────────────────────────────────────
# 🚀 MAIN SEMANTIC MATCH FUNCTION
# ─────────────────────────────────────────────────────────
def semantic_match(resume_skills, job_description):

    # Step 1 — Parse structured job data
    job_data = extract_structured_job_data(job_description)

    # Step 2 — Extract required skills from job description
    job_skills = extract_job_skills(job_description)

    # Edge case — no skills on resume
    if not resume_skills:
        return {
            **job_data,
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": job_skills,
            "missing_important_skills": job_skills,
            "suggestions": [
                "No skills were detected in your resume. Add a dedicated Skills section.",
                "Make sure your resume is a text-based PDF (not a scanned image).",
            ]
        }

    # Edge case — no skills in job description
    if not job_skills:
        return {
            **job_data,
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "missing_important_skills": [],
            "suggestions": [
                "Could not detect specific technical skills from this job description.",
                "Try pasting a more detailed job description with clear skill requirements.",
            ]
        }

    # ─────────────────────────────────────────
    # Step 3 — Semantic similarity matching
    # ─────────────────────────────────────────
    resume_skills_lower = [s.lower() for s in resume_skills]
    job_skills_lower = [s.lower() for s in job_skills]

    # Encode resume skills and job skills
    resume_embeddings = model.encode(resume_skills_lower, convert_to_tensor=True)
    job_embeddings = model.encode(job_skills_lower, convert_to_tensor=True)

    matched_skills = []
    missing_skills = []

    for i, r_skill in enumerate(resume_skills_lower):
        # Compute similarity against all job skills
        similarities = util.cos_sim(resume_embeddings[i], job_embeddings)
        max_score = similarities.max().item()

        if max_score >= 0.55:
            matched_skills.append(r_skill)
        else:
            missing_skills.append(r_skill)

    # ─────────────────────────────────────────
    # Step 4 — Missing important skills
    # (job requires them but NOT in resume at all)
    # ─────────────────────────────────────────
    missing_important = [
        s for s in job_skills_lower
        if s not in resume_skills_lower
    ]

    # Cross-check with semantic similarity too
    # (avoid flagging skills that are semantically covered)
    if missing_important and resume_embeddings is not None:
        missing_imp_embeddings = model.encode(missing_important, convert_to_tensor=True)
        truly_missing = []

        for i, m_skill in enumerate(missing_important):
            sims = util.cos_sim(missing_imp_embeddings[i], resume_embeddings)
            max_sim = sims.max().item()
            if max_sim < 0.60:
                truly_missing.append(m_skill)

        missing_important = truly_missing

    # ─────────────────────────────────────────
    # Step 5 — Calculate match score
    # ─────────────────────────────────────────
    # Score = how many job-required skills are covered by resume
    covered = [s for s in job_skills_lower if s in resume_skills_lower or s in matched_skills]
    match_score = int((len(covered) / len(job_skills_lower)) * 100)
    match_score = min(match_score, 100)

    # ─────────────────────────────────────────
    # Step 6 — Suggestions
    # ─────────────────────────────────────────
    suggestions = generate_suggestions(missing_important, match_score, resume_skills_lower)

    # ─────────────────────────────────────────
    # Step 7 — Return everything
    # ─────────────────────────────────────────
    return {
        **job_data,
        "match_score": match_score,
        "matched_skills": sorted(list(set(matched_skills))),
        "missing_skills": sorted(list(set(missing_skills))),
        "missing_important_skills": sorted(missing_important),
        "suggestions": suggestions,
    }