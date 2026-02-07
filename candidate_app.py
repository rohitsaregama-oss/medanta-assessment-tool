import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURATION ---
ADMIN_PASSWORD = "Medanta@2026"
# UPDATE THIS WITH YOUR "PUBLISH TO WEB" CSV LINK
SHEET_CSV_URL = "https://script.google.com/macros/s/AKfycbzi-r_-An34y1vTBMDtR90_P8XCxuG9SmYuA9XS38UdTQTCLsCZlQHxomAk7KZLe-I4/exec"

st.set_page_config(page_title="Medanta Admin Dashboard", layout="wide")

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏥 Medanta Admin Login")
        pw = st.text_input("Enter Master Key", type="password")
        if st.button("Access Dashboard"):
            if pw == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.rerun()
            else: st.error("Invalid Key")
else:
    st.title("🏥 Medanta Assessment Analytics")
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        if not df.empty:
            df['score_num'] = df['score'].astype(str).str.replace('%', '').astype(float)
            df['dur_num'] = df['duration'].astype(str).str.replace(' mins', '').astype(float)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Candidates", len(df))
            m2.metric("Avg. Score", f"{round(df['score_num'].mean(), 1)}%")
            m3.metric("Pass Rate (>=80%)", f"{round((len(df[df['score_num'] >= 80])/len(df))*100, 1)}%")
            m4.metric("Avg. Time", f"{round(df['dur_num'].mean(), 1)} mins")

            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Score Distribution")
                st.plotly_chart(px.histogram(df, x="score_num", nbins=10, color_discrete_sequence=['#e63946']), use_container_width=True)
            with c2:
                st.subheader("Staff Categories")
                st.plotly_chart(px.pie(df, names='category', hole=0.4), use_container_width=True)

            st.subheader("📋 JCI Audit Log")
            st.dataframe(df[['Timestamp', 'name', 'category', 'reg_no', 'score', 'duration']], use_container_width=True)
            
            st.download_button("📥 Download JCI Report", df.to_csv(index=False).encode('utf-8'), "Medanta_Report.csv", "text/csv")
        else: st.warning("Sheet is empty.")
    except Exception as e:
        st.error("Sync Error: Ensure Google Sheet is 'Published to Web' as CSV.")

    if st.sidebar.button("Logout"):
        st.session_state.admin_logged_in = False
        st.rerun()
