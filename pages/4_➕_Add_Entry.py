import streamlit as st
import gspread
# Import the shared client from your utils.py
from utils import get_gspread_client

st.set_page_config(page_title="Add New Entry", layout="wide")
st.header("Insert Management System Entry")

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
fields_config = schema_sheet.get_all_records()

with st.form("create_record_form", clear_on_submit=True):
    form_inputs = {}
    add_cols = st.columns(2)
    
    for idx, field in enumerate(fields_config):
        name = field["column_name"]
        f_type = field["type"]
        opts = [o.strip() for o in field["options"].split(",")] if field["options"] else []
        
        with add_cols[idx % 2]:
            if f_type == "date":
                form_inputs[name] = st.date_input(name).strftime("%Y-%m-%d")
            elif f_type == "single select":
                form_inputs[name] = st.selectbox(name, opts if opts else [""])
            elif f_type == "multi select":
                selected_opts = st.multiselect(name, opts if opts else [])
                form_inputs[name] = ", ".join(selected_opts)
            else:
                form_inputs[name] = st.text_input(name)
                
    submit_record = st.form_submit_button("Commit Entry To Sheet", type="primary")
    if submit_record:
        ordered_row = [form_inputs[field["column_name"]] for field in fields_config]
        data_sheet.append_row(ordered_row)
        st.cache_data.clear()
        st.success("New record successfully saved to Google Sheets!")
        # (Note: clear_on_submit=True already clears the form, st.rerun() optional here)