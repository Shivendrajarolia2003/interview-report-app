import pandas as pd

def read_excel_file(uploaded_file):
    """
    Reads an uploaded Excel (.xlsx, .xls) or CSV file into a pandas DataFrame.
    """
    file_name = uploaded_file.name.lower()
    if file_name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    
    # Clean whitespace in column headers
    df.columns = [str(col).strip() for col in df.columns]
    return df
