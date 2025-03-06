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

def screen_cv(cv_path, subscription='basic'):
    if '\0' in cv_path:
        raise ValueError("Invalid file path: embedded null byte")
    if cv_path.endswith('.pdf'):
        cv_text = extract_text_from_pdf(cv_path)
    else:
        with open(cv_path, 'r') as file:
            cv_text = file.read()
    
    doc = nlp(cv_text)
    # Extract skills (this is a placeholder – you may use more complex logic)
    skills = [ent.text for ent in doc.ents if ent.label_ in ["SKILL", "ORG", "WORK_OF_ART"]]
    store_skills_in_db(skills)
    # Simple sentence-based extraction for experience mention
    experience = [sent.text for sent in doc.sents if "experience" in sent.text.lower()]
    
    with open('cv.txt', 'w') as file:
        file.write('\n'.join(skills))
    
    if subscription == 'premium':
        feedback = f"Detailed Analysis: {len(skills)} skills detected ({', '.join(skills)}). " \
                   f"Found {len(experience)} experience-related sections."
    else:
        feedback = f"Basic Feedback: {len(skills)} skills detected."
    return feedback
