import random

def generate_exam(job_field, num_questions=2):
    questions = QUESTION_BANK.get(job_field, [])
    return random.sample(questions, min(num_questions, len(questions)))

def grade_exam(answers, questions):
    # Simple grading: count answers that mention expected keywords.
    score = 0
    feedback = []
    
    for answer, q in zip(answers, questions):
        matched_keywords = [kw for kw in q.get("expected_keywords", []) if kw.lower() in answer.lower()]
        if matched_keywords:
            score += 1
        feedback.append({
            "question": q["question"],
            "matched_keywords": matched_keywords,
            "expected_keywords": q["expected_keywords"]
        })
    
    return score, feedback

QUESTION_BANK = {
    "software_engineer": [
        {
            "question": "Explain polymorphism in OOP.",
            "expected_keywords": ["inheritance", "multiple forms", "runtime"]
        },
        {
            "question": "What is a REST API?",
            "expected_keywords": ["HTTP", "stateless", "CRUD"]
        }
    ],
    "data_scientist": [
        {
            "question": "Define overfitting.",
            "expected_keywords": ["generalization", "model", "training data"]
        },
        {
            "question": "How does a decision tree work?",
            "expected_keywords": ["splitting", "nodes", "branches"]
        }
    ]
}