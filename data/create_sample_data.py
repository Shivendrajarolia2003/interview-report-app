import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
SAMPLE_FILE = DATA_DIR / "sample_input.xlsx"

sample_data = [
    {
        "Student Name": "Rahul Sharma",
        "Student Email": "rahul.sharma@example.com",
        "Interview Date": "2026-10-01",
        "DSA Score": 7,
        "Python Score": 9,
        "Communication Score": 8,
        "Interviewer Comments": "Good technical foundation with strong Python skills. Needs improvement in complex DSA problem solving and explanation clarity.",
        "Strengths": "Python OOP, Problem Decomposition, Quick Learner",
        "Weaknesses": "Trees & Graphs, Explanation structure under time pressure"
    },
    {
        "Student Name": "Priya Patel",
        "Student Email": "priya.patel@example.com",
        "Interview Date": "2026-10-01",
        "DSA Score": 5,
        "Python Score": 8,
        "Communication Score": 7,
        "Interviewer Comments": "Conceptually good in basic syntax, needs more practical practice on algorithmic complexity.",
        "Strengths": "Clean code writing, Logical reasoning",
        "Weaknesses": "Time complexity optimization, Dynamic Programming"
    },
    {
        "Student Name": "Aman Verma",
        "Student Email": "aman.verma@example.com",
        "Interview Date": "2026-10-02",
        "DSA Score": 9,
        "Python Score": 7,
        "Communication Score": 6,
        "Interviewer Comments": "Strong algorithmic problem solving capabilities. Communication could be more concise.",
        "Strengths": "Recursion, Array Manipulation, Fast coding",
        "Weaknesses": "Verbalizing thought process, Talking too fast"
    },
    {
        "Student Name": "Sneha Reddy",
        "Student Email": "sneha.invalid-email", # Invalid email for validation testing
        "Interview Date": "2026-10-02",
        "DSA Score": 8,
        "Python Score": 8,
        "Communication Score": 9,
        "Interviewer Comments": "Excellent communication and structured thinking. Solved problem using optimal approach.",
        "Strengths": "System design concepts, Articulate answers",
        "Weaknesses": "Minor edge case handling"
    },
    {
        "Student Name": "Rahul Sharma (Duplicate)",
        "Student Email": "rahul.sharma@example.com", # Duplicate email for validation testing
        "Interview Date": "2026-10-03",
        "DSA Score": 6,
        "Python Score": 6,
        "Communication Score": 7,
        "Interviewer Comments": "Average performance across topics. Retest recommended.",
        "Strengths": "Basic data structures",
        "Weaknesses": "Advanced Python features"
    }
]

def generate_sample_excel():
    df = pd.DataFrame(sample_data)
    df.to_excel(SAMPLE_FILE, index=False, engine='openpyxl')
    print(f"Sample Excel generated successfully at: {SAMPLE_FILE}")

if __name__ == "__main__":
    generate_sample_excel()
