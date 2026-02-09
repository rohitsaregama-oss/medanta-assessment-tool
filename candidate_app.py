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
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyevoLAfqRpNG74ZxaLgL_vzlDqqlE19S1BvI_y-8wlwCsHfm_und3q6WXoWPV3c61C/exec"

st.set_page_config(page_title="Medanta Assessment", layout="centered", initial_sidebar_state="collapsed")

# ================= SESSION STATE =================
if "started" not in st.session_state:
    st.session_state.update({
        "started": False, "questions": [], "answers": {}, "idx": 0, "start_time": None,
        "q_start": None, "q_limit": DEFAULT_Q_TIME, "slow": 0, "show_result": False,
        "candidate": {}, "admin": False, "level": "Beginner", "submitted": False
    })

# ================= ADMIN & STYLES =================
with st.sidebar:
    if st.checkbox("⚙️ Admin"):
        if not st.session_state.admin:
            key = st.text_input("Admin Key", type="password")
            if st.button("Unlock"):
                if key == ADMIN_KEY: st.session_state.admin = True; st.rerun()
        else:
            st.session_state.level = st.selectbox("Exam Level", ["Beginner", "Intermediate", "Advanced"])
            if st.button("Lock"): st.session_state.admin = False; st.rerun()

st.markdown("""
<style>
.card { background:white; padding:20px; border-radius:15px; box-shadow:0 4px 10px rgba(0,0,0,0.1); margin-bottom:20px; }
.timer-text { color:#0B5394; font-weight:bold; text-align:center; font-size:18px; }
.center { text-align:center; }
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
try:
    st.image("MHPL logo 2.png", width=250)
except:
    st.title("🏥 Medanta Assessment")

st.markdown("<h4 class='center'>Staff Clinical Competency Assessment</h4>", unsafe_allow_html=True)

# ================= STAFF INFO =================
if not st.session_state.started:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    name = st.text_input("Full Name *")
    mobile = st.text_input("Mobile Number *")
    reg_no = st.text_input("Nursing Registration Number")
    
    reg_auth = st.selectbox("Select the Nursing Registration Authority *", [
        "Choose an option...",
        "Andhra Pradesh Nurses & Midwives Council", "Arunachal Pradesh Nursing Council",
        "Assam Nurses' Midwives' & Health Visitors' Council", "Bihar Nurses Registration Council",
        "Chhattisgarh Nursing Council", "Delhi Nursing Council", "Goa Nursing Council",
        "Gujarat Nursing Council", "Haryana Nurses & Nurse-Midwives Council",
        "Himachal Pradesh Nurses Registration Council", "Indian Nursing Council (NRTS)",
        "Jharkhand Nurses Registration Council", "Karnataka State Nursing Council",
        "Kerala Nurses and Midwives Council", "Madhya Pradesh Nurses Registration Council",
        "Maharashtra Nursing Council", "Manipur Nursing Council", "Meghalaya Nursing Council",
        "Mizoram Nursing Council", "Nagaland Nursing Council", "Odisha Nurses & Midwives Council",
        "Punjab Nurses Registration Council", "Rajasthan Nursing Council", "Sikkim Nursing Council",
        "Tamil Nadu Nurses & Midwives Council", "Telangana State Nursing Council",
        "Tripura Nursing Council", "Uttar Pradesh Nurses & Midwives Council",
        "Uttarakhand Nurses & Midwives Council", "West Bengal Nursing Council",
        "Other State Council", "Foreign Nursing Council", "Not Applicable"
    ])
    
    college = st.text_input("College / Institute")

    if st.button("Start Assessment"):
        if not name or not mobile or reg_auth == "Choose an option...":
            st.error("Please fill Name, Mobile, and Registration Authority.")
        else:
            try:
                tech = pd.read_excel("questions.xlsx")
                beh = pd.read_excel("Behavioural_Questions_100_with_Competency.xlsx")
                t_q = tech[tech["level"].str.lower() == st.session_state.level.lower()].sample(20)
                b_q = beh.sample(5)
                st.session_state.questions = pd.concat([t_q, b_q]).sample(25).to_dict("records")
                
                b_key = f"MED-{random.randint(100,999)}-{int(time.time()%1000)}"
                st.session_state.candidate = {
                    "bridge_key": b_key, "name": name, "mobile": mobile, 
                    "reg_no": reg_no, "reg_auth": reg_auth, "level": st.session_state.level, "college": college
                }
                st.session_state.start_time = time.time()
                st.session_state.started = True
                st.rerun()
            except Exception as e:
                st.error(f"Error loading files: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# ================= EXAM =================
elif not st.session_state.show_result:
    if st.session_state.q_start is None: st.session_state.q_start = time.time()
    elapsed = int(time.time() - st.session_state.q_start)
    remain = max(0, st.session_state.q_limit - elapsed)

    st.markdown(f"<p class='timer-text'>⏱ Time Left: {remain}s</p>", unsafe_allow_html=True)
    
    q = st.session_state.questions[st.session_state.idx]
    st.markdown(f"<div class='card'><strong>Question {st.session_state.idx+1}/25</strong><br><br>{q['question']}</div>", unsafe_allow_html=True)
    
    choice = st.radio("Select Answer:", [q["option_a"], q["option_b"], q["option_c"], q["option_d"]], key=f"q{st.session_state.idx}")

    if st.button("Next Question") or remain <= 0:
        st.session_state.answers[f"Q{st.session_state.idx+1}"] = choice
        st.session_state.idx += 1
        st.session_state.q_start = None
        if st.session_state.idx >= 25: st.session_state.show_result = True
        st.rerun()

# ================= RESULTS =================
else:
    correct = 0
    payload = {**st.session_state.candidate}
    for i in range(25):
        u_ans = st.session_state.answers.get(f"Q{i+1}")
        c_ans = st.session_state.questions[i]["correct_answer"]
        is_right = (u_ans == c_ans)
        if is_right: correct += 1
        payload[f"Q{i+1}"] = u_ans
        payload[f"Q{i+1}_status"] = "CORRECT" if is_right else "WRONG"

    payload["score"] = f"{correct}/25"
    st.markdown(f"<div class='card center'><h2>Score: {correct}/25</h2><p>ID: {st.session_state.candidate['bridge_key']}</p></div>", unsafe_allow_html=True)

    if not st.session_state.submitted:
        try:
            r = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=20)
            if r.status_code == 200:
                st.success("Assessment Submitted Successfully!")
                st.session_state.submitted = True
        except:
            st.error("Submission failed. Please contact Admin.")

    if st.button("Finish"):
        st.session_state.clear()
        st.rerun()
