import streamlit as st
import pandas as pd
import requests
import time
import random
from datetime import date

# ================= CONFIG =================
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbz1qT4L2mNOusKQ3wjTHwh4tbPHGn0Kb-ek9Anyyn9J7YJKrzCYzQvOKv-FLYlsHmAS/exec"

TOTAL_TEST_TIME = 25 * 60  # 25 minutes

TECH_MIN, TECH_MAX = 17, 20
BEHAV_MIN, BEHAV_MAX = 5, 8
PASS_PERCENT = 0.60

# Per-question timer logic
DEFAULT_Q_TIME = 60
REDUCED_Q_TIME = 40
SUSPICIOUS_THRESHOLD = 55
SUSPICIOUS_LIMIT = 3

st.set_page_config(page_title="Medanta Staff Assessment", layout="centered")

# ================= UI / THEME =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #F4F8FB 0%, #FFFFFF 100%);
    font-family: "Segoe UI", sans-serif;
}
.card {
    background-color: #FFFFFF;
    padding: 24px;
    border-radius: 14px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
    margin-bottom: 22px;
}
.section-title {
    color: #0B5394;
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 14px;
}
div[data-testid="stRadio"] > label {
    background-color: #F8FBFF;
    padding: 14px;
    border-radius: 10px;
    border: 1px solid #DDE7F1;
    margin-bottom: 8px;
}
div[data-testid="stRadio"] > label:hover {
    background-color: #EAF2FB;
    border-color: #0B5394;
}
.stButton button {
    background: linear-gradient(90deg, #0B5394, #073763);
    color: white;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.6rem 1.4rem;
}
.timer-box {
    position: fixed;
    top: 90px;
    right: 20px;
    background: #FFFFFF;
    border-radius: 12px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    padding: 14px 18px;
    min-width: 190px;
    border-left: 6px solid #0B5394;
    z-index: 9999;
}
.timer-title {
    font-size: 14px;
    font-weight: 600;
    color: #0B5394;
}
.timer-text {
    font-size: 13px;
    color: #333;
}
.timer-warning {
    color: #B30000;
    font-weight: 600;
}
.tip-box {
    background-color: #EAF2FB;
    border-left: 6px solid #0B5394;
    padding: 12px 16px;
    border-radius: 8px;
    color: #0B5394;
    font-size: 14px;
    margin-bottom: 12px;
}
</style>

<script>
window.onbeforeunload = function () {
    return "Refreshing or leaving will terminate the assessment.";
};
document.addEventListener('contextmenu', e => e.preventDefault());
document.addEventListener('copy', e => e.preventDefault());
document.addEventListener('cut', e => e.preventDefault());
document.addEventListener('paste', e => e.preventDefault());
document.addEventListener('selectstart', e => e.preventDefault());

let blurCount = 0;
window.addEventListener('blur', () => {
    blurCount++;
    if (blurCount <= 3) {
        alert("⚠ Please stay on the assessment screen.");
    }
});
</script>
""", unsafe_allow_html=True)

# ================= BRANDING =================
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("MHPL logo 2.png", use_container_width=True)

st.markdown("""
<div style="text-align:center;">
<h2 style="color:#0B5394;">Staff Assessment & Competency Evaluation</h2>
<p style="color:#555;">Medanta – The Medicity</p>
</div>
<hr>
""", unsafe_allow_html=True)

# ================= SESSION INIT =================
if "started" not in st.session_state:
    st.session_state.update({
        "started": False,
        "attempt_started": False,
        "questions": [],
        "answers": {},
        "results": {},
        "competency_map": {},
        "q_index": 0,
        "start_time": None,
        "question_start_time": None,
        "current_q_time_limit": DEFAULT_Q_TIME,
        "suspicious_streak": 0,
        "show_result": False,
        "candidate": {}
    })

if st.session_state.attempt_started and not st.session_state.started:
    st.error("⚠ This assessment session has ended. Please contact HR for a fresh attempt.")
    st.stop()

# ================= TIPS =================
IN_EXAM_TIPS = [
    "Read the question carefully — often the answer is in the wording.",
    "Take your time. Calm thinking leads to safer decisions.",
    "Eliminate unsafe options first — patient safety comes before speed.",
    "Trust your training and professional judgement.",
    "If unsure, choose the option aligned with hospital protocol."
]

# ================= QUESTION ENGINE =================
def prepare_questions(category, level="beginner"):
    tech_df = pd.read_excel("questions.xlsx")
    behav_df = pd.read_excel("Behavioural_Questions_100_with_Competency.xlsx")

    tech_q = tech_df[
        (tech_df["category"] == category) &
        (tech_df["level"].str.lower() == level.lower())
    ].sample(random.randint(TECH_MIN, TECH_MAX))

    behav_q = behav_df.sample(random.randint(BEHAV_MIN, BEHAV_MAX))

    questions = []

    for _, r in tech_q.iterrows():
        opts = [r["Option A"], r["Option B"], r["Option C"], r["Option D"]]
        random.shuffle(opts)
        questions.append({
            "question": r["question"],
            "options": opts,
            "correct": r["Correct Answer"],
            "competency": "Technical"
        })

    for _, r in behav_q.iterrows():
        opts = [r["Option A"], r["Option B"], r["Option C"], r["Option D"]]
        random.shuffle(opts)
        questions.append({
            "question": r["question"],
            "options": opts,
            "correct": r["Correct Answer"],
            "competency": r["competency"]
        })

    random.shuffle(questions)
    return questions

# ================= START SCREEN =================
if not st.session_state.started:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Candidate Information</div>', unsafe_allow_html=True)

    name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth", min_value=date(1960,1,1))
    qualification = st.text_input("Qualification")
    category = st.selectbox("Staff Category", ["Nursing","Clinician","Non Clinical","Support"])

    reg_no = st.text_input("Registration Number") if category in ["Nursing","Clinician"] else st.text_input("Registration Number (Optional)")
    mobile = st.text_input("Mobile Number (10 digits)")
    college = st.text_input("College / Institute")

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Start Assessment"):
        if not name or not mobile.isdigit() or len(mobile) != 10:
            st.warning("Please enter valid candidate details.")
            st.stop()
        if category in ["Nursing","Clinician"] and not reg_no:
            st.warning("Registration Number is mandatory for this category.")
            st.stop()

        st.session_state.questions = prepare_questions(category)
        st.session_state.started = True
        st.session_state.attempt_started = True
        st.session_state.start_time = time.time()
        st.session_state.candidate = {
            "name": name,
            "dob": str(dob),
            "qualification": qualification,
            "category": category,
            "registration_no": reg_no,
            "mobile": mobile,
            "college": college
        }
        st.rerun()

# ================= EXAM =================
elif not st.session_state.show_result:
    total_q = len(st.session_state.questions)

    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(0, TOTAL_TEST_TIME - elapsed)

    if remaining <= 0:
        st.session_state.show_result = True
        st.rerun()

    if st.session_state.question_start_time is None:
        st.session_state.question_start_time = time.time()

    q_elapsed = int(time.time() - st.session_state.question_start_time)
    q_remaining = max(0, st.session_state.current_q_time_limit - q_elapsed)

    warning = "timer-warning" if q_remaining <= 10 else ""

    st.markdown(f"""
    <div class="timer-box">
        <div class="timer-title">⏱ Time</div>
        <div class="timer-text">Test: {remaining//60:02d}:{remaining%60:02d}</div>
        <div class="timer-text {warning}">Question: {q_remaining:02d}s</div>
    </div>
    """, unsafe_allow_html=True)

    if q_remaining <= 0:
        qn = f"Q{st.session_state.q_index + 1}"
        st.session_state.results[qn] = "✖"
        st.session_state.q_index += 1
        st.session_state.question_start_time = None
        if st.session_state.q_index >= total_q:
            st.session_state.show_result = True
        st.rerun()

    q = st.session_state.questions[st.session_state.q_index]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>Question {st.session_state.q_index+1} of {total_q}</div>", unsafe_allow_html=True)
    st.markdown(f"<p>{q['question']}</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='tip-box'>💡 {random.choice(IN_EXAM_TIPS)}</div>", unsafe_allow_html=True)

    choice = st.radio("", q["options"], index=None)
    st.markdown('</div>', unsafe_allow_html=True)

    if choice:
        time_taken = time.time() - st.session_state.question_start_time

        if time_taken >= SUSPICIOUS_THRESHOLD:
            st.session_state.suspicious_streak += 1
        else:
            st.session_state.suspicious_streak = 0

        if st.session_state.suspicious_streak >= SUSPICIOUS_LIMIT:
            st.session_state.current_q_time_limit = REDUCED_Q_TIME

        qn = f"Q{st.session_state.q_index + 1}"
        st.session_state.answers[st.session_state.q_index] = choice
        st.session_state.results[qn] = "✔" if choice == q["correct"] else "✖"
        st.session_state.competency_map[qn] = q["competency"]

        st.session_state.q_index += 1
        st.session_state.question_start_time = None

        if st.session_state.q_index >= total_q:
            st.session_state.show_result = True
        st.rerun()

# ================= RESULT =================
else:
    elapsed = int(time.time() - st.session_state.start_time)
    mins, secs = divmod(elapsed, 60)

    total_q = len(st.session_state.questions)
    correct = list(st.session_state.results.values()).count("✔")

    score_text = f"{correct}/{total_q}"
    result_text = "PASS" if (correct / total_q) >= PASS_PERCENT else "NOT CLEARED"

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Assessment Report Card</div>', unsafe_allow_html=True)
    st.metric("Score", score_text)
    st.metric("Result", result_text)
    st.metric("Time Taken", f"{mins}m {secs}s")
    st.markdown('</div>', unsafe_allow_html=True)

    payload = {
        **st.session_state.candidate,
        "score": score_text,
        "duration": f"{mins}m {secs}s",
        "result": result_text,
        "answers": st.session_state.answers
    }

    requests.post(BRIDGE_URL, json=payload, timeout=10)
    st.stop()
