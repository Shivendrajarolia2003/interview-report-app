import os
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

# App Configurations
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SENDER_NAME = os.getenv("SENDER_NAME", "Company Recruitment Team")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

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
