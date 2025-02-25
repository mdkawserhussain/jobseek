import spacy

# Load the pre-trained spaCy model (ensure you have installed en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def screen_cv(cv_text, subscription='basic'):
    doc = nlp(cv_text)
    # Extract skills (this is a placeholder – you may use more complex logic)
    skills = [ent.text for ent in doc.ents if ent.label_ in ["SKILL", "ORG", "WORK_OF_ART"]]
    # Simple sentence-based extraction for experience mention
    experience = [sent.text for sent in doc.sents if "experience" in sent.text.lower()]
    
    if subscription == 'premium':
        feedback = f"Detailed Analysis: {len(skills)} skills detected ({', '.join(skills)}). " \
                   f"Found {len(experience)} experience-related sections."
    else:
        feedback = f"Basic Feedback: {len(skills)} skills detected."
    return feedback
