import streamlit as st
import gspread
# Import the shared client from your utils.py
from utils import get_gspread_client

st.set_page_config(page_title="Delete Record", layout="wide")
st.header("🗑️ Destructive Entry Disposal")

from sidebar import render_sidebar  # Import the sidebar component

st.set_page_config(page_title="View Ledger", layout="wide")

# Render the custom sidebar settings at the bottom
render_sidebar()

st.markdown("""
    <style>
        header[data-testid="stHeader"] {
            display: none !important;
        }
        .block-container {
            padding-top: 0.3rem !important;
            padding-bottom: 2rem !important;
            max-width: 100% !important;
        }
        body, html, [data-testid="stAppViewContainer"] {
            overflow-y: auto !important;
        }
        
        /* Permanently keep sidebar open & hide collapse toggle */
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }

        /* --- MAXIMUM READABILITY GLOBAL FONT SIZE INCREASE --- */
        html, body, [class*="st"] {
            font-size: 20px !important; /* Large, comfortable base font size */
        }
        
        /* Boost form inputs, dropdown select boxes, labels, and textboxes */
        input, select, textarea, label, .stSelectbox div, .stTextInput div {
            font-size: 19px !important;
        }
        
        /* Enlarge main titles and headers for easy scanning */
        h1 {
            font-size: 34px !important;
        }
        h2 {
            font-size: 28px !important;
        }
        h3 {
            font-size: 24px !important;
        }
        
        /* Enlarge table text and expand row heights for effortless reading */
        [data-testid="stDataFrame"] div, 
        [data-testid="stDataFrame"] span, 
        [data-testid="stDataFrame"] th, 
        [data-testid="stDataFrame"] td {
            font-size: 18px !important;
        }
        [data-testid="stDataFrame"] th div {
            font-size: 19px !important;
            font-weight: bold !important;
        }
        [data-testid="stDataFrame"] tr {
            height: 50px !important; /* Taller rows so text never looks cramped */
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_sheets():
    # Use the secure shared client instead of looking for a local json file
    gc = get_gspread_client()
    spreadsheet = gc.open("Management app")
    data_worksheet = spreadsheet.worksheet("Data")
    config_worksheet = spreadsheet.worksheet("FieldsConfig")
    return data_worksheet, config_worksheet

data_sheet, schema_sheet = get_sheets()
raw_data = data_sheet.get_all_records()

if not raw_data:
    st.info("No active records available to delete.")
else:
    del_cts_filter = st.text_input("🔍 Filter options by CTS/U no (Optional)", placeholder="Type full or partial CTS/U no...")
    
    filtered_del_rows = []
    for idx, r in enumerate(raw_data):
        cts_val = str(r.get('CTS/U no', ''))
        if not del_cts_filter or del_cts_filter.lower() in cts_val.lower():
            filtered_del_rows.append((idx, r))
            
    del_row_options = [f"Row {idx + 2}: {r.get('Client name', 'No Name')} (CTS/U: {r.get('CTS/U no', 'N/A')})" for idx, r in filtered_del_rows]
    
    if not del_row_options:
        st.warning("No records matched your CTS/U search filter.")
    else:
        selected_del_label = st.selectbox("Select Target Entry to Permanently Erase", del_row_options)
        
        if selected_del_label:
            target_row_idx = int(selected_del_label.split(":")[0].replace("Row ", "").strip())
            st.error(f"Attention: You are initializing deletion procedures for: **{selected_del_label}**.")
            safety_lock = st.checkbox("Verify system authorization override request.")
            
            delete_btn = st.button("Purge Entry Row from Ledger", type="primary", disabled=not safety_lock)
            if delete_btn:
                data_sheet.delete_rows(target_row_idx)
                # Example inside your Add/Edit/Delete forms after saving:
                st.cache_data.clear()
                st.success("Target row removed from ledger registry database successfully.")
                st.rerun()