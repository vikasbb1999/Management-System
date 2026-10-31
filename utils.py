# utils.py
import streamlit as st
import gspread

@st.cache_resource
def get_gspread_client():
    """Caches the gspread connection client securely."""
    return gspread.service_account(filename="excel-management-513006-e71d85907364.json")

@st.cache_data(ttl=60)
def load_all_data():
    """Fetches records and schema with a 60-second cache to prevent network lag."""
    gc = get_gspread_client()
    sh = gc.open("Management app")
    
    data_sheet = sh.worksheet("Data")
    schema_sheet = sh.worksheet("Schema")
    
    raw_data = data_sheet.get_all_records()
    fields_config = schema_sheet.get_all_records()
    
    return raw_data, fields_config

def get_sheets_raw():
    """Returns raw worksheet objects for performing write/update operations."""
    gc = get_gspread_client()
    sh = gc.open("Management app")
    return sh.worksheet("Data"), sh.worksheet("Schema")