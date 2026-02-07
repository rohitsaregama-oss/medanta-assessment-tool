import streamlit as st
import pandas as pd
import json
import io
import plotly.express as px

# --- CONFIGURATION ---
ADMIN_IDS = ["01003061", "01003038"]
# Ensure this is your "Publish to Web" CSV link
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQBqxPaHhsk-AUD4E70Sph8chi_MgRyOM8xDhRnGHX1s70nvokG-u8K9dWhT4ZPRPDy5IRYWJZZYpFz/pub?gid=0&single=true&output=csv"

st.set_page_config(page_title="Medanta Admin Console", layout="wide")

# --- CUSTOM CSS FOR MEDANTA BRANDING ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { background-color: #d32f2f; color: white; border-radius: 5px; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True) # <--- FIXED: Changed from unsafe_allow_code

st.title("🛠 Medanta Admin Console")
st.write("JCI 8th Edition Compliance Dashboard")

# --- AUTHENTICATION ---
admin_id = st.text_input("Enter Admin ID", type="password")
if admin_id not in ADMIN_IDS:
    st.warning("Admin authentication required to view JCI Audit Data.")
    st.stop()

@st.cache_data(ttl=30) # Auto-refresh every 30 seconds
def load_and_process_data():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        
        # Mapping all 11 columns from the Bridge
        df.columns = [
            "Timestamp", "Name", "DOB", "Qualification", "Category", 
            "Reg No", "College", "Contact", "Score", "Duration", "RawAnswers"
        ]
        
        # Process Numeric Score for Analytics
        df['Numeric Score'] = pd.to_numeric(df['Score'].astype(str).str.replace('%', ''), errors='coerce').fillna(0)
        df['Result'] = df['Numeric Score'].apply(lambda x: "✅ PASS" if x >= 80 else "❌ FAIL")
        
        return df
    except Exception as e:
        st.error(f"Error connecting to Google Sheet: {e}")
        return pd.DataFrame()

# --- DASHBOARD LOGIC ---
data = load_and_process_data()

if not data.empty:
    # --- METRICS ROW ---
    st.subheader("📊 Training Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Staff Tested", len(data))
    m2.metric("Overall Pass Rate", f"{round((data['Result'] == '✅ PASS').mean() * 100)}%")
    m3.metric("Avg Score", f"{round(data['Numeric Score'].mean(), 1)}%")
    m4.metric("Nursing Staff", len(data[data['Category'] == 'Nursing']))

    # --- ANALYTICS CHARTS ---
    
    c1, c2 = st.columns(2)
    
    fig_pie = px.pie(data, names='Result', title='Compliance Status (Threshold 80%)', 
                     color='Result', color_discrete_map={'✅ PASS':'#2E7D32', '❌ FAIL':'#C62828'})
    c1.plotly_chart(fig_pie, use_container_width=True)
    
    fig_hist = px.histogram(data, x='Numeric Score', nbins=10, title='Score Distribution',
                            labels={'Numeric Score': 'Score (%)'}, color_discrete_sequence=['#1976D2'])
    c2.plotly_chart(fig_hist, use_container_width=True)

    # --- DETAILED RECORDS ---
    st.subheader("📋 Detailed Candidate Records")
    # Sidebar Filters
    st.sidebar.header("Filter Audit Data")
    cat_filter = st.sidebar.multiselect("Category", data["Category"].unique(), default=data["Category"].unique())
    res_filter = st.sidebar.multiselect("Result", ["✅ PASS", "❌ FAIL"], default=["✅ PASS", "❌ FAIL"])
    
    filtered_df = data[(data["Category"].isin(cat_filter)) & (data["Result"].isin(res_filter))]
    
    st.dataframe(filtered_df.drop(columns=['RawAnswers']), use_container_width=True)

    # --- JCI EXCEL EXPORT ---
    st.divider()
    st.subheader("📄 Export Audit Documentation")
    st.info("The exported file includes individual answers for every question to provide full JCI transparency.")
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='JCI_Compliance_Evidence')
    
    st.download_button(
        label="📥 Download Official Training Log (Excel)",
        data=buffer.getvalue(),
        file_name=f"Medanta_JCI_Audit_Log_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.ms-excel"
    )
else:
    st.info("No data found. Ensure your Google Sheet is 'Published to web' as a CSV.")