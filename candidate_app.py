import streamlit as st
import pandas as pd
import random
import time
import requests
from datetime import date

# ================= CONFIG =================
TOTAL_QUESTIONS = 25

DEFAULT_Q_TIME = 60
REDUCED_Q_TIME = 40
SUSPICIOUS_THRESHOLD = 55
SUSPICIOUS_LIMIT = 3

ADMIN_KEY = "Medanta@Admin2026"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz1qT4L2mNOusKQ3wjTHwh4tbPHGn0Kb-ek9Anyyn9J7YJKrzCYzQvOKv-FLYlsHmAS/exec"

st.set_page_config(
    page_title="Medanta Staff Assessment",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= DESIGN LANGUAGE =================
st.markdown("""
<style>
body {
    background:#F6F8FB;
}

.center {
    text-align:center;
}

.card {
    background:#FFFFFF;
    padding:22px;
    border-radius:18px;
    box-shadow:0 12px 28px rgba(0,0,0,0.08);
    margin-bottom:22px;
}

.integrity {
    background:#FFF4F4;
    border-left:6px solid #B30000;
    padding:14px 16px;
    border-radius:12px;
    font-size:14px;
    color:#5A1A1A;
    margin:18px 0 22px 0;
}

.slogan {
    font-size:22px;
    font-weight:700;
    color:#B30000;
    margin-top:6px;
}

.subtle {
    font-size:13px;
    color:#666;
    margin-bottom:22px;
}

.timer {
    background:linear-gradient(135deg,#1a1a1a,#e11d48);
    color:white;
    padding:12px;
    border-radius:14px;
    text-align:center;
    font-weight:600;
    margin-bottom:18px;
}

.tip {
    background:#E8F4FF;
    padding:14px;
    border-radius:12px;
    margin-top:16px;
    font-size:14px;
}

@media(max-width:600px){
    .card { padding:16px; }
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION =================
if "started" not in st.session_state:
    st.session_state.update({
        "started": False,
        "questions": [],
        "answers": {},
        "idx": 0,
        "start_time": None,
        "q_start": None,
        "q_limit": DEFAULT_Q_TIME,
        "slow": 0,
        "result": False,
        "candidate": {},
        "admin": False,
        "level": "Beginner"
    })

# ================= ADMIN (HIDDEN) =================
with st.sidebar:
    if st.checkbox("⚙️"):
        if not st.session_state.admin:
            k = st.text_input("Admin Key", type="password")
            if st.button("Unlock"):
                if k == ADMIN_KEY:
                    st.session_state.admin = True
                    st.success("Admin Unlocked")
                else:
                    st.error("Invalid Key")
        else:
            st.session_state.level = st.selectbox(
                "Assessment Level",
                ["Beginner", "Intermediate", "Advanced"]
            )

# ================= HEADER =================
st.image("MHPL logo 2.png", width=140)

st.markdown("<h2 class='center'>Medanta Staff Assessment</h2>", unsafe_allow_html=True)

st.markdown("""
<div class="integrity">
<b>Integrity Declaration</b><br>
This assessment is the exclusive intellectual property of
<b>Medanta Hospital, Lucknow</b>.<br>
Any form of copying, sharing, recording, or external assistance
is strictly prohibited and may invite disciplinary action.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="center slogan">हर एक जान अनमोल</div>
<div class="center subtle">Compassion • Care • Clinical Excellence</div>
""", unsafe_allow_html=True)

# ================= STAFF INFO =================
if not st.session_state.started:

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Staff Information")

    name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth", min_value=date(1960,1,1))
    qualification = st.text_input("Qualification")
    category = st.selectbox("Staff Category", ["Nursing","Non-Nursing","Other"])
    reg_no = st.text_input("Registration Number")
    mobile = st.text_input("Mobile Number")
    college = st.text_input("College / Institute")

    if st.button("Start Assessment"):
        if not name or not mobile:
            st.warning("Full Name and Mobile Number are mandatory.")
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

        tech = pd.read_excel("questions.xlsx")
        beh = pd.read_excel("Behavioural_Questions_100_with_Competency.xlsx")

        t = random.randint(17, 20)
        b = TOTAL_QUESTIONS - t

        tq = tech[tech["level"].str.lower() == st.session_state.level.lower()].sample(t)
        bq = beh.sample(b)

        st.session_state.questions = (
            pd.concat([tq, bq])
            .sample(TOTAL_QUESTIONS)
            .to_dict("records")
        )

        st.session_state.start_time = time.time()
        st.session_state.started = True
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ================= EXAM =================
elif not st.session_state.result:

    if st.session_state.q_start is None:
        st.session_state.q_start = time.time()

    q_elapsed = int(time.time() - st.session_state.q_start)
    q_remain = max(0, st.session_state.q_limit - q_elapsed)

    st.markdown(
        f"<div class='timer'>⏱ Question Time Remaining: {q_remain}s</div>",
        unsafe_allow_html=True
    )

    q = st.session_state.questions[st.session_state.idx]

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(
        f"**Question {st.session_state.idx+1}/{TOTAL_QUESTIONS}**  \n{q['question']}"
    )

    options = [
        q.get("Option A"),
        q.get("Option B"),
        q.get("Option C"),
        q.get("Option D"),
    ]

    choice = st.radio(
        "Select one option:",
        options,
        key=f"q{st.session_state.idx}"
    )

    if st.button("Next"):
        if q_elapsed >= SUSPICIOUS_THRESHOLD:
            st.session_state.slow += 1
        else:
            st.session_state.slow = 0

        if st.session_state.slow >= SUSPICIOUS_LIMIT:
            st.session_state.q_limit = REDUCED_Q_TIME

        st.session_state.answers[f"Q{st.session_state.idx+1}"] = choice
        st.session_state.idx += 1
        st.session_state.q_start = None

        if st.session_state.idx >= TOTAL_QUESTIONS:
            st.session_state.result = True

        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ================= RESULT =================
else:
    correct = sum(
        1 for i, q in enumerate(st.session_state.questions)
        if st.session_state.answers.get(f"Q{i+1}") == q.get("Correct Answer")
    )

    mins, secs = divmod(int(time.time() - st.session_state.start_time), 60)
    result = "CLEARED" if correct >= 15 else "NOT CLEARED"

    tip = (
        "You demonstrate strong professional judgment. Continue reinforcing safe clinical practices."
        if correct >= 15 else
        "Focus on protocols, calm decision-making, and situational awareness. Improvement is well within reach."
    )

    st.markdown(f"""
    <div class="card">
        <h3>Assessment Report</h3>
        <b>Score:</b> {correct}/{TOTAL_QUESTIONS}<br>
        <b>Result:</b> {result}<br>
        <b>Time Taken:</b> {mins}m {secs}s
        <div class="tip"><b>Professional Insight:</b><br>{tip}</div>
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
        requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=20)
    except:
        pass

    st.success("Assessment submitted successfully.")
