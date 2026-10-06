import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
REPORTS_DIR = OUTPUTS_DIR / "reports"
DB_PATH = BASE_DIR / "interview_reports.db"

# Create directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def get_secret(key_name, default_val=""):
    """Fetches key from env vars, Streamlit Secrets, or fallback default."""
    if os.getenv(key_name):
        return os.getenv(key_name)
    try:
        if hasattr(st, "secrets") and key_name in st.secrets:
            return str(st.secrets[key_name])
    except Exception:
        pass
    return default_val

# App Configurations
GEMINI_API_KEY = get_secret("GEMINI_API_KEY", "")
SMTP_SERVER = get_secret("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(get_secret("SMTP_PORT", 587))
SMTP_USERNAME = get_secret("SMTP_USERNAME", "")
SMTP_PASSWORD = get_secret("SMTP_PASSWORD", "")
SENDER_NAME = get_secret("SENDER_NAME", "Company Recruitment Team")
ADMIN_PASSWORD = get_secret("ADMIN_PASSWORD", "admin123")

# Standard Target Field Definitions for Column Mapping
STANDARD_FIELDS = {
    "student_name": {"label": "Student Name", "required": True},
    "student_email": {"label": "Student Email", "required": True},
    "interview_date": {"label": "Interview Date", "required": False},
    "dsa_score": {"label": "DSA Score", "required": False},
    "python_score": {"label": "Python Score", "required": False},
    "communication_score": {"label": "Communication Score", "required": False},
    "interviewer_comments": {"label": "Interviewer Comments / Observations", "required": False},
    "strengths": {"label": "Strengths", "required": False},
    "weaknesses": {"label": "Weaknesses", "required": False},
}

# Status Constants
STATUS_PENDING = "Pending"
STATUS_GENERATING = "Generating"
STATUS_GENERATED = "Generated"
STATUS_NEEDS_REVIEW = "Needs Review"
STATUS_APPROVED = "Approved"
STATUS_SENT = "Sent"
STATUS_FAILED = "Failed"
