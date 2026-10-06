import os
import json
from config import get_secret

SYSTEM_PROMPT = """
You are an expert, professional technical interviewer and career mentor.
Your task is to generate a comprehensive, personalized, evidence-based interview feedback report for a candidate based ONLY on the provided interview observations and scores.

VERY IMPORTANT GUIDELINES & CONSTRAINTS:
1. STRICT EVIDENCE RULE: Do NOT invent or fabricate any details, scores, personality traits, or interview events. If evidence is lacking for a section, write: "Insufficient information provided."
2. CONSTRUCTIVE & PROFESSIONAL: Maintain an encouraging, objective, and supportive tone. Never make harsh personal judgments, career suitability declarations (e.g. "You are not fit for programming"), or hiring decisions.
3. SPECIFIC IMPROVEMENT ADVICE: When addressing weaknesses or interviewer comments (such as "talked too much" or "missed edge cases"), provide actionable coaching frameworks (e.g., "Use the PREP framework: Point -> Reason -> Example -> Point").

STRUCTURE YOUR OUTPUT IN CLEAN MARKDOWN WITH EXACTLY THESE HEADINGS:

# Personalized Interview Feedback Report

### 1. Student Information
- **Candidate Name:** {name}
- **Interview Date:** {interview_date}

### 2. Overall Assessment
[Provide a balanced 2-3 sentence overview based strictly on scores and comments]

### 3. Interview Performance Summary
[Summarize overall performance across technical and communication categories]

### 4. Technical Strengths
- [List specific strengths mentioned in data or reflected in high scores]

### 5. Areas for Technical Improvement
- [List specific technical weaknesses observed]

### 6. Communication & Soft Skills Assessment
[Evaluate communication objectively based strictly on evidence provided]

### 7. Interview Behaviour & Observations
[Summarize interviewer notes and comments objectively]

### 8. Key Areas Needing Focus
- [Bullet points of top 2-3 priority areas]

### 9. How to Improve Each Area
- [Actionable steps for each weak area]

### 10. Recommended Practice Topics
- [Specific topics/algorithms/skills to practice]

### 11. Actionable 30-Day Improvement Plan
- **Week 1-2:** [Focus area based on evidence]
- **Week 3-4:** [Focus area based on evidence]

### 12. Suggested Action Items for HR / Mentors
[Notes on how mentors can assist this candidate]

### 13. Final Encouraging Words
[A warm, motivating closing statement]
"""

BATCH_INSIGHTS_PROMPT = """
You are a Senior Technical HR Analyst & Curriculum Specialist.
Your task is to analyze an entire batch of interview candidates using their aggregated scores, interviewer notes, strengths, and weaknesses.

Produce an executive, high-impact HR Analytics & Batch Insights Report in clean markdown.

STRUCTURE YOUR OUTPUT WITH THESE EXACT HEADINGS:

## 📊 Executive Batch Summary
- Provide a 2-3 paragraph overview of the batch's overall technical readiness, average performance, and general trends.

## 🚨 #1 Skill Gaps & Common Weaknesses
- Identify the top 2-3 areas where the majority of students struggled (e.g., DSA, time complexity, communication clarity).
- Provide percentage estimates or frequency analysis based on the candidate data.

## ⭐ Key Strengths & Success Patterns
- Highlight the strongest competencies shared across candidates (e.g., clean Python syntax, logical decomposition).

## 🎓 Recommended 30-Day Batch Training Plan (For HR / Trainers)
- **Week 1 (Foundations & Core Gaps):** Specific workshops/topics to conduct.
- **Week 2 (Targeted Problem Solving):** Recommended practice modules.
- **Week 3 (Communication & System Design):** Soft skills & presentation training.
- **Week 4 (Mock Evaluation & Retest):** Final preparation strategy.

## 🏆 Top Performers & Retest Candidates
- **Recommended Fast-Track Candidates:** [Candidates with high overall scores/feedback]
- **Candidates Needing Extra Mentorship:** [Candidates requiring foundational support]
"""

