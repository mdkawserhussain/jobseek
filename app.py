from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash
from config import Config
from models import db, User, CV, Exam, Payment
from ai import screen_cv
from scraper import scrape_jobs
from payment import process_payment
from exam import generate_exam, grade_exam
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

db.init_app(app)
with app.app_context():
    db.create_all()

# -------------------------
# User Registration Endpoint
# -------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form if request.form else request.get_json()
        email = data.get('email')
        password = data.get('password')
        subscription = data.get('subscription', 'basic')
        
        if User.query.filter_by(email=email).first():
            flash("User already exists.")
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password, subscription=subscription)
        db.session.add(new_user)
        db.session.commit()
        
        # Process registration fee (£5)
        if process_payment(new_user, 5.0, "Registration Fee"):
            payment_record = Payment(amount=5.0, description="Registration Fee", user_id=new_user.id)
            db.session.add(payment_record)
            db.session.commit()
        
        flash("Registration successful. Please log in.")
        return redirect(url_for('login'))
    
    return render_template('register.html')

# -------------------------
# User Login Endpoint
# -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # Fix the unmatched parenthesis here
        data = request.form if request.form else request.get_json()
        email = data.get('email')
        password = data.get('password')
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password, password):
            flash("Invalid credentials.")
            return redirect(url_for('login'))
        
        session['user_id'] = user.id
        flash("Login successful.")
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

# -------------------------
# User Dashboard
# -------------------------
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first.")
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    return render_template('dashboard.html', user=user)

# -------------------------
# CV Upload & Screening Endpoint
# -------------------------
@app.route('/upload_cv', methods=['GET', 'POST'])
def upload_cv():
    user_id = session.get('user_id')
    if not user_id:
        flash("Unauthorized.")
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if request.method == 'POST':
        cv_text = request.form.get('cv_text')
        if not cv_text:
            flash("No CV content provided.")
            return redirect(url_for('upload_cv'))
        # Save CV and run screening
        feedback = screen_cv(cv_text, subscription=user.subscription)
        cv = CV(content=cv_text, feedback=feedback, user_id=user.id)
        db.session.add(cv)
        db.session.commit()
        flash("CV uploaded and screened.")
        return redirect(url_for('screen_cv_route'))
    
    return render_template('upload_cv.html', user=user)

@app.route('/screen_cv')
def screen_cv_route():
    user_id = session.get('user_id')
    if not user_id:
        flash("Unauthorized.")
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if not user.cv:
        flash("Please upload your CV first.")
        return redirect(url_for('upload_cv'))
    return render_template('cv_feedback.html', feedback=user.cv.feedback, user=user)

# -------------------------
# Exam Generation & Submission
# -------------------------
@app.route('/take_exam', methods=['GET', 'POST'])
def take_exam():
    user_id = session.get('user_id')
    if not user_id:
        flash("Unauthorized.")
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if request.method == 'POST':
        answers = request.form.getlist('answer')
        # For demonstration, assume questions were stored in session
        questions = session.get('exam_questions')
        score = grade_exam(answers, questions) if questions else 0
        exam_record = Exam(score=score, attempts=1, user_id=user.id)
        db.session.add(exam_record)
        db.session.commit()
        flash(f"Exam submitted. Your score is {score}.")
        return redirect(url_for('dashboard'))
    else:
        # Assume the exam is based on a fixed job category – adjust as needed.
        questions = generate_exam("software_engineer")
        session['exam_questions'] = questions
        return render_template('take_exam.html', user=user, questions=questions)

# -------------------------
# Job Scraping Endpoint
# -------------------------
@app.route('/jobs')
def jobs():
    job_list = scrape_jobs()
    return jsonify({"jobs": job_list})

# -------------------------
# Employer Communication Endpoint
# -------------------------
@app.route('/employer_reply', methods=['POST'])
def employer_reply():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    reply_content = request.get_json().get('reply')
    user = User.query.get(user_id)
    # For basic users, require a small fee to view employer replies
    if user.subscription == "basic":
        return jsonify({"status": "Payment required", "fee": 0.50})
    else:
        return jsonify({"reply": reply_content})

# -------------------------
# Payment Processing Endpoint (For On-Demand Charges)
# -------------------------
@app.route('/pay', methods=['POST'])
def pay():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    token = request.get_json().get('token')
    amount = request.get_json().get('amount')
    user = User.query.get(user_id)
    # Process the payment (dummy integration)
    if process_payment(user, amount, "On-Demand Charge"):
        payment_record = Payment(amount=amount, description="On-Demand Charge", user_id=user.id)
        db.session.add(payment_record)
        db.session.commit()
        return jsonify({"status": "Payment successful"})
    else:
        return jsonify({"status": "Payment failed"}), 400

@app.route('/')
def index():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
