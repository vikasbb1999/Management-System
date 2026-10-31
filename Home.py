# import streamlit as st
# from sidebar import render_sidebar  # Import the sidebar component

# st.set_page_config(page_title="View Ledger", layout="wide")

# # Render the custom sidebar settings at the bottom
# render_sidebar()
# st.set_page_config(page_title="Dynamic CRUD System", layout="wide")

# # st.markdown("""
# #     <style>
# #         .block-container {
# #             padding-top: 1.5rem;
# #             padding-bottom: 2rem;
# #         }
# #     </style>
# # """, unsafe_allow_html=True)

# st.markdown("""
#     <style>
#         /* Completely hides the default top header bar/toolbar */
#         header[data-testid="stHeader"] {
#             display: none !important;
#         }
        
#         /* Compact top padding */
#         .block-container {
#             padding-top: 0.3rem !important;
#             padding-bottom: 2rem !important;
#             max-width: 100% !important;
#         }
        
#         /* REMOVES PAGE LOCK: Allows normal vertical scrolling for all pages if content overflows */
#         body, html, [data-testid="stAppViewContainer"] {
#             overflow-y: auto !important;
#         }
        
#         /* INCREASES GLOBAL TEXT SIZE FOR EVERYTHING */
#         html, body, [class*="st"] {
#             font-size: 18px !important;
#         }
        
#         /* Specific boost for form inputs, labels, and textboxes */
#         input, select, textarea, label {
#             font-size: 17px !important;
#         }
        
#         /* Tighter header margins */
#         h1, h2, h3 {
#             margin-top: 0px !important;
#             padding-top: 0px !important;
#         }
#     </style>
# """, unsafe_allow_html=True)





# import streamlit as st
# import pandas as pd
# import datetime
# import plotly.express as px
# from utils import load_all_data
# from sidebar import render_sidebar

# st.set_page_config(page_title="Management Dashboard", layout="wide")

# # --- CUSTOM CSS: LARGE READABLE FONTS & CLEAN LAYOUT ---
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
#         html, body, [class*="st"] {
#             font-size: 18px !important;
#         }
#         input, select, textarea, label {
#             font-size: 17px !important;
#         }
#         h1 {
#             font-size: 28px !important;
#         }
#         h2, h3 {
#             font-size: 22px !important;
#         }
#     </style>
# """, unsafe_allow_html=True)

# # Render sidebar settings
# render_sidebar()

# st.header("📊 Interactive Management Dashboard")
# st.markdown("Showing **all rows** from your Google Sheets database. **Click on any donut chart segment** to instantly filter and inspect those records in the View Ledger tab.")

# # Load live data from cache
# raw_data, fields_config = load_all_data()

# if raw_data:
#     df = pd.DataFrame(raw_data)
#     total_raw_rows = len(df)
    
#     # Safe date parsing for optional filtering
#     if "Date" in df.columns:
#         df["Parsed_Date"] = pd.to_datetime(df["Date"], errors="coerce")
    
#     # --- TOGGLE: OPTIONAL DATE RANGE FILTER ---
#     enable_date_filter = st.checkbox("📅 Filter data by specific Date Range", value=False)
    
#     filtered_df = df.copy()
    
#     if enable_date_filter and "Parsed_Date" in filtered_df.columns:
#         valid_dates = filtered_df["Parsed_Date"].dropna()
#         if not valid_dates.empty:
#             min_date = valid_dates.min().date()
#             max_date = valid_dates.max().date()
#         else:
#             min_date = max_date = datetime.date.today()
            
#         d_col1, d_col2 = st.columns(2)
#         with d_col1:
#             start_date = st.date_input("Start Date", value=min_date)
#         with d_col2:
#             end_date = st.date_input("End Date", value=max_date)
            
#         filtered_df = filtered_df[
#             (filtered_df["Parsed_Date"].dt.date >= start_date) & 
#             (filtered_df["Parsed_Date"].dt.date <= end_date)
#         ]
    
#     current_count = len(filtered_df)
    