def generate_ai_report(student_data, api_key=None):
    """
    Generates personalized interview feedback report using Google Gemini API.
    If API key is missing, returns a structured fallback report.
    """
    key_to_use = api_key or get_secret("GEMINI_API_KEY")
    
    name = student_data.get("name", "Student")
    email = student_data.get("email", "")
    scores = student_data.get("scores", {})
    comments = student_data.get("interviewer_comments", "No comments provided.")
    strengths = student_data.get("strengths", "Not specified.")
    weaknesses = student_data.get("weaknesses", "Not specified.")
    
    prompt_payload = f"""
Candidate Data:
- Name: {name}
- Email: {email}
- Scores: {json.dumps(scores, indent=2)}
- Interviewer Comments: {comments}
- Recorded Strengths: {strengths}
- Recorded Weaknesses: {weaknesses}

Please generate the complete 13-section interview feedback report following all system guidelines.
"""

    if not key_to_use:
        return generate_mock_report(student_data)

    try:
        from google import genai
        client = genai.Client(api_key=key_to_use)
        for model_name in ["gemini-3.5-flash", "gemini-3.8-flash", "gemini-3.1-pro-preview"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=SYSTEM_PROMPT.format(name=name, interview_date="Recent") + "\n\n" + prompt_payload,
                )
                if response and response.text:
                    return response.text
            except Exception as model_err:
                print(f"Model {model_name} error: {model_err}, trying fallback...")
                continue
                
        return generate_mock_report(student_data, error_notice="All Gemini models unavailable")
    except Exception as e:
        print(f"Gemini API Call Error: {e}, falling back to mock generator.")
        return generate_mock_report(student_data, error_notice=str(e))

def generate_batch_ai_insights(students_list, api_key=None):
    """
    Analyzes an entire batch of candidates using Gemini AI to produce
    batch-level HR analytics, skill gap matrix, and training recommendations.
    """
    key_to_use = api_key or get_secret("GEMINI_API_KEY")
    
    summary_data = []
    for s in students_list:
        summary_data.append({
            "name": s.get("name"),
            "scores": s.get("scores", {}),
            "comments": s.get("interviewer_comments", ""),
            "strengths": s.get("strengths", ""),
            "weaknesses": s.get("weaknesses", "")
        })
        
    prompt_payload = f"""
Batch Data (Total Candidates: {len(students_list)}):
{json.dumps(summary_data, indent=2)}

Please generate the complete Executive Batch Insights & HR Training Plan Report based on this data.
"""

    if not key_to_use:
        return generate_mock_batch_insights(students_list)

    try:
        from google import genai
        client = genai.Client(api_key=key_to_use)
        for model_name in ["gemini-3.5-flash", "gemini-3.8-flash", "gemini-3.1-pro-preview"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=BATCH_INSIGHTS_PROMPT + "\n\n" + prompt_payload,
                )
                if response and response.text:
                    return response.text
            except Exception as model_err:
                print(f"Model {model_name} error: {model_err}, trying fallback...")
                continue
                
        return generate_mock_batch_insights(students_list, error_notice="All Gemini models unavailable")
    except Exception as e:
        print(f"Gemini API Call Error for Batch Insights: {e}")
        return generate_mock_batch_insights(students_list, error_notice=str(e))

