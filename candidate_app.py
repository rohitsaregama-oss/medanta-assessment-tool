import streamlit as st
import pandas as pd
import random, time, requests
from datetime import date

# ================= CONFIG =================
TOTAL_QUESTIONS = 25
TOTAL_EXAM_TIME = 25 * 60  # 25 Minutes Total
DEFAULT_Q_TIME = 60        # 60 Seconds per Question
PASS_MARK = 15             # 60% of 25

# YOUR NEW BRIDGE KEY URL
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzepAmuGns-HWBwagxxUjnHiew_UJjBw4KpC1iLzFchHWStEEIgnYAfCwiqNJxw5odJ/exec"

st.set_page_config(page_title="Medanta Assessment", layout="centered", initial_sidebar_state="collapsed")

# ================= SESSION STATE =================
if "started" not in st.session_state:
    st.session_state.update({
        "started": False, "questions": [], "answers": {}, "idx": 0,
        "start_time": None, "q_start": None, "show_result": False,
        "candidate": {}, "submitted": False
    })

# ================= STYLES =================
st.markdown("""
<style>
.card { background:white; padding:22px; border-radius:16px; box-shadow:0 10px 24px rgba(0,0,0,0.06); margin-bottom:20px; }
.integrity { background:#FFF4F4; border-left:6px solid #B30000; padding:14px; border-radius:12px; font-size:14px; color:#5A1A1A; margin-bottom:18px; }
.slogan { color:#B30000; font-size:24px; font-weight:700; text-align:center; margin-top:10px; }
.subtle { color:#666; font-size:13px; text-align:center; margin-bottom:20px; }
.timer-box { background:#0B5394; color:white; padding:10px; border-radius:10px; text-align:center; font-weight:600; margin-bottom:10px; }
</style>
""", unsafe_allow_html=True)

# ================= HEADER & BANNERS =================
try: 
    st.image("MHPL logo 2.png", width=250)
except: 
    st.title("🏥 Medanta Hospital")

st.markdown("""
<div class="integrity">
<b>🔒 Integrity Declaration</b><br>
This assessment is the property of <b>Medanta Hospital, Lucknow</b>. Sharing, copying, or external assistance is strictly prohibited.
</div>
<div class="slogan">हर एक जान अनमोल</div>
<div class="subtle">Compassion • Care • Clinical Excellence</div>
""", unsafe_allow_html=True)

# ================= STAFF INFO (8 HEADERS) =================
if not st.session_state.started:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Candidate Information")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Candidate Name *")
        dob = st.date_input("Date of Birth", min_value=date(1960,1,1), max_value=date.today())
        qualification = st.text_input("Qualification")
        category = st.selectbox("Category", ["Nursing", "Non-Nursing", "Other"])
    with col2:
        reg_no = st.text_input("Registration Number")
        reg_auth = st.selectbox("Registration Authority *", [
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
            "Uttarakhand Nurses & Midwives Council", "West Bengal Nursing Council", "Other"
        ])
        mobile = st.text_input("Mobile Number *")
        college = st.text_input("College")

    if st.button("Start Assessment"):
        if not name or not mobile or reg_auth == "Choose an option...":
            st.error("⚠️ Please fill Candidate Name, Mobile Number, and Registration Authority.")
        else:
            try:
                tech = pd.read_excel("questions.xlsx")
                beh = pd.read_excel("Behavioural_Questions_100_with_Competency.xlsx")
                t_q = tech.sample(20)
                b_q = beh.sample(5)
                st.session_state.questions = pd.concat([t_q, b_q]).sample(25).to_dict("records")
                st.session_state.candidate = {
                    "name": name, "dob": str(dob), "qualification": qualification, "category": category,
                    "reg_no": reg_no, "reg_auth": reg_auth, "mobile": mobile, "college": college
                }
                st.session_state.start_time = time.time()
                st.session_state.started = True
                st.rerun()
            except Exception as e:
                st.error(f"Excel Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# ================= EXAM INTERFACE (TIMERS) =================
elif not st.session_state.show_result:
    total_elapsed = time.time() - st.session_state.start_time
    total_remain = max(0, TOTAL_EXAM_TIME - total_elapsed)
    
    if st.session_state.q_start is None: st.session_state.q_start = time.time()
    q_elapsed = time.time() - st.session_state.q_start
    q_remain = max(0, DEFAULT_Q_TIME - q_elapsed)

    c1, c2 = st.columns(2)
    with c1: st.markdown(f"<div class='timer-box'>Total Exam: {int(total_remain//60)}m {int(total_remain%60)}s</div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='timer-box'>Question Time: {int(q_remain)}s</div>", unsafe_allow_html=True)

    if total_remain <= 0: 
        st.session_state.show_result = True
        st.rerun()

    q = st.session_state.questions[st.session_state.idx]
    st.markdown(f"<div class='card'><b>Question {st.session_state.idx+1} of 25</b><br><br>{q['question']}</div>", unsafe_allow_html=True)
    
    # Attempting Tips
    if st.session_state.idx < 3:
        st.info("💡 Clinical Tip: Always prioritize patient safety and hospital protocols.")

    choice = st.radio("Select Option:", [q["option_a"], q["option_b"], q["option_c"], q["option_d"]], key=f"q{st.session_state.idx}")

    if st.button("Next →") or q_remain <= 0:
        st.session_state.answers[f"Q{st.session_state.idx+1}"] = choice
        st.session_state.idx += 1
        st.session_state.q_start = None
        if st.session_state.idx >= 25: 
            st.session_state.show_result = True
        st.rerun()

# ================= RESULT & GOOGLE SYNC =================
else:
    correct = 0
    payload = {**st.session_state.candidate}
    for i in range(25):
        u_ans = st.session_state.answers.get(f"Q{i+1}")
        c_ans = st.session_state.questions[i]["correct_answer"]
        is_right = (u_ans == c_ans)
        if is_right: correct += 1
        payload[f"Q{i+1}"] = u_ans
        payload[f"Q{i+1}_is_correct"] = is_right

    duration_secs = int(time.time() - st.session_state.start_time)
    duration_str = f"{duration_secs//60}m {duration_secs%60}s"
    result_str = "PASSED" if correct >= PASS_MARK else "FAILED"
    
    # Column J, K, L Mapping
    payload.update({"score": f"{correct}/25", "duration": duration_str, "result": result_str})

    st.markdown(f"<div class='card' style='text-align:center;'><h2>Assessment Result: {result_status if 'result_status' in locals() else result_str}</h2><h1 style='color:#B30000;'>{correct}/25</h1></div>", unsafe_allow_html=True)
    
    # Final Result Tip
    if correct >= PASS_MARK:
        st.success("🎉 Professional Tip: Excellent work! Your clinical knowledge aligns with Medanta's excellence standards.")
    else:
        st.warning("📋 Professional Tip: We suggest reviewing basic clinical protocols and patient care standards.")

    if not st.session_state.submitted:
        try:
            r = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=20)
            if r.status_code == 200:
                st.session_state.submitted = True
                st.success("✓ Assessment data securely synced with Medanta Registry.")
        except:
            st.error("⚠️ Sync Error. Please capture a screenshot of this result.")

    if st.button("Finish & Logout"):
        st.session_state.clear()
        st.rerun()
