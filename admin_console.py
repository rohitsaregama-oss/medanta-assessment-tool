import streamlit as st
import sqlite3
import uuid
import pandas as pd

DB_FILE = "assessments.db"
ALLOWED_ADMINS = ["01003061", "01003038"]

st.set_page_config(page_title="Medanta Admin Console", layout="wide")
st.markdown("## Medanta Admin Console")

admin_id = st.text_input("Enter Admin ID")

if admin_id not in ALLOWED_ADMINS:
    st.warning("Unauthorized admin.")
    st.stop()

conn = sqlite3.connect(DB_FILE, check_same_thread=False)

# ---------------- CREATE ASSESSMENTS ----------------
st.markdown("### Create Assessment Links")

level = st.selectbox("Audience Level", ["Beginner", "Intermediate", "Advanced"])
count = st.number_input("Number of Candidates", min_value=1, max_value=100, value=1)

if st.button("Generate Links"):
    links = []
    for _ in range(count):
        aid = str(uuid.uuid4())[:8]
        links.append(f"http://localhost:8501/?aid={aid}&level={level}")
    st.success("Links generated")
    st.text_area("Assessment Links (share via WhatsApp Web)", "\n".join(links), height=200)

# ---------------- LIVE TRACKING ----------------
st.markdown("### Live Assessment Tracking")

progress = pd.read_sql("SELECT * FROM progress", conn)
attempts = pd.read_sql("SELECT * FROM attempts", conn)

if not progress.empty:
    merged = progress.merge(
        attempts.groupby("aid").agg(
            answered=("question_no", "max"),
            score=("is_correct", "sum")
        ),
        on="aid",
        how="left"
    )

    merged["status"] = merged["completed"].apply(lambda x: "Completed" if x else "In Progress")
    st.dataframe(merged)

# ---------------- DOWNLOAD RESULTS ----------------
st.markdown("### Download Results")

if st.button("Download All Attempts"):
    csv = attempts.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CSV",
        csv,
        "assessment_results.csv",
        "text/csv"
    )
