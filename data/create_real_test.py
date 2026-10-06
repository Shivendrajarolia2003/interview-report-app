import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
REAL_TEST_FILE = DATA_DIR / "real_test.xlsx"

real_data = [
    {
        "Student Name": "Shivendra Jaroliya (Test Candidate)",
        "Student Email": "shivendrajaroliya2003@gmail.com",
        "Interview Date": "2026-10-06",
        "DSA Score": 9,
        "Python Score": 9,
        "Communication Score": 8,
        "Interviewer Comments": "Excellent problem solving capabilities. Solved complex DSA algorithms efficiently and explained logic clearly.",
        "Strengths": "Python OOP, Dynamic Programming, Clear explanation",
        "Weaknesses": "Minor edge case handling under strict time limits"
    }
]

def generate_real_excel():
    df = pd.DataFrame(real_data)
    df.to_excel(REAL_TEST_FILE, index=False, engine='openpyxl')
    print(f"Real test Excel generated at: {REAL_TEST_FILE}")

if __name__ == "__main__":
    generate_real_excel()
