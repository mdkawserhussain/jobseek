from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash
from config import Config
from models import db, User, CV, Exam, Payment
from ai import screen_cv
from scraper import scrape_jobs
from payment import process_payment
from exam import generate_exam, grade_exam
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Enable CORS for the Flask app
CORS(app, resources={r"/*": {"origins": "https://appery.io"}})

logging.basicConfig(level=logging.DEBUG)

# Create the uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.init_app(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

with app.app_context():
    db.create_all()

def send_email(to_address, subject, body, attachment_path=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = Config.MAIL_USERNAME
        msg['To'] = to_address
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        if attachment_path:
            attachment = open(attachment_path, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            filename = os.path.basename(attachment_path)  # Get the filename from the path
            part.add_header('Content-Disposition', f"attachment; filename= {filename}")
            msg.attach(part)

        print(f"Connecting to SMTP server: {Config.MAIL_SERVER}:{Config.MAIL_PORT}")
        server = smtplib.SMTP_SSL(Config.MAIL_SERVER, Config.MAIL_PORT)
        print("Starting SSL...")
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        print("Logged in to SMTP server")
        text = msg.as_string()
        server.sendmail(Config.MAIL_USERNAME, to_address, text)
        server.quit()
        print(f"Email sent successfully to {to_address}")
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
        flash("Failed to send email. Please try again later.")
    except Exception as e:
        print(f"Failed to send email: {e}")
        flash("Failed to send email. Please try again later.")

# Function to forward CV to relevant employers and notify users

def forward_cv_to_employers(user, cv_path, industry_name=None):
    employer_email = "career@britsync.co.uk"  # Replace with the actual employer's email
    subject = "New CV Submission"
    body = f"Dear Employer,\n\nA new CV has been submitted by {user.email}.\n\nFeedback:\n{user.cv.feedback}\n\nBest regards,\nBritSync"
    send_email(employer_email, subject, body, attachment_path=cv_path)

    if user.subscription == 'premium' and industry_name:
        user_notification = f"Your CV was sent to {industry_name} employers."
    else:
        user_notification = "Your CV was sent to an employer."

    send_email(user.email, "CV Submission Notification", user_notification)
    return user_notification  # Return the notification message

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
        stripe_token = data.get('stripeToken')
        
        if User.query.filter_by(email=email).first():
            flash("User already exists.")
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password, subscription=subscription)
        db.session.add(new_user)
        db.session.commit()
        ###if process_payment(new_user, 5.0, "Registration Fee", stripe_token):

        # Replace the process_payment function call with a dummy implementation for testing
        if True:  # Bypass actual payment processing for testing
            payment_record = Payment(amount=5.0, description="Registration Fee", user_id=new_user.id)
            db.session.add(payment_record)


        # Replace the process_payment function call with a dummy implementation for testing
        if True:  # Bypass actual payment processing for testing
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
    user = db.session.get(User, user_id)
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
    
    user = db.session.get(User, user_id)
    if request.method == 'POST':
        if 'cv_file' not in request.files:
            flash("No file part.")
            return redirect(url_for('upload_cv'))
        
        file = request.files['cv_file']
        if file.filename == '':
            flash("No selected file.")
            return redirect(url_for('upload_cv'))
        
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Analyze CV
            analysis = screen_cv(file_path, subscription=user.subscription)
            feedback = analysis["feedback"]
            recommendations = "\n".join(analysis["recommendations"])

            # Save to database
            new_cv = CV(content=file_path, feedback=feedback, recommendations=recommendations, user_id=user.id)
            db.session.add(new_cv)
            db.session.commit()

            flash("File successfully uploaded and analyzed.")
            return redirect(url_for('screen_cv_route'))
    
    return render_template('upload_cv.html', user=user)

@app.route('/screen_cv')
def screen_cv_route():
    user_id = session.get('user_id')
    if not user_id:
        flash("Unauthorized.")
        return redirect(url_for('login'))

    user = db.session.get(User, user_id)
    if not user.cv:
        flash("Please upload your CV first.")
        return redirect(url_for('upload_cv'))
    
    return render_template(
        'cv_feedback.html',
        feedback=user.cv.feedback,
        recommendations=user.cv.recommendations,
        user=user
    )

# -------------------------
# Exam Generation & Submission
# -------------------------
@app.route('/take_exam', methods=['GET', 'POST'])
def take_exam():
    user_id = session.get('user_id')
    if not user_id:
        flash("Unauthorized.")
        return redirect(url_for('login'))
    user = db.session.get(User, user_id)
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
    user = db.session.get(User, user_id)
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
    user = db.session.get(User, user_id)
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
