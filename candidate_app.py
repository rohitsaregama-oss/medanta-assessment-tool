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
# Replace with your new Deployment URL from Google Apps Script
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzP--MA4yBRrm59UWWiSk6xFsaSm2TsBb4aoq4GsSDx3loYSL0R90QV2J0c3XCICGde/exec"

st.set_page_config(
    page_title="Medanta Staff Assessment",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= HELPERS =================
def normalize_columns(df):
    df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(" ", "_")
    return df

# ================= STYLES =================
st.markdown("""
<style>
body { background:#F6F8FB; }
.center { text-align:center; }
.card {
    background:white; padding:22px; border-radius:16px;
    box-shadow:0 10px 24px rgba(0,0,0,0.06); margin-bottom:20px;
}
.integrity {
    background:#FFF4F4; border-left:6px solid #B30000;
    padding:14px; border-radius:12px; font-size:14px; color:#5A1A1A; margin-bottom:18px;
}
.timer {
    background:#0B5394; color:white; padding:12px; border-radius:12px;
    text-align:center; font-weight:600; margin-bottom:16px;
}
.slogan { color:#B30000; font-size:22px; font-weight:700; margin-top:6px; }
.subtle { color:#666; font-size:13px; }
</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
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
        "show_result": False,
        "candidate": {},
        "admin": False,
        "level": "Beginner"
    })

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
                    st.error("Invalid key")
        else:
            st.session_state.level = st.selectbox(
                "Set Assessment Level",
                ["Beginner", "Intermediate", "Advanced"],
                index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.level)
            )
            st.info(f"Current Level: {st.session_state.level}")
            if st.button("Lock Admin"):
                st.session_state.admin = False
                st.rerun()

# ================= HEADER =================
st.markdown("<h2 class='center'>Medanta Staff Assessment</h2>", unsafe_allow_html=True)
st.markdown('<div class="integrity"><b>Integrity Declaration:</b> This assessment is the property of <b>Medanta Hospital, Lucknow</b>. Sharing or copying is prohibited.</div>', unsafe_allow_html=True)
st.markdown("<div class='center slogan'>हर एक जान अनमोल</div><div class='center subtle'>Compassion • Care • Clinical Excellence</div>", unsafe_allow_html=True)

# ================= STAFF INFO =================
if not st.session_state.started:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Candidate Information")
    
    name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth", min_value=date(1960,1,1))
    qualification = st.text_input("Qualification")
    category = st.selectbox("Staff Category", ["Nursing","Non-Nursing","Other"])
    
    reg_no = st.text_input("Registration Number")
    
    # Comprehensive Registration Authority Dropdown
    reg_auth = st.selectbox("Registration Authority", options=[
        "Choose an option...",  # Placeholder
        "Andhra Pradesh Nurses & Midwives Council", 
        "Arunachal Pradesh Nursing Council",
        "Assam Nurses' Midwives' & Health Visitors' Council", 
        "Bihar Nurses Registration Council",
        "Chhattisgarh Nursing Council", 
        "Delhi Nursing Council", 
        "Goa Nursing Council",
        "Gujarat Nursing Council", 
        "Haryana Nurses & Nurse-Midwives Council",
        "Himachal Pradesh Nurses Registration Council", 
        "Indian Nursing Council (NRTS)",
        "Jharkhand Nurses Registration Council", 
        "Karnataka State Nursing Council",
        "Kerala Nurses and Midwives Council", 
        "Madhya Pradesh Nurses Registration Council",
        "Maharashtra Nursing Council", 
        "Manipur Nursing Council", 
        "Meghalaya Nursing Council",
        "Mizoram Nursing Council", 
        "Nagaland Nursing Council", 
        "Odisha Nurses & Midwives Council",
        "Punjab Nurses Registration Council", 
        "Rajasthan Nursing Council", 
        "Sikkim Nursing Council",
        "Tamil Nadu Nurses & Midwives Council", 
        "Telangana State Nursing Council",
        "Tripura Nursing Council", 
        "Uttar Pradesh Nurses & Midwives Council",
        "Uttarakhand Nurses & Midwives Council", 
        "West Bengal Nursing Council",
        "Other / Foreign Council", 
        "Not Applicable"
    ]
)
    
    mobile = st.text_input("Mobile Number")
    college = st.text_input("College / Institute")

    if st.button("Start Assessment"):
        if not name or not mobile:
            st.warning("Please fill Name and Mobile Number.")
        else:
            try:
                # Load Excel Files
                tech = normalize_columns(pd.read_excel("questions.xlsx"))
                beh = normalize_columns(pd.read_excel("Behavioural_Questions_100_with_Competency.xlsx"))

                t_count = random.randint(17, 20)
                b_count = TOTAL_QUESTIONS - t_count

                tech_q = tech[tech["level"].str.lower() == st.session_state.level.lower()].sample(t_count)
                beh_q = beh.sample(b_count)

                st.session_state.questions = pd.concat([tech_q, beh_q]).sample(TOTAL_QUESTIONS).to_dict("records")
                st.session_state.candidate = {
                    "name": name, "dob": str(dob), "qualification": qualification,
                    "category": category, "registration_number": reg_no,
                    "registration_authority": reg_auth, "mobile": mobile, "college": college
                }
                st.session_state.start_time = time.time()
                st.session_state.started = True
                st.rerun()
            except Exception as e:
                st.error(f"Error loading questions: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# ================= EXAM INTERFACE =================
elif not st.session_state.show_result:
    if st.session_state.q_start is None:
        st.session_state.q_start = time.time()

    elapsed = int(time.time() - st.session_state.q_start)
    remain = max(0, st.session_state.q_limit - elapsed)

    st.markdown(f"<div class='timer'>⏱ Question Time: {remain}s</div>", unsafe_allow_html=True)
    
    q = st.session_state.questions[st.session_state.idx]
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"**Question {st.session_state.idx+1}/{TOTAL_QUESTIONS}** \n\n{q['question']}")

    choice = st.radio("Select Option:", [q["option_a"], q["option_b"], q["option_c"], q["option_d"]], key=f"q{st.session_state.idx}")

    if st.button("Next") or remain <= 0:
        if elapsed >= SUSPICIOUS_THRESHOLD: st.session_state.slow += 1
        else: st.session_state.slow = 0
        
        if st.session_state.slow >= SUSPICIOUS_LIMIT:
            st.session_state.q_limit = REDUCED_Q_TIME

        st.session_state.answers[f"Q{st.session_state.idx+1}"] = choice
        st.session_state.idx += 1
        st.session_state.q_start = None
        
        if st.session_state.idx >= TOTAL_QUESTIONS:
            st.session_state.show_result = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ================= RESULT & SUBMISSION =================
else:
    correct = sum(1 for i, q in enumerate(st.session_state.questions) if st.session_state.answers.get(f"Q{i+1}") == q["correct_answer"])
    mins, secs = divmod(int(time.time() - st.session_state.start_time), 60)
    result_status = "CLEARED" if correct >= 15 else "NOT CLEARED"

    st.markdown(f"""
    <div class="card" style="text-align:center;">
        <h3>Assessment Result</h3>
        <h1 style="color:#0B5394;">{correct} / {TOTAL_QUESTIONS}</h1>
        <p><b>Status:</b> {result_status}</p>
        <p><b>Time:</b> {mins}m {secs}s | <b>Level:</b> {st.session_state.level}</p>
    </div>
    """, unsafe_allow_html=True)

    # Sync to Google Sheets
    payload = {
        **st.session_state.candidate,
        "score": f"{correct}/{TOTAL_QUESTIONS}",
        "duration": f"{mins}m {secs}s",
        "result": result_status,
        "level": st.session_state.level,
        **st.session_state.answers
    }

    try:
        response = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=15)
        if response.status_code == 200:
            st.success("Results submitted successfully.")
    except:
        st.warning("Connection error. Please take a screenshot of your score.")

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

