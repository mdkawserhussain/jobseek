'''
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////media/ticktick/F/office-code/jobseek/instance/britsync.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads/'
    MAIL_SERVER = 'smtp.hostinger.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'career@britsync.co.uk'  # Replace with your email address
    MAIL_PASSWORD = 'Career@bs23'  # Replace with your email app password
    MAIL_DEFAULT_SENDER = 'career@britsync.co.uk'  # Replace with your email address
    MAIL_SUBJECT_PREFIX = '[BritSync]'
'''


import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////media/ticktick/F/office-code/jobseek/instance/britsync.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads/'

    # SMTP (Outgoing Mail)
    MAIL_SERVER = 'smtp.hostinger.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False  # Using SSL, so TLS is disabled.
    MAIL_USERNAME = 'career@britsync.co.uk'  # Replace with your email address
    MAIL_PASSWORD = 'Career@bs23'  # Replace with your email app password
    MAIL_DEFAULT_SENDER = 'career@britsync.co.uk'  # Replace with your email address
    MAIL_SUBJECT_PREFIX = '[BritSync]'

    # IMAP (Incoming Mail)
    IMAP_SERVER = 'imap.hostinger.com'
    IMAP_PORT = 993
    IMAP_USE_SSL = True
