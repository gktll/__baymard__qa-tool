import os
import pandas as pd
import streamlit as st

UPLOAD_FOLDER = "uploaded_files"

def save_uploaded_file(uploaded_file):
    """Saves uploaded file to a designated folder and returns its path."""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path


def load_csv(file_path: str) -> pd.DataFrame:
    """Load and clean CSV file **before any other processing**."""
    try:
        df = pd.read_csv(file_path)

        # 🔹 **Standardize Column Names (Remove Extra Spaces)**
        df.columns = df.columns.str.strip()

        # 🔹 **Drop Completely Empty Columns**
        df.dropna(axis=1, how="all", inplace=True)

        # 🔹 **Drop Rows Where Key Fields Are Empty**
        df.dropna(subset=['Case Study Title', 'Title', 'Catalog Theme Title'], how='any', inplace=True)

        # 🔹 **Drop Rows Where 'Citation Code: Platform-Specific' Is NaN or Empty**
        df.dropna(subset=['Citation Code: Platform-Specific'], inplace=True)

        # 🔹 **Remove Empty Strings in 'Citation Code: Platform-Specific'**
        df = df[df['Citation Code: Platform-Specific'].astype(str).str.strip() != ""]

        return df
        
    except Exception as e:
        print(f"Error loading file: {e}")
        return None


# Required columns based on your description
REQUIRED_COLUMNS = [
    "Citation Code: Platform-Specific", "Review Title", "Case Study Title", "Judgement", "Title"
]

def validate_csv(df):
    """
    Validates the uploaded CSV by checking:
    - Presence of required columns.
    - Ensuring no entirely empty rows.
    - Checking proper format for 'Citation Code: Platform-Specific'.
    
    Returns:
        bool: True if valid, False otherwise.
    """
    if df is None or df.empty:
        st.error("CSV file is empty.")
        return False

    # Check if all required columns are present
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
        return False

    # Remove completely empty rows
    df.dropna(how="all", inplace=True)

    # Validate 'Citation Code: Platform-Specific' (must contain platform ID)
    if not df["Citation Code: Platform-Specific"].astype(str).str.match(r"#289[DMA]").any():
        st.error("Invalid or missing platform identifiers in 'Citation Code: Platform-Specific'. Expected values: #289D (Desktop), #289M (Mobile), #289A (App).")
        return False

    return True