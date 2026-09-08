import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///hirewise.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200MB max upload for 80+ resumes

    # Email Configuration — values are stripped because dashboard/env
    # edits sometimes paste trailing newlines, which would corrupt the
    # From: header and make SMTP servers reject outgoing mail
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com').strip()
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER', '').strip()
    SMTP_PASS = os.getenv('SMTP_PASS', '').strip()
    SMTP_SENDER = os.getenv('SMTP_SENDER', '').strip()

    # ML Model paths
    MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ml', 'models')
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
