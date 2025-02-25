import random

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

def generate_exam(job_field, num_questions=2):
    questions = QUESTION_BANK.get(job_field, [])
    return random.sample(questions, min(num_questions, len(questions)))

def grade_exam(answers, questions):
    # Simple grading: count answers that mention expected keywords.
    score = 0
    for answer, q in zip(answers, questions):
        for keyword in q.get("expected_keywords", []):
            if keyword.lower() in answer.lower():
                score += 1
                break
    return score