#     # Show active click filter notice if set
#     if "filter_col" in st.session_state and "filter_val" in st.session_state:
#         st.info(f"💡 Active Chart Filter: **{st.session_state['filter_col']}** = `{st.session_state['filter_val']}`. Go to **View Ledger** to see results.")
#         if st.button("Clear Chart Filter"):
#             st.session_state.pop("filter_col", None)
#             st.session_state.pop("filter_val", None)
#             st.rerun()

#     st.markdown("---")

#     # Helper function to create interactive donut charts with robust click capture
#     def render_donut_chart(data_df, column_name, title_text, chart_key):
#         if column_name not in data_df.columns or data_df.empty:
#             st.warning(f"Column '{column_name}' not available.")
#             return

#         counts_df = data_df[column_name].fillna("Unassigned").astype(str).value_counts().reset_index()
#         counts_df.columns = [column_name, "Count"]

#         fig = px.pie(
#             counts_df, 
#             names=column_name, 
#             values="Count", 
#             hole=0.4, 
#             title=title_text
#         )
#         fig.update_traces(textinfo="label+value", textfont_size=16)
#         fig.update_layout(
#             title_font_size=20,
#             legend=dict(font=dict(size=15)),
#             height=380,
#             margin=dict(l=20, r=20, t=50, b=20)
#         )

#         # Interactive click handler using Streamlit's selection event stream
#         event = st.plotly_chart(fig, use_container_width=True, key=chart_key, on_select="rerun")
        
#         if event and "selection" in event:
#             points = event["selection"].get("points", [])
#             if points:
#                 selected_point = points[0]
#                 selected_category = selected_point.get("label")
#                 if selected_category:
#                     st.session_state["filter_col"] = column_name
#                     st.session_state["filter_val"] = selected_category
#                     st.rerun()

#     # --- 4 DONUT CHARTS LAID OUT CLEANLY (2x2 GRID) ---
#     row1_c1, row1_c2 = st.columns(2)
#     with row1_c1:
#         render_donut_chart(filtered_df, "Final Status", "🎯 Final Status Breakdown", "donut_final_status")
#     with row1_c2:
#         render_donut_chart(filtered_df, "Type", "📁 Project Type Breakdown (Govt / Pvt)", "donut_type")

#     row2_c1, row2_c2 = st.columns(2)
#     with row2_c1:
#         # Changed to Desk 1 Status as requested
#         render_donut_chart(filtered_df, "Desk 1 Status", "✏️ Desk 1 Status Breakdown", "donut_desk1_status")
#     with row2_c2:
#         # Changed to Desk 2 Status as requested
#         render_donut_chart(filtered_df, "Desk 2 Status", "📐 Desk 2 Status Breakdown", "donut_desk2_status")

# else:
#     st.info("No records found inside Google Sheets yet.")






import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from utils import load_all_data
from sidebar import render_sidebar

st.set_page_config(page_title="Management Dashboard", layout="wide")

# --- CUSTOM CSS: LARGE READABLE FONTS & CLEAN LAYOUT ---
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

# Render sidebar settings
render_sidebar()

st.header("📊 Interactive Management Dashboard")
st.markdown("Showing **all rows** from your database. **Click on any donut chart segment** to instantly view the filtered list of records right here on this page.")

# Load live data from cache
raw_data, fields_config = load_all_data()

