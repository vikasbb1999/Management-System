import streamlit as st
import pandas as pd
import gspread

from sidebar import render_sidebar  # Import the sidebar component

st.set_page_config(page_title="View Ledger", layout="wide")

# Render the custom sidebar settings at the bottom
render_sidebar()

st.set_page_config(page_title="Columns Configuration", layout="wide")
st.header("Manage Dynamic Structural Database Elements")

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
    gc = gspread.service_account(filename="excel-management-513006-e71d85907364.json")
    sh = gc.open("Management app")
    return sh.worksheet("Data"), sh.worksheet("Schema")

data_sheet, schema_sheet = get_sheets()
fields_config = schema_sheet.get_all_records()

def save_new_column(name, field_type, options_str):
    schema_sheet.append_row([name, field_type, options_str])
    current_headers = data_sheet.row_values(1)
    next_col_idx = len(current_headers) + 1
    data_sheet.update_cell(1, next_col_idx, name)

def delete_column_from_system(col_name_to_del):
    schema_records = schema_sheet.get_all_records()
    schema_sheet.clear()
    schema_sheet.append_row(["column_name", "type", "options"])
    
    updated_config_headers = []
    for row in schema_records:
        if row["column_name"] != col_name_to_del:
            schema_sheet.append_row([row["column_name"], row["type"], row["options"]])
            updated_config_headers.append(row["column_name"])
            
    data_sheet.update(range_name="A1", values=[updated_config_headers])

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("➕ Create Custom Tracking Field")
    with st.form("new_column_form", clear_on_submit=True):
        new_col_name = st.text_input("New Field Title / Header Name")
        new_col_type = st.selectbox("Field Control Type Mode", ["text", "date", "single select", "multi select"])
        new_col_options = st.text_area("Input Values (Separated with commas)", placeholder="e.g. Option1, Option2")
        
        submit_col = st.form_submit_button("Deploy Column Extension")
        if submit_col:
            if new_col_name:
                if new_col_name in [f["column_name"] for f in fields_config]:
                    st.error("A column with this name already exists.")
                else:
                    save_new_column(new_col_name, new_col_type, new_col_options)
                    st.cache_data.clear()
                    st.success(f"Column extension '{new_col_name}' added!")
                    st.rerun()
            else:
                st.error("Column label parameter cannot remain unassigned.")
                
with col_b:
    st.subheader("🗑️ Drop Active Column Attribute")
    all_current_cols = [f["column_name"] for f in fields_config]
    col_to_drop = st.selectbox("Select Target Column to Delete", [""] + all_current_cols)
    
    if col_to_drop:
        st.warning(f"Dropping column '{col_to_drop}' clears schema configurations.")
        confirm_col_drop = st.checkbox("Authorize structural layout alignment modification.")
        
        if st.button("Erase Tracking Column Attribute", type="primary", disabled=not confirm_col_drop):
            delete_column_from_system(col_to_drop)
            st.cache_data.clear()
            st.success(f"Column component '{col_to_drop}' successfully cleared.")
            st.rerun()
            
st.markdown("---")
st.subheader("Active Structural Layout Map Overview")
st.dataframe(pd.DataFrame(fields_config), use_container_width=True, height=200)