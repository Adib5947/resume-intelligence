def calculate_score(name, email, skills, text):
    score = 0
    feedback = []
    text_lower = text.lower()

    # ── Name detected ──
    if name:
        score += 10
    else:
        feedback.append("Name could not be detected. Make sure your name is at the top of the resume.")

    # ── Email detected ──
    if email:
        score += 10
    else:
        feedback.append("Email address not found. Add a professional email to your resume.")

    # ── Skills ──
    if skills:
        skill_score = min(len(skills) * 4, 35)
        score += skill_score
        if len(skills) < 5:
            feedback.append("Very few skills detected. Add a dedicated 'Skills' section with relevant technologies.")
        elif len(skills) < 10:
            feedback.append("Consider adding more technical skills to strengthen your profile.")
    else:
        feedback.append("No skills detected. Add a 'Skills' or 'Technical Skills' section.")

    # ── Content keywords ──
    keywords = {
        "experience": 5,
        "project": 5,
        "education": 4,
        "internship": 4,
        "certification": 3,
        "achievement": 3,
        "volunteer": 2,
        "leadership": 2,
        "research": 3,
        "publication": 3,
    }

    for kw, pts in keywords.items():
        if kw in text_lower:
            score += pts

    # ── Resume length ──
    word_count = len(text.split())
    if word_count < 200:
        score -= 15
        feedback.append("Resume is very short (under 200 words). Add more detail about your experience and projects.")
    elif word_count < 400:
        score -= 5
        feedback.append("Resume could be more detailed. Aim for at least 400-600 words.")
    elif word_count > 1200:
        feedback.append("Resume is quite long. Consider trimming to 1-2 pages for better readability.")

    # ── Phone number ──
    import re
    if re.search(r'[\+\(]?\d[\d\s\-\(\)]{8,}', text):
        score += 5
    else:
        feedback.append("Phone number not detected. Add your contact number.")

    # ── LinkedIn / GitHub / Portfolio ──
    if "linkedin" in text_lower or "github" in text_lower or "portfolio" in text_lower:
        score += 5
        feedback.append("Good — professional profile links detected.")
    else:
        feedback.append("Add LinkedIn or GitHub profile links to strengthen your resume.")

    # ── Clamp score ──
    score = max(0, min(score, 100))

    # ── Overall verdict ──
    if score >= 85:
        feedback.append("Excellent resume! Strong and well-structured. 💪")
    elif score >= 65:
        feedback.append("Good resume. A few improvements can make it stronger.")
    elif score >= 45:
        feedback.append("Average resume. Focus on adding more relevant content and skills.")
    else:
        feedback.append("Resume needs significant improvement. Follow the suggestions above.")

    return {"score": score, "feedback": feedback}