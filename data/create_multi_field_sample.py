import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
MULTI_FIELD_FILE = DATA_DIR / "multi_field_students.xlsx"

multi_field_data = [
    {
        "Student Name": "Aarav Sharma",
        "Student Email": "aarav.sharma01@gmail.com",
        "Career Field": "Software Engineer",
        "Interview Date": "2026-09-15",
        "Scores": "K1: 8, K2: 9, K3: 8, K4: 8 (Overall: 42/50)",
        "Key Strengths": "Good coding skills, clear problem solving approach",
        "Weaknesses": "Can improve system design knowledge",
        "Interviewer Comments": "Strong candidate with good technical foundation and positive attitude."
    },
    {
        "Student Name": "Priya Verma",
        "Student Email": "priya.verma22@gmail.com",
        "Career Field": "Doctor (MBBS)",
        "Interview Date": "2026-09-15",
        "Scores": "K1: 7, K2: 8, K3: 8, K4: 7 (Overall: 40/50)",
        "Key Strengths": "Good clinical understanding and empathetic communication",
        "Weaknesses": "Can improve confidence in complex case discussions",
        "Interviewer Comments": "Shows strong interest in patient care and continuous learning."
    },
    {
        "Student Name": "Rohan Mehta",
        "Student Email": "rohan.mehta03@gmail.com",
        "Career Field": "IAS Officer (Civil Services)",
        "Interview Date": "2026-09-15",
        "Scores": "K1: 8, K2: 7, K3: 8, K4: 8 (Overall: 41/50)",
        "Key Strengths": "Good awareness of current affairs and logical reasoning",
        "Weaknesses": "Needs deeper knowledge of economic policies",
        "Interviewer Comments": "Confident and well-informed. Good potential for administrative roles."
    },
    {
        "Student Name": "Sneha Patel",
        "Student Email": "sneha.patel04@gmail.com",
        "Career Field": "Agricultural Scientist",
        "Interview Date": "2026-09-15",
        "Scores": "K1: 7, K2: 8, K3: 7, K4: 7 (Overall: 39/50)",
        "Key Strengths": "Good understanding of modern farming techniques",
        "Weaknesses": "Can improve data analysis of field results",
        "Interviewer Comments": "Shows genuine interest in agriculture and rural development."
    },
    {
        "Student Name": "Karan Singh",
        "Student Email": "karan.singh05@gmail.com",
        "Career Field": "Entrepreneur (Business)",
        "Interview Date": "2026-09-15",
        "Scores": "K1: 8, K2: 7, K3: 9, K4: 8 (Overall: 42/50)",
        "Key Strengths": "Innovative thinking and clear execution plan",
        "Weaknesses": "Needs stronger financial planning knowledge",
        "Interviewer Comments": "Very good ideas and understanding of market dynamics."
    },
    {
        "Student Name": "Ananya Gupta",
        "Student Email": "ananya.gupta06@gmail.com",
        "Career Field": "Research Scientist",
        "Interview Date": "2026-09-15",
        "Scores": "K1: 8, K2: 8, K3: 7, K4: 8 (Overall: 41/50)",
        "Key Strengths": "Strong analytical skills and good subject knowledge",
        "Weaknesses": "Can improve research paper writing and presentation skills",
        "Interviewer Comments": "Highly knowledgeable and curious. Good potential for academic research."
    },
    {
        "Student Name": "Vikram Joshi",
        "Student Email": "vikram.joshi07@gmail.com",
        "Career Field": "Teacher (Education)",
        "Interview Date": "2026-09-15",
        "Scores": "K1: 7, K2: 8, K3: 8, K4: 8 (Overall: 41/50)",
        "Key Strengths": "Excellent subject knowledge and teaching approach",
        "Weaknesses": "Can improve use of digital teaching tools",
        "Interviewer Comments": "Very good explanation skills and student-friendly approach."
    },
    {
        "Student Name": "Isha Nair",
        "Student Email": "isha.nair08@gmail.com",
        "Career Field": "Lawyer (Law / Judiciary)",
        "Interview Date": "2026-09-15",
        "Scores": "K1: 8, K2: 7, K3: 8, K4: 7 (Overall: 40/50)",
        "Key Strengths": "Good legal knowledge and strong arguments",
        "Weaknesses": "Needs more real-world case exposure",
        "Interviewer Comments": "Confident and articulate. Shows good understanding of legal principles."
    },
    {
        "Student Name": "Aditya Kulkarni",
        "Student Email": "aditya.kulkarni09@gmail.com",
        "Career Field": "Designer (UI/UX)",
        "Interview Date": "2026-09-15",
        "Scores": "K1: 8, K2: 8, K3: 8, K4: 7 (Overall: 41/50)",
        "Key Strengths": "Creative ideas and strong portfolio",
        "Weaknesses": "Can improve user research depth",
        "Interviewer Comments": "Good design sense and understanding of user needs."
    },
    {
        "Student Name": "Neha Reddy",
        "Student Email": "neha.reddy10@gmail.com",
        "Career Field": "Data Analyst",
        "Interview Date": "2026-09-15",
        "Scores": "K1: 8, K2: 8, K3: 9, K4: 8 (Overall: 43/50)",
        "Key Strengths": "Strong analytical skills and good data visualization",
        "Weaknesses": "Can improve advanced machine learning knowledge",
        "Interviewer Comments": "Detail-oriented and good with data-driven insights."
    }
]

def generate_multi_field_excel():
    df = pd.DataFrame(multi_field_data)
    df.to_excel(MULTI_FIELD_FILE, index=False, engine='openpyxl')
    print(f"Multi-field Excel generated at: {MULTI_FIELD_FILE}")

if __name__ == "__main__":
    generate_multi_field_excel()
