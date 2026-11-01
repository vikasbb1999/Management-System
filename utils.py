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

@st.cache_data(ttl=60)
def load_all_data():
    client = get_gspread_client()
    # Updated to match your exact Google Sheet name
    spreadsheet = client.open("Management app") 
    
    data_worksheet = spreadsheet.worksheet("Data")
    raw_data = data_worksheet.get_all_records()
    
    try:
        config_worksheet = spreadsheet.worksheet("Schema")
        fields_config = config_worksheet.get_all_records()
    except Exception:
        fields_config = []
        
    return raw_data, fields_config

def get_sheets_raw():
    client = get_gspread_client()
    spreadsheet = client.open("Management app") # Updated here too
    data_worksheet = spreadsheet.worksheet("Data")
    config_worksheet = spreadsheet.worksheet("FieldsConfig")
    return data_worksheet, config_worksheet