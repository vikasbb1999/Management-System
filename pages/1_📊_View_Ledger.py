


# import streamlit as st
# import pandas as pd
# import datetime
# from utils import load_all_data, get_sheets_raw
# from sidebar import render_sidebar

# st.set_page_config(page_title="View & Status Editor", layout="wide")

# # --- CUSTOM CSS: MAXIMUM READABILITY, FIXED SIDEBAR, HIDE HEADER ---
# st.markdown("""
#     <style>
#         header[data-testid="stHeader"] {
#             display: none !important;
#         }
#         .block-container {
#             padding-top: 0.3rem !important;
#             padding-bottom: 2rem !important;
#             max-width: 100% !important;
#         }
#         body, html, [data-testid="stAppViewContainer"] {
#             overflow-y: auto !important;
#         }
        
#         /* Permanently keep sidebar open & hide collapse toggle */
#         [data-testid="stSidebarCollapseButton"] {
#             display: none !important;
#         }

#         /* --- MAXIMUM READABILITY GLOBAL FONT SIZE INCREASE --- */
#         html, body, [class*="st"] {
#             font-size: 20px !important;
#         }
#         input, select, textarea, label, .stSelectbox div, .stTextInput div {
#             font-size: 19px !important;
#         }
#         h1 {
#             font-size: 34px !important;
#         }
#         h2 {
#             font-size: 28px !important;
#         }
#         h3 {
#             font-size: 24px !important;
#         }
        
#         /* Enlarge table text and expand row heights */
#         [data-testid="stDataFrame"] div, 
#         [data-testid="stDataFrame"] span, 
#         [data-testid="stDataFrame"] th, 
#         [data-testid="stDataFrame"] td {
#             font-size: 18px !important;
#         }
#         [data-testid="stDataFrame"] th div {
#             font-size: 19px !important;
#             font-weight: bold !important;
#         }
#         [data-testid="stDataFrame"] tr {
#             height: 50px !important;
#         }
#     </style>
# """, unsafe_allow_html=True)

# render_sidebar()

# st.header("📋 Live System Spreadsheet Ledger & Status Updater")
# st.markdown("You can update **only** the 4 status columns (`Desk 1 Status`, `Desk 2 Status`, `Final Status`, and `Priority`) using the dropdown cells below. All other data fields are read-only.")

# # Fast load from cache
# raw_data, fields_config = load_all_data()

# if raw_data:
#     df = pd.DataFrame(raw_data)
#     total_records_count = len(df)
    
#     # --- FILTERS & SEARCH ---
#     col_f1, col_f2 = st.columns(2)
#     with col_f1:
#         search_query = st.text_input("🔍 Universal Search", placeholder="Type keyword/name/number...")
#     with col_f2:
#         status_options = ["All"] + list(df["Final Status"].unique()) if "Final Status" in df.columns else ["All"]
#         status_filter = st.selectbox("🎯 Filter Final Status", status_options)
        
#     filtered_df = df.copy()

#     if search_query:
#         mask = filtered_df.astype(str).apply(lambda col: col.str.contains(search_query, case=False, na=False)).any(axis=1)
#         filtered_df = filtered_df[mask]
        
#     if status_filter != "All":
#         filtered_df = filtered_df[filtered_df["Final Status"] == status_filter]
        
#     filtered_records_count = len(filtered_df)

#     # --- COLOR-CODED STATUS SUMMARY CARDS ---
#     if "Final Status" in filtered_df.columns:
#         done_count = len(filtered_df[filtered_df["Final Status"].str.lower().str.contains("done", na=False)])
#         progress_count = len(filtered_df[filtered_df["Final Status"].str.lower().str.contains("inprogress", na=False)])
#         incomplete_count = len(filtered_df[filtered_df["Final Status"].str.lower().str.contains("incomplete", na=False)])
#     else:
#         done_count = progress_count = incomplete_count = 0

