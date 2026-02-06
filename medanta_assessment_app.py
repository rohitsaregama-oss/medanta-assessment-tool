import streamlit as st
import pandas as pd
import sqlite3
import uuid
import random
import time
from pathlib import Path

# ---------------- CONFIG ----------------
EXCEL_FILE = "Nursing_Assessment_Medanta_Final_Tagged.xlsx"
DB_FILE = "assessments.db"
LOGO_FILE = "Assessment_tool_logo.png"
QUESTIONS_PER_TEST = 25

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="Medanta Assessment Tool", layout="wide")

col1, col2 = st.columns([6, 1])
with col1:
    st.markdown("## Medanta Assessment Tool")
with col2:
    if Path(LOGO_FILE).exists():
        st.image(LOGO_FILE, width=120)

# ---------------- DATABASE ----------------
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS attempts (
    aid TEXT,
    name TEXT,
    mobile TEXT,
    level TEXT,
    question_no INTEGER,
    selected TEXT,
    correct TEXT,
    is_correct INTEGER,
    timestamp REAL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS progress (
    aid TEXT PRIMARY KEY,
    current_q INTEGER,
    completed INTEGER
)
""")
conn.commit()

# ---------------- LOAD QUESTIONS ----------------
df = pd.read_excel(EXCEL_FILE)
df.columns = [c.strip().lower() for c in df.columns]

REQUIRED = ["category", "level", "question", "option a", "option b", "option c", "option d", "correct_answer"]
for col in REQUIRED:
    if col not in df.columns:
        st.error(f"Excel missing column: {col}")
        st.stop()

# ---------------- SESSION ----------------
if "aid" not in st.session_state:
    params = st.query_params
    if "aid" not in params:
        st.error("Invalid assessment link.")
        st.stop()
    st.session_state.aid = params["aid"]

aid = st.session_state.aid

if "questions" not in st.session_state:
    level = params.get("level", "Beginner")
    pool = df[df["level"].str.lower() == level.lower()]
    st.session_state.questions = pool.sample(QUESTIONS_PER_TEST).to_dict("records")
    st.session_state.q_index = 0
    st.session_state.answers = {}
    cur.execute("INSERT OR IGNORE INTO progress VALUES (?, ?, ?)", (aid, 0, 0))
    conn.commit()

questions = st.session_state.questions
q_index = st.session_state.q_index

# ---------------- ASSESSMENT ----------------
if q_index < QUESTIONS_PER_TEST:
    q = questions[q_index]

    st.markdown(f"### Question {q_index+1} of {QUESTIONS_PER_TEST}")
    st.markdown(q["question"])

    options = {
        "A": q["option a"],
        "B": q["option b"],
        "C": q["option c"],
        "D": q["option d"]
    }

    choice = st.radio(
        "Select one option",
        options.keys(),
        format_func=lambda x: f"{x}. {options[x]}",
        key=f"q_{q_index}"
    )

    if st.button("Next"):
        if q_index in st.session_state.answers:
            st.warning("Answer already locked.")
        else:
            correct = q["correct_answer"].strip().upper()
            is_correct = 1 if choice == correct else 0

            st.session_state.answers[q_index] = choice
            cur.execute("""
                INSERT INTO attempts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                aid, "", "", q["level"], q_index+1,
                choice, correct, is_correct, time.time()
            ))
            cur.execute("""
                UPDATE progress SET current_q=? WHERE aid=?
            """, (q_index+1, aid))
            conn.commit()

            st.session_state.q_index += 1
            st.rerun()

else:
    cur.execute("UPDATE progress SET completed=1 WHERE aid=?", (aid,))
    conn.commit()

    df_attempts = pd.read_sql("SELECT * FROM attempts WHERE aid=?", conn, params=(aid,))
    score = df_attempts["is_correct"].sum()

    st.success("Assessment Completed")
    st.markdown(f"### Final Score: **{score} / {QUESTIONS_PER_TEST}**")

    st.dataframe(df_attempts[["question_no", "selected", "correct", "is_correct"]])
