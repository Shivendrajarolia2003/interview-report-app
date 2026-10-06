import sqlite3
import json
import shutil
from datetime import datetime
from config import DB_PATH, REPORTS_DIR, STATUS_PENDING, STATUS_GENERATED, STATUS_APPROVED, STATUS_SENT, STATUS_FAILED

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Batches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_name TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,
            total_students INTEGER DEFAULT 0,
            valid_count INTEGER DEFAULT 0,
            problem_count INTEGER DEFAULT 0
        )
    ''')

    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id INTEGER NOT NULL,
            name TEXT,
            email TEXT,
            scores_json TEXT,
            interviewer_comments TEXT,
            strengths TEXT,
            weaknesses TEXT,
            custom_data_json TEXT,
            is_valid INTEGER DEFAULT 1,
            validation_errors TEXT,
            FOREIGN KEY (batch_id) REFERENCES batches (id) ON DELETE CASCADE
        )
    ''')

    # Reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER UNIQUE NOT NULL,
            batch_id INTEGER NOT NULL,
            overall_assessment TEXT,
            report_markdown TEXT,
            pdf_path TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TEXT,
            updated_at TEXT,
            admin_notes TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
            FOREIGN KEY (batch_id) REFERENCES batches (id) ON DELETE CASCADE
        )
    ''')

    # Email logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            recipient_email TEXT NOT NULL,
            status TEXT NOT NULL,
            sent_at TEXT,
            error_message TEXT,
            attempt_count INTEGER DEFAULT 1,
            FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

def create_batch(batch_name, total_students, valid_count, problem_count):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO batches (batch_name, uploaded_at, total_students, valid_count, problem_count)
        VALUES (?, ?, ?, ?, ?)
    ''', (batch_name, now, total_students, valid_count, problem_count))
    batch_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return batch_id

def save_students(batch_id, students_list):
    conn = get_connection()
    cursor = conn.cursor()
    for s in students_list:
        scores_json = json.dumps(s.get("scores", {}))
        custom_data_json = json.dumps(s.get("custom_data", {}))
        val_errors = json.dumps(s.get("validation_errors", []))
        
        cursor.execute('''
            INSERT INTO students (
                batch_id, name, email, scores_json, interviewer_comments,
                strengths, weaknesses, custom_data_json, is_valid, validation_errors
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            batch_id,
            s.get("name"),
            s.get("email"),
            scores_json,
            s.get("interviewer_comments", ""),
            s.get("strengths", ""),
            s.get("weaknesses", ""),
            custom_data_json,
            1 if s.get("is_valid", True) else 0,
            val_errors
        ))
        student_id = cursor.lastrowid
        
        # Initialize report entry
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO reports (student_id, batch_id, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, batch_id, STATUS_PENDING, now, now))
        
    conn.commit()
    conn.close()

def get_batches():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM batches ORDER BY id DESC")
    batches = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return batches

def get_students_by_batch(batch_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.*, r.id as report_id, r.status as report_status, r.overall_assessment,
               r.report_markdown, r.pdf_path, r.updated_at as report_updated_at
        FROM students s
        LEFT JOIN reports r ON s.id = r.student_id
        WHERE s.batch_id = ?
        ORDER BY s.id ASC
    ''', (batch_id,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # parse JSON fields
    for row in rows:
        row['scores'] = json.loads(row['scores_json']) if row['scores_json'] else {}
        row['custom_data'] = json.loads(row['custom_data_json']) if row['custom_data_json'] else {}
        row['validation_errors'] = json.loads(row['validation_errors']) if row['validation_errors'] else []
    return rows

def update_report(report_id, report_markdown, overall_assessment="", pdf_path="", status=STATUS_GENERATED):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        UPDATE reports
        SET report_markdown = ?, overall_assessment = ?, pdf_path = ?, status = ?, updated_at = ?
        WHERE id = ?
    ''', (report_markdown, overall_assessment, pdf_path, status, now, report_id))
    conn.commit()
    conn.close()

def update_report_status(report_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        UPDATE reports
        SET status = ?, updated_at = ?
        WHERE id = ?
    ''', (new_status, now, report_id))
    conn.commit()
    conn.close()

def update_batch_report_statuses(batch_id, from_status, to_status):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        UPDATE reports
        SET status = ?, updated_at = ?
        WHERE batch_id = ? AND status = ?
    ''', (to_status, now, batch_id, from_status))
    conn.commit()
    conn.close()

def log_email_attempt(report_id, recipient_email, status, error_message=""):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO email_logs (report_id, recipient_email, status, sent_at, error_message)
        VALUES (?, ?, ?, ?, ?)
    ''', (report_id, recipient_email, status, now, error_message))
    
    # Update report status
    report_status = STATUS_SENT if status == "Sent" else STATUS_FAILED
    cursor.execute('''
        UPDATE reports
        SET status = ?, updated_at = ?
        WHERE id = ?
    ''', (report_status, now, report_id))
    
    conn.commit()
    conn.close()

def get_email_logs(batch_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    if batch_id:
        cursor.execute('''
            SELECT l.*, s.name as student_name
            FROM email_logs l
            JOIN reports r ON l.report_id = r.id
            JOIN students s ON r.student_id = s.id
            WHERE r.batch_id = ?
            ORDER BY l.id DESC
        ''', (batch_id,))
    else:
        cursor.execute('''
            SELECT l.*, s.name as student_name
            FROM email_logs l
            JOIN reports r ON l.report_id = r.id
            JOIN students s ON r.student_id = s.id
            ORDER BY l.id DESC
        ''')
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return logs

def delete_batch(batch_id):
    """Deletes a specific batch and all associated students, reports, and logs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM batches WHERE id = ?", (batch_id,))
    cursor.execute("DELETE FROM students WHERE batch_id = ?", (batch_id,))
    cursor.execute("DELETE FROM reports WHERE batch_id = ?", (batch_id,))
    conn.commit()
    conn.close()

def reset_all_data():
    """Wipes all database records and removes generated PDF files."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM email_logs")
    cursor.execute("DELETE FROM reports")
    cursor.execute("DELETE FROM students")
    cursor.execute("DELETE FROM batches")
    conn.commit()
    conn.close()
    
    # Clean PDF output directory
    if REPORTS_DIR.exists():
        for item in REPORTS_DIR.glob("*"):
            if item.is_file():
                try:
                    item.unlink()
                except Exception:
                    pass
