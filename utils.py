import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

def get_gspread_client():
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Check if running on Streamlit Cloud using st.secrets
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return gspread.authorize(creds)
    else:
        # Fallback for local testing if JSON file exists
        return gspread.service_account(filename="excel-management-513006-e71d85907364.json")