#     m1, m2, m3, m4, m5 = st.columns(5)
#     with m1:
#         st.metric(label="Filtered Rows", value=filtered_records_count)
#     with m2:
#         st.metric(label="Total Database Rows", value=total_records_count)
#     with m3:
#         st.markdown(f'<div style="background-color: #d4edda; padding: 10px; border-radius: 8px; text-align: center;"><span style="color: #155724; font-size: 16px; font-weight: bold;">Done</span><br><span style="color: #155724; font-size: 24px; font-weight: bold;">{done_count}</span></div>', unsafe_allow_html=True)
#     with m4:
#         st.markdown(f'<div style="background-color: #ffe6cc; padding: 10px; border-radius: 8px; text-align: center;"><span style="color: #cc6600; font-size: 16px; font-weight: bold;">In Progress</span><br><span style="color: #cc6600; font-size: 24px; font-weight: bold;">{progress_count}</span></div>', unsafe_allow_html=True)
#     with m5:
#         st.markdown(f'<div style="background-color: #ffcccc; padding: 10px; border-radius: 8px; text-align: center;"><span style="color: #cc0000; font-size: 16px; font-weight: bold;">Incomplete</span><br><span style="color: #cc0000; font-size: 24px; font-weight: bold;">{incomplete_count}</span></div>', unsafe_allow_html=True)

#     st.markdown("---")

#     # --- ALLOW EDITING ONLY FOR THE 4 SPECIFIED COLUMNS ---
#     allowed_editable_columns = ["Desk 1 Status", "Desk 2 Status", "Final Status", "Priority"]

#     column_configs = {}
#     for field in fields_config:
#         col_name = field["column_name"]
#         f_type = field["type"]
#         opts_str = field["options"]
        
#         # If the column is one of the 4 allowed status fields, make it an editable dropdown
#         if col_name in allowed_editable_columns and opts_str:
#             options_list = [o.strip() for o in opts_str.split(",")]
#             column_configs[col_name] = st.column_config.SelectboxColumn(
#                 col_name,
#                 options=options_list,
#                 required=False
#             )
#         else:
#             # Everything else is locked as read-only to prevent accidental edits
#             column_configs[col_name] = st.column_config.Column(
#                 col_name,
#                 disabled=True
#             )

#     # --- INTERACTIVE EDITABLE TABLE (DATA EDITOR) ---
#     edited_df = st.data_editor(
#         filtered_df,
#         column_config=column_configs,
#         use_container_width=True,
#         height=480,
#         key="ledger_inline_editor"
#     )

#     # --- SAVE CHANGES BUTTON ---
#     if st.button("💾 Save Status Changes to Google Sheets", type="primary"):
#         with st.spinner("Updating Google Sheets with new status values..."):
#             data_sheet, _ = get_sheets_raw()
#             headers = df.columns.tolist()
            
#             update_count = 0
#             for idx, row in edited_df.iterrows():
#                 orig_row = df.loc[idx]
#                 if not row.equals(orig_row):
#                     sheet_row_num = idx + 2
                    
#                     row_values = []
#                     for col in headers:
#                         val = row[col]
#                         if pd.isna(val):
#                             row_values.append("")
#                         elif isinstance(val, (pd.Timestamp, datetime.date, datetime.datetime)):
#                             row_values.append(pd.to_datetime(val).strftime("%Y-%m-%d"))
#                         else:
#                             row_values.append(str(val))
                            
#                     data_sheet.update(range_name=f"A{sheet_row_num}", values=[row_values])
#                     update_count += 1
            
#             st.cache_data.clear()
#             st.success(f"Successfully updated status changes for {update_count} record(s) in Google Sheets!")
#             st.rerun()

# else:
#     st.info("No data ledger records found inside Google Sheets yet.")




import streamlit as st
import pandas as pd
import datetime
from utils import load_all_data, get_sheets_raw
from sidebar import render_sidebar

st.set_page_config(page_title="View & Status Editor", layout="wide")

# --- CUSTOM CSS: MAXIMUM READABILITY, FIXED SIDEBAR, HIDE HEADER ---
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

render_sidebar()

st.header("📋 Live System Spreadsheet Ledger & Status Updater")
st.markdown("You can update **only** the 4 status columns (`Desk 1 Status`, `Desk 2 Status`, `Final Status`, and `Priority`) using the dropdown cells below. All other data fields are read-only.")

# Fast load from cache
raw_data, fields_config = load_all_data()