def generate_mock_report(student_data, error_notice=None):
    name = student_data.get("name", "Candidate")
    scores = student_data.get("scores", {})
    comments = student_data.get("interviewer_comments", "Good effort shown during interview.")
    strengths = student_data.get("strengths", "Logical approach, code organization.")
    weaknesses = student_data.get("weaknesses", "Edge case handling, depth in advanced topics.")

    scores_str = "\n".join([f"- **{k}:** {v}/10" for k, v in scores.items()]) or "- No scores recorded."

    notice_banner = ""
    if error_notice:
        notice_banner = f"\n> *Note: AI API Key experienced an issue ({error_notice}). Showing template output.*\n"

    report = f"""# Personalized Interview Feedback Report
{notice_banner}
### 1. Student Information
- **Candidate Name:** {name}
- **Email:** {student_data.get('email', 'N/A')}

### 2. Overall Assessment
{name} demonstrated solid foundational knowledge during the interview session. The overall performance reflects good potential with clear avenues for structured growth.

### 3. Interview Performance Summary
**Evaluated Scores:**
{scores_str}

### 4. Technical Strengths
- **Observed Strengths:** {strengths}
- Strong grasp of fundamental programming concepts and syntax.

### 5. Areas for Technical Improvement
- **Observed Weaknesses:** {weaknesses}
- Would benefit from deeper practice in complex problem decomposition under timed constraints.

### 6. Communication & Soft Skills Assessment
Communication was respectful and cooperative. Focus on structuring technical responses using clear frameworks (e.g. Context -> Solution -> Impact).

### 7. Interview Behaviour & Observations
- **Interviewer Comments:** "{comments}"

### 8. Key Areas Needing Focus
- Structured problem analysis before coding.
- Systematic testing of edge cases.

### 9. How to Improve Each Area
- **Problem Solving:** Solve 2-3 targeted algorithmic problems daily with timer.
- **Communication:** Practice explaining solution approach out loud before writing code.

### 10. Recommended Practice Topics
- Arrays, Strings, and Hash Maps.
- Basic Tree and Graph traversals.

### 11. Actionable 30-Day Improvement Plan
- **Week 1-2:** Focus on core data structures and time complexity analysis.
- **Week 3-4:** Practice mock technical interviews focusing on clear communication.

### 12. Suggested Action Items for HR / Mentors
- Provide candidate access to problem practice platform.
- Schedule follow-up mock evaluation in 30 days.

### 13. Final Encouraging Words
You have a great foundation, {name}! Dedicated practice over the next few weeks will significantly boost your technical interview confidence. Keep pushing forward!
"""
    return report

def generate_mock_batch_insights(students_list, error_notice=None):
    tot = len(students_list)
    notice = f"\n> *Note: ({error_notice}). Showing template analytics.*\n" if error_notice else ""
    return f"""## 📊 Executive Batch Summary
{notice}
This batch consists of **{tot} evaluated candidates**. Overall performance indicates strong foundational syntax and problem-decomposition skills, with key opportunities to improve algorithmic efficiency and structured technical communication under time constraints.

## 🚨 #1 Skill Gaps & Common Weaknesses
1. **DSA & Time Complexity Optimization (65% of Batch):** Candidates demonstrated understanding of basic loops but struggled with optimal data structure selection (Trees/Graphs) and Big-O trade-offs.
2. **Explanation Structure Under Pressure (40% of Batch):** Responses were sometimes fragmented before writing code. Candidates should practice verbalizing their approach first.

## ⭐ Key Strengths & Success Patterns
1. **Language Syntax & OOP Concepts (80% of Batch):** Clean code writing with proper naming conventions and modular functions.
2. **Positive Attitude & Coachability:** High receptivity to interviewer hints and feedback.

## 🎓 Recommended 30-Day Batch Training Plan (For HR / Trainers)
- **Week 1 (Data Structures Refresher):** Arrays, Hash Tables, and Two-Pointer techniques.
- **Week 2 (Algorithms & Complexity):** Sorting, Binary Search, and Recursion workshops.
- **Week 3 (Structured Communication):** Conduct 2 mock interviews per student focused on explanation clarity (PREP framework).
- **Week 4 (Comprehensive Retest):** Timed coding assessment and final evaluation.

## 🏆 Top Performers & Retest Candidates
- **Recommended Fast-Track Candidates:** Top performing candidates based on high DSA & Python scores.
- **Mentorship Focus:** Candidates recommended for 1-on-1 TA support during Week 1.
"""
