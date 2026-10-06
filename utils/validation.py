import re
import pandas as pd
from config import STANDARD_FIELDS

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

def auto_detect_columns(columns):
    """
    Intelligently maps uploaded Excel column names to system standard fields
    based on fuzzy keyword matching.
    """
    mapping = {}
    cols_lower = [str(c).strip().lower() for c in columns]
    
    for key in STANDARD_FIELDS:
        best_match = None
        for orig_col in columns:
            col_clean = str(orig_col).strip().lower()
            
            if key == "student_name" and any(k in col_clean for k in ["student name", "candidate name", "full name", "name"]):
                best_match = orig_col
                break
            elif key == "student_email" and any(k in col_clean for k in ["email", "e-mail", "mail"]):
                best_match = orig_col
                break
            elif key == "interview_date" and any(k in col_clean for k in ["date", "interview date", "day"]):
                best_match = orig_col
                break
            elif key == "dsa_score" and any(k in col_clean for k in ["dsa", "data structure", "algo"]):
                best_match = orig_col
                break
            elif key == "python_score" and "python" in col_clean:
                best_match = orig_col
                break
            elif key == "communication_score" and any(k in col_clean for k in ["comm", "communication", "english", "soft skill"]):
                best_match = orig_col
                break
            elif key == "interviewer_comments" and any(k in col_clean for k in ["comment", "observation", "remark", "feedback", "note"]):
                best_match = orig_col
                break
            elif key == "strengths" and "strength" in col_clean:
                best_match = orig_col
                break
            elif key == "weaknesses" and any(k in col_clean for k in ["weakness", "area of improvement", "improvement"]):
                best_match = orig_col
                break
                
        mapping[key] = best_match
    return mapping

def validate_and_parse_excel(df, column_mapping):
    """
    Parses dataframe with mapped columns and validates every row.
    Detects:
    - Missing student name
    - Missing email
    - Invalid email format
    - Duplicate email within batch
    - Blank rows
    """
    students = []
    seen_emails = set()
    
    name_col = column_mapping.get("student_name")
    email_col = column_mapping.get("student_email")
    comments_col = column_mapping.get("interviewer_comments")
    strengths_col = column_mapping.get("strengths")
    weaknesses_col = column_mapping.get("weaknesses")
    
    for idx, row in df.iterrows():
        row_num = idx + 2  # Excel 1-indexed header offset
        
        # Check blank row
        if row.dropna().empty:
            continue
            
        errors = []
        name = str(row[name_col]).strip() if name_col and pd.notna(row[name_col]) else ""
        email = str(row[email_col]).strip().lower() if email_col and pd.notna(row[email_col]) else ""
        
        if not name or name.lower() in ["nan", "none", "null"]:
            errors.append("Missing Student Name")
            name = f"Unknown Student (Row {row_num})"
            
        if not email or email.lower() in ["nan", "none", "null"]:
            errors.append("Missing Student Email")
        elif not re.match(EMAIL_REGEX, email):
            errors.append(f"Invalid email format: '{email}'")
        elif email in seen_emails:
            errors.append(f"Duplicate email found in batch: '{email}'")
        else:
            seen_emails.add(email)
            
        # Extract scores dynamically
        scores = {}
        for key in ["dsa_score", "python_score", "communication_score"]:
            col_name = column_mapping.get(key)
            if col_name and pd.notna(row.get(col_name)):
                val = row.get(col_name)
                try:
                    scores[STANDARD_FIELDS[key]['label']] = float(val) if '.' in str(val) else int(val)
                except (ValueError, TypeError):
                    scores[STANDARD_FIELDS[key]['label']] = str(val)
                    
        # Extract remaining numerical/score columns as custom scores
        unmapped_cols = [c for c in df.columns if c not in column_mapping.values()]
        custom_data = {}
        for c in unmapped_cols:
            if pd.notna(row[c]):
                val = row[c]
                if isinstance(val, (int, float)):
                    scores[str(c)] = val
                else:
                    custom_data[str(c)] = str(val)
                    
        comments = str(row[comments_col]).strip() if comments_col and pd.notna(row[comments_col]) else ""
        strengths = str(row[strengths_col]).strip() if strengths_col and pd.notna(row[strengths_col]) else ""
        weaknesses = str(row[weaknesses_col]).strip() if weaknesses_col and pd.notna(row[weaknesses_col]) else ""
        
        student_obj = {
            "row_num": row_num,
            "name": name,
            "email": email,
            "scores": scores,
            "interviewer_comments": comments,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "custom_data": custom_data,
            "is_valid": len(errors) == 0,
            "validation_errors": errors
        }
        students.append(student_obj)
        
    total_students = len(students)
    valid_count = sum(1 for s in students if s["is_valid"])
    problem_count = total_students - valid_count
    
    return {
        "students": students,
        "total_students": total_students,
        "valid_count": valid_count,
        "problem_count": problem_count
    }