if raw_data:
    df = pd.DataFrame(raw_data)
    total_records_count = len(df)
    
    # --- FILTERS & SEARCH ---
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        search_query = st.text_input("🔍 Universal Search", placeholder="Type keyword/name/number...")
    with col_f2:
        status_options = ["All"] + list(df["Final Status"].unique()) if "Final Status" in df.columns else ["All"]
        status_filter = st.selectbox("🎯 Filter Final Status", status_options)
        
    filtered_df = df.copy()

    if search_query:
        mask = filtered_df.astype(str).apply(lambda col: col.str.contains(search_query, case=False, na=False)).any(axis=1)
        filtered_df = filtered_df[mask]
        
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["Final Status"] == status_filter]
        
    filtered_records_count = len(filtered_df)

    # --- COLOR-CODED STATUS SUMMARY CARDS ---
    if "Final Status" in filtered_df.columns:
        done_count = len(filtered_df[filtered_df["Final Status"].str.lower().str.contains("done", na=False)])
        progress_count = len(filtered_df[filtered_df["Final Status"].str.lower().str.contains("inprogress", na=False)])
        incomplete_count = len(filtered_df[filtered_df["Final Status"].str.lower().str.contains("incomplete", na=False)])
    else:
        done_count = progress_count = incomplete_count = 0

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric(label="Filtered Rows", value=filtered_records_count)
    with m2:
        st.metric(label="Total Database Rows", value=total_records_count)
    with m3:
        st.markdown(f'<div style="background-color: #d4edda; padding: 10px; border-radius: 8px; text-align: center;"><span style="color: #155724; font-size: 16px; font-weight: bold;">Done</span><br><span style="color: #155724; font-size: 24px; font-weight: bold;">{done_count}</span></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div style="background-color: #ffe6cc; padding: 10px; border-radius: 8px; text-align: center;"><span style="color: #cc6600; font-size: 16px; font-weight: bold;">In Progress</span><br><span style="color: #cc6600; font-size: 24px; font-weight: bold;">{progress_count}</span></div>', unsafe_allow_html=True)
    with m5:
        st.markdown(f'<div style="background-color: #ffcccc; padding: 10px; border-radius: 8px; text-align: center;"><span style="color: #cc0000; font-size: 16px; font-weight: bold;">Incomplete</span><br><span style="color: #cc0000; font-size: 24px; font-weight: bold;">{incomplete_count}</span></div>', unsafe_allow_html=True)

    st.markdown("---")

    # --- ALLOW EDITING ONLY FOR THE 4 SPECIFIED COLUMNS ---
    allowed_editable_columns = ["Desk 1 Status", "Desk 2 Status", "Final Status", "Priority"]

    column_configs = {}
    for field in fields_config:
        col_name = field["column_name"]
        opts_str = field["options"]
        
        if col_name in allowed_editable_columns and opts_str:
            options_list = [o.strip() for o in opts_str.split(",")]
            column_configs[col_name] = st.column_config.SelectboxColumn(
                col_name,
                options=options_list,
                required=False
            )
        else:
            column_configs[col_name] = st.column_config.Column(
                col_name,
                disabled=True
            )

    # --- INTERACTIVE EDITABLE TABLE (DATA EDITOR) ---
    edited_df = st.data_editor(
        filtered_df,
        column_config=column_configs,
        use_container_width=True,
        height=480,
        key="ledger_inline_editor"
    )

    # --- SAVE CHANGES BUTTON ---
    if st.button("💾 Save Status Changes to Google Sheets", type="primary"):
        with st.spinner("Updating Google Sheets with new status values..."):
            data_sheet, _ = get_sheets_raw()
            headers = df.columns.tolist()
            
            update_count = 0
            # Iterate through the edited view and accurately map back to original master df indices
            for idx, row in edited_df.iterrows():
                orig_row = df.loc[idx]
                if not row.equals(orig_row):
                    # Google Sheets row numbers start at 2 (Row 1 is headers)
                    sheet_row_num = int(idx) + 2 
                    
                    row_values = []
                    for col in headers:
                        val = row[col]
                        if pd.isna(val):
                            row_values.append("")
                        elif isinstance(val, (pd.Timestamp, datetime.date, datetime.datetime)):
                            row_values.append(pd.to_datetime(val).strftime("%Y-%m-%d"))
                        else:
                            row_values.append(str(val))
                            
                    data_sheet.update(range_name=f"A{sheet_row_num}", values=[row_values])
                    update_count += 1
            
            st.cache_data.clear()
            st.success(f"Successfully updated status changes for {update_count} record(s) in Google Sheets!")
            st.rerun()

else:
    st.info("No data ledger records found inside Google Sheets yet.")