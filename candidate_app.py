import streamlit as st
import pandas as pd
import random
import time
import requests
import base64
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

# ================= CSS =================
st.markdown("""
<style>
.stApp { background:#F7F9FC; }

.block-container { max-width:900px; padding:1rem; }

.main-title {
    text-align:center;
    color:#0B5394;
    font-weight:800;
    font-size:28px;
    margin-bottom:12px;
}

.card {
    background:white;
    padding:22px;
    border-radius:18px;
    box-shadow:0 10px 25px rgba(0,0,0,0.08);
    margin-bottom:22px;
}

.section-title {
    font-size:20px;
    font-weight:700;
    color:#0B5394;
    margin-bottom:14px;
}

.timer-box {
    position:fixed;
    top:100px;
    right:20px;
    background:white;
    padding:12px 16px;
    border-radius:12px;
    box-shadow:0 6px 18px rgba(0,0,0,0.15);
    border-left:6px solid #0B5394;
    z-index:9999;
    font-size:14px;
}

.tip-box {
    background:#EDF4EE;
    border-left:6px solid #4F772D;
    padding:14px;
    border-radius:12px;
    font-size:14px;
}

.stButton > button {
    background:linear-gradient(90deg,#F28C28,#E6761C);
    color:white;
    border-radius:14px;
    padding:12px 22px;
    font-weight:600;
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
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================

logo_base64 = base64.b64encode(open("MHPL logo 2.png","rb").read()).decode()

st.markdown(f"""
<div style="display:flex; justify-content:center; margin-bottom:8px;">
    <img src="data:image/png;base64,{logo_base64}" width="140">
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Medanta Staff Assessment</div>', unsafe_allow_html=True)

# ---- INTEGRITY (TOP) ----
st.markdown("""
<div style="
    background:#FFF4F4;
    border-left:6px solid #B30000;
    padding:14px;
    border-radius:12px;
    margin-bottom:14px;
    font-size:14px;
    color:#5A1A1A;
">
<b>Integrity Declaration</b><br>
This assessment is the exclusive intellectual property of
<b>Medanta Hospital, Lucknow</b>.<br>
Sharing, copying, recording, or receiving external assistance
is strictly prohibited and may lead to disciplinary action.
</div>
""", unsafe_allow_html=True)

# ---- HAR EK JAAN ANMOL ----
st.markdown("""
<div style="
    background:linear-gradient(90deg,#B30000,#6E6E6E);
    padding:18px;
    border-radius:16px;
    text-align:center;
    margin-bottom:26px;
">
    <div style="color:white; font-size:22px; font-weight:700;">
        हर एक जान अनमोल
    </div>
    <div style="color:#F2F2F2; font-size:13px; margin-top:6px;">
        Compassion • Care • Clinical Excellence
    </div>
</div>
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

# ================= SIDEBAR ADMIN =================
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
