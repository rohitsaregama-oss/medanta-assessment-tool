import streamlit as st
import pandas as pd
import requests
import time
import random
from datetime import date
import os

# ================= SAFE SECRET LOAD =================
try:
    ADMIN_MASTER_KEY = st.secrets["ADMIN_MASTER_KEY"]
except:
    ADMIN_MASTER_KEY = None

# ================= CONFIG =================
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbzCICknuaFGUOqwPX_kMnTy_1FtA4ppm44ZAft56-Y21_4xCidrjvTkM6gwcuZW_4so/exec"

TOTAL_QUESTIONS = 25
TECH_Q_COUNT = 18
BEHAV_Q_COUNT = 7
PASS_PERCENT = 60

GLOBAL_TEST_TIME = 25 * 60
DEFAULT_Q_TIME = 45
REDUCED_Q_TIME = 25
REVIEW_TIME_LIMIT = 120  # 2 minutes

st.set_page_config(page_title="Medanta Staff Assessment", layout="centered")

# ================= SESSION INIT =================
if "started" not in st.session_state:
    st.session_state.update({
        "started": False,
        "q_index": 0,
        "answers": {},
        "candidate_data": {},
        "questions": [],
        "level": "beginner",
        "start_time": None,
        "question_start_time": None,
        "question_times": [],
        "fishy_counter": 0,
        "per_q_time": DEFAULT_Q_TIME,
        "review_mode": False,
        "review_start": None,
        "admin_unlocked": False
    })

# ================= SIDEBAR ADMIN =================
with st.sidebar:
    st.subheader("⚙️ Admin")

    if st.checkbox("Unlock Level Settings"):
        key = st.text_input("Master Key", type="password")
        if ADMIN_MASTER_KEY and key == ADMIN_MASTER_KEY:
            st.session_state.admin_unlocked = True
            st.success("Admin unlocked")

    if st.session_state.admin_unlocked and not st.session_state.started:
        st.session_state.level = st.selectbox(
            "Difficulty",
            ["beginner", "intermediate", "advanced"],
            index=["beginner", "intermediate", "advanced"].index(st.session_state.level)
        )

    st.divider()
    st.info(f"Difficulty: **{st.session_state.level.upper()}**")

# ================= QUESTION PREP =================
def prepare_questions(df):
    questions = []
    for _, row in df.iterrows():
        opts = [row["Option A"], row["Option B"], row["Option C"], row["Option D"]]
        correct = row["Correct Answer"]
        random.shuffle(opts)
        questions.append({
            "question": row["question"],
            "options": opts,
            "correct": correct
        })
    random.shuffle(questions)
    return questions

# ================= SCREEN 1 =================
if not st.session_state.started:
    st.title("🏥 Medanta Staff Assessment")

    name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth", min_value=date(1960,1,1))
    qual = st.text_input("Qualification")
    cat = st.selectbox("Staff Category", ["Nursing", "Non-Nursing"])
    reg = st.text_input("Registration Number") if cat == "Nursing" else "N/A"
    college = st.text_input("College Name")
    contact = st.text_input("Contact Number")

    if st.button("Start Assessment"):
        if not (name and contact.isdigit() and len(contact)==10):
            st.warning("Invalid details")
            st.stop()

        if not os.path.exists("questions.xlsx"):
            st.error("questions.xlsx missing")
            st.stop()

        df = pd.read_excel("questions.xlsx")
        tech = df[df["level"].str.lower() == st.session_state.level].sample(TECH_Q_COUNT)
        behav = pd.DataFrame(random.sample(BEHAVIORAL_BANK, BEHAV_Q_COUNT))
        full = pd.concat([tech, behav])

        st.session_state.questions = prepare_questions(full)
        st.session_state.candidate_data = {
            "name": name, "dob": str(dob), "qualification": qual,
            "category": cat, "reg_no": reg, "college": college,
            "contact": contact
        }
        st.session_state.start_time = time.time()
        st.session_state.question_start_time = time.time()
        st.session_state.started = True
        st.rerun()

# ================= SCREEN 2 =================
else:
    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, GLOBAL_TEST_TIME - elapsed)

    st.sidebar.metric("⏳ Test Time Left", f"{int(remaining//60)}m {int(remaining%60)}s")

    if remaining <= 0:
        st.session_state.review_mode = True
        st.session_state.review_start = time.time()

    # -------- REVIEW MODE (2 min cap) --------
    if st.session_state.review_mode:
        if not st.session_state.review_start:
            st.session_state.review_start = time.time()

        review_left = REVIEW_TIME_LIMIT - (time.time() - st.session_state.review_start)
        if review_left <= 0:
            st.warning("Review time expired. Submitting...")
            st.session_state.review_mode = False
        else:
            st.info(f"Review time left: {int(review_left)} sec")

        cols = st.columns(5)
        for i in range(TOTAL_QUESTIONS):
            mark = "✅" if i in st.session_state.answers else "⚪"
            if cols[i % 5].button(f"{mark} Q{i+1}"):
                st.session_state.q_index = i
                st.session_state.review_mode = False
                st.rerun()

        if st.button("Final Submit"):
            correct = sum(
                1 for i,q in enumerate(st.session_state.questions)
                if st.session_state.answers.get(i) == q["correct"]
            )
            score = round((correct/TOTAL_QUESTIONS)*100,2)

            requests.post(BRIDGE_URL, json={
                **st.session_state.candidate_data,
                "score": score
            })

            if score >= PASS_PERCENT:
                st.success(f"PASS – {score}%")
            else:
                st.error(f"NOT CLEARED – {score}%")

            st.session_state.started = False
            st.stop()

    # -------- QUESTION MODE --------
    q = st.session_state.questions[st.session_state.q_index]

    # Per-question timer
    q_elapsed = time.time() - st.session_state.question_start_time
    if q_elapsed > st.session_state.per_q_time:
        st.session_state.q_index += 1
        st.session_state.question_start_time = time.time()
        st.rerun()

    st.subheader(f"Question {st.session_state.q_index+1}")
    st.write(q["question"])
    st.caption(f"Time left for this question: {int(st.session_state.per_q_time - q_elapsed)} sec")

    choice = st.radio(
        "Select answer",
        q["options"],
        index=None,
        key=f"q_{st.session_state.q_index}"
    )

    if choice:
        # record time
        time_taken = q_elapsed
        st.session_state.question_times.append(time_taken)

        # fishy detection
        if time_taken > 40:
            st.session_state.fishy_counter += 1
        else:
            st.session_state.fishy_counter = 0

        if st.session_state.fishy_counter >= 3:
            st.session_state.per_q_time = REDUCED_Q_TIME

        st.session_state.answers[st.session_state.q_index] = choice
        st.session_state.q_index += 1
        st.session_state.question_start_time = time.time()

        if st.session_state.q_index >= TOTAL_QUESTIONS:
            st.session_state.review_mode = True
            st.session_state.review_start = time.time()

        st.rerun()
