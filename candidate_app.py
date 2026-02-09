import streamlit as st
import pandas as pd
import random
import time
import requests
from datetime import date

# ================= CONFIG =================
TOTAL_QUESTIONS = 25
TOTAL_TEST_TIME = 25 * 60

DEFAULT_Q_TIME = 60
REDUCED_Q_TIME = 40
SUSPICIOUS_THRESHOLD = 55
SUSPICIOUS_LIMIT = 3

ADMIN_MASTER_KEY = "Medanta@Admin2026"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz1qT4L2mNOusKQ3wjTHwh4tbPHGn0Kb-ek9Anyyn9J7YJKrzCYzQvOKv-FLYlsHmAS/exec"

st.set_page_config(page_title="Medanta Staff Assessment", layout="centered")

# ================= CSS (DESKTOP + MOBILE) =================
st.markdown("""
<style>
.stApp { background:#F7F9FC; }
.block-container { max-width:900px; padding:1rem; }

.card {
    background:#FFFFFF;
    padding:22px;
    border-radius:18px;
    box-shadow:0 10px 25px rgba(0,0,0,0.08);
    margin-bottom:22px;
}

.section-title {
    font-size:22px;
    font-weight:700;
    color:#0B5394;
    margin-bottom:16px;
}

.slogan-bar {
    background:#FFFFFF;
    padding:16px;
    border-radius:16px;
    box-shadow:0 6px 16px rgba(0,0,0,0.06);
    text-align:center;
    margin-bottom:26px;
}

.timer-box {
    position:fixed;
    top:110px;
    right:20px;
    background:#FFFFFF;
    padding:14px 18px;
    border-radius:14px;
    box-shadow:0 6px 18px rgba(0,0,0,0.15);
    border-left:6px solid #0B5394;
    z-index:9999;
    font-size:14px;
}

.timer-warning { color:#B30000; font-weight:600; }

.tip-box {
    background:#EDF4EE;
    border-left:6px solid #4F772D;
    padding:14px;
    border-radius:12px;
    font-size:14px;
    color:#2F4F2F;
}

.stButton > button {
    background:linear-gradient(90deg,#F28C28,#E6761C);
    color:white;
    border-radius:14px;
    padding:12px 22px;
    font-weight:600;
    border:none;
    width:100%;
}

@media (max-width:768px) {
    .timer-box {
        bottom:16px;
        top:auto;
        left:16px;
        right:16px;
        text-align:center;
    }
    .section-title { text-align:center; font-size:20px; }
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "started" not in st.session_state:
    st.session_state.update({
        "started": False,
        "questions": [],
        "answers": {},
        "q_index": 0,
        "start_time": None,
        "question_start_time": None,
        "current_q_time_limit": DEFAULT_Q_TIME,
        "slow_streak": 0,
        "show_result": False,
        "candidate": {},
        "admin_unlocked": False,
        "assessment_level": "Beginner"
    })

# ================= SIDEBAR ADMIN (HIDDEN) =================
with st.sidebar:
    st.markdown("### ⚙️")
    if st.checkbox("Admin Controls"):
        if not st.session_state.admin_unlocked:
            key = st.text_input("Admin Key", type="password")
            if st.button("Unlock"):
                if key == ADMIN_MASTER_KEY:
                    st.session_state.admin_unlocked = True
                    st.success("Admin Unlocked")
                else:
                    st.error("Invalid Key")
        else:
            st.session_state.assessment_level = st.selectbox(
                "Assessment Level",
                ["Beginner", "Intermediate", "Advanced"]
            )
            st.info(f"Active Level: {st.session_state.assessment_level}")

# ================= HEADER =================
st.image("MHPL logo 2.png", width=150)

st.markdown(
    "<h2 style='color:#0B5394; margin-bottom:10px;'>Medanta Staff Assessment</h2>",
    unsafe_allow_html=True
)

st.markdown("""
<div class="slogan-bar">
    <div style="color:#B30000; font-size:22px; font-weight:600; letter-spacing:1px;">
        हर एक जान अनमोल
    </div>
    <div style="margin-top:6px; color:#777; font-size:13px;">
        Compassion • Care • Clinical Excellence
    </div>
</div>
""", unsafe_allow_html=True)

# ================= STAFF INFO =================
if not st.session_state.started:

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Staff Information</div>', unsafe_allow_html=True)

    name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth", min_value=date(1960,1,1))
    qualification = st.text_input("Qualification")
    category = st.selectbox("Staff Category", ["Nursing","Non-Nursing","Other"])
    reg_no = st.text_input("Registration Number")
    mobile = st.text_input("Mobile Number")
    college = st.text_input("College / Institute")

    st.markdown("""
    <div class="tip-box">
    ⚠️ <b>Integrity Reminder:</b><br>
    This assessment is the exclusive property of Medanta Hospital, Lucknow.
    Sharing, copying, recording, or external assistance is strictly prohibited.
    </div>
    """, unsafe_allow_html=True)

    if st.button("Start Assessment"):
        if not name or not mobile:
            st.warning("Please fill mandatory fields.")
            st.stop()

        st.session_state.candidate = {
            "name": name,
            "dob": str(dob),
            "qualification": qualification,
            "category": category,
            "registration_number": reg_no,
            "mobile": mobile,
            "college": college
        }

        tech_df = pd.read_excel("questions.xlsx")
        beh_df = pd.read_excel("Behavioural_Questions_100_with_Competency.xlsx")

        tech_count = random.randint(17,20)
        beh_count = TOTAL_QUESTIONS - tech_count

        tech_q = tech_df[tech_df["level"].str.lower()==st.session_state.assessment_level.lower()].sample(tech_count)
        beh_q = beh_df.sample(beh_count)

        st.session_state.questions = pd.concat([tech_q, beh_q]).sample(TOTAL_QUESTIONS).to_dict("records")
        st.session_state.start_time = time.time()
        st.session_state.started = True
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ================= EXAM =================
elif not st.session_state.show_result:

    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(0, TOTAL_TEST_TIME - elapsed)

    q_elapsed = int(time.time() - st.session_state.question_start_time) if st.session_state.question_start_time else 0
    q_remaining = max(0, st.session_state.current_q_time_limit - q_elapsed)

    st.markdown(f"""
    <div class="timer-box">
        ⏱ Test: {remaining//60:02d}:{remaining%60:02d}<br>
        <span class="{'timer-warning' if q_remaining<=10 else ''}">
        Question: {q_remaining}s
        </span>
    </div>
    """, unsafe_allow_html=True)

    if remaining <= 0:
        st.session_state.show_result = True
        st.rerun()

    q = st.session_state.questions[st.session_state.q_index]

    if st.session_state.question_start_time is None:
        st.session_state.question_start_time = time.time()

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<b>Question {st.session_state.q_index+1} of {TOTAL_QUESTIONS}</b><br>{q['question']}", unsafe_allow_html=True)

    choice = st.radio(
        "Select one option:",
        [q["option_a"], q["option_b"], q["option_c"], q["option_d"]],
        key=f"q_{st.session_state.q_index}"
    )

    if q_remaining <= 0:
        st.session_state.answers[f"Q{st.session_state.q_index+1}"] = "TIMEOUT"
        st.session_state.q_index += 1
        st.session_state.question_start_time = None
        st.rerun()

    if st.button("Next"):
        time_taken = time.time() - st.session_state.question_start_time

        if time_taken >= SUSPICIOUS_THRESHOLD:
            st.session_state.slow_streak += 1
        else:
            st.session_state.slow_streak = 0

        if st.session_state.slow_streak >= SUSPICIOUS_LIMIT:
            st.session_state.current_q_time_limit = REDUCED_Q_TIME

        st.session_state.answers[f"Q{st.session_state.q_index+1}"] = choice
        st.session_state.q_index += 1
        st.session_state.question_start_time = None

        if st.session_state.q_index >= TOTAL_QUESTIONS:
            st.session_state.show_result = True

        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ================= RESULT =================
else:
    correct = 0
    for i,q in enumerate(st.session_state.questions):
        if st.session_state.answers.get(f"Q{i+1}") == q["correct_answer"]:
            correct += 1

    percentage = correct / TOTAL_QUESTIONS
    mins,secs = divmod(int(time.time()-st.session_state.start_time),60)
    result = "CLEARED" if percentage>=0.6 else "NOT CLEARED"

    if percentage < 0.4:
        tip = "Focus on strengthening core concepts and protocols."
    elif percentage < 0.6:
        tip = "You are progressing well. Targeted practice will help."
    else:
        tip = "Strong performance. Continue reinforcing best practices."

    st.markdown(f"""
    <div class="card">
        <div class="section-title">Assessment Report</div>
        <b>Score:</b> {correct}/{TOTAL_QUESTIONS}<br>
        <b>Result:</b> {result}<br>
        <b>Time Taken:</b> {mins}m {secs}s
        <hr>
        <div class="tip-box">
            🌱 <b>Professional Insight:</b><br>{tip}
        </div>
    </div>
    """, unsafe_allow_html=True)

    payload = {
        **st.session_state.candidate,
        "score": f"{correct}/{TOTAL_QUESTIONS}",
        "duration": f"{mins}m {secs}s",
        "result": result,
        **st.session_state.answers
    }

    try:
        requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=25)
    except:
        pass

    st.success("Assessment submitted successfully.")
