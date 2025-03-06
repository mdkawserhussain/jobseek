import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////media/ticktick/F/office-code/jobseek/instance/britsync.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads/'
    MAIL_SERVER = 'sandbox.smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'b06b3ddffe1de7'
    MAIL_PASSWORD = 'a72dcaef27dd5e'
    MAIL_DEFAULT_SENDER = 'your_email@example.com'
    MAIL_SUBJECT_PREFIX = '[BritSync]'