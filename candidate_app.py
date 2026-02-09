import streamlit as st
import pandas as pd
import requests
import time
import random
from datetime import date

# ===================== CONFIG =====================
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbz1qT4L2mNOusKQ3wjTHwh4tbPHGn0Kb-ek9Anyyn9J7YJKrzCYzQvOKv-FLYlsHmAS/exec"

TOTAL_TEST_TIME = 25 * 60  # 25 minutes

# Per-question integrity rules
DEFAULT_Q_TIME = 60
REDUCED_Q_TIME = 40
SUSPICIOUS_THRESHOLD = 55
SUSPICIOUS_LIMIT = 3

TECH_MIN, TECH_MAX = 17, 20
BEH_MIN, BEH_MAX = 5, 8

st.set_page_config(
    page_title="Medanta Staff Assessment",
    layout="centered"
)

# ===================== STYLES =====================
st.markdown("""
<style>
body {
    background-color: #F6F8FA;
}
.card {
    background: #FFFFFF;
    padding: 24px;
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}
.section-title {
    font-size: 20px;
    font-weight: 600;
    color: #0B5394;
    margin-bottom: 14px;
}
.tip-box {
    background: #F0F7FF;
    border-left: 6px solid #0B5394;
    padding: 14px;
    border-radius: 10px;
    font-size: 14px;
}
.timer-box {
    position: fixed;
    top: 110px;
    right: 20px;
    background: #FFFFFF;
    border-radius: 12px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    padding: 14px 18px;
    min-width: 180px;
    border-left: 6px solid #0B5394;
    z-index: 9999;
}
.timer-title {
    font-size: 14px;
    font-weight: 600;
    color: #0B5394;
}
.timer-warning {
    color: #B30000;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ===================== SESSION INIT =====================
if "started" not in st.session_state:
    st.session_state.update({
        "started": False,
        "questions": [],
        "answers": {},
        "q_index": 0,
        "start_time": None,
        "question_start_time": None,
        "current_q_time_limit": DEFAULT_Q_TIME,
        "suspicious_streak": 0,
        "show_result": False,
        "candidate": {}
    })

# ===================== HEADER =====================
st.image("MHPL logo 2.png", width=160)

st.markdown("""
<div style="
    width:100%;
    background: linear-gradient(90deg, #B30000 0%, #7A7A7A 100%);
    padding:22px 10px;
    border-radius:14px;
    text-align:center;
    margin-bottom:24px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
">
    <div style="color:white; font-size:26px; font-weight:700;">
        हर एक जान अनमोल
    </div>
    <div style="color:#F2F2F2; font-size:14px;">
        Compassion • Care • Clinical Excellence
    </div>
</div>
""", unsafe_allow_html=True)

# ===================== CANDIDATE INFO =====================
if not st.session_state.started:

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Staff Information</div>', unsafe_allow_html=True)

    name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth", min_value=date(1960, 1, 1))
    qualification = st.text_input("Qualification")
    category = st.selectbox("Staff Category", ["Nursing", "Non-Nursing", "Other"])
    reg_no = st.text_input("Registration Number (if applicable)")
    mobile = st.text_input("Mobile Number")
    college = st.text_input("College / Institute")

    st.markdown("""
    <div class="tip-box">
    ⚠️ <b>Integrity Reminder:</b><br>
    This assessment is the exclusive intellectual property of Medanta Hospital, Lucknow.
    Sharing, copying, or external assistance is strictly prohibited.
    </div>
    """, unsafe_allow_html=True)

    if st.button("Start Assessment"):
        if name and mobile:
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

            tech_q = tech_df.sample(random.randint(TECH_MIN, TECH_MAX)).to_dict("records")
            beh_q = beh_df.sample(random.randint(BEH_MIN, BEH_MAX)).to_dict("records")

            st.session_state.questions = random.sample(tech_q + beh_q, len(tech_q + beh_q))
            st.session_state.start_time = time.time()
            st.session_state.started = True
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ===================== EXAM =====================
elif not st.session_state.show_result:

    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(0, TOTAL_TEST_TIME - elapsed)

    emin, esec = divmod(elapsed, 60)
    rmin, rsec = divmod(remaining, 60)

    st.markdown(f"""
    <div class="timer-box">
        <div class="timer-title">⏱ Assessment Time</div>
        Elapsed: {emin:02d}:{esec:02d}<br>
        <span class="{'timer-warning' if remaining <= 120 else ''}">
        Remaining: {rmin:02d}:{rsec:02d}
        </span>
    </div>
    """, unsafe_allow_html=True)

    if remaining <= 0:
        st.session_state.show_result = True
        st.rerun()

    q = st.session_state.questions[st.session_state.q_index]

    if st.session_state.question_start_time is None:
        st.session_state.question_start_time = time.time()

    q_elapsed = int(time.time() - st.session_state.question_start_time)
    q_remaining = max(0, st.session_state.current_q_time_limit - q_elapsed)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<b>Question {st.session_state.q_index + 1}</b><br>{q['question']}", unsafe_allow_html=True)

    option = st.radio(
        "Select one option:",
        [q["Option A"], q["Option B"], q["Option C"], q["Option D"]],
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
            st.session_state.suspicious_streak += 1
        else:
            st.session_state.suspicious_streak = 0

        if st.session_state.suspicious_streak >= SUSPICIOUS_LIMIT:
            st.session_state.current_q_time_limit = REDUCED_Q_TIME

        st.session_state.answers[f"Q{st.session_state.q_index+1}"] = option
        st.session_state.q_index += 1
        st.session_state.question_start_time = None

        if st.session_state.q_index >= len(st.session_state.questions):
            st.session_state.show_result = True

        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ===================== RESULT =====================
else:
    total_q = len(st.session_state.questions)
    correct = 0

    for i, q in enumerate(st.session_state.questions):
        ans = st.session_state.answers.get(f"Q{i+1}")
        if ans == q["Correct Answer"]:
            correct += 1

    percentage = correct / total_q
    mins, secs = divmod(int(time.time() - st.session_state.start_time), 60)

    result_text = "CLEARED" if percentage >= 0.6 else "NOT CLEARED"

    if percentage < 0.4:
        tip = "Strengthen fundamentals and revise core protocols regularly."
    elif percentage < 0.6:
        tip = "You are progressing well. Focused practice will improve outcomes."
    else:
        tip = "Excellent performance. Continue reinforcing best practices."

    st.markdown(f"""
    <div class="card">
        <div class="section-title">Assessment Report Card</div>

        <b>Score:</b> {correct}/{total_q}<br>
        <b>Result:</b> {result_text}<br>
        <b>Time Taken:</b> {mins}m {secs}s

        <hr>
        <div class="tip-box">
        🌱 <b>Professional Insight:</b><br>
        {tip}
        </div>
    </div>
    """, unsafe_allow_html=True)

    payload = {
        **st.session_state.candidate,
        "score": f"{correct}/{total_q}",
        "duration": f"{mins}m {secs}s",
        "result": result_text,
        **st.session_state.answers
    }

    try:
        requests.post(BRIDGE_URL, json=payload, timeout=25)
    except Exception:
        pass

    st.success("Assessment submitted successfully.")
