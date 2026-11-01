import streamlit as st
import datetime
import gspread
from sidebar import render_sidebar  # Import the sidebar component

st.set_page_config(page_title="View Ledger", layout="wide")

# Render the custom sidebar settings at the bottom
render_sidebar()

# st.markdown("""
#     <style>
#         .block-container {
#             padding-top: 1.5rem;
#             padding-bottom: 2rem;
#         }
#     </style>
# """, unsafe_allow_html=True)

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

st.set_page_config(page_title="Edit Record", layout="wide")
st.header("📝 Modify Existing Row Cells")


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
fields_config = schema_sheet.get_all_records()

if not raw_data:
    st.info("No active records available to edit.")
else:
    edit_cts_filter = st.text_input("🔍 Filter options by CTS/U no (Optional)", placeholder="Type full or partial CTS/U no...")
    
    filtered_edit_rows = []
    for idx, r in enumerate(raw_data):
        cts_val = str(r.get('CTS/U no', ''))
        if not edit_cts_filter or edit_cts_filter.lower() in cts_val.lower():
            filtered_edit_rows.append((idx, r))
            
    edit_row_options = [f"Row {idx + 2}: {r.get('Client name', 'No Name')} (CTS/U: {r.get('CTS/U no', 'N/A')})" for idx, r in filtered_edit_rows]
    
    if not edit_row_options:
        st.warning("No records matched your CTS/U search filter.")
    else:
        selected_edit_label = st.selectbox("Select Target Entry to Update", edit_row_options)
        
        if selected_edit_label:
            target_row_idx = int(selected_edit_label.split(":")[0].replace("Row ", "").strip())
            current_row_data = raw_data[target_row_idx - 2]
            
            with st.form("edit_record_form"):
                st.write(f"Editing row entry values for: **{selected_edit_label}**")
                updated_inputs = {}
                form_cols = st.columns(2)
                
                for idx, field in enumerate(fields_config):
                    name = field["column_name"]
                    f_type = field["type"]
                    opts = [o.strip() for o in field["options"].split(",")] if field["options"] else []
                    current_val = str(current_row_data.get(name, ""))
                    
                    with form_cols[idx % 2]:
                        if f_type == "date":
                            try:
                                d_val = datetime.datetime.strptime(current_val, "%Y-%m-%d").date()
                            except:
                                d_val = datetime.date.today()
                            updated_inputs[name] = st.date_input(name, value=d_val).strftime("%Y-%m-%d")
                        elif f_type == "single select":
                            default_idx = opts.index(current_val) if current_val in opts else 0
                            updated_inputs[name] = st.selectbox(name, opts if opts else [" "], index=default_idx)
                        elif f_type == "multi select":
                            default_selected = [x.strip() for x in current_val.split(",")] if current_val else []
                            valid_defaults = [x for x in default_selected if x in opts]
                            selected_opts = st.multiselect(name, opts, default=valid_defaults)
                            updated_inputs[name] = ", ".join(selected_opts)
                        else:
                            updated_inputs[name] = st.text_input(name, value=current_val)
                            
                save_btn = st.form_submit_button("Save Row Changes", type="primary")
                if save_btn:
                    new_values = [updated_inputs[f["column_name"]] for f in fields_config]
                    data_sheet.update(range_name=f"A{target_row_idx}", values=[new_values])
                    # Example inside your Add/Edit/Delete forms after saving:
                    st.cache_data.clear()
                    st.success("Record row changes saved successfully!")
                    st.rerun()