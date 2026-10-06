# 🎓 AI Interview Report & Auto Email System

An internal, private web application built for companies to automate the student interview reporting and email delivery workflow:
**Excel Upload → Data Validation & Column Mapping → Gemini AI Report Generation → Admin Review/Editing → PDF Export → Auto Email Delivery → Dashboard Tracking**.

---

## 📁 Project Structure

```
interview-report-app/
├── app.py                     # Main Streamlit web app UI
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable configuration template
├── config.py                  # Core system settings & constants
├── utils/
│   ├── validation.py          # Data validation (email syntax, missing fields, duplicates)
│   ├── excel_reader.py        # OpenPyXL & Pandas Excel file reader
│   ├── database.py            # SQLite database manager (batches, students, reports, logs)
│   ├── report_generator.py    # Google Gemini AI report generator (with strict non-hallucination rules)
│   ├── pdf_generator.py       # ReportLab PDF report creation engine
│   └── email_sender.py        # SMTP email delivery & status logger
├── data/
│   ├── create_sample_data.py  # Script to generate sample Excel
│   └── sample_input.xlsx      # Sample Excel with 5 dummy students for instant testing
└── outputs/
    └── reports/               # Generated PDF reports storage
```

---

## ⚡ How to Run the Web Application

### Option A: Using Installed Python Executable (1-Click Command)

Open **PowerShell** or Command Prompt in this folder and run:

```powershell
& "C:\Users\shive\.gemini\antigravity\scratch\python-embed\python.exe" -m streamlit run app.py
```

### Option B: Standard Python (if Python is added to system PATH)

```bash
streamlit run app.py
```

The web application will open automatically in your browser at `http://localhost:8501`!

---

## 🚀 Step-by-Step Workflow Guide

### Step 1: Upload & Validate Excel (`Tab 1`)
1. Open **Tab 1: Upload & Validate Excel**.
2. Click **"Load Sample Test Data"** (or upload your own `.xlsx` file).
3. Confirm or adjust the **Column Mapping** (maps your custom Excel columns to standard system fields like *Student Name*, *Student Email*, *DSA Score*, *Comments*, etc.).
4. Click **"Validate Data & Save Batch"**.
5. The system will automatically check for missing names, invalid email formats, and duplicate emails, giving you a clear breakdown (**Valid Students vs Problematic Students**).

### Step 2: Generate AI Feedback Reports (`Tab 2`)
1. Open **Tab 2: AI Report Generator**.
2. Optional: Enter your **Google Gemini API Key** in the sidebar (if omitted, the system will generate structured template reports so you can test right away).
3. Click **"Generate AI Reports for All Valid Students"**.
4. The AI generates personalized, evidence-based feedback reports following strict professional rules (no hallucinations, no career suitability judgments).

### Step 3: Admin Review, Edit & Approve (`Tab 3`)
1. Open **Tab 3: Review & Approve Reports**.
2. Select any student to inspect their generated markdown report.
3. Edit the text inline if you wish to customize feedback, click **"Save Changes"**, **"Regenerate with AI"**, or **"Download PDF"**.
4. Click **"Approve This Report"** (or **"Approve ALL Generated Reports in Batch"**).

### Step 4: Automated Email Dispatch (`Tab 4`)
1. Open **Tab 4: Auto Email Delivery**.
2. Ensure SMTP settings are configured in `.env` (e.g. Gmail App Password).
3. Click **"Send Emails to All Approved Students"**.
4. The system sends branded HTML emails with PDF feedback reports attached, strictly enforcing human approval.

### Step 5: Dashboard & Tracking (`Tab 5`)
1. Open **Tab 5: Batch Dashboard & Logs**.
2. View batch statistics (**Total Students**, **Reports Generated**, **Approved**, **Emails Sent**, **Failed**).
3. View category score averages (DSA, Python, Communication) and audit email delivery logs.

---

## 🔑 Environment Variables Setup (`.env`)

Copy `.env.example` to `.env` and fill in your details:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_company_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SENDER_NAME="Company HR Team"
```

*Note: For Gmail SMTP, generate an **App Password** from Google Account -> Security -> 2-Step Verification -> App Passwords.*