if raw_data:
    df = pd.DataFrame(raw_data)
    total_raw_rows = len(df)
    
    # Safe date parsing for optional filtering
    if "Date" in df.columns:
        df["Parsed_Date"] = pd.to_datetime(df["Date"], errors="coerce")
    
    # --- TOGGLE: OPTIONAL DATE RANGE FILTER ---
    enable_date_filter = st.checkbox("📅 Filter data by specific Date Range", value=False)
    
    filtered_df = df.copy()
    
    if enable_date_filter and "Parsed_Date" in filtered_df.columns:
        valid_dates = filtered_df["Parsed_Date"].dropna()
        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()
        else:
            min_date = max_date = datetime.date.today()
            
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            start_date = st.date_input("Start Date", value=min_date)
        with d_col2:
            end_date = st.date_input("End Date", value=max_date)
            
        filtered_df = filtered_df[
            (filtered_df["Parsed_Date"].dt.date >= start_date) & 
            (filtered_df["Parsed_Date"].dt.date <= end_date)
        ]
    
    current_count = len(filtered_df)
    st.info(f"Displaying dashboard metrics based on **{current_count}** out of **{total_raw_rows}** total row records.")

    st.markdown("---")

    # Helper function to create interactive donut charts and capture clicks locally
    def render_donut_chart(data_df, column_name, title_text, chart_key):
        if column_name not in data_df.columns or data_df.empty:
            st.warning(f"Column '{column_name}' not available.")
            return None

        counts_df = data_df[column_name].fillna("Unassigned").astype(str).value_counts().reset_index()
        counts_df.columns = [column_name, "Count"]

        fig = px.pie(
            counts_df, 
            names=column_name, 
            values="Count", 
            hole=0.4, 
            title=title_text
        )
        fig.update_traces(textinfo="label+value", textfont_size=16)
        fig.update_layout(
            title_font_size=20,
            legend=dict(font=dict(size=15)),
            height=380,
            margin=dict(l=20, r=20, t=50, b=20)
        )

        event = st.plotly_chart(fig, use_container_width=True, key=chart_key, on_select="rerun")
        
        selected_category = None
        if event and "selection" in event:
            points = event["selection"].get("points", [])
            if points:
                selected_category = points[0].get("label")
        return selected_category

    # --- 4 DONUT CHARTS LAID OUT CLEANLY (2x2 GRID) ---
    row1_c1, row1_c2 = st.columns(2)
    with row1_c1:
        clicked_final = render_donut_chart(filtered_df, "Final Status", "🎯 Final Status Breakdown", "donut_final_status")
    with row1_c2:
        clicked_type = render_donut_chart(filtered_df, "Type", "📁 Project Type Breakdown (Govt / Pvt)", "donut_type")

    row2_c1, row2_c2 = st.columns(2)
    with row2_c1:
        clicked_desk1 = render_donut_chart(filtered_df, "Desk 1 Status", "✏️ Desk 1 Status Breakdown", "donut_desk1_status")
    with row2_c2:
        clicked_desk2 = render_donut_chart(filtered_df, "Desk 2 Status", "📐 Desk 2 Status Breakdown", "donut_desk2_status")

    # Determine if any chart segment was clicked on this page
    active_dash_col = None
    active_dash_val = None

    if clicked_final:
        active_dash_col, active_dash_val = "Final Status", clicked_final
    elif clicked_type:
        active_dash_col, active_dash_val = "Type", clicked_type
    elif clicked_desk1:
        active_dash_col, active_dash_val = "Desk 1 Status", clicked_desk1
    elif clicked_desk2:
        active_dash_col, active_dash_val = "Desk 2 Status", clicked_desk2

    # --- LOCAL DRILL-DOWN TABLE DISPLAY ON HOME PAGE ---
    if active_dash_col and active_dash_val:
        st.markdown("---")
        st.subheader(f"🔍 Filtered Records for `{active_dash_col} = {active_dash_val}`")
        
        drill_df = filtered_df[filtered_df[active_dash_col].astype(str) == str(active_dash_val)]
        
        if st.button("Clear Chart Selection Filter"):
            st.rerun()
            
        def style_status_cells(val):
            val_str = str(val).lower().strip()
            if "incomplete" in val_str:
                return "background-color: #ffcccc; color: #cc0000; font-weight: bold;"
            elif "inprogress" in val_str:
                return "background-color: #ffe6cc; color: #cc6600; font-weight: bold;"
            elif "done" in val_str:
                return "background-color: #d4edda; color: #155724; font-weight: bold;"
            return ""

        styled_drill_df = drill_df.style.map(style_status_cells)
        st.dataframe(styled_drill_df, use_container_width=True, height=400)

else:
    st.info("No records found inside Google Sheets yet.")