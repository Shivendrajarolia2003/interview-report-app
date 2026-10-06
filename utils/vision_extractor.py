import os
import json
import re
from PIL import Image
import pandas as pd
import streamlit as st
from config import get_secret

VISION_PROMPT = """
You are an expert OCR & Document Intelligence AI.
Analyze the uploaded image / document page which contains interview notes or a candidate evaluation matrix table.

The image may contain evaluation records for candidates across different professional fields (e.g., Software Engineer, Doctor, Lawyer, Teacher, Designer, Data Analyst, Entrepreneur, etc.).

STRICT INSTRUCTIONS:
1. Extract ALL candidate evaluation records present in the image table.
2. For EVERY candidate, extract:
   - "Student Name": Candidate Name
   - "Student Email": Email Address (If missing, generate a standard format like firstname.lastname@example.com)
   - "Career Field": Role/Field (e.g. Software Engineer, Doctor, Lawyer, Designer, Data Analyst, etc.)
   - "Interview Date": Date from sheet header or default to recent date
   - "Scores": Map all score columns (e.g. K1, K2, K3, K4 or overall score) as numerical values (1-10 or 1-50)
   - "Key Strengths": Strengths mentioned
   - "Weaknesses": Areas for Improvement mentioned
   - "Interviewer Comments": Observations/Comments

RETURN ONLY A VALID JSON ARRAY OF OBJECTS WITH NO MARKDOWN OR EXTRA TEXT. Example:
[
  {
    "Student Name": "Aarav Sharma",
    "Student Email": "aarav.sharma01@gmail.com",
    "Career Field": "Software Engineer",
    "Interview Date": "2026-09-15",
    "Scores": {"K1": 8, "K2": 9, "K3": 8, "K4": 8, "Overall": 42},
    "Key Strengths": "Good coding skills, clear problem solving approach",
    "Weaknesses": "Can improve system design knowledge",
    "Interviewer Comments": "Strong candidate with good technical foundation and positive attitude."
  }
]
"""

def extract_students_from_image(uploaded_image_file, api_key=None):
    """
    Uses Gemini Vision API to extract structured candidate data from photos
    of handwritten/printed interview assessment sheets, supporting multi-domain fields.
    """
    key_to_use = api_key or get_secret("GEMINI_API_KEY")
    
    if not key_to_use:
        return False, "Google Gemini API Key is missing. Please enter it in the Sidebar or configure Streamlit Secrets.", None

    try:
        from google import genai
        client = genai.Client(api_key=key_to_use)
        
        # Load image with PIL
        image = Image.open(uploaded_image_file)
        
        # Call Gemini Vision API with high-quota lite models
        response = None
        last_error = None
        for model_name in ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.6-flash", "gemini-3.8-flash"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[VISION_PROMPT, image]
                )
                if response and response.text:
                    break
            except Exception as err:
                last_error = str(err)
                continue
                
        if not response or not response.text:
            return False, f"Could not extract text from image. ({last_error or 'No response from API'}).", None
            
        raw_text = response.text.strip()
        
        # Clean JSON markdown if wrapped in ```json ... ```
        if "```" in raw_text:
            raw_text = re.sub(r'```json\s*', '', raw_text)
            raw_text = re.sub(r'```\s*', '', raw_text)
            
        student_records = json.loads(raw_text)
        if isinstance(student_records, dict):
            student_records = [student_records]
            
        for r in student_records:
            if "Key Strengths" in r and "strengths" not in r:
                r["strengths"] = r["Key Strengths"]
            if "Weaknesses" in r and "weaknesses" not in r:
                r["weaknesses"] = r["Weaknesses"]
                
        df = pd.DataFrame(student_records)
        return True, f"Successfully extracted {len(student_records)} student record(s) across different career fields!", df
        
    except Exception as e:
        return False, f"Vision OCR Error: {str(e)}", None
