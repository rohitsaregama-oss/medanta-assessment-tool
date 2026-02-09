import streamlit as st
import pandas as pd
import random, time, requests
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
    page_title="Medanta Assessment",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= AESTHETIC STYLES =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #f0f4f8 0%, #e6eef7 100%); }
.block-container { max-width: 600px; padding: 1rem 1.5rem; margin: 0 auto; }
.header-wrap { text-align: center; margin-bottom: 1rem; }
.logo-circle { width: 70px; height: 70px; background: white; border-radius: 50%; margin: 0 auto 0.75rem; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(179, 0, 0, 0.15); border: 2px solid #B30000; }
.title-main { font-size: 1.4rem; font-weight: 700; color: #1e293b; margin: 0; }
.tagline-hindi { color: #B30000; font-size: 1rem; font-weight: 600; margin: 0.25rem 0; }
.tagline-sub { color: #64748b; font-size: 0.7rem; font-weight: 500; text-transform: uppercase; }
.integrity-box { background: linear-gradient(135deg, #fff5f5 0%, #ffe0e0 100%); border-left: 4px solid #B30000; padding: 0.875rem; border-radius: 0 10px 10px 0; margin-bottom: 1rem; font-size: 0.8rem; color: #7f1d1d; }
.card { background: white; border-radius: 14px; padding: 1.25rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 0.875rem; }
.q-badge { background: #B30000; color: white; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; }
.timer-bar { background: #1e293b; color: white; padding: 0.625rem; border-radius: 10px; text-align: center; margin-bottom: 0.75rem; font-weight: 600; }
.success-box { background: #dcfce7; color: #166534; padding: 0.75rem; border-radius: 8px; text-align: center; margin-top: 0.75rem; }
.error-box { background: #fee2e2; color: #991b1b; padding: 0.75rem; border-radius: 8px; text-align: center; }
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
        "result": False,
        "candidate": {},
        "admin": False,
        "level": "Beginner",
        "submitted": False
    })

# ================= ADMIN SIDEBAR =================
with st.sidebar:
    if st.checkbox("⚙️ Admin"):
        if not st.session_state.admin:
            k = st.text_input("Key", type="password")
            if st.button("Unlock"):
                if k == ADMIN_KEY:
                    st.session_state.admin = True
                    st.rerun()
                else:
                    st.error("Invalid Key")
        else:
            st.session_state.level = st.selectbox("Exam Level", ["Beginner", "Intermediate", "Advanced"])
            if st.button("Lock"):
                st.session_state.admin = False
                st.rerun()

# ================= HEADER =================
st.markdown("""
<div class="header-wrap">
    <div class="logo-circle"><span style="font-size: 1.75rem;">🏥</span></div>
    <h1 class="title-main">Medanta Staff Assessment</h1>
    <div class="tagline-hindi">हर एक जान अनमोल</div>
    <div class="tagline-sub">Compassion • Care • Clinical Excellence</div>
</div>
""", unsafe_allow_html=True)

# ================= STAFF INFO =================
if not st.session_state.started:
    st.markdown('<div class="integrity-box"><b>🔒 Integrity:</b> This assessment is Medanta property. Sharing or copying is prohibited.</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *")
            dob = st.date_input("Date of Birth", min_value=date(1960,1,1))
            category = st.selectbox("Category", ["Nursing", "Non-Nursing", "Other"])
        with col2:
            mobile = st.text_input("Mobile *")
            reg_no = st.text_input("Registration No")
            college = st.text_input("College/Institute")

        if st.button("Start Assessment →"):
            if not name or not mobile:
                st.error("Name and Mobile are required")
            else:
                try:
                    tech = pd.read_excel("questions.xlsx")
                    beh = pd.read_excel("Behavioural_Questions_100_with_Competency.xlsx")
                    
                    t_count = random.randint(17, 20)
                    b_count = TOTAL_QUESTIONS - t_count
                    
                    tq = tech[tech["level"].str.lower() == st.session_state.level.lower()].sample(t_count)
                    bq = beh.sample(b_count)
                    
                    st.session_state.questions = pd.concat([tq, bq]).sample(TOTAL_QUESTIONS).to_dict("records")
                    st.session_state.candidate = {"name": name, "mobile": mobile, "dob": str(dob), "reg": reg_no, "college": college, "cat": category}
                    st.session_state.start_time = time.time()
                    st.session_state.started = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Excel Load Error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

# ================= EXAM INTERFACE =================
elif not st.session_state.result:
    if st.session_state.q_start is None:
        st.session_state.q_start = time.time()

    elapsed = int(time.time() - st.session_state.q_start)
    remain = max(0, st.session_state.q_limit - elapsed)

    # UI Components
    st.write(f"Question {st.session_state.idx + 1} / {TOTAL_QUESTIONS}")
    st.progress((st.session_state.idx + 1) / TOTAL_QUESTIONS)
    
    st.markdown(f'<div class="timer-bar">⏱ Time Remaining: {remain}s</div>', unsafe_allow_html=True)

    q = st.session_state.questions[st.session_state.idx]
    st.markdown(f"<div class='card'><div class='q-text'><b>{q['question']}</b></div></div>", unsafe_allow_html=True)
    
    # Selection
    choice = st.radio("Choose one:", [q["option_a"], q["option_b"], q["option_c"], q["option_d"]], index=None, key=f"r{st.session_state.idx}")

    if st.button("Next Question →") or remain <= 0:
        # Anti-cheat logic
        if elapsed >= SUSPICIOUS_THRESHOLD:
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
    
    # Auto-refresh timer every 2 seconds
    if remain > 0:
        time.sleep(2)
        st.rerun()

# ================= RESULTS =================
else:
    correct = sum(1 for i, q in enumerate(st.session_state.questions) if st.session_state.answers.get(f"Q{i+1}") == q["correct_answer"])
    passed = correct >= 15
    duration = int(time.time() - st.session_state.start_time)
    
    st.markdown(f"<div class='card' style='text-align:center'><h2>Score: {correct}/25</h2></div>", unsafe_allow_html=True)

    # Submit to Google Sheets (Once only)
    if not st.session_state.submitted:
        payload = {**st.session_state.candidate, "score": f"{correct}/25", "result": "Passed" if passed else "Failed"}
        try:
            requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)
            st.session_state.submitted = True
            st.success("Results synced successfully!")
        except:
            st.error("Sync failed. Please screenshot this page.")

    if st.button("Finish & Logout"):
        st.session_state.clear()
        st.rerun()
