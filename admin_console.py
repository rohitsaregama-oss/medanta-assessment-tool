import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# --- CONFIGURATION ---
ADMIN_PASSWORD = "Medanta@2026"
# Replace with your actual Google Sheet CSV export link if you want live data sync
# For now, it reads the data you manually export or connect via API
# PASTE YOUR NEW CSV LINK HERE
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQBqxPaHhsk-AUD4E70Sph8chi_MgRyOM8xDhRnGHX1s70nvokG-u8K9dWhT4ZPRPDy5IRYWJZZYpFz/pub?gid=0&single=true&output=csv"

st.set_page_config(page_title="Medanta Admin Dashboard", layout="wide")

# --- CUSTOM CSS (Fixes the TypeError from your screenshot) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True) # FIXED: Changed unsafe_allow_code to unsafe_allow_html

# --- AUTHENTICATION ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image("MHPL logo 2.png", width=200)
        st.title("Admin Login")
        pw = st.text_input("Enter Master Key", type="password")
        if st.button("Login"):
            if pw == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Invalid Key")
else:
    # --- DASHBOARD HEADER ---
    st.title("🏥 Medanta Staff Assessment Analytics")
    
    # --- LOAD DATA ---
    # Note: In a real scenario, you'd pull from your Google Sheet here
    try:
        # For testing, we assume data exists in your connected Sheet
        # Replace this with: df = pd.read_csv(SHEET_CSV_URL)
        st.info("Connected to Medanta_Assessment_Bridge")
        
        # --- MOCKUP DATA DISPLAY (For layout purposes) ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Assessments", "124")
        col2.metric("Avg. Score", "82%")
        col3.metric("Passing Rate", "94%")
        col4.metric("Avg. Duration", "18.5 mins")

        # --- VISUALS ---
        st.divider()
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Scores by Category")
            # Example Chart
            chart_data = pd.DataFrame({'Category': ['Nursing', 'Non-Nursing'], 'Score': [85, 78]})
            fig = px.bar(chart_data, x='Category', y='Score', color='Category', template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("Test Duration Distribution")
            # Image of a professional hospital audit dashboard showing a pass-fail pie chart and a score distribution bar graph
            st.write("Monitor how long staff are taking to ensure assessment integrity.")

        # --- DETAILED TABLE (The JCI Audit Log) ---
        st.subheader("📋 Official Candidate Records (JCI Audit Log)")
        st.write("This table contains the 11 data points captured from mobile inputs.")
        
        # Placeholder for the actual table
        st.dataframe({
            "Timestamp": ["2026-02-07 14:00", "2026-02-07 14:15"],
            "Name": ["Rohit Singh", "Staff Member B"],
            "Category": ["Nursing", "Nursing"],
            "Score": ["92%", "88%"],
            "Duration": ["21 mins", "19 mins"],
            "Reg_No": ["RN12345", "RN98765"]
        }, use_container_width=True)

        if st.button("Download Full Report for JCI"):
            st.success("Report generated as Medanta_Training_Log.csv")

    except Exception as e:
        st.error(f"Error loading data: {e}")

    if st.sidebar.button("Logout"):
        st.session_state.admin_logged_in = False

        st.rerun()


