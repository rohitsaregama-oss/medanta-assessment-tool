import streamlit as st
import pandas as pd
import random
import time
import requests
from datetime import date

# ================= CONFIG =================
TOTAL_QUESTIONS = 25
DEFAULT_Q_TIME = 60
ADMIN_KEY = "Medanta@Admin2026"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyevoLAfqRpNG74ZxaLgL_vzlDqqlE19S1BvI_y-8wlwCsHfm_und3q6WXoWPV3c61C/exec"

st.set_page_config(page_title="Medanta Assessment", layout="centered", initial_sidebar_state="collapsed")

# ================= SESSION STATE =================
if "started" not in st.session_state:
    st.session_state.update({
        "started": False, "questions": [], "answers": {}, "idx": 0, "start_time": None,
        "q_start": None, "show_result": False, "candidate": {}, "admin": False, 
        "level": "Beginner", "submitted": False
    })

# ================= STYLES =================
st.markdown("""
<style>
.card { background:white; padding:22px; border-radius:16px; box-shadow:0 10px 24px rgba(0,0,0,0.06); margin-bottom:20px; }
.integrity { background:#FFF4F4; border-left:6px solid #B30000; padding:14px; border-radius:12px; font-size:14px; color:#5A1A1A; margin-bottom:18px; }
.slogan { color:#B30000; font-size:24px; font-weight:700; text-align:center; margin-top:10px; }
.subtle { color:#666; font-size:13px; text-align:center; margin-bottom:20px; }
.timer-box { background:#0B5394; color:white; padding:10px; border-radius:10px; text-align:center; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ================= ADMIN PANEL =================
with st.sidebar:
    if st.checkbox("⚙️ Admin"):
        if not st.session_state.admin:
            key = st.text_input("Admin Key", type="password")
            if st.button("Unlock"):
                if key == ADMIN_KEY:
                    st.session_state.admin = True
                    st.rerun()
        else:
            st.session_state.level = st.selectbox("Exam Level", ["Beginner", "Intermediate", "Advanced"])
            if st.button("Lock"):
                st.session_state.admin = False
                st.rerun()

# ================= HEADER =================
try:
    st.image("MHPL logo 2.png", width=250)
except:
    st.title("🏥 Medanta Hospital")

st.markdown("<h2 style='text-align:center;'>Staff Clinical Assessment</h2>", unsafe_allow_html=True)

st.markdown("""
<div class="integrity">
<b>🔒 Integrity Declaration</b><br>
This assessment is the exclusive intellectual property of <b>Medanta Hospital, Lucknow</b>. 
Sharing, copying, or external assistance is strictly prohibited.
</div>
<div class="slogan">हर एक जान अनमोल</div>
<div class="subtle">Compassion • Care • Clinical Excellence</div>
""", unsafe_allow_html=True)

# ================= STAFF INFO =================
if not st.session_state.started:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Candidate Information")
    name = st.text_input("Full Name *")
    mobile = st.text_input("Mobile Number *")
    reg_no = st.text_input("Registration Number")
    
    reg_auth = st.selectbox("Select the Nursing Registration Authority *", [
        "Choose an option...", "Andhra Pradesh Nurses & Midwives Council", "Arunachal Pradesh Nursing Council",
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
            st.error("Please complete all mandatory fields (*).")
        else:
            try:
                tech = pd.read_excel("questions.xlsx")
                beh = pd.read_excel("Behavioural_Questions_100_with_Competency.xlsx")
                t_q = tech[tech["level"].str.lower() == st.session_state.level.lower()].sample(20)
                b_q = beh.sample(5)
                st.session_state.questions = pd.concat([t_q, b_q]).sample(TOTAL_QUESTIONS).to_dict("records")
                
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

# ================= EXAM INTERFACE =================
elif not st.session_state.show_result:
    if st.session_state.q_start is None: st.session_state.q_start = time.time()
    elapsed = int(time.time() - st.session_state.q_start)
    remain = max(0, DEFAULT_Q_TIME - elapsed)

    st.markdown(f"<div class='timer-box'>⏱ Question Time Remaining: {remain}s</div>", unsafe_allow_html=True)
    
    q = st.session_state.questions[st.session_state.idx]
    st.markdown(f"<div class='card'><b>Question {st.session_state.idx+1} of 25</b><br><br>{q['question']}</div>", unsafe_allow_html=True)
    
    choice = st.radio("Choose the correct option:", [q["option_a"], q["option_b"], q["option_c"], q["option_d"]], key=f"q{st.session_state.idx}")

    if st.button("Submit Answer & Next"):
        st.session_state.answers[f"Q{st.session_state.idx+1}"] = choice
        st.session_state.idx += 1
        st.session_state.q_start = None
        if st.session_state.idx >= TOTAL_QUESTIONS: 
            st.session_state.show_result = True
        st.rerun()

# ================= RESULTS & SUBMISSION =================
else:
    correct = 0
    payload = {**st.session_state.candidate}
    for i in range(TOTAL_QUESTIONS):
        u_ans = st.session_state.answers.get(f"Q{i+1}")
        c_ans = st.session_state.questions[i]["correct_answer"]
        is_right = (u_ans == c_ans)
        if is_right: correct += 1
        payload[f"Q{i+1}"] = u_ans
        payload[f"Q{i+1}_status"] = "CORRECT" if is_right else "WRONG"

    payload["score"] = f"{correct}/25"
    st.markdown(f"<div class='card' style='text-align:center;'><h2>Assessment Score: {correct}/25</h2><p>Ref ID: {st.session_state.candidate['bridge_key']}</p></div>", unsafe_allow_html=True)

    if not st.session_state.submitted:
        try:
            r = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=20)
            if r.status_code == 200:
                st.success("Results submitted to Medanta Registry.")
                st.session_state.submitted = True
        except:
            st.error("Submission error. Please take a screenshot for HR.")

    if st.button("Close Assessment"):
        st.session_state.clear()
        st.rerun()
