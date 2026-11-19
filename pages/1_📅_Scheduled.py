import streamlit as st
import pandas as pd
import datetime
from utils import load_schedule_data, get_data_and_schedule_sheets
from sidebar import render_sidebar


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
            font-size: 20px !important;
        }
        input, select, textarea, label, .stSelectbox div, .stTextInput div {
            font-size: 19px !important;
        }
        h1 {
            font-size: 34px !important;
        }
        h2 {
            font-size: 28px !important;
        }
        h3 {
            font-size: 24px !important;
        }
        
        /* Enlarge table text and expand row heights */
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
            height: 50px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Scheduled Sites", layout="wide")
render_sidebar()


def format_cell_value(val):
    if pd.isna(val) or val is None:
        return ""
    if isinstance(val, (pd.Timestamp, datetime.date, datetime.datetime)):
        return pd.to_datetime(val).strftime("%Y-%m-%d")
    return str(val).strip()


def build_aligned_data_row(row_dict, data_headers):
    """
    Matches columns strictly against the Data worksheet headers.
    If any status column is missing or blank, sets it to 'incomplete'.
    """
    status_columns = {"desk 1 status", "desk 2 status", "final status"}
    # Case-insensitive lookup of the scheduled row's values
    normalized_row = {str(k).strip().lower(): format_cell_value(v) for k, v in row_dict.items()}

    aligned_values = []
    for col in data_headers:
        clean_col = str(col).strip()
        col_lower = clean_col.lower()
        val = normalized_row.get(col_lower, "")

        # Mark missing or empty status columns as 'incomplete'
        if (col_lower in status_columns or "status" in col_lower) and not val:
            val = "incomplete"

        aligned_values.append(val)
    return aligned_values


@st.dialog("➕ Add Scheduled Task")
def add_schedule_dialog(headers, schedule_sheet):
    with st.form("add_scheduled_task_form", clear_on_submit=True):
        inputs = {}
        for col in headers:
            if "date" in col.lower():
                inputs[col] = st.date_input(col, value=datetime.date.today())
            else:
                inputs[col] = st.text_input(col, placeholder=f"Enter {col}...")

        if st.form_submit_button("Save Scheduled Task", type="primary"):
            row_values = [format_cell_value(inputs[col]) for col in headers]
            schedule_sheet.append_row(row_values, value_input_option="USER_ENTERED")
            st.cache_data.clear()
            st.success("Scheduled task added!")
            st.rerun()


@st.dialog("✏️ Edit Scheduled Task")
def edit_schedule_dialog(headers, row_data, sheet_row_num, schedule_sheet):
    with st.form(f"edit_scheduled_task_form_{sheet_row_num}"):
        inputs = {}
        for col in headers:
            current_val = format_cell_value(row_data.get(col, ""))
            if "date" in col.lower():
                try:
                    parsed_date = pd.to_datetime(current_val).date() if current_val else datetime.date.today()
                except Exception:
                    parsed_date = datetime.date.today()
                inputs[col] = st.date_input(col, value=parsed_date)
            else:
                inputs[col] = st.text_input(col, value=current_val)

        if st.form_submit_button("Update Task", type="primary"):
            updated_values = [format_cell_value(inputs[col]) for col in headers]
            schedule_sheet.update(range_name=f"A{sheet_row_num}", values=[updated_values])
            st.cache_data.clear()
            st.success("Scheduled task updated!")
            st.rerun()


try:
    schedule_records = load_schedule_data()
    data_sheet, schedule_sheet = get_data_and_schedule_sheets()
except Exception as e:
    st.error(f"Could not connect to 'Schedule' tab: {e}")
    schedule_records = []
    data_sheet = None
    schedule_sheet = None

# Resolve headers from Schedule tab (fallback to Data tab if Schedule row 1 is empty)
sheet_headers = []
if schedule_sheet is not None:
    sheet_headers = schedule_sheet.row_values(1)
if not sheet_headers and data_sheet is not None:
    sheet_headers = data_sheet.row_values(1)
if not sheet_headers and schedule_records:
    sheet_headers = list(schedule_records[0].keys())

title_col, add_col = st.columns([6, 1])
with title_col:
    st.header("📅 Scheduled Sites")
with add_col:
    st.write("")
    if st.button("➕ Add", key="open_add_schedule_popup", type="primary", use_container_width=True):
        if sheet_headers and schedule_sheet is not None:
            add_schedule_dialog(sheet_headers, schedule_sheet)
        else:
            st.warning("Please make sure your 'Schedule' tab has column headers in row 1.")

st.markdown("Use **Done** to move completed tasks into the **Data** tab, **Edit** to update a task, or **Delete** to remove it.")

if schedule_records:
    df = pd.DataFrame(schedule_records)
    display_headers = sheet_headers if sheet_headers else list(df.columns)

    # Action columns (Done, Edit, Delete) at the start of each row
    col_widths = [0.9, 0.8, 0.9] + [2] * len(display_headers)
    header_cols = st.columns(col_widths)
    header_cols[0].markdown("**Done**")
    header_cols[1].markdown("**Edit**")
    header_cols[2].markdown("**Delete**")
    for i, col_name in enumerate(display_headers):
        header_cols[i + 3].markdown(f"**{col_name}**")

    st.divider()

    for idx, row in df.iterrows():
        row_cols = st.columns(col_widths)
        sheet_row_num = int(idx) + 2  # Row 1 is headers in Google Sheets
        row_dict = row.to_dict()

        # 1. DONE BUTTON -> Aligns to Data sheet headers, marks missing status as 'incomplete', moves to Data
        with row_cols[0]:
            if st.button("✅ Done", key=f"done_btn_{idx}", type="primary"):
                with st.spinner("Moving to Data..."):
                    data_ws, sched_ws = get_data_and_schedule_sheets()
                    data_headers = data_ws.row_values(1)
                    if not data_headers:
                        st.error("The 'Data' worksheet has no header row.")
                    else:
                        aligned_values = build_aligned_data_row(row_dict, data_headers)
                        data_ws.append_row(aligned_values, value_input_option="USER_ENTERED")
                        sched_ws.delete_rows(sheet_row_num)
                        st.cache_data.clear()
                        st.success("Moved to Data tab!")
                        st.rerun()

        # 2. EDIT BUTTON -> Opens modal to edit row in Schedule tab
        with row_cols[1]:
            if st.button("✏️ Edit", key=f"edit_btn_{idx}"):
                _, sched_ws = get_data_and_schedule_sheets()
                edit_schedule_dialog(display_headers, row_dict, sheet_row_num, sched_ws)

        # 3. DELETE BUTTON -> Deletes row from Schedule tab
        with row_cols[2]:
            if st.button("🗑️ Del", key=f"del_btn_{idx}"):
                with st.spinner("Deleting..."):
                    _, sched_ws = get_data_and_schedule_sheets()
                    sched_ws.delete_rows(sheet_row_num)
                    st.cache_data.clear()
                    st.success("Deleted scheduled task.")
                    st.rerun()

        # Row Data Columns
        for i, col_name in enumerate(display_headers):
            row_cols[i + 3].write(row.get(col_name, ""))

else:
    st.info("No scheduled sites in the 'Schedule' tab right now. Click **➕ Add** to create one.")