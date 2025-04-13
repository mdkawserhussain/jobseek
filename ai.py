import spacy
import sqlite3
import fitz  # PyMuPDF

# Load the pre-trained spaCy model (ensure you have installed en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def store_skills_in_db(skills):
    conn = sqlite3.connect('instance/britsync.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS skills (id INTEGER PRIMARY KEY, skill TEXT)''')
    for skill in skills:
        cursor.execute('''INSERT INTO skills (skill) VALUES (?)''', (skill,))
    conn.commit()
    conn.close()

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_experience(doc):
    experience = []
    for sent in doc.sents:
        if "experience" in sent.text.lower() or "worked" in sent.text.lower() or "responsible" in sent.text.lower():
            experience.append(sent.text)
    return experience

def analyze_cv_with_ai(text):
    """
    Analyze the CV text using AI to provide detailed feedback and recommendations.
    """
    # Example analysis logic (can be replaced with actual AI model integration)
    feedback = "Your CV uses clear language and has a professional tone."
    recommendations = []

    if "team player" not in text.lower():
        recommendations.append("Consider adding 'team player' to highlight collaboration skills.")

    if len(text.split()) > 1000:
        recommendations.append("Your CV is too lengthy. Aim for a concise format under 2 pages.")

    return {
        "feedback": feedback,
        "recommendations": recommendations
    }

def screen_cv(cv_path, subscription='basic'):
    """
    Analyze a CV based on UK standards and provide feedback and recommendations.
    """
    with open(cv_path, 'rb') as f:
        text = extract_text_from_pdf(f)  # Extract text from the PDF

    feedback = ""
    recommendations = []

    # Basic UK CV Guidelines
    if len(text) < 200:
        feedback = "Your CV seems too short. Ensure you include detailed work experience and skills."
        recommendations.append({
            "what": "Expand your CV",
            "why": "A short CV may not provide enough information to showcase your qualifications and experience.",
            "how": "Add more details about your work experience, skills, and achievements. Use quantifiable metrics where possible."
        })

    if "Objective" in text or "Career Objective" in text:
        recommendations.append({
            "what": "Replace 'Career Objective' with 'Personal Statement'",
            "why": "'Career Objective' is considered outdated in modern CVs. A 'Personal Statement' is more concise and impactful.",
            "how": "Write a brief summary of your professional background, key skills, and career goals. Keep it under 4-5 lines."
        })

    if not any(kw in text.lower() for kw in ["skills", "experience", "education"]):
        recommendations.append({
            "what": "Include key sections",
            "why": "Employers expect to see sections like Skills, Experience, and Education to evaluate your qualifications.",
            "how": "Add these sections with relevant details. For example, list your skills in bullet points and describe your work experience with job titles, responsibilities, and achievements."
        })

    # Premium subscription analysis
    if subscription == "premium":
        analysis_result = analyze_cv_with_ai(text)
        feedback += analysis_result.get("feedback", "")
        recommendations.extend(analysis_result.get("recommendations", []))

    return {
        "feedback": feedback or "Your CV is well-structured and meets UK standards!",
        "recommendations": recommendations
    }
