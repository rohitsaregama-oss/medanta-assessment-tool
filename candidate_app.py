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
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz1qT4L2mNOusKQ3wjTHwh4tbPHGn0Kb-ek9Anyyn9J7YJKrzCYzQvOKv-FLYlsHmAS/exec "

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

.stApp {
    background: linear-gradient(135deg, #f0f4f8 0%, #e6eef7 100%);
}

.block-container {
    max-width: 600px;
    padding: 1rem 1.5rem;
    margin: 0 auto;
}

/* Header */
.header-wrap {
    text-align: center;
    margin-bottom: 1rem;
}

.logo-circle {
    width: 70px;
    height: 70px;
    background: white;
    border-radius: 50%;
    margin: 0 auto 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 15px rgba(179, 0, 0, 0.15);
    border: 2px solid #B30000;
}

.title-main {
    font-size: 1.4rem;
    font-weight: 700;
    color: #1e293b;
    margin: 0;
    letter-spacing: -0.5px;
}

.tagline-hindi {
    color: #B30000;
    font-size: 1rem;
    font-weight: 600;
    margin: 0.25rem 0;
}

.tagline-sub {
    color: #64748b;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* Integrity Banner */
.integrity-box {
    background: linear-gradient(135deg, #fff5f5 0%, #ffe0e0 100%);
    border-left: 4px solid #B30000;
    padding: 0.875rem;
    border-radius: 0 10px 10px 0;
    margin-bottom: 1rem;
    font-size: 0.8rem;
    color: #7f1d1d;
    line-height: 1.4;
}

.integrity-title {
    font-weight: 700;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Cards */
.card {
    background: white;
    border-radius: 14px;
    padding: 1.25rem;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    border: 1px solid #e2e8f0;
    margin-bottom: 0.875rem;
}

.card-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 1rem;
}

/* Form Grid */
.form-grid {
    display: grid;
    gap: 0.75rem;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}

/* Inputs */
.stTextInput input, .stSelectbox select, .stDateInput input {
    border-radius: 8px !important;
    border: 1.5px solid #e2e8f0 !important;
    padding: 0.625rem !important;
    font-size: 0.875rem !important;
    transition: all 0.2s !important;
}

.stTextInput input:focus, .stSelectbox select:focus {
    border-color: #B30000 !important;
    box-shadow: 0 0 0 3px rgba(179,0,0,0.1) !important;
}

.stTextInput label, .stSelectbox label, .stDateInput label {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: #64748b !important;
    margin-bottom: 0.25rem !important;
}

/* Button */
.stButton button {
    width: 100%;
    background: linear-gradient(135deg, #B30000 0%, #dc2626 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    margin-top: 0.5rem !important;
    box-shadow: 0 4px 6px -1px rgba(179,0,0,0.3) !important;
    transition: transform 0.2s !important;
}

.stButton button:hover {
    transform: translateY(-2px) !important;
}

/* Progress */
.progress-wrap {
    margin-bottom: 0.75rem;
}

.progress-bg {
    background: #e2e8f0;
    height: 5px;
    border-radius: 3px;
    overflow: hidden;
}

.progress-fill {
    background: linear-gradient(90deg, #B30000 0%, #dc2626 100%);
    height: 100%;
   border-radius: 3px;
    transition: width 0.3s ease;
}

.progress-text {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.375rem;
    text-align: center;
    font-weight: 500;
}

/* Timer */
.timer-bar {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: white;
    padding: 0.625rem 1rem;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    font-weight: 600;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
}

.timer-value {
    font-size: 1.125rem;
    font-weight: 700;
    color: #fca5a5;
    font-variant-numeric: tabular-nums;
}

/* Question */
.question-header {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #f1f5f9;
}

.q-badge {
    background: linear-gradient(135deg, #B30000 0%, #dc2626 100%);
    color: white;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.8rem;
    flex-shrink: 0;
}

.q-text {
    font-size: 0.95rem;
    font-weight: 500;
    color: #1e293b;
    line-height: 1.5;
    margin: 0;
}

/* Radio Options */
.stRadio > div {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.stRadio > div > div > label {
    background: #f8fafc !important;
    border: 2px solid #e2e8f0 !important;
    border-radius: 8px !important;
    padding: 0.625rem 0.875rem !important;
    margin: 0 !important;
    font-size: 0.875rem !important;
    color: #334155 !important;
    transition: all 0.2s !important;
}

.stRadio > div > div > label:hover {
    border-color: #cbd5e1 !important;
    background: #f1f5f9 !important;
}

.stRadio > div > div:has(input:checked) > label {
    background: #fef2f2 !important;
    border-color: #B30000 !important;
    color: #B30000 !important;
    font-weight: 600 !important;
}

/* Results */
.result-card {
    text-align: center;
    padding: 1.5rem;
}

.result-emoji {
    font-size: 3rem;
    margin-bottom: 0.5rem;
}

.result-status {
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.result-score {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #B30000 0%, #dc2626 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0.5rem 0;
}

.stats-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.625rem;
    margin: 1rem 0;
}

.stat-pill {
    background: #f8fafc;
    padding: 0.625rem;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
}

.stat-num {
    font-size: 1rem;
    font-weight: 700;
    color: #0f172a;
}

.stat-label {
    font-size: 0.625rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.insight-box {
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    border-left: 3px solid #3b82f6;
    padding: 0.875rem;
    border-radius: 0 8px 8px 0;
    text-align: left;
    margin-top: 1rem;
}

.insight-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: #1e40af;
    margin-bottom: 0.25rem;
}

.insight-text {
    font-size: 0.8125rem;
    color: #1e3a8a;
    line-height: 1.4;
    margin: 0;
}

.success-box {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    border: 1px solid #86efac;
    color: #166534;
    padding: 0.75rem;
    border-radius: 8px;
    text-align: center;
    font-weight: 600;
    font-size: 0.875rem;
    margin-top: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

.error-box {
    background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    border: 1px solid #fecaca;
    color: #991b1b;
    padding: 0.75rem;
    border-radius: 8px;
    text-align: center;
    font-weight: 600;
    font-size: 0.875rem;
    margin-top: 0.75rem;
}

/* Mobile */
@media (max-width: 640px) {
    .block-container { padding: 0.75rem !important; }
    .form-row { grid-template-columns: 1fr; }
    .stats-row { grid-template-columns: 1fr; }
    .title-main { font-size: 1.25rem; }
}

#MainMenu, footer, header { visibility: hidden; }
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

# ================= ADMIN =================
with st.sidebar:
    if st.checkbox("⚙️ Admin", key="admin_toggle"):
        if not st.session_state.admin:
            k = st.text_input("Key", type="password")
            if st.button("Unlock"):
                if k == ADMIN_KEY:
                    st.session_state.admin = True
                    st.success("✓ Access Granted")
                    st.rerun()
                else:
                    st.error("✗ Invalid Key")
        else:
            st.session_state.level = st.selectbox(
                "Level",
                ["Beginner", "Intermediate", "Advanced"],
                index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.level)
            )
            if st.button("Lock"):
                st.session_state.admin = False
                st.rerun()

# ================= HEADER =================
st.markdown("""
<div class="header-wrap">
    <div class="logo-circle">
        <span style="font-size: 1.75rem;">🏥</span>
    </div>
    <h1 class="title-main">Medanta Staff Assessment</h1>
    <div class="tagline-hindi">हर एक जान अनमोल</div>
    <div class="tagline-sub">Compassion • Care • Clinical Excellence</div>
</div>

<div class="integrity-box">
    <div class="integrity-title">🔒 Integrity Declaration</div>
    <div>This assessment is the exclusive intellectual property of <b>Medanta Hospital, Lucknow</b>. Sharing, copying, recording, or external assistance is strictly prohibited.</div>
</div>
""", unsafe_allow_html=True)

# ================= STAFF INFO =================
if not st.session_state.started:

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>Candidate Information</div>", unsafe_allow_html=True)
    
    # Form with validation
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name *", placeholder="Enter full name", key="name")
        dob = st.date_input("Date of Birth", min_value=date(1960,1,1), max_value=date.today())
        qualification = st.text_input("Qualification", placeholder="Degree/Certification")
        category = st.selectbox("Category", ["Nursing", "Non-Nursing", "Other"])
    
    with col2:
        mobile = st.text_input("Mobile *", placeholder="Phone number", key="mobile")
        reg_no = st.text_input("Registration No", placeholder="Reg. ID")
       college = st.text_input("College/Institute", placeholder="Institution name")

    # Validation without st.stop()
    if st.button("Start Assessment →", type="primary"):
        if not name or not mobile:
            st.markdown('<div class="error-box">⚠️ Name and Mobile are required fields</div>', unsafe_allow_html=True)
        else:
            # Proceed only if validation passes
            st.session_state.candidate = {
                "name": name,
                "dob": str(dob),
                "qualification": qualification,
                "category": category,
                "registration_number": reg_no,
                "mobile": mobile,
                "college": college
            }

            try:
                tech = pd.read_excel("questions.xlsx")
                beh = pd.read_excel("Behavioural_Questions_100_with_Competency.xlsx")

                t = random.randint(17, 20)
                b = TOTAL_QUESTIONS - t

                tq = tech[tech["level"].str.lower() == st.session_state.level.lower()].sample(t)
                bq = beh.sample(b)

                st.session_state.questions = (
                    pd.concat([tq, bq]).sample(TOTAL_QUESTIONS).to_dict("records")
                )

                st.session_state.start_time = time.time()
                st.session_state.started = True
                st.rerun()
            except Exception as e:
                st.error(f"Error loading questions: {str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)

# ================= EXAM =================
elif not st.session_state.result:

    if st.session_state.q_start is None:
        st.session_state.q_start = time.time()

    q_elapsed = int(time.time() - st.session_state.q_start)
    q_remain = max(0, st.session_state.q_limit - q_elapsed)
    progress = ((st.session_state.idx + 1) / TOTAL_QUESTIONS) * 100

    # Progress and Timer
    st.markdown(f"""
    <div class="progress-wrap">
        <div class="progress-bg">
            <div class="progress-fill" style="width: {progress}%"></div>
        </div>
        <div class="progress-text">Question {st.session_state.idx + 1} of {TOTAL_QUESTIONS}</div>
    </div>
    """, unsafe_allow_html=True)

    timer_color = "#ef4444" if q_remain < 10 else "#fca5a5"
    st.markdown(f"""
    <div class="timer-bar">
        <span>⏱</span>
        <span>Time Remaining:</span>
        <span class="timer-value" style="color: {timer_color};">{q_remain}s</span>
    </div>
    """, unsafe_allow_html=True)

    q = st.session_state.questions[st.session_state.idx]

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="question-header">
        <div class="q-badge">{st.session_state.idx + 1}</div>
        <div class="q-text">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    choice = st.radio(
        "Select your answer:",
        [q["option_a"], q["option_b"], q["option_c"], q["option_d"]],
        key=f"q{st.session_state.idx}",
        label_visibility="collapsed"
    )

    cols = st.columns([2, 1])
    with cols[1]:
        if st.button("Next →", type="primary"):
            if q_elapsed >= SUSPICIOUS_THRESHOLD:
                st.session_state.slow += 1
            else:
                st.session_state.slow = 0

            if st.session_state.slow >= SUSPICIOUS_LIMIT:
                st.session_state.q_limit = REDUCED_Q_TIME
                st.toast("⚡ Timer reduced due to slow responses", icon="⚠️")

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
        if st.session_state.answers.get(f"Q{i+1}") == q["correct_answer"]
    )

    mins, secs = divmod(int(time.time() - st.session_state.start_time), 60)
    passed = correct >= 15
    result_text = "CLEARED" if passed else "NOT CLEARED"
    result_color = "#166534" if passed else "#991b1b"
    emoji = "🎉" if passed else "📋"

    tip = (
        "Excellent work! You demonstrate strong clinical knowledge and decision-making skills. Continue maintaining high standards of patient care."
        if passed else
        "Focus on reviewing clinical protocols and patient safety procedures. With dedicated preparation, you can achieve the required competency level."
    )

    st.markdown(f"""
    <div class="card result-card">
        <div class="result-emoji">{emoji}</div>
        <div class="result-status" style="color: {result_color};">{result_text}</div>
        <div class="result-score">{correct}<span style="font-size: 1.25rem; color: #64748b;">/25</span></div>
        
        <div class="stats-row">
            <div class="stat-pill">
                <div class="stat-num">{int((correct/25)*100)}%</div>
                <div class="stat-label">Accuracy</div>
            </div>
            <div class="stat-pill">
                <div class="stat-num">{mins}m {secs}s</div>
                <div class="stat-label">Duration</div>
            </div>
            <div class="stat-pill">
                <div class="stat-num">{st.session_state.level[:3]}</div>
                <div class="stat-label">Level</div>
            </div>
        </div>
        
        <div class="insight-box">
            <div class="insight-title">💡 Professional Insight</div>
            <div class="insight-text">{tip}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Submit results
    payload = {
        **st.session_state.candidate,
        "score": f"{correct}/25",
        "percentage": f"{int((correct/25)*100)}%",
        "duration": f"{mins}m {secs}s",
        "result": result_text,
        "level": st.session_state.level,
        **st.session_state.answers
    }

    try:
        response = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=20)
        if response.status_code == 200:
            st.markdown('<div class="success-box"><span>✓</span><span>Assessment submitted successfully</span></div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ Submission issue. Please screenshot results.")
    except:
        st.error("✗ Network error. Please contact administrator with screenshot.")

    if st.button("← Return to Home"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
