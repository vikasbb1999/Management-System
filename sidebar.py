# sidebar.py
import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.markdown("---")
        st.subheader("⚙️ System Preferences")
        
        # Theme / Mode Selector (Note: Streamlit handles themes via config, but you can let users select preferences)
        app_mode = st.selectbox("Display Theme", ["Light Mode", "Dark Mode", "System Default"], key="global_theme_mode")
        
        # Notification or Refresh toggle preference
        auto_refresh = st.checkbox("Enable Fast Cache Sync", value=True)
        
        if st.button("Clear App Cache"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("Cache cleared successfully!")
            st.rerun()
            
        st.markdown("<p style='font-size: 20px; color: gray;'>Management System v2.5</p>", unsafe_allow_html=True)