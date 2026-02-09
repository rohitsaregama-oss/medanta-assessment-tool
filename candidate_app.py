import streamlit as st
import pandas as pd
import requests
import time
import random
from datetime import date

# ================== CONFIG ==================
BRIDGE_URL = "https://script.google.com/macros/s/AKfycbxF7Cp_rN_Zge3RYeDbYzMBEhNGUWDTlAg0M9UajBkFeThOcfGV36Kg98fy6488K-Q/exec"

TECH_MIN, TECH_MAX = 17, 20
BEHAV_MIN, BEHAV_MAX = 5, 8
PASS_PERCENT = 0.60   # 60%

st.set_page_config(page_title="Medanta Staff Assessment", layout="centered")

# ================== UI STYLING ==================
st.markdown("""
<style>
.stApp { background-color: #F4F8FB; }
h3 { font-weight: 600; }

div[data-testid="stRadio"] > label {
    background-color: #FFFFFF;
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #E0E7EF;
    margin-bottom: 6px;
}
div[data-testid="stRadio"] > label:hover { background-color: #EAF2FB; }

.stButton button {
    background-color: #0B5394;
    color: white;
    border-radius: 6px;
    font-weight: 600;
}
.stButton button:hover { background-color: #073763; }

[data-testid="stProgress"] > div > div { background-color: #0B5394; }
</style>
""", unsafe_allow_html=True)

# ================== BRANDING ==================
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("MHPL logo 2.png", use_container_width=True)

st.markdown("""
<h3 style="text-align:center; color:#0B5394;">Staff Assessment & Competency Evaluation</h3>
<p style="text-align:center; color:#555;">Medanta – Lucknow</p>
<hr>
""", unsafe_allow_html=True)

# ================== SESSION ==================
if "started" not in st.session_state:
    st.session_state.update({
        "started": False,
        "questions": [],
        "answers": {},
        "results": {},
        "competency_map": {},
        "q_index": 0,
        "start_time": None,
        "show_result": False,
        "candidate": {}
    })

# ================== TIPS ==================
IN_EXAM_TIPS = [
    "🔍 Read the question carefully — often the answer is in the wording.",
    "🧘 Take your time. Calm thinking leads to safer decisions.",
    "✅ Eliminate unsafe options first — patient safety comes before speed.",
    "💡 Trust your training and judgement.",
    "📘 If unsure, choose the option aligned with hospital protocol."
]

# ================== QUESTION ENGINE ==================
def prepare_questions(category, level="beginner"):
    tech_df = pd.read_excel("questions.xlsx")
    behav_df = pd.read_excel("Behavioural_Questions_100_with_Competency.xlsx")

    tech_count = random.randint(TECH_MIN, TECH_MAX)
    behav_count = random.randint(BEHAV_MIN, BEHAV_MAX)

    tech_pool = tech_df[
    (tech_df["category"] == category) &
    (tech_df["level"].str.lower() == level.lower())
    ]

    tech_q = tech_pool.sample(tech_count)
    behav_q = behav_df.sample(behav_count)

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

# ================== START SCREEN ==================
if not st.session_state.started:
    st.subheader("Candidate Information")

    name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth", min_value=date(1960,1,1))
    qualification = st.text_input("Qualification")
    category = st.selectbox("Staff Category", ["Nursing","Clinician","Non Clinical","Support"])

    reg_no = st.text_input("Registration Number") if category in ["Nursing","Clinician"] else st.text_input("Registration Number (Optional)")
    mobile = st.text_input("Mobile Number (10 digits)")
    college = st.text_input("College / Institute")

    if st.button("Start Assessment"):
        if not name or not mobile.isdigit() or len(mobile) != 10:
            st.warning("Please enter valid details.")
            st.stop()

        if category in ["Nursing","Clinician"] and not reg_no:
            st.warning("Registration Number is mandatory.")
            st.stop()

        st.session_state.questions = prepare_questions(category)
        st.session_state.start_time = time.time()
        st.session_state.started = True
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

# ================== EXAM ==================
elif not st.session_state.show_result:
    total_q = len(st.session_state.questions)
    st.progress((st.session_state.q_index + 1) / total_q)

    q = st.session_state.questions[st.session_state.q_index]
    st.subheader(f"Question {st.session_state.q_index + 1} of {total_q}")
    st.write(q["question"])
    st.info(random.choice(IN_EXAM_TIPS))

    choice = st.radio("Select your answer", q["options"], index=None)

    if choice:
        qn = f"Q{st.session_state.q_index + 1}"
        correct = choice == q["correct"]

        st.session_state.answers[st.session_state.q_index] = choice
        st.session_state.results[qn] = "✔" if correct else "✖"
        st.session_state.competency_map[qn] = q["competency"]

        st.session_state.q_index += 1
        if st.session_state.q_index >= total_q:
            st.session_state.show_result = True
        st.rerun()

# ================== RESULT ==================
else:
    elapsed = int(time.time() - st.session_state.start_time)
    mins, secs = divmod(elapsed, 60)

    total_q = len(st.session_state.questions)
    correct_count = list(st.session_state.results.values()).count("✔")
    score_text = f"{correct_count}/{total_q}"
    result_text = "PASS" if (correct_count / total_q) >= PASS_PERCENT else "NOT CLEARED"

    st.markdown("<h2 style='color:#0B5394;'>Assessment Report Card</h2>", unsafe_allow_html=True)
    st.success(f"Score: {score_text}")
    st.write(f"**Result:** {result_text}")
    st.write(f"**Time Taken:** {mins} min {secs} sec")

    if (correct_count / total_q) >= 0.80:
        tip = "🌟 Excellent fundamentals. Keep reinforcing best practices."
    elif (correct_count / total_q) >= 0.60:
        tip = "👍 Good base. Revisit patient safety and communication scenarios."
    else:
        tip = "📘 Learning opportunity. Focus on protocols and safety basics."

    st.info(f"**Self-Improvement Tip:** {tip}")

    st.divider()
    st.write("### Question-wise Summary")
    for qn, res in st.session_state.results.items():
        st.write(f"{qn} : {res}")

    payload = {
        **st.session_state.candidate,
        "score": score_text,
        "duration": f"{mins}m {secs}s",
        "result": result_text,
        "question_map": st.session_state.results,
        "answers": st.session_state.answers,
        "competency_map": st.session_state.competency_map
    }

    requests.post(BRIDGE_URL, json=payload, timeout=10)
    st.stop()